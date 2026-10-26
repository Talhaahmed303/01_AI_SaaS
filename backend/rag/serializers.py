from rest_framework import serializers
from .models import ChatSession, ChatMessage, MessageCitation

class MessageCitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageCitation
        fields = ('id', 'document_title', 'page_number', 'relevance_score', 'cited_text')

class ChatMessageSerializer(serializers.ModelSerializer):
    citations = MessageCitationSerializer(many=True, read_only=True)

    class Meta:
        model = ChatMessage
        fields = (
            'id', 'sender', 'content', 'model_used', 'prompt_tokens',
            'completion_tokens', 'total_tokens', 'latency_ms', 'is_fallback',
            'citations', 'created_at'
        )

class ChatSessionSerializer(serializers.ModelSerializer):
    messages_count = serializers.IntegerField(source='messages.count', read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ('id', 'workspace', 'title', 'messages_count', 'last_message', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_last_message(self, obj):
        msg = obj.messages.last()
        return msg.content[:80] if msg else None

class AskQuestionSerializer(serializers.Serializer):
    workspace_id = serializers.UUIDField()
    session_id = serializers.UUIDField(required=False, allow_null=True)
    query = serializers.CharField(min_length=2, max_length=2000)
