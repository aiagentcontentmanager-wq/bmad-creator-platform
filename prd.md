# BMAD Product Requirements Document

## Executive Summary

**Product Name:** BMAD (Blueprint-Manifest-Agents-Deployment)  
**Version:** 1.0  
**Document Status:** Draft  
**Last Updated:** January 2026

### Vision Statement

BMAD is an integrated, autonomous development and execution framework designed to build, manage, and evolve intelligent, modular systems through multi-agent collaboration, self-orchestration, and test-driven development.

### Core Value Proposition

BMAD automates human workflows without removing the human element, monetizing automation and insight rather than raw content. The platform provides:

- **Automation Engine** - Multi-agent orchestration replacing manual tasks
- **Transparency Layer** - Auditable AI governance for regulated industries
- **Extensibility** - Plug-and-play modules for resale
- **Self-Hosting Freedom** - No vendor lock-in with premium orchestration options

---

## 1. Product Overview

### 1.1 Purpose

Primary goals:
- Zero-cost operation until first revenue
- Deterministic, testable AI behavior
- Full offline capability
- Hardware-aware execution
- Developer-first transparency

Core Principles:

- Rule-first, AI-second
- Explainability over blackbox behavior
- Deterministic and reproducible execution
- Every step must be loggable
- Reuse existing solutions before building new ones
- No cloud dependency without fallback

Included Features:

- Multi-agent AI architecture (Architect, Coder, QA, Refactor, Reviewer)
- Local + Cloud AI execution with fallback
- Code generation, refactoring, testing, documentation
- Workflow orchestration via n8n
- Persistent user data
- Authentication & authorization
- Admin dashboard
- Monitoring & metrics
- Alerting (Telegram / Email)

Explicitly Out of Scope (for MVP):

- Paid-only AI providers
- Vendor-locked SaaS dependencies
- Undocumented automation
- Non-deterministic execution paths


BMAD represents a self-learning automation platform capable of:

- Managing user/model onboarding via structured forms (Telegram, web)
- Generating creative content autonomously using local AI (text, image, video)
- Scheduling and posting across social platforms with rate control
- Collecting analytics and adapting strategies through reinforcement
- Operating in full GDPR compliance with ethical AI policies
- Running entirely on self-hosted, open-source infrastructure

### 1.2 Target Users

| User Type | Description | Primary Needs |
|-----------|-------------|---------------|
| **Content Creators** | Individual creators managing social media presence | Automated content generation, scheduling, analytics |
| **Talent Managers** | Agencies managing multiple creator accounts | Multi-tenant management, revenue tracking, compliance |
| **System Administrators** | Technical operators of BMAD instances | Monitoring, scaling, security management |
| **Developers** | Contributors extending BMAD functionality | Clear APIs, documentation, modular architecture |

### 1.3 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Developer Activation Rate | >30% | % of clones running locally within 7 days |
| System Uptime | 99.9% | Monthly availability monitoring |
| Content Generation Quality | >85% approval | User satisfaction ratings |
| Revenue Per Model | €500+/month | Financial analytics |
| GDPR Compliance Score | 100% | Automated audit results |

---

## 2. Core Principles

### 2.1 Architectural Principles

1. **Autonomy** - Agents perform complex workflows without human intervention but can defer when policies require it
2. **Transparency** - Every decision, transformation, and action is traceable via logs and audit records
3. **Security** - PII and credentials stored encrypted; no secrets leave the system unprotected
4. **Scalability** - Every module independently scalable or replaceable
5. **Test-Driven Everything** - TDD and TBCG enforced across all agents
6. **Open-Source First** - All components run using open-source tools
7. **Continuous Self-Evolution** - System learns autonomously through feedback loops

### 2.2 Technology Principles

- **Local-First AI** - No reliance on external paid APIs
- **Explainability** - All model outputs reproducible with saved parameters
- **Fine-tuning Loop** - Agents learn continuously from performance metrics
- **Modularity** - Each model (text, image, video) containerized and callable over REST

---

## 3. System Architecture

### 3.1 Layer Overview

