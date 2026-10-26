from rest_framework import serializers
from .models import Document, DocumentChunk
from workspaces.models import Workspace

class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = ('id', 'chunk_index', 'content', 'page_number', 'token_count', 'created_at')

class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    file_size_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            'id', 'workspace', 'workspace_name', 'uploaded_by', 'uploaded_by_email',
            'file', 'file_name', 'file_type', 'file_size', 'file_size_formatted',
            'file_hash', 'status', 'error_message', 'chunk_count', 'total_tokens',
            'summary', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'file_hash', 'status', 'error_message', 'chunk_count', 'total_tokens', 'created_at', 'updated_at')

    def get_file_size_formatted(self, obj):
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

class DocumentUploadSerializer(serializers.Serializer):
    workspace_id = serializers.UUIDField()
    file = serializers.FileField()

    def validate_file(self, value):
        # 10 MB limit check
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size exceeds maximum allowed threshold of 10 MB.")
        
        allowed_extensions = ['.pdf', '.txt', '.docx', '.md', '.markdown']
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(f"Unsupported file format '{ext}'. Allowed formats: {', '.join(allowed_extensions)}")
        return value
