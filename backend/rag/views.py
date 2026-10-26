from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer, AskQuestionSerializer
from .services.rag_engine import RAGEngine
from workspaces.models import Workspace

class AskQuestionView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = AskQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workspace_id = serializer.validated_data['workspace_id']
        session_id = serializer.validated_data.get('session_id')
        query = serializer.validated_data['query']

        # Multi-tenant isolation verification
        workspace = get_object_or_404(Workspace, id=workspace_id, memberships__user=request.user)

        # Get or create chat session
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, workspace=workspace, user=request.user)
        else:
            title = query[:40] + ("..." if len(query) > 40 else "")
            session = ChatSession.objects.create(
                workspace=workspace,
                user=request.user,
                title=title
            )

        # Execute grounded RAG pipeline
        result = RAGEngine.answer_query(
            session=session,
            user=request.user,
            query=query
        )

        return Response({
            'status': 'success',
            'session_id': str(session.id),
            'session_title': session.title,
            **result
        }, status=status.HTTP_200_OK)

class ChatSessionListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChatSessionSerializer

    def get_queryset(self):
        workspace_id = self.request.query_params.get('workspace_id')
        qs = ChatSession.objects.filter(user=self.request.user)
        if workspace_id:
            qs = qs.filter(workspace_id=workspace_id)
        return qs.order_by('-updated_at')

    def perform_create(self, serializer):
        workspace_id = self.request.data.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id, memberships__user=self.request.user)
        serializer.save(user=self.request.user, workspace=workspace)

class ChatSessionDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        session = get_object_or_404(ChatSession, id=pk, user=request.user)
        messages = session.messages.all().order_by('created_at')
        return Response({
            'session': ChatSessionSerializer(session).data,
            'messages': ChatMessageSerializer(messages, many=True).data
        })

    def delete(self, request, pk):
        session = get_object_or_404(ChatSession, id=pk, user=request.user)
        session.delete()
        return Response({'status': 'success', 'message': 'Chat session deleted.'}, status=status.HTTP_200_OK)
