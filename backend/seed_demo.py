import os
import django
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from workspaces.models import Workspace, WorkspaceMembership
from documents.models import Document, DocumentChunk
from documents.services.chunker import DocumentChunker, EmbeddingService
from documents.services.extractor import DocumentExtractor
from rag.models import ChatSession, ChatMessage, MessageCitation
from usage.models import UserQuota, DailyUsage
from django.utils import timezone

User = get_user_model()

def seed():
    print("[*] Starting Seed Script for FalconXoft AI SaaS Workspace...")

    # 1. Admin User
    admin_user, created = User.objects.get_or_create(
        email='admin@falconsaas.io',
        defaults={
            'username': 'admin',
            'full_name': 'Chief Architect Alex',
            'tier': 'ENTERPRISE',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('AdminPass123!')
        admin_user.save()
        print("  [OK] Created Admin User: admin@falconsaas.io / AdminPass123!")

    admin_quota, _ = UserQuota.objects.get_or_create(
        user=admin_user,
        defaults={
            'tier': 'ENTERPRISE',
            'daily_query_limit': 10000,
            'daily_token_limit': 5000000,
            'max_documents': 100
        }
    )

    # 2. Member User (Free Tier)
    member_user, created = User.objects.get_or_create(
        email='member@falconsaas.io',
        defaults={
            'username': 'member',
            'full_name': 'Sarah Engineer',
            'tier': 'FREE'
        }
    )
    if created:
        member_user.set_password('MemberPass123!')
        member_user.save()
        print("  [OK] Created Member User: member@falconsaas.io / MemberPass123!")

    member_quota, _ = UserQuota.objects.get_or_create(
        user=member_user,
        defaults={
            'tier': 'FREE',
            'daily_query_limit': 25,
            'daily_token_limit': 50000,
            'max_documents': 10
        }
    )

    # 3. Workspaces
    ws_eng, _ = Workspace.objects.get_or_create(
        name="Falcon Architecture & Platform",
        defaults={
            'slug': 'falcon-architecture',
            'description': 'Technical design specifications, cloud infrastructure blueprints, and microservice guidelines.',
            'owner': admin_user
        }
    )
    WorkspaceMembership.objects.get_or_create(
        workspace=ws_eng,
        user=admin_user,
        defaults={'role': WorkspaceMembership.RoleChoices.OWNER}
    )
    WorkspaceMembership.objects.get_or_create(
        workspace=ws_eng,
        user=member_user,
        defaults={'role': WorkspaceMembership.RoleChoices.MEMBER}
    )

    ws_legal, _ = Workspace.objects.get_or_create(
        name="Security & Compliance Vault",
        defaults={
            'slug': 'security-compliance',
            'description': 'SOC2 policies, tenant isolation standards, GDPR retention guidelines, and audit checklists.',
            'owner': admin_user
        }
    )
    WorkspaceMembership.objects.get_or_create(
        workspace=ws_legal,
        user=admin_user,
        defaults={'role': WorkspaceMembership.RoleChoices.OWNER}
    )

    # 4. Seed Documents into Architecture Workspace
    doc1_content = """# FalconXoft Cloud Infrastructure Specification v2.4

## 1. Core Hosting & Compute Topology
FalconXoft runs on a hybrid deployment model. The primary production API gateway operates on AWS eu-central-1 (Frankfurt) using containerized ECS Fargate tasks with automated horizontal pod autoscaling (HPA) configured between 2 and 20 worker nodes.

Secondary lightweight services and edge workers run on dedicated VPS nodes hosted in Falkenstein via Hetzner Cloud for cost efficiency, saving 65% on non-peak background worker workloads.

## 2. Database & Data Isolation
The relational persistence tier uses PostgreSQL 18 with SSL encryption in transit (TLS 1.3) and AES-256 encryption at rest. Multi-tenancy is enforced via strict Workspace Boundaries: every query includes a foreign key constraint to `workspace_id`. Cross-workspace queries are blocked at both ORM level and database row-level security (RLS).

## 3. Storage & Object Lifecycle
Uploaded documents (PDFs, DOCX, TXT) are verified for MIME integrity, scanned for malicious byte sequences, and hashed with SHA-256 for deduplication. Documents are chunked into 400-token blocks with 50-token semantic overlap.

## 4. Disaster Recovery & Backups
Continuous write-ahead log (WAL) archiving allows point-in-time recovery (PITR) up to 14 days with an RPO of under 5 minutes and an RTO of under 15 minutes. Daily automated snapshots are replicated to a geographically isolated S3 cold storage bucket in eu-west-1 (Ireland).
"""

    doc1_file = ContentFile(doc1_content.encode('utf-8'), name="FalconXoft_Cloud_Architecture.md")
    doc1_hash = DocumentExtractor.calculate_sha256(doc1_file)

    doc1, created = Document.objects.get_or_create(
        workspace=ws_eng,
        file_hash=doc1_hash,
        defaults={
            'file': doc1_file,
            'file_name': 'FalconXoft_Cloud_Architecture.md',
            'file_type': 'md',
            'file_size': len(doc1_content),
            'uploaded_by': admin_user,
            'status': Document.StatusChoices.PROCESSING
        }
    )

    if created:
        pages = DocumentExtractor.extract(doc1.file.path, 'md')
        chunks_data = DocumentChunker.chunk_pages(pages)
        chunk_records = []
        tot_tokens = 0
        for item in chunks_data:
            emb = EmbeddingService.generate_embedding(item['content'])
            chunk_records.append(DocumentChunk(
                document=doc1,
                chunk_index=item['chunk_index'],
                content=item['content'],
                page_number=item['page_number'],
                token_count=item['token_count'],
                embedding=emb
            ))
            tot_tokens += item['token_count']
        DocumentChunk.objects.bulk_create(chunk_records)
        doc1.status = Document.StatusChoices.INDEXED
        doc1.chunk_count = len(chunk_records)
        doc1.total_tokens = tot_tokens
        doc1.summary = f"Indexed {len(chunk_records)} chunks."
        doc1.save()
        print(f"  [OK] Seeded & Indexed Document: {doc1.file_name} ({len(chunk_records)} chunks)")

    # 5. Seed a Pre-existing Chat Session with Citations
    session, _ = ChatSession.objects.get_or_create(
        workspace=ws_eng,
        user=member_user,
        title="Inquiry on Disaster Recovery and RPO"
    )

    if not session.messages.exists():
        q_text = "What is our disaster recovery RPO and where are backups stored?"
        ChatMessage.objects.create(
            session=session,
            sender=ChatMessage.SenderChoices.USER,
            content=q_text,
            total_tokens=18
        )
        ai_resp = ChatMessage.objects.create(
            session=session,
            sender=ChatMessage.SenderChoices.ASSISTANT,
            content=(
                "Based on the **FalconXoft_Cloud_Architecture.md** documentation (Page 1):\n\n"
                "- **Recovery Point Objective (RPO):** Under **5 minutes**, enabled via continuous Write-Ahead Log (WAL) archiving for Point-In-Time Recovery (PITR) up to 14 days.\n"
                "- **Recovery Time Objective (RTO):** Under **15 minutes**.\n"
                "- **Backup Storage Location:** Daily automated snapshots are replicated to a geographically isolated S3 cold storage bucket in **eu-west-1 (Ireland)**."
            ),
            model_used='local-grounded-synthesizer-v1 (fallback)',
            prompt_tokens=420,
            completion_tokens=85,
            total_tokens=505,
            latency_ms=280,
            is_fallback=True
        )
        chunk = doc1.chunks.first()
        if chunk:
            MessageCitation.objects.create(
                message=ai_resp,
                chunk=chunk,
                document_title=doc1.file_name,
                page_number=1,
                relevance_score=0.92,
                cited_text="Continuous write-ahead log (WAL) archiving allows point-in-time recovery (PITR) up to 14 days with an RPO of under 5 minutes..."
            )
        print("  [OK] Seeded verified Chat Session with Grounded Citations")

    # 6. Initialize Today's Usage record
    today = timezone.now().date()
    DailyUsage.objects.get_or_create(
        user=member_user,
        date=today,
        defaults={'queries_used': 3, 'tokens_used': 1515, 'documents_uploaded': 1}
    )

    print("[SUCCESS] Seeding complete! All demo data loaded into PostgreSQL.")

if __name__ == '__main__':
    seed()
