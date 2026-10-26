# FalconXoft AI SaaS Workspace — Database Design & ERD Specification
**Weekend 2 Intern Engineering Evaluation | Project 1**  
**Author:** Engineering Evaluation Candidate  
**Target Engine:** PostgreSQL 18.3 (ACID-Compliant Relational Store)  
**Schema Dump File:** [`03 - schema.sql`](./03%20-%20schema.sql) (1,349 lines of executable DDL)  
**Lucidchart Editable URL Reference:** [https://lucid.app/lucidchart/461d616a-0e24-427c-b3ff-982f809db8ea/edit?viewport_loc=-852%2C112%2C4776%2C2316%2C0_0&invitationId=inv_a714faba-a61b-4cb5-b1fd-687c6c5d68f9](https://lucid.app/lucidchart/461d616a-0e24-427c-b3ff-982f809db8ea/edit?viewport_loc=-852%2C112%2C4776%2C2316%2C0_0&invitationId=inv_a714faba-a61b-4cb5-b1fd-687c6c5d68f9)  
**Exported Artifacts:** [`03 - database-design.png`](./03%20-%20database-design.png) | [`03 - database-design.pdf`](./03%20-%20database-design.pdf)

---

## 1. Entity-Relationship Diagram (Mermaid ERD)

```mermaid
erDiagram
    auth_users ||--o{ workspaces : "owns"
    auth_users ||--o{ workspace_memberships : "has"
    auth_users ||--o| user_quotas : "governed_by"
    auth_users ||--o{ daily_usage_records : "accumulates"
    auth_users ||--o{ audit_request_logs : "initiates"

    workspaces ||--o{ workspace_memberships : "contains"
    workspaces ||--o{ documents : "partitions"
    workspaces ||--o{ chat_sessions : "hosts"

    documents ||--o{ document_chunks : "chunked_into"
    documents }o--|| auth_users : "uploaded_by"

    chat_sessions ||--o{ chat_messages : "contains"
    chat_sessions }o--|| auth_users : "created_by"

    chat_messages ||--o{ message_citations : "cites"
    document_chunks ||--o{ message_citations : "referenced_in"

    auth_users {
        uuid id PK
        string email UK
        string username UK
        string password_hash
        string full_name
        string tier
        boolean is_active
        timestamp created_at
    }

    user_quotas {
        bigint id PK
        uuid user_id FK, UK
        string tier
        int daily_query_limit
        int daily_token_limit
        int max_upload_size_mb
        int max_documents
        int rate_limit_per_minute
    }

    workspaces {
        uuid id PK
        string name
        string slug UK
        text description
        uuid owner_id FK
        boolean is_active
        timestamp created_at
    }

    workspace_memberships {
        uuid id PK
        uuid workspace_id FK
        uuid user_id FK
        string role "OWNER, ADMIN, MEMBER, VIEWER"
        timestamp joined_at
    }

    documents {
        uuid id PK
        uuid workspace_id FK
        uuid uploaded_by_id FK
        string file_name
        string file_type
        bigint file_size
        string file_hash "SHA-256 Checksum"
        string status "PENDING, PROCESSING, INDEXED, FAILED"
        int chunk_count
        int total_tokens
        text summary
        timestamp created_at
    }

    document_chunks {
        uuid id PK
        uuid document_id FK
        int chunk_index
        text content
        int page_number
        int token_count
        jsonb embedding "384-dim Normalized Float Array"
        timestamp created_at
    }

    chat_sessions {
        uuid id PK
        uuid workspace_id FK
        uuid user_id FK
        string title
        timestamp created_at
        timestamp updated_at
    }

    chat_messages {
        uuid id PK
        uuid session_id FK
        string sender "USER, ASSISTANT, SYSTEM"
        text content
        string model_used
        int prompt_tokens
        int completion_tokens
        int total_tokens
        int latency_ms
        boolean is_fallback
        timestamp created_at
    }

    message_citations {
        uuid id PK
        uuid message_id FK
        uuid chunk_id FK
        string document_title
        int page_number
        float relevance_score
        text cited_text
    }

    daily_usage_records {
        bigint id PK
        uuid user_id FK
        date date
        int queries_used
        int tokens_used
        int documents_uploaded
        timestamp last_request_at
    }

    audit_request_logs {
        uuid id PK
        uuid user_id FK
        uuid workspace_id FK
        string endpoint
        string method
        int status_code
        inet ip_address
        int latency_ms
        int tokens_consumed
        text error_details
        timestamp created_at
    }
```

---

## 2. Table Specifications, Constraints & Indexing Strategy

### Table: `workspaces` (Multi-Tenant Partition Root)
- **Primary Key**: `id` (`UUID DEFAULT gen_random_uuid()`)
- **Fields**:
  - `name VARCHAR(150) NOT NULL`
  - `slug VARCHAR(180) UNIQUE NOT NULL` (indexed)
  - `description TEXT DEFAULT ''`
  - `owner_id UUID NOT NULL REFERENCES auth_users(id) ON DELETE CASCADE`
  - `is_active BOOLEAN DEFAULT TRUE`
  - `created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()`
- **Indexes**:
  - `workspaces_slug_idx` ON `slug`
  - `workspaces_owner_idx` ON `owner_id`

### Table: `workspace_memberships` (RBAC Junction)
- **Primary Key**: `id` (`UUID`)
- **Fields**:
  - `workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE`
  - `user_id UUID REFERENCES auth_users(id) ON DELETE CASCADE`
  - `role VARCHAR(20) NOT NULL CHECK (role IN ('OWNER', 'ADMIN', 'MEMBER', 'VIEWER'))`
  - `joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()`
- **Constraints & Indexes**:
  - `UNIQUE (workspace_id, user_id)` — Guarantees a user cannot have duplicate memberships in the same workspace.

### Table: `documents` (Workspace Knowledge Artifacts)
- **Primary Key**: `id` (`UUID`)
- **Fields**:
  - `workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE`
  - `uploaded_by_id UUID NULL REFERENCES auth_users(id) ON DELETE SET NULL`
  - `file VARCHAR(255) NOT NULL`
  - `file_name VARCHAR(255) NOT NULL`
  - `file_type VARCHAR(50) NOT NULL` (`pdf`, `docx`, `txt`, `md`)
  - `file_size BIGINT NOT NULL` (bytes)
  - `file_hash VARCHAR(64) NOT NULL` (SHA-256 hexadecimal string)
  - `status VARCHAR(20) NOT NULL DEFAULT 'PENDING'` (`PENDING`, `PROCESSING`, `INDEXED`, `FAILED`)
  - `chunk_count INT DEFAULT 0`
  - `total_tokens INT DEFAULT 0`
  - `error_message TEXT NULL`
  - `summary TEXT DEFAULT ''`
  - `created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()`
- **Compound Indexes for Multi-Tenant Query Optimization**:
  - `documents_workspace_status_idx` ON `(workspace_id, status)` — Optimizes RAG retrieval candidates.
  - `documents_workspace_hash_idx` ON `(workspace_id, file_hash)` — Instant O(1) deduplication lookup during upload.

### Table: `document_chunks` (Semantic Segment Store)
- **Primary Key**: `id` (`UUID`)
- **Fields**:
  - `document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE`
  - `chunk_index INT NOT NULL`
  - `content TEXT NOT NULL`
  - `page_number INT NULL`
  - `token_count INT DEFAULT 0`
  - `embedding JSONB NULL` (384-dimensional normalized float array)
  - `created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()`
- **Indexes**:
  - `document_chunk_doc_idx` ON `(document_id, chunk_index)`

### Table: `daily_usage_records` (Quota Enforcement)
- **Primary Key**: `id` (`BIGINT GENERATED ALWAYS AS IDENTITY`)
- **Fields**:
  - `user_id UUID NOT NULL REFERENCES auth_users(id) ON DELETE CASCADE`
  - `date DATE NOT NULL`
  - `queries_used INT DEFAULT 0`
  - `tokens_used INT DEFAULT 0`
  - `documents_uploaded INT DEFAULT 0`
  - `last_request_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()`
- **Constraints & Indexes**:
  - `UNIQUE (user_id, date)` — Eliminates race conditions in daily rollups.
  - `daily_usage_user_date_idx` ON `(user_id, date)`

---

## 3. Data Integrity & Concurrency Guarantees

1. **Multi-Tenant Boundary Enforcement**:
   - Every file read, chunk retrieval, and chat query enforces `WHERE workspace_id = :active_workspace`.
   - Users cannot join workspaces without an explicit invite/admin membership row.

2. **Deduplication via Cryptographic Hashing**:
   - Files are hashed via SHA-256 before disk writes. If `documents.objects.filter(workspace=ws, file_hash=hash).exists()`, the backend returns the existing document immediately, avoiding redundant re-chunking and vector re-indexing.

3. **Atomic Quota Updates & Concurrency**:
   - Quota tracking uses database transactions with Django `F()` expressions or atomic increments (`queries_used = queries_used + 1`) to prevent lost updates under concurrent API invocations.

4. **Executable Schema Dump**:
   - The full, executable PostgreSQL DDL dump is exported at [`03 - schema.sql`](./03%20-%20schema.sql) and validated against PostgreSQL 18.
