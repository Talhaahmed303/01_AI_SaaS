import os
import logging
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from .models import Document, DocumentChunk
from .serializers import DocumentSerializer, DocumentUploadSerializer, DocumentChunkSerializer
from .services.extractor import DocumentExtractor
from .services.chunker import DocumentChunker, EmbeddingService
from workspaces.models import Workspace, WorkspaceMembership
from usage.models import DailyUsage, UserQuota
from config.exceptions import QuotaExceededException

logger = logging.getLogger(__name__)

class DocumentUploadView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workspace_id = serializer.validated_data['workspace_id']
        file_obj = serializer.validated_data['file']

        # 1. Tenant/Workspace access verification
        workspace = get_object_or_404(Workspace, id=workspace_id)
        membership = workspace.memberships.filter(user=request.user).first()
        if not membership or membership.role == WorkspaceMembership.RoleChoices.VIEWER:
            return Response({
                'status': 'error',
                'code': 'PERMISSION_DENIED',
                'message': 'You lack permissions to upload documents to this workspace (Viewer role).'
            }, status=status.HTTP_403_FORBIDDEN)

        # 2. Quota check
        quota, _ = UserQuota.objects.get_or_create(user=request.user)
        current_docs_count = Document.objects.filter(workspace=workspace).count()
        if current_docs_count >= quota.max_documents:
            raise QuotaExceededException(
                f"Workspace document limit of {quota.max_documents} reached. Upgrade tier to expand storage."
            )

        # 3. File hash & deduplication check
        file_hash = DocumentExtractor.calculate_sha256(file_obj)
        existing_doc = Document.objects.filter(workspace=workspace, file_hash=file_hash).first()
        if existing_doc:
            return Response({
                'status': 'success',
                'code': 'DOCUMENT_ALREADY_EXISTS',
                'message': 'Document with identical SHA-256 fingerprint already exists and is indexed in this workspace.',
                'document': DocumentSerializer(existing_doc).data
            }, status=status.HTTP_200_OK)

        # 4. Save initial Document record
        ext = os.path.splitext(file_obj.name)[1].lower().replace('.', '')
        document = Document.objects.create(
            workspace=workspace,
            uploaded_by=request.user,
            file=file_obj,
            file_name=file_obj.name,
            file_type=ext,
            file_size=file_obj.size,
            file_hash=file_hash,
            status=Document.StatusChoices.PROCESSING
        )

        # 5. Ingestion Pipeline
        try:
            file_path = document.file.path
            pages = DocumentExtractor.extract(file_path, ext)
            chunks_data = DocumentChunker.chunk_pages(pages)

            if not chunks_data:
                document.status = Document.StatusChoices.FAILED
                document.error_message = "No extractable text found in uploaded document."
                document.save()
                return Response({
                    'status': 'error',
                    'code': 'EMPTY_DOCUMENT',
                    'message': 'The document contained no readable text.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Generate embeddings and prepare bulk records
            chunk_records = []
            total_tokens = 0
            api_key = getattr(settings, 'OPENAI_API_KEY', '')

            for item in chunks_data:
                embedding = EmbeddingService.generate_embedding(item['content'], api_key=api_key)
                chunk_records.append(DocumentChunk(
                    document=document,
                    chunk_index=item['chunk_index'],
                    content=item['content'],
                    page_number=item['page_number'],
                    token_count=item['token_count'],
                    embedding=embedding
                ))
                total_tokens += item['token_count']

            DocumentChunk.objects.bulk_create(chunk_records)

            # Update Document status
            document.status = Document.StatusChoices.INDEXED
            document.chunk_count = len(chunk_records)
            document.total_tokens = total_tokens
            document.summary = f"Indexed {len(chunk_records)} chunks across {len(pages)} page(s)."
            document.save()

            # Update daily usage tracking
            today = timezone.now().date()
            daily_usage, _ = DailyUsage.objects.get_or_create(user=request.user, date=today)
            daily_usage.documents_uploaded += 1
            daily_usage.save()

            return Response({
                'status': 'success',
                'message': f"Document '{document.file_name}' successfully processed and indexed into workspace.",
                'document': DocumentSerializer(document).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Ingestion failed for doc {document.id}: {str(e)}", exc_info=True)
            document.status = Document.StatusChoices.FAILED
            document.error_message = str(e)
            document.save()
            return Response({
                'status': 'error',
                'code': 'INGESTION_ERROR',
                'message': f"Failed to ingest document: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DocumentListView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, id=workspace_id, memberships__user=request.user)
        documents = Document.objects.filter(workspace=workspace).order_by('-created_at')
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

class DocumentDetailDeleteView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        document = get_object_or_404(Document, id=pk, workspace__memberships__user=request.user)
        return Response(DocumentSerializer(document).data)

    def delete(self, request, pk):
        document = get_object_or_404(Document, id=pk, workspace__memberships__user=request.user)
        membership = document.workspace.memberships.filter(user=request.user).first()
        if not membership or membership.role not in [WorkspaceMembership.RoleChoices.OWNER, WorkspaceMembership.RoleChoices.ADMIN]:
            return Response({'error': 'Only workspace Owners and Admins can delete documents.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Remove physical file if exists
        try:
            if document.file and os.path.exists(document.file.path):
                os.remove(document.file.path)
        except Exception:
            pass

        document.delete()
        return Response({'status': 'success', 'message': 'Document deleted successfully.'}, status=status.HTTP_200_OK)

class DocumentChunksListView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        document = get_object_or_404(Document, id=pk, workspace__memberships__user=request.user)
        chunks = document.chunks.all().order_by('chunk_index')
        return Response(DocumentChunkSerializer(chunks, many=True).data)