| Layer | Description | Core Technologies |
|-------|-------------|-------------------|
| **Interface Layer** | User entry points (Telegram Bot, REST API, Admin Dashboard) | Node.js, React, Fastify, Telegraf |
| **Orchestration Layer** | Workflow and data coordination | n8n, Redis, RabbitMQ |
| **Intelligence Layer** | Autonomous agents (content, analytics, moderation) | TypeScript, Python, Ollama, Stable Diffusion |
| **Persistence Layer** | Structured storage, metadata, embeddings | PostgreSQL, MinIO, Weaviate |
| **Governance Layer** | Security, GDPR, agent supervision | Governance Agent, Policy Engine, Vault |

### 3.2 Agent Hierarchy

```
SupervisorAgent (Parent)
├── RecruiterAgent
├── OnboardAgent
├── ContentAgent
├── CuratorAgent
├── PublisherAgent
├── EngagementAgent
├── AnalyticsAgent
├── FinanceAgent
├── EscrowAgent
└── GovernanceAgent
```

---

## 4. Functional Requirements

### 4.1 Module 1: Onboarding & Telegram Intake

**Objective:** Capture all initial user/model data securely and trigger contract generation

**Key Features:**
- Telegram bot integration for form submission
- Multi-language support (EN, DE, RU)
- File upload handling (photos, documents)
- GDPR consent collection
- Automated contract generation trigger

**API Endpoints:**
- `POST /onboard/telegram` - Submit onboarding data
- `GET /onboard/status/:id` - Check onboarding status

**Acceptance Criteria:**
- ✓ Validation rejects missing required fields
- ✓ File uploads stored in MinIO with signed URLs
- ✓ Database record created with consent flag
- ✓ Contract generation event triggered
- ✓ 100% test coverage

### 4.2 Module 2: Contract Generator

**Objective:** Automate GDPR-compliant consent and contract creation

**Key Features:**
- Google Docs template integration
- Placeholder replacement (ModelName, ModelID, Email, Date)
- PDF export to MinIO
- Digital signature support
- Audit trail logging

**API Endpoints:**
- `POST /contracts/generate` - Generate contract from template
- `GET /contracts/:id` - Retrieve contract PDF

**Acceptance Criteria:**
- ✓ All placeholders correctly replaced
- ✓ PDF accessible and valid
- ✓ Contract linked to model record
- ✓ Event `contract.ready` published

### 4.3 Module 3: AI Content Engine

**Objective:** Generate high-quality media autonomously

**Key Features:**
- Prompt building from persona data
- Text generation via Ollama (Mistral/Llama3)
- Image generation via Stable Diffusion
- Video assembly via FFmpeg
- Content moderation (NSFW detection)

**API Endpoints:**
- `POST /content/generate` - Generate content variants
- `GET /content/samples/:model_id` - Retrieve generated content
- `POST /content/approve/:id` - Approve content for publishing

**Acceptance Criteria:**
- ✓ Prompt contains all persona tags
- ✓ Images pass moderation checks
- ✓ Content stored in MinIO
- ✓ Metadata saved with reproducible parameters
- ✓ Event `content.ready` triggered

**AI Model Tier Strategy**
- Tier	Purpose	Models	Cost
- Local GPU Primary	Code, Tests, Refactor	llama-3.1-8b-q5	0€
- Local GPU Specialist	Code-only	codellama-7b-q4	0€
- Local CPU Fallback	Offline / Emergency	phi-3-mini-q4	0€
- Cloud Free Tier	Large Context / Reasoning	Gemini / Llama 70B	0€

Acceptance Rule:
No feature may be Cloud-only.

**Mandatory Routing Layer**

- All AI calls MUST go through:
    - TaskRouter
    - ModelOrchestrator

- Direct model calls from agents are forbidden.

**ModelOrchestrator (NEW)*

- Responsibility

- Execute routed tasks

- Manage quotas

- Rotate providers

- Handle failures

- Forbidden Responsibilities

- Prompt design

- Business logic

- Agent state management

### 4.4 Module 4: Curator & Scheduler

**Objective:** Rank content variants and optimize posting schedule

**Key Features:**
- ML-based content ranking (scikit-learn)
- Randomized scheduling within windows
- Platform-specific optimization
- Engagement prediction

**API Endpoints:**
- `POST /schedule/create` - Schedule content post
- `GET /schedule/list/:model_id` - View scheduled posts
- `PUT /schedule/update/:id` - Modify schedule

**Acceptance Criteria:**
- ✓ Ranking algorithm produces consistent ordering
- ✓ Time slots respect no-overlap rules
- ✓ Posts queued in RabbitMQ
- ✓ Status tracking (scheduled/posted)

