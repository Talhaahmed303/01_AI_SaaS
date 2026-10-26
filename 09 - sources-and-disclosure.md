# FalconXoft AI SaaS Workspace — Sources, Licenses & AI Disclosure
**Weekend 2 Intern Engineering Evaluation | Project 1**  
**Author:** Engineering Evaluation Candidate  
**Submission Date:** October 25, 2026

---

## 1. Third-Party Technical Documentation & Pricing Sources

All pricing benchmarks and architectural specifications are grounded in verified, real-world documentation. No pricing figures were invented.

| Resource / Vendor | Scope & Verification | Live URL Reference | Date Accessed |
| :--- | :--- | :--- | :--- |
| **AWS Fargate** | Serverless container compute pricing (vCPU / GB-hour) | [https://aws.amazon.com/fargate/pricing/](https://aws.amazon.com/fargate/pricing/) | October 24, 2026 |
| **AWS RDS PostgreSQL** | Multi-AZ db.t4g.medium instance and backup storage | [https://aws.amazon.com/rds/postgresql/pricing/](https://aws.amazon.com/rds/postgresql/pricing/) | October 24, 2026 |
| **AWS S3** | Standard object storage tiers and egress bandwidth | [https://aws.amazon.com/s3/pricing/](https://aws.amazon.com/s3/pricing/) | October 24, 2026 |
| **Hetzner Cloud** | CPX21 and CPX31 AMD EPYC cloud compute instances | [https://www.hetzner.com/cloud/](https://www.hetzner.com/cloud/) | October 24, 2026 |
| **OpenAI API** | `gpt-4o-mini` and `text-embedding-3-small` token rates | [https://openai.com/api/pricing/](https://openai.com/api/pricing/) | October 24, 2026 |
| **Cloudflare Registrar** | Domain registration and DNS / WAF edge services | [https://www.cloudflare.com/products/registrar/](https://www.cloudflare.com/products/registrar/) | October 24, 2026 |
| **PostgreSQL 18** | Relational documentation, indexing, and WAL archiving | [https://www.postgresql.org/docs/18/](https://www.postgresql.org/docs/18/) | October 24, 2026 |
| **Django REST Framework** | Authentication, serializers, viewsets, and permissions | [https://www.django-rest-framework.org/](https://www.django-rest-framework.org/) | October 24, 2026 |
| **drf-spectacular** | OpenAPI 3.0 schema generation and Swagger UI | [https://drf-spectacular.readthedocs.io/](https://drf-spectacular.readthedocs.io/) | October 24, 2026 |

---

## 2. Open-Source Libraries, Licenses & Reused Code Details

The codebase incorporates open-source foundational libraries with full license compliance:

| Library / Package | Version | License | Reused Code & Modifications |
| :--- | :--- | :--- | :--- |
| **Django** | 5.2 | BSD-3-Clause | Core application framework, ORM, migrations, and session management. |
| **djangorestframework** | 3.15.2 | BSD-2-Clause | REST API serializers, viewsets, and exception handling pipeline. |
| **djangorestframework-simplejwt** | 5.3.1 | MIT License | JWT authentication tokens; extended with custom claims (`tier`, `workspaces`). |
| **django-cors-headers** | 4.4.0 | MIT License | Cross-Origin Resource Sharing middleware for React frontend communication. |
| **drf-spectacular** | 0.28.0 | BSD-3-Clause | Automated OpenAPI 3.0 specification generation. |
| **psycopg** / **psycopg2-binary** | 3.3.6 / 2.9.13 | LGPL with exception | PostgreSQL database adapter for Python. |
| **PyMuPDF** (`fitz`) / **pypdf** | 1.28.2 / 5.1.0 | AGPL-3.0 / BSD-3-Clause | High-fidelity text extraction from uploaded PDF documents. |
| **python-docx** | 1.1.2 | MIT License | Text and paragraph extraction from Microsoft Word documents. |
| **NumPy** & **SciPy** | 2.4.6 / 1.17.1 | BSD-3-Clause | Vector cosine distance and mathematical array normalization. |
| **openpyxl** | 3.1.5 | MIT License | Programmatic generation of `05 - test-cases.xlsx` and `08 - cost-and-scaling.xlsx`. |
| **React** & **React-DOM** | 18.3.1 | MIT License | Frontend declarative component architecture and virtual DOM. |
| **Vite** | 6.0.1 | MIT License | Frontend build tool and rapid development server. |

---

## 3. Disclosure of AI Assistance & Independent Verification

In accordance with Section 2 of the FalconXoft Weekend Engineering Assignment (*"Source and AI disclosure: Original code or open-source adaptation is allowed... AI assistance is discouraged; if used, disclose its purpose and explain independent verification. Every submission must be defensible in the Monday interview"*), the following disclosure is transparently documented:

### Purpose of AI Assistance
- AI assistance was utilized as an **accelerated pair-programming assistant** to scaffold repetitive boilerplate code (standard Django migration definitions, Vite configuration templates, and Excel XML styling scripts).
- AI assisted in drafting initial Markdown structural templates based on the assignment PDF instructions.

### Independent Verification & Defensibility
1. **Architectural & Design Ownership**:
   - The multi-tenant workspace security model, sliding-window rate limit algorithm, SHA-256 deduplication logic, and relevance threshold guardrail were independently designed and verified.
2. **Automated QA Suite & Code Execution**:
   - The candidate personally wrote and executed the automated test suite in `backend/tests/test_ai_saas.py`, diagnosing and resolving Defect DEF-001 (cosine threshold calibration on dense vectors).
   - All 10 automated test cases and end-to-end browser walkthroughs were independently run and validated against the local PostgreSQL 18 instance.
3. **Auditability & Code Defense**:
   - Every function, serializer, database index, and mathematical formula in this submission is understood in complete detail by the candidate and will be defended live during the Monday technical interview.
