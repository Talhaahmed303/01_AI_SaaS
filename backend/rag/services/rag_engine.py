import time
import re
import logging
from typing import List, Dict, Any, Tuple
from django.conf import settings
from django.utils import timezone
from documents.models import DocumentChunk, Document
from documents.services.chunker import EmbeddingService
from rag.models import ChatSession, ChatMessage, MessageCitation
from usage.models import DailyUsage, UserQuota
from config.exceptions import QuotaExceededException, ServiceFailureException

logger = logging.getLogger(__name__)

class RAGEngine:
    """
    Enterprise-grade RAG Engine implementing:
    - Multi-tenant workspace data boundary isolation
    - Semantic similarity matching & chunk retrieval
    - Prompt injection defense & boundary sandboxing
    - Unsupported question detection & explicit refusal
    - Provider failure resilience & deterministic local fallback
    - Real-time token accounting & quota tracking
    """
    SIMILARITY_THRESHOLD = 0.20  # Minimum similarity threshold to consider content relevant
    MAX_CONTEXT_CHUNKS = 4
    MAX_CONTEXT_TOKENS = 3000

    INJECTION_PATTERNS = [
        r'ignore\s+all\s+previous\s+instructions',
        r'ignore\s+previous\s+instructions',
        r'system\s+override',
        r'you\s+are\s+now\s+in\s+developer\s+mode',
        r'jailbreak',
        r'reveal\s+your\s+system\s+prompt',
        r'<\|endoftext\|>'
    ]

    @classmethod
    def sanitize_input(cls, query: str) -> Tuple[str, bool]:
        """
        Scans and sanitizes user prompt against adversarial injections.
        Returns (cleaned_query, is_injection_detected).
        """
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                logger.warning(f"Adversarial prompt injection pattern detected: '{pattern}'")
                return query, True
        return query, False

    @classmethod
    def check_user_quota(cls, user) -> None:
        """
        Enforces per-user daily query and token limits before executing inference.
        """
        quota, _ = UserQuota.objects.get_or_create(user=user)
        today = timezone.now().date()
        daily_usage, _ = DailyUsage.objects.get_or_create(user=user, date=today)

        if daily_usage.queries_used >= quota.daily_query_limit:
            raise QuotaExceededException(
                f"You have reached your daily query quota ({quota.daily_query_limit} queries/day). Upgrade to Pro or Enterprise for higher limits."
            )

        if daily_usage.tokens_used >= quota.daily_token_limit:
            raise QuotaExceededException(
                f"You have exhausted your daily token budget ({quota.daily_token_limit} tokens/day). Upgrade tier to continue."
            )

    @classmethod
    def retrieve_chunks(cls, workspace_id, query: str) -> List[Dict[str, Any]]:
        """
        Retrieves top relevant chunks strictly isolated within the target workspace.
        """
        api_key = getattr(settings, 'OPENAI_API_KEY', '')
        query_embedding = EmbeddingService.generate_embedding(query, api_key=api_key)

        # Scoped strictly to workspace documents
        chunks = DocumentChunk.objects.filter(
            document__workspace_id=workspace_id,
            document__status=Document.StatusChoices.INDEXED
        ).select_related('document')

        scored_chunks = []
        query_words = set(re.findall(r'\b\w{3,}\b', query.lower()))

        for chunk in chunks:
            if not chunk.embedding:
                continue

            sim = EmbeddingService.cosine_similarity(query_embedding, chunk.embedding)
            
            # Keyword overlap boost
            content_lower = chunk.content.lower()
            keyword_matches = sum(1 for w in query_words if w in content_lower)
            if query_words:
                sim += (keyword_matches / len(query_words)) * 0.15

            scored_chunks.append({
                'chunk': chunk,
                'score': sim,
                'content': chunk.content,
                'page_number': chunk.page_number,
                'document_title': chunk.document.file_name,
                'token_count': chunk.token_count
            })

        # Sort descending by relevance score
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        return scored_chunks[:cls.MAX_CONTEXT_CHUNKS]

    @classmethod
    def answer_query(cls, session: ChatSession, user, query: str) -> Dict[str, Any]:
        start_time = time.time()

        # 1. Enforce Quota
        cls.check_user_quota(user)

        # 2. Defense against Prompt Injection
        cleaned_query, injection_detected = cls.sanitize_input(query)
        if injection_detected:
            return cls._handle_security_violation(session, user, query, start_time)

        # 3. Retrieve Candidate Context Chunks
        candidate_chunks = cls.retrieve_chunks(session.workspace_id, cleaned_query)

        # 4. Clear Handling of Unsupported Answers
        top_score = candidate_chunks[0]['score'] if candidate_chunks else 0.0
        if not candidate_chunks or top_score < cls.SIMILARITY_THRESHOLD:
            return cls._handle_unsupported_answer(session, user, query, start_time)

        # 5. Build Context and Token Window
        context_blocks = []
        citations_to_save = []
        accumulated_tokens = 0

        for item in candidate_chunks:
            if accumulated_tokens + item['token_count'] > cls.MAX_CONTEXT_TOKENS:
                break
            context_blocks.append(
                f"[Source: {item['document_title']} | Page: {item['page_number'] or 1}]\n{item['content']}"
            )
            citations_to_save.append(item)
            accumulated_tokens += item['token_count']

        context_text = "\n\n---\n\n".join(context_blocks)

        # 6. Call LLM or Seamless Local Synthesizer Fallback
        answer_text, model_name, is_fallback, prompt_toks, comp_toks = cls._generate_response(
            query=cleaned_query,
            context=context_text,
            citations=citations_to_save
        )

        total_tokens = prompt_toks + comp_toks
        latency_ms = int((time.time() - start_time) * 1000)

        # 7. Persist User Message and AI Assistant Message
        user_msg = ChatMessage.objects.create(
            session=session,
            sender=ChatMessage.SenderChoices.USER,
            content=query,
            total_tokens=prompt_toks
        )

        ai_msg = ChatMessage.objects.create(
            session=session,
            sender=ChatMessage.SenderChoices.ASSISTANT,
            content=answer_text,
            model_used=model_name,
            prompt_tokens=prompt_toks,
            completion_tokens=comp_toks,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            is_fallback=is_fallback
        )

        # 8. Store Citations
        saved_citations = []
        for cite in citations_to_save:
            c = MessageCitation.objects.create(
                message=ai_msg,
                chunk=cite['chunk'],
                document_title=cite['document_title'],
                page_number=cite['page_number'],
                relevance_score=cite['score'],
                cited_text=cite['content'][:300]
            )
            saved_citations.append({
                'id': str(c.id),
                'document_title': c.document_title,
                'page_number': c.page_number,
                'relevance_score': round(c.relevance_score, 3),
                'snippet': c.cited_text
            })

        # 9. Deduct Quota Usage
        today = timezone.now().date()
        daily_usage, _ = DailyUsage.objects.get_or_create(user=user, date=today)
        daily_usage.queries_used += 1
        daily_usage.tokens_used += total_tokens
        daily_usage.save()

        return {
            'user_message_id': str(user_msg.id),
            'message_id': str(ai_msg.id),
            'answer': answer_text,
            'citations': saved_citations,
            'model_used': model_name,
            'is_fallback': is_fallback,
            'latency_ms': latency_ms,
            'prompt_tokens': prompt_toks,
            'completion_tokens': comp_toks,
            'total_tokens': total_tokens
        }

    @classmethod
    def _generate_response(cls, query: str, context: str, citations: List[Dict[str, Any]]) -> Tuple[str, str, bool, int, int]:
        """
        Attempts OpenAI generation with timeout and error trapping.
        Falls back smoothly to grounded local synthesis if key missing, invalid, or service down.
        """
        api_key = getattr(settings, 'OPENAI_API_KEY', '')
        if api_key and api_key.startswith('sk-'):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key, timeout=12.0)
                
                system_prompt = (
                    "You are Falcon AI, an enterprise assistant strictly grounded in the provided workspace documents.\n"
                    "INSTRUCTIONS:\n"
                    "1. Answer the user question using ONLY the verified context below.\n"
                    "2. If the context does not contain sufficient facts to answer accurately, explicitly state:\n"
                    "   'I cannot answer this question based on the documents currently uploaded to this workspace.'\n"
                    "3. Cite sources inline using [Source: <filename>, Page: <page>].\n"
                    "4. Do NOT speculate or extrapolate beyond what is stated in the context."
                )

                response = client.chat.completions.create(
                    model=getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini'),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"<workspace_documents>\n{context}\n</workspace_documents>\n\nUser Question: {query}"}
                    ],
                    temperature=0.2,
                    max_tokens=600
                )
                answer = response.choices[0].message.content
                prompt_toks = response.usage.prompt_tokens
                comp_toks = response.usage.completion_tokens
                return answer, getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini'), False, prompt_toks, comp_toks
            except Exception as e:
                logger.warning(f"OpenAI call failed ({str(e)}). Engaging deterministic grounded fallback engine.")

        # Built-in deterministic grounded synthesizer (Fallback Mode)
        return cls._local_grounded_synthesizer(query, citations)

    @classmethod
    def _local_grounded_synthesizer(cls, query: str, citations: List[Dict[str, Any]]) -> Tuple[str, str, bool, int, int]:
        """
        Synthesizes a clean, grounded answer directly from retrieved chunks without hallucination.
        """
        primary = citations[0]
        doc_name = primary['document_title']
        page_num = primary['page_number'] or 1
        
        # Extract the most salient sentences
        sentences = [s.strip() for s in primary['content'].split('.') if len(s.strip()) > 15]
        query_words = set(re.findall(r'\b\w{3,}\b', query.lower()))
        
        scored_sentences = []
        for s in sentences:
            score = sum(1 for w in query_words if w in s.lower())
            scored_sentences.append((score, s))
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        
        top_sentences = [s[1] for s in scored_sentences[:3]]
        extracted_facts = ". ".join(top_sentences) + "." if top_sentences else primary['content'][:300] + "..."

        answer = (
            f"Based on the workspace document **{doc_name}** (Page {page_num}), here is the verified information:\n\n"
            f"> {extracted_facts}\n\n"
            f"*Citation: [{doc_name}, Page {page_num} — Relevance Match: {int(primary['score'] * 100)}%]*"
        )

        prompt_tokens = len(query) // 4 + 400
        comp_tokens = len(answer) // 4
        return answer, "local-grounded-synthesizer-v1 (fallback)", True, prompt_tokens, comp_tokens

    @classmethod
    def _handle_unsupported_answer(cls, session: ChatSession, user, query: str, start_time: float) -> Dict[str, Any]:
        """
        Handles unsupported questions where workspace lacks sufficient grounded data.
        """
        latency_ms = int((time.time() - start_time) * 1000)
        refusal_text = (
            "⚠️ **Unsupported Query Refusal**\n\n"
            "I cannot answer this question based on the documents currently uploaded to this workspace. "
            "The verified materials in this workspace do not contain sufficient information regarding your query.\n\n"
            "**Suggested Actions:**\n"
            "- Upload relevant documents (PDF, DOCX, TXT) containing the necessary data.\n"
            "- Check if the target document has finished indexing.\n"
            "- Refine your question with specific keywords found in the workspace files."
        )

        user_msg = ChatMessage.objects.create(
            session=session,
            sender=ChatMessage.SenderChoices.USER,
            content=query,
            total_tokens=len(query) // 4
        )

        ai_msg = ChatMessage.objects.create(
            session=session,
            sender=ChatMessage.SenderChoices.ASSISTANT,
            content=refusal_text,
            model_used='grounding-guardrail',
            prompt_tokens=len(query) // 4,
            completion_tokens=len(refusal_text) // 4,
            total_tokens=(len(query) + len(refusal_text)) // 4,
            latency_ms=latency_ms,
            is_fallback=True
        )

        # Track usage
        today = timezone.now().date()
        daily_usage, _ = DailyUsage.objects.get_or_create(user=user, date=today)
        daily_usage.queries_used += 1
        daily_usage.save()

        return {
            'user_message_id': str(user_msg.id),
            'message_id': str(ai_msg.id),
            'answer': refusal_text,
            'citations': [],
            'model_used': 'grounding-guardrail',
            'is_fallback': True,
            'latency_ms': latency_ms,
            'prompt_tokens': len(query) // 4,
            'completion_tokens': len(refusal_text) // 4,
            'total_tokens': (len(query) + len(refusal_text)) // 4
        }

    @classmethod
    def _handle_security_violation(cls, session: ChatSession, user, query: str, start_time: float) -> Dict[str, Any]:
        latency_ms = int((time.time() - start_time) * 1000)
        warning_text = (
            "🛑 **Security Violation: Adversarial Prompt Injection Blocked**\n\n"
            "Your inquiry matched restricted prompt injection or system override patterns. "
            "For corporate compliance and safety, queries attempting to alter system instructions are rejected."
        )

        user_msg = ChatMessage.objects.create(
            session=session,
            sender=ChatMessage.SenderChoices.USER,
            content=query,
            total_tokens=len(query) // 4
        )

        ai_msg = ChatMessage.objects.create(
            session=session,
            sender=ChatMessage.SenderChoices.ASSISTANT,
            content=warning_text,
            model_used='injection-defense-guardrail',
            prompt_tokens=len(query) // 4,
            completion_tokens=len(warning_text) // 4,
            total_tokens=(len(query) + len(warning_text)) // 4,
            latency_ms=latency_ms,
            is_fallback=True
        )

        return {
            'user_message_id': str(user_msg.id),
            'message_id': str(ai_msg.id),
            'answer': warning_text,
            'citations': [],
            'model_used': 'injection-defense-guardrail',
            'is_fallback': True,
            'latency_ms': latency_ms,
            'prompt_tokens': len(query) // 4,
            'completion_tokens': len(warning_text) // 4,
            'total_tokens': (len(query) + len(warning_text)) // 4
        }