### 4.5 Module 5: Publisher

**Objective:** Publish content to social media platforms

**Key Features:**
- Instagram Graph API integration
- Telegram Bot API integration
- Twitter v2 API integration
- Rate limiting per platform
- Retry logic with exponential backoff

**API Endpoints:**
- `POST /publish/post` - Publish content to platform
- `GET /publish/status/:id` - Check publication status

**Acceptance Criteria:**
- ✓ Successful posts update status
- ✓ Failed posts retry 3x with backoff
- ✓ Rate limits enforced (1 post/2min per model)
- ✓ Platform post IDs stored

### 4.6 Module 6: Engagement Agent

**Objective:** Automate chat interactions with followers

**Key Features:**
- Conversation memory via Weaviate
- LLM-powered responses (Ollama)
- Sentiment analysis
- Escalation triggers for restricted content
- GDPR-compliant message handling

**API Endpoints:**
- `POST /engagement/message` - Process incoming message
- `GET /engagement/history/:model_id` - Retrieve conversation history

**Acceptance Criteria:**
- ✓ Persona memory retrieval accurate
- ✓ Escalation triggered on keywords
- ✓ Message deletion compliance
- ✓ Interaction logs stored

### 4.7 Module 7: Analytics & Reporter

**Objective:** Collect metrics and generate performance reports

**Key Features:**
- Platform API metric collection
- Aggregation and visualization
- Weekly PDF report generation
- Email delivery
- Grafana dashboard integration

**API Endpoints:**
- `GET /analytics/metrics/:model_id` - Retrieve metrics
- `POST /analytics/report/generate` - Generate report
- `GET /analytics/trends` - View trend analysis

**Acceptance Criteria:**
- ✓ CTR calculation accurate
- ✓ Charts rendered correctly
- ✓ PDF reports non-empty
- ✓ Email delivery verified

### 4.8 Module 8: Finance & Payout

**Objective:** Compute revenue, apply commissions, manage payouts

**Key Features:**
- Multi-source revenue aggregation
- Configurable commission splits (60/40 default)
- Escrow wallet management
- Payout approval workflow
- Double-entry ledger

**API Endpoints:**
- `POST /finance/deposit` - Record revenue deposit
- `POST /finance/payout/request` - Request payout
- `GET /finance/balance/:model_id` - View balance

**Acceptance Criteria:**
- ✓ Calculations accurate within 0.01 tolerance
- ✓ Splits applied per configuration
- ✓ Ledger entries balanced
- ✓ Audit trail complete

### 4.9 Module 9: Supervisor Agent

**Objective:** Orchestrate and monitor all child agents

**Key Features:**
- Health check monitoring (60s interval)
- Policy evaluation and enforcement
- Auto-restart degraded agents
- Alert generation
- Operational reporting

**API Endpoints:**
- `GET /supervisor/health` - System health overview
- `GET /supervisor/agents` - Agent status list
- `POST /supervisor/restart/:agent` - Restart specific agent

**Acceptance Criteria:**
- ✓ Failed agents detected and paused
- ✓ Policy rules executed from YAML
- ✓ Alerts sent to admin
- ✓ Dashboard updated in real-time

### 4.10 Module 10: Governance Agent

**Objective:** Ensure GDPR compliance and security

**Key Features:**
- Consent ledger management
- Right-to-erasure workflow
- Audit log generation
- Policy enforcement
- Data minimization

**API Endpoints:**
- `POST /governance/consent` - Record consent
- `DELETE /governance/erase/:user_id` - Process erasure request
- `GET /governance/audit` - Retrieve audit logs

**Acceptance Criteria:**
- ✓ Consent hashes unique and immutable
- ✓ Erasure removes all PII
- ✓ Audit logs complete and searchable
- ✓ Compliance reports generated

---

## 5. Non-Functional Requirements

### 5.1 Performance

| Requirement | Target | Measurement |
|-------------|--------|-------------|
| API Response Time | <500ms (p95) | Prometheus metrics |
| Content Generation | <30s per image | Agent telemetry |
| Database Query | <100ms (p95) | PostgreSQL logs |
| Queue Processing | <5s latency | RabbitMQ monitoring |

### 5.2 Scalability

