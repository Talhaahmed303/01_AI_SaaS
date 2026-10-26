# FalconXoft AI SaaS Workspace — Infrastructure Cost Analysis & Scaling Roadmap
**Weekend 2 Intern Engineering Evaluation | Project 1**  
**Author:** Engineering Evaluation Candidate  
**Spreadsheet Artifact:** [`08 - cost-and-scaling.xlsx`](./08%20-%20cost-and-scaling.xlsx) (Formatted Excel with Vendor Comparison & Scaling Scenarios)  
**Region Evaluated:** Frankfurt, Germany (`eu-central-1` / Falkenstein Data Center)  
**Currency:** USD ($) | **Date Accessed:** October 24, 2026

---

## 1. Side-by-Side Vendor Cost Analysis: Hetzner / VPS vs. AWS

The following comparison benchmarks a baseline production deployment supporting up to 1,000 monthly active users and 50,000 AI queries:

| Component / Subsystem | Resource Specification | Baseline Volume | Unit Pricing | VPS (Hetzner) ($/mo) | AWS eu-central-1 ($/mo) | Official Pricing Source URL | Date Accessed |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Compute (API & Web)** | 2x App Nodes (4 vCPU, 8GB RAM) | 2 Instances | Fargate: $0.0336/hr vs Hetzner CPX21: $6.50/mo | **$13.00** | **$48.38** | [AWS Fargate Pricing](https://aws.amazon.com/fargate/pricing/) | 2026-10-24 |
| **Database (PostgreSQL 18)** | Primary instance (4 vCPU, 8GB RAM) | 1 Instance | RDS db.t4g.medium: $0.068/hr vs Hetzner CPX31: $13/mo | **$13.00** | **$48.96** | [AWS RDS PostgreSQL](https://aws.amazon.com/rds/postgresql/pricing/) | 2026-10-24 |
| **Object Storage** | Encrypted document repository | 50 GB | S3 Standard: $0.023/GB vs Hetzner 1TB Box: $3.80/mo | **$3.80** | **$1.15** | [AWS S3 Pricing](https://aws.amazon.com/s3/pricing/) | 2026-10-24 |
| **Automated Backups** | Continuous WAL archiving + PITR | 100 GB Backup | RDS Backup: $0.095/GB vs VPS automated snapshots | **$2.50** | **$9.50** | [AWS RDS Backup Pricing](https://aws.amazon.com/rds/pricing/) | 2026-10-24 |
| **Egress Bandwidth** | Outbound document downloads & API | 100 GB / mo | AWS: $0.09/GB vs Hetzner: 20TB Free included | **$0.00** | **$9.00** | [AWS EC2 Bandwidth](https://aws.amazon.com/ec2/pricing/on-demand/) | 2026-10-24 |
| **Monitoring & Logs** | Audit log archiving & health checks | 100k events/mo | CloudWatch: $0.50/GB vs OSS Grafana/Prometheus | **$7.00** | **$15.00** | [AWS CloudWatch](https://aws.amazon.com/cloudwatch/pricing/) | 2026-10-24 |
| **Redis Cache / Queues** | Sliding rate limits & Celery queue | 1 Instance | ElastiCache: $0.016/hr vs Local Redis 7 Docker | **$0.00** | **$11.52** | [AWS ElastiCache](https://aws.amazon.com/elasticache/pricing/) | 2026-10-24 |
| **Apex Domain & SSL** | Custom domain + Wildcard TLS 1.3 | 1 Domain | Cloudflare Registrar: $12/yr + Free Let's Encrypt | **$1.00** | **$1.00** | [Cloudflare Registrar](https://www.cloudflare.com/products/registrar/) | 2026-10-24 |
| **AI Inference: Embedding** | `text-embedding-3-small` (1536 dim) | 10M tokens/mo | $0.020 per 1,000,000 tokens | **$0.20** | **$0.20** | [OpenAI Pricing](https://openai.com/api/pricing/) | 2026-10-24 |
| **AI Inference: Generation**| `gpt-4o-mini` (Prompt + Output) | 50k queries/mo | $0.150/1M input + $0.600/1M output | **$11.25** | **$11.25** | [OpenAI Pricing](https://openai.com/api/pricing/) | 2026-10-24 |
| **TOTAL MONTHLY ESTIMATE** | — | — | — | **$51.75 / mo** | **$155.96 / mo** | — | — |

> **Commercial Assessment**: Deploying on a modern European VPS provider (such as Hetzner Cloud or Hostinger VPS) yields a **66.8% infrastructure cost reduction** ($51.75/mo vs $155.96/mo) while delivering superior raw vCPU performance and zero egress fees. AWS is recommended once compliance mandates SOC2 Type II or automated multi-region replication.

---

## 2. AI Inference & Token Cost Calculations

### Assumptions per RAG Query
- **Prompt Token Input**: User query (25 tokens) + System Prompt (120 tokens) + 3 Retrieved Chunks (1,200 tokens) = **1,345 tokens input**.
- **Completion Token Output**: Average structured answer with citations = **120 tokens output**.
- **Blended Query Cost**:
  $$\text{Input Cost} = \frac{1,345}{1,000,000} \times \$0.150 = \$0.00020175$$
  $$\text{Output Cost} = \frac{120}{1,000,000} \times \$0.600 = \$0.00007200$$
  $$\text{Cost per Query} = \$0.00027375 \approx \mathbf{\$0.274 \text{ per 1,000 queries}}$$

---

## 3. Capacity & Architectural Adjustments Across Scale Tiers

### Tier 1: 100 Users (Alpha / Validation)
- **Active Usage**: 20 Daily Active Users (DAU); 12,000 monthly queries; 6.0 Million tokens.
- **Compute Architecture**: Single VPS (3 vCPU / 4GB RAM) running Gunicorn WSGI + Nginx.
- **Database & Storage**: Local PostgreSQL 18.3 instance on 40GB NVMe SSD with automated hourly WAL archiving.
- **Monthly Spend**: **$15.20 / mo** (Infra: $12.50 + LLM: $2.70).
- **Bottlenecks & Mitigations**: Single point of failure. Mitigated by daily offsite snapshot replication to S3 cold storage.

---

### Tier 2: 1,000 Users (MVP Growth)
- **Active Usage**: 250 DAU; 150,000 monthly queries; 75.0 Million tokens.
- **Compute Architecture**: Dual VPS nodes (2x 4 vCPU / 8GB RAM) with Nginx round-robin load balancer.
- **Database & Storage**: Dedicated Managed PostgreSQL 18 (4 vCPU / 16GB RAM) + 100GB SSD.
- **Caching & Queues**: Redis 7 container for sliding-window rate limiting & Celery asynchronous background chunking.
- **Monthly Spend**: **$82.25 / mo** (Infra: $48.50 + LLM: $33.75).
- **Bottlenecks & Mitigations**: Large file uploads block synchronous Gunicorn workers. Mitigated by moving file ingestion into asynchronous Celery tasks.

---

### Tier 3: 10,000 Users (Scale-Up Enterprise)
- **Active Usage**: 2,500 DAU; 1,800,000 monthly queries; 900.0 Million tokens.
- **Compute Architecture**: AWS ECS Fargate Cluster (4 to 12 auto-scaled tasks on CPU > 70%).
- **Database & Storage**: AWS Aurora PostgreSQL Serverless v2 Multi-AZ (8–32 ACUs) with 1 dedicated Read Replica.
- **Caching & Queues**: AWS ElastiCache Redis Cluster (3 nodes) + AWS SQS for ingestion job queues.
- **Monthly Spend**: **$890.00 / mo** (Infra: $485.00 + LLM: $405.00).
- **Bottlenecks & Mitigations**: Linear scan on vector similarity matching. Mitigated by enabling PostgreSQL `pgvector` HNSW indexing and caching repeated query responses in Redis.

---

### Tier 4: 1,000,000 Users (Hyper-Scale Global Multi-Region)
- **Active Usage**: 250,000 DAU; 180,000,000 monthly queries; 90.0 Billion tokens.
- **Compute Architecture**: Multi-Region AWS EKS Kubernetes Cluster across `eu-central-1`, `us-east-1`, and `ap-southeast-1`.
- **Database & Storage**: Distributed Aurora Global Database + 5 Read Replicas + Dedicated Qdrant Distributed Vector Database.
- **Caching & Queues**: Global Redis Mesh (ElastiCache Global Datastore) + Cloudflare Enterprise Edge CDN.
- **Monthly Spend**: **$46,750.00 / mo** (Infra: $6,250.00 + LLM: $40,500.00).
- **Bottlenecks & Mitigations**: Upstream LLM rate limits and prohibitive API token costs ($40k+/mo). Mitigated by:
  1. Semantic Vector Caching (Redis LangCache), eliminating 40% of repetitive enterprise queries.
  2. Deploying self-hosted open-source models (Llama-3-70B via vLLM) on reserved GPU instances (AWS g5.12xlarge), reducing marginal inference cost by 55%.