- Horizontal scaling of stateless agents
- Redis Cluster for queue management
- PostgreSQL read replicas
- Weaviate vector sharding
- HPA: CPU >70% or queue >50 jobs → +1 pod

### 5.3 Security

- All secrets stored in Vault
- JWT authentication for API
- Mutual TLS between services
- RBAC for admin dashboard
- Data-at-rest encryption (pgcrypto)
- Regular vulnerability scanning (Trivy)

### 5.4 Reliability

- 99.9% uptime target
- Automated failover for critical services
- Nightly backups (PostgreSQL, Redis, Weaviate)
- Disaster recovery tested quarterly
- Self-healing orchestration

### 5.5 Compliance

- GDPR-compliant data handling
- Consent management with immutable ledger
- Right-to-erasure workflow
- Data minimization principles
- Explainable AI decisions
- Audit trail for all PII access

---

## 6. Data Requirements

### 6.1 Data Models

**Models Table:**
```sql
CREATE TABLE models (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE,
  language TEXT DEFAULT 'en',
  persona JSONB,
  consent BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Posts Table:**
```sql
CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  model_id INT REFERENCES models(id),
  caption TEXT,
  media_url TEXT,
  platform TEXT,
  posted_at TIMESTAMP,
  engagement JSONB
);
```

**Metrics Table:**
```sql
CREATE TABLE metrics (
  id SERIAL PRIMARY KEY,
  post_id INT REFERENCES posts(id),
  likes INT DEFAULT 0,
  comments INT DEFAULT 0,
  shares INT DEFAULT 0,
  views INT DEFAULT 0,
  collected_at TIMESTAMP DEFAULT NOW()
);
```

### 6.2 Data Flow

```
Telegram Bot → OnboardAgent → PostgreSQL
                           → MinIO (files)
                           → RabbitMQ (events)

ContentAgent → Ollama → Stable Diffusion → MinIO
           → Weaviate (embeddings)
           → PostgreSQL (metadata)

PublisherAgent → Social APIs → PostgreSQL (status)
                            → RabbitMQ (events)

AnalyticsAgent → Platform APIs → PostgreSQL (metrics)
                              → Grafana (visualization)
```

---

## 7. Integration Requirements

### 7.0.1 Deterministic Routing Rules

Routing decisions must be based on:

- Task type
- Estimated token count
- Complexity score
- Priority
- Internet availability

Each decision must be:
- Logged
- Reproducible
- Testable

### 7.0.2 Routing Strategies
Strategy | Order
cloud_first  |cloud → local_gpu → local_cpu
local_first	 |local_gpu → cloud → local_cpu
offline_only	 |local_gpu → local_cpu
balanced	 |local_gpu → cloud → local_cpu

### 7.1 External APIs

| Service | Purpose | Authentication |
|---------|---------|----------------|
| Instagram Graph API | Content publishing | OAuth 2.0 |
| Telegram Bot API | User interaction | Bot token |
| Twitter API v2 | Content publishing | OAuth 2.0 |
| Google Docs API | Contract generation | Service account |

### 7.2 Internal Services

| Service | Protocol | Port |
|---------|----------|------|
| PostgreSQL | TCP | 5432 |
| Redis | TCP | 6379 |
| RabbitMQ | AMQP | 5672 |
| MinIO | HTTP | 9000 |
| Ollama | HTTP | 11434 |
| Weaviate | HTTP | 8080 |

---

## 8. Testing Strategy
### 8.0.1 Testing Requirements (TDD Mandatory)
### 8.0.2 Required Test Suites
- ModelRouting.spec.ts
- QuotaEnforcement.spec.ts
- OfflineMode.spec.ts
- ProviderRotation.spec.ts
- FallbackSequence.spec.ts

### 8.0.3 Failure Simulation (Mandatory)

- Cloud unavailable
- GPU unavailable
- CPU-only mode
- Rate limits exceeded
- Partial provider outage

No merge is allowed without passing all tests.

### 8.0.4 Cost & Revenue Constraints

- All tooling must be open-source

- All AI execution must be free-tier or local

- Paid services allowed only AFTER revenue

- Costs must be tracked and reported

### 8.0.5 Acceptance Criteria

- System runs fully offline

- All AI decisions are logged

- Re-running the same task yields equivalent output

- Cloud usage < 30% average

- Local GPU usage > 60% average

### 8.0.6 Non-Functional Requirements

- Deterministic behavior

- Explainable decisions

- Observable metrics

- Graceful degradation

- Self-healing pipelines

### 8.0.7 Definition of Done

- All tests passing

- Logs available for every AI call

- No hardcoded providers

- Documentation generated automatically

Architecture drift checks clean
### 8.1 Test Levels

| Level | Coverage Target | Tools |
|-------|----------------|-------|
| Unit | 90%+ | Jest, Pytest |
| Integration | 85%+ | Supertest, HTTPX |
| Behavioral | 100% critical paths | Postman, n8n |
| Performance | All endpoints | k6, Locust |
| Security | All components | Bandit, Trivy |

### 8.2 TDD Requirements

1. Tests written before implementation
2. All tests must pass before commit
3. No implementation without failing test
4. Coverage reports in CI/CD
5. Automated test generation via TBCG

---

## 9. Deployment Requirements

### 9.1 Environments

| Environment | Purpose | Infrastructure |
|-------------|---------|----------------|
| Local Dev | Rapid prototyping | Docker Compose |
| Staging | Pre-production testing | Kubernetes cluster |
| Production | Live operations | Kubernetes (HA) |

### 9.2 Deployment Process

1. Build & lint code
2. Run test suite (unit + integration)
3. Build Docker images
4. Push to container registry
5. Deploy via Helm
6. Run health checks
7. Smoke tests
8. Monitor metrics

---

## 10. Monetization Strategy

### 10.1 Revenue Streams

| Stream | Description | Pricing |
|--------|-------------|---------|
| **Community (Free)** | Self-hosted basic stack | €0 |
| **Professional SaaS** | Hosted orchestration | €49-299/month |
| **Enterprise** | Private deployment + support | €25,000+/year |
| **Marketplace** | Module sales (10% platform fee) | Variable |
| **API Credits** | Pay-per-use endpoints | €0.01-0.05/call |

### 10.2 Business Model

- **Freemium** - Free self-hosted version drives ecosystem growth
- **Subscription** - Managed instances with premium features
- **Revenue Share** - 2% from federated network nodes
- **Consulting** - Enterprise support contracts

---

## 11. Roadmap

### Phase 1 (2025-2026) - Core Stack Stabilization
- ✓ Complete all 10 core modules
- ✓ Achieve 95%+ test coverage
- ✓ Local deployment via Docker Compose
- ✓ v1.0 release + documentation

### Phase 2 (2026-2027) - Federated Learning
- Marketplace for modules
- BMAD Hub Network
- Multi-tenant SaaS
- Advanced analytics

### Phase 3 (2027-2028) - Autonomous Optimization
- RLHF at scale
- Automated model improvement
- Predictive analytics
- Self-optimizing agents

### Phase 4 (2028-2030) - Global AI Co-ops
- Decentralized governance token
- DAO structure
- Cross-instance collaboration
- Community-driven development

---

## 12. Success Criteria

### 12.1 Launch Criteria

- [ ] All 10 modules implemented and tested
- [ ] 95%+ test coverage achieved
- [ ] Docker Compose stack operational
- [ ] Documentation complete
- [ ] GDPR compliance verified
- [ ] Security audit passed

### 12.2 Adoption Metrics (Year 1)

- 500+ active nodes
- 300+ contributors
- €1M+ ARR
- 99.9% uptime
- 100% GDPR compliance

---

## 13. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Compute cost surge | High | Medium | Dynamic scaling + edge offloading |
| License violations | High | Low | Automated SPDX scans |
| Model bias complaints | Medium | Medium | Transparent retraining logs |
| Legal uncertainty | High | Medium | Jurisdictional compliance matrix |
| Community fatigue | Medium | Low | Incentive programs + governance votes |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Agent** | Autonomous service responsible for specific domain |
| **BMAD** | Blueprint-Manifest-Agents-Deployment |
| **TBCG** | Test-Based Code Generation |
| **TDD** | Test-Driven Development |
| **Escrow** | Temporary holding of funds pending approval |
| **Ledger** | Double-entry accounting record |
| **Persona** | AI-generated personality profile for content |

## Appendix B: References

- BMAD Architecture Documentation
- GDPR Compliance Guidelines
- Open Source Licensing Guide
- API Reference Documentation
- Agent Development Guide