# BMAD Architecture Documentation

## Document Information

**Version:** 1.0  
**Status:** Technical Specification  
**Last Updated:** January 2026  
**Target Audience:** System Architects, DevOps Engineers, Senior Developers

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architectural Principles](#2-architectural-principles)
3. [System Layers](#3-system-layers)
4. [Multi-Agent Architecture](#4-multi-agent-architecture)
5. [Data Architecture](#5-data-architecture)
6. [Infrastructure Architecture](#6-infrastructure-architecture)
7. [Security Architecture](#7-security-architecture)
8. [Integration Architecture](#8-integration-architecture)
9. [Deployment Architecture](#9-deployment-architecture)
10. [Monitoring & Observability](#10-monitoring--observability)

---

## 1. System Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BMAD Ecosystem                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Frontend   │  │  Telegram    │  │   Admin      │    │
│  │   Dashboard  │  │     Bot      │  │     API      │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
│                   ┌────────▼────────┐                      │
│                   │  API Gateway    │                      │
│                   │  (Auth/RBAC)    │                      │
│                   └────────┬────────┘                      │
│                            │                                │
│         ┌──────────────────┼──────────────────┐           │
│         │                  │                  │            │
│    ┌────▼─────┐    ┌──────▼──────┐    ┌─────▼────┐      │
│    │Supervisor│    │ n8n Workflow│    │ Agents   │      │
│    │  Agent   │    │ Orchestrator│    │ Cluster  │      │
│    └────┬─────┘    └──────┬──────┘    └─────┬────┘      │
│         │                  │                  │            │
│         └──────────────────┴──────────────────┘            │
│                            │                                │
│         ┌──────────────────┼──────────────────┐           │
│         │                  │                  │            │
│    ┌────▼─────┐    ┌──────▼──────┐    ┌─────▼────┐      │
│    │PostgreSQL│    │   Redis     │    │ RabbitMQ │      │
│    │          │    │   Cache/Q   │    │  Events  │      │
│    └──────────┘    └─────────────┘    └──────────┘      │
│                                                             │
│    ┌──────────┐    ┌─────────────┐    ┌──────────┐      │
│    │  MinIO   │    │  Weaviate   │    │  Ollama  │      │
│    │ Storage  │    │  Vectors    │    │   AI     │      │
│    └──────────┘    └─────────────┘    └──────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Architecture Characteristics

| Characteristic | Approach | Rationale |
|----------------|----------|-----------|
| **Distribution** | Microservices | Independent scaling, fault isolation |
| **Communication** | Event-driven + REST | Loose coupling, async processing |
| **Data Storage** | Polyglot persistence | Optimized for use case |
| **Deployment** | Containerized | Portability, consistency |
| **Orchestration** | Kubernetes | Auto-scaling, self-healing |
| **AI Models** | Local-first | No vendor lock-in, cost control |

---

## 2. Architectural Principles

### 2.1 Design Philosophy

#### Principle 1: Autonomy with Oversight
- Agents operate independently
- Parent-child supervision model
- Human-in-the-loop for critical decisions
- Policy-driven governance

#### Principle 2: Transparency by Default
- All decisions logged with trace IDs
- Immutable audit trails
- Explainable AI outputs
- Observable metrics

#### Principle 3: Security-First Design
- Zero-trust architecture
- Encrypted data at rest and in transit
- Secret management via Vault
- RBAC enforcement

#### Principle 4: Scalability from Day One
- Stateless service design
- Horizontal pod autoscaling
- Database sharding ready
- Cache-first strategies

#### Principle 5: Test-Driven Everything
- Tests before implementation
- Automated test generation (TBCG)
- 95%+ coverage requirement
- Contract testing between services

#### Principle 6: Open Source Commitment
- No proprietary dependencies
- Self-hostable infrastructure
- Community-driven development
- Transparent governance

#### Principle 7: Continuous Evolution
- Feedback loops at every layer
- Automated performance optimization
- Self-learning agents
- Model retraining pipelines

---

## 3. System Layers

### 3.1 Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  INTERFACE LAYER                        │
│  - React Dashboard - Telegram Bot - REST API           │
│  - WebSocket Events - Admin Console                    │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│               ORCHESTRATION LAYER                       │
│  - n8n Workflows - Event Bus (RabbitMQ)                │
│  - Job Queue (Redis) - API Gateway                     │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│               INTELLIGENCE LAYER                        │
│  - Supervisor Agent - Content Agent                    │
│  - Analytics Agent - Finance Agent                     │
│  - Governance Agent - All Domain Agents                │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│               PERSISTENCE LAYER                         │
│  - PostgreSQL (Relational) - Redis (Cache)             │
│  - Weaviate (Vectors) - MinIO (Objects)                │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                GOVERNANCE LAYER                         │
│  - Policy Engine - Audit Logger                        │
│  - Vault (Secrets) - Compliance Monitor                │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Layer Responsibilities

#### Interface Layer
**Purpose:** User and system interaction  
**Components:**
- React 18 + TypeScript frontend
- Telegram Bot (Telegraf)
- REST API (Fastify)
- WebSocket server (Socket.io)

**Key Patterns:**
- BFF (Backend for Frontend)
- JWT authentication
- Rate limiting
- Input validation

#### Orchestration Layer
**Purpose:** Workflow coordination and event routing  
**Components:**
- n8n workflow engine
- RabbitMQ message broker
- Redis job queue
- API Gateway (Kong/custom)

**Key Patterns:**
- Event sourcing
- SAGA pattern for distributed transactions
- Dead letter queues
- Idempotent consumers

#### Intelligence Layer
**Purpose:** Autonomous decision-making and execution  
**Components:**
- 10+ specialized agents
- Ollama LLM server
- Stable Diffusion API
- Weaviate vector store

**Key Patterns:**
- Parent-child agent hierarchy
- Circuit breakers
- Retry with exponential backoff
- Bulkhead isolation

#### Persistence Layer
**Purpose:** Data storage and retrieval  
**Components:**
- PostgreSQL (structured data)
- Redis (cache + sessions)
- Weaviate (embeddings)
- MinIO (object storage)

**Key Patterns:**
- CQRS (Command Query Responsibility Segregation)
- Event store
- Time-series partitioning
- Write-ahead logging

#### Governance Layer
**Purpose:** Security, compliance, policy enforcement  
**Components:**
- HashiCorp Vault
- Policy engine (OPA)
- Audit log aggregator
- Compliance scanner

**Key Patterns:**
- Policy as code
- Immutable audit logs
- Cryptographic verification
- Zero-knowledge proofs

---

## 4. Multi-Agent Architecture

### 4.1 Agent Taxonomy

```
SupervisorAgent (Root)
│
├── Onboarding Domain
│   ├── RecruiterAgent
│   └── OnboardAgent
│
├── Content Domain
│   ├── ContentAgent
│   ├── CuratorAgent
│   └── PublisherAgent
│
├── Engagement Domain
│   └── EngagementAgent
│
├── Analytics Domain
│   └── AnalyticsAgent
│
├── Finance Domain
│   ├── FinanceAgent
│   ├── EscrowAgent
│   └── BillingAgent
│
├── Governance Domain
│   ├── GovernanceAgent
│   ├── AntiFraudAgent
│   └── KYCAgent
│
└── ModelOrchestrator Domain
    └── ModelOrchestrator
```

### 4.5 ModelOrchestrator Responsibilities

#### Verantwortlichkeiten:

1. **Ausführung von gerouteten Aufgaben:**
   - Der ModelOrchestrator ist für die Ausführung von Aufgaben verantwortlich, die an ihn geroutet werden. Dies umfasst die Verarbeitung von Anfragen und die Weiterleitung an die entsprechenden Modelle oder Dienste.

2. **Verwaltung von Quotas:**
   - Der ModelOrchestrator überwacht und verwaltet die Nutzungsquoten für Modelle und Dienste. Dies stellt sicher, dass Ressourcen fair verteilt werden und keine Überlastung entsteht.

3. **Rotation von Providern:**
   - Der ModelOrchestrator implementiert eine Rotationsstrategie für Provider, um die Last zu verteilen und die Verfügbarkeit zu erhöhen. Dies kann durch Round-Robin, gewichtete Verteilung oder andere Algorithmen erfolgen.

4. **Fehlerbehandlung:**
   - Der ModelOrchestrator ist für die Erkennung und Behandlung von Fehlern zuständig. Dies umfasst das Logging von Fehlern, das Retry von fehlgeschlagenen Anfragen und das Escalation-Management bei kritischen Fehlern.

#### Verbotene Verantwortlichkeiten:

1. **Prompt-Design:**
   - Der ModelOrchestrator ist nicht für das Design oder die Erstellung von Prompts verantwortlich. Diese Aufgabe obliegt den jeweiligen Agenten oder spezialisierten Diensten.

2. **Business-Logik:**
   - Der ModelOrchestrator sollte keine Business-Logik enthalten. Diese sollte in den jeweiligen Domänen-Agenten oder -Diensten implementiert sein.

3. **Agent-State-Management:**
   - Der ModelOrchestrator verwaltet keinen Zustand von Agenten. Das State-Management obliegt den Agenten selbst oder einem dedizierten State-Management-Service.

#### Beispielhafte Implementierung:

```typescript
// Pseudo-code für ModelOrchestrator
class ModelOrchestrator {
  private providers: Provider[];
  private quotas: Map<string, number>;
  private currentProviderIndex: number = 0;

  constructor(providers: Provider[]) {
    this.providers = providers;
    this.quotas = new Map();
  }

  async executeTask(task: Task): Promise<Result> {
    try {
      // Überprüfe Quota
      if (!this.checkQuota(task.modelId)) {
        throw new Error("Quota exceeded");
      }

      // Wähle Provider (Rotation)
      const provider = this.selectProvider();

      // Führe Aufgabe aus
      const result = await provider.execute(task);

      // Aktualisiere Quota
      this.updateQuota(task.modelId);

      return result;
    } catch (error) {
      // Fehlerbehandlung
      this.handleError(error, task);
      throw error;
    }
  }

  private checkQuota(modelId: string): boolean {
    const currentQuota = this.quotas.get(modelId) || 0;
    return currentQuota < MAX_QUOTA;
  }

  private updateQuota(modelId: string): void {
    const currentQuota = this.quotas.get(modelId) || 0;
    this.quotas.set(modelId, currentQuota + 1);
  }

  private selectProvider(): Provider {
    // Round-Robin Rotation
    const provider = this.providers[this.currentProviderIndex];
    this.currentProviderIndex = (this.currentProviderIndex + 1) % this.providers.length;
    return provider;
  }

  private handleError(error: Error, task: Task): void {
    // Logging
    console.error(`Error executing task ${task.id}:`, error);

    // Retry oder Escalation
    if (error.retryable) {
      this.retryTask(task);
    } else {
      this.escalateError(error, task);
    }
  }
}
```

### 4.2 Agent Communication Protocol

#### Message Envelope Schema
```json
{
  "job_id": "uuid-v4",
  "agent_from": "source-agent-id",
  "agent_to": "target-agent-id",
  "type": "event.namespace.action",
  "payload": { /* domain-specific data */ },
  "trace": ["onboard:123", "content:456"],
  "priority": "normal|high|critical",
  "retries": 0,
  "created_at": "ISO-8601 timestamp",
  "signature": "HMAC-SHA256"
}
```

#### Event Types
```
# Onboarding
onboard.model_created
onboard.contract_ready

# Content
content.generate_request
content.ready
content.approved

# Publishing
publish.schedule_created
publish.posted
publish.failed

# Analytics
analytics.metrics_collected
analytics.report_generated

# Finance
finance.deposit_received
finance.payout_requested
finance.payout_released

# Governance
governance.policy_violated
governance.audit_required
governance.erasure_requested
```

### 4.3 Agent Lifecycle States

```
INIT → READY → RUNNING → DEGRADED → PAUSED → SHUTDOWN
  ↑                         ↓
  └─────── RECOVERING ←─────┘
```

**State Transitions:**
- `INIT` → `READY`: Health check passes
- `READY` → `RUNNING`: Receives first job
- `RUNNING` → `DEGRADED`: Error rate >10%
- `DEGRADED` → `RECOVERING`: Auto-restart triggered
- `DEGRADED` → `PAUSED`: Manual intervention required
- `PAUSED` → `READY`: Admin approval
- `*` → `SHUTDOWN`: Graceful termination

### 4.4 Supervisor Agent Responsibilities

**Health Monitoring:**
```typescript
// Pseudo-code
setInterval(async () => {
  for (const agent of agents) {
    const health = await axios.get(`${agent.url}/healthz`);
    redis.hset(`health:${agent.id}`, {
      status: health.status,
      timestamp: Date.now(),
      metrics: health.data
    });
    
    if (health.status !== 'ok') {
      await handleDegradedAgent(agent);
    }
  }
}, 60000); // Every 60s
```

**Policy Evaluation:**
```yaml
# policies/moderation.yaml
moderation:
  max_nudity_score: 0.85
  max_toxicity_score: 0.90
  auto_pause_threshold: 5
  escalate_to: governance
  actions:
    - type: pause_agent
      condition: violations > threshold
    - type: alert_admin
      channels: [telegram, email]
```

**Job Allocation:**
- Round-robin with priority weights
- Load-based distribution
- Affinity routing (sticky sessions)
- Circuit breaker pattern

---

## 5. Data Architecture

### 5.1 Database Schema Design

#### PostgreSQL Schema
```sql
-- Core Models
CREATE SCHEMA bmad AUTHORIZATION bmad_app;

CREATE TABLE bmad.models (
  id SERIAL PRIMARY KEY,
  external_id TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  email TEXT UNIQUE,
  language TEXT DEFAULT 'en',
  persona JSONB,
  consent BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE bmad.posts (
  id SERIAL PRIMARY KEY,
  model_id INT REFERENCES bmad.models(id) ON DELETE CASCADE,
  caption TEXT,
  media_url TEXT,
  platform TEXT CHECK (platform IN ('instagram', 'telegram', 'twitter')),
  status TEXT CHECK (status IN ('draft', 'scheduled', 'posted', 'failed')),
  posted_at TIMESTAMP,
  engagement JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE bmad.metrics (
  id SERIAL PRIMARY KEY,
  post_id INT REFERENCES bmad.posts(id) ON DELETE CASCADE,
  likes INT DEFAULT 0,
  comments INT DEFAULT 0,
  shares INT DEFAULT 0,
  views INT DEFAULT 0,
  collected_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE bmad.audit_log (
  id SERIAL PRIMARY KEY,
  agent_id TEXT NOT NULL,
  action TEXT NOT NULL,
  entity_type TEXT,
  entity_id TEXT,
  trace_id TEXT NOT NULL,
  outcome TEXT,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_models_external_id ON bmad.models(external_id);
CREATE INDEX idx_posts_model_id ON bmad.posts(model_id);
CREATE INDEX idx_posts_status ON bmad.posts(status);
CREATE INDEX idx_metrics_post_id ON bmad.metrics(post_id);
CREATE INDEX idx_audit_log_trace_id ON bmad.audit_log(trace_id);
CREATE INDEX idx_audit_log_created_at ON bmad.audit_log(created_at);
```

#### Finance Schema
```sql
CREATE TABLE bmad.escrow_wallets (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  balance NUMERIC(12,2) NOT NULL DEFAULT 0,
  locked BOOLEAN DEFAULT TRUE,
  currency TEXT DEFAULT 'EUR',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE bmad.payouts (
  id TEXT PRIMARY KEY,
  wallet_id TEXT REFERENCES bmad.escrow_wallets(id),
  amount NUMERIC(12,2) NOT NULL,
  currency TEXT DEFAULT 'EUR',
  model_id INT REFERENCES bmad.models(id),
  manager_id TEXT,
  status TEXT CHECK (status IN ('pending', 'approved', 'released', 'cancelled')),
  approved_by TEXT,
  approved_at TIMESTAMP,
  released_at TIMESTAMP,
  external_tx_id TEXT,
  meta JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE bmad.ledger_entries (
  id TEXT PRIMARY KEY,
  entry_type TEXT CHECK (entry_type IN ('DEBIT', 'CREDIT')),
  wallet_id TEXT REFERENCES bmad.escrow_wallets(id),
  amount NUMERIC(12,2) NOT NULL,
  currency TEXT DEFAULT 'EUR',
  related_id TEXT,
  hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 5.2 Redis Data Structures

```redis
# Job Queue
LPUSH queue:content:generate '{"job_id": "uuid", ...}'
RPOP queue:content:generate

# Cache
SET cache:model:M001 '{"name": "...", ...}' EX 300

# Rate Limiting
INCR ratelimit:api:user123
EXPIRE ratelimit:api:user123 60

# Agent Health
HSET health:content_agent status "ok" uptime "3600" queue_len "5"

# Session
SET session:token123 '{"user_id": "U001", ...}' EX 3600

# Pub/Sub
PUBLISH bmad.events.analytics '{"type": "metrics.collected", ...}'
```

### 5.3 Weaviate Vector Schema

```json
{
  "class": "ModelMemory",
  "properties": [
    {"name": "model_id", "dataType": ["string"]},
    {"name": "topic", "dataType": ["string"]},
    {"name": "content", "dataType": ["text"]},
    {"name": "timestamp", "dataType": ["date"]},
    {"name": "metadata", "dataType": ["object"]}
  ],
  "vectorizer": "text2vec-transformers",
  "moduleConfig": {
    "text2vec-transformers": {
      "model": "sentence-transformers/all-MiniLM-L6-v2"
    }
  }
}
```

### 5.4 Data Flow Patterns

#### Write Path
```
User Action → API Gateway → Agent → 
  ├─> PostgreSQL (structured data)
  ├─> Redis (cache invalidation)
  ├─> Weaviate (embeddings)
  ├─> MinIO (media files)
  └─> RabbitMQ (events)
```

#### Read Path
```
User Request → API Gateway → 
  Redis Cache Hit? → Return
  │
  └─> Cache Miss → PostgreSQL → 
      ├─> Enrich from Weaviate (semantic)
      ├─> Add media URLs (MinIO)
      └─> Cache result (Redis)
```

---

## 6. Infrastructure Architecture

### 6.1 Container Architecture

```yaml
# docker-compose.yml (Development)
version: '3.9'

services:
  backend:
    build: ./backend
    ports: ["3000:3000"]
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://bmad:bmad@postgres:5432/bmad
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    networks:
      - bmad_net

  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    environment:
      - VITE_API_URL=http://localhost:3000
    networks:
      - bmad_net

  postgres:
    image: postgres:16-alpine
    volumes:
      - pg_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=bmad
      - POSTGRES_PASSWORD=bmad
      - POSTGRES_DB=bmad
    networks:
      - bmad_net

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - bmad_net

  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports: ["5672:5672", "15672:15672"]
    networks:
      - bmad_net

  weaviate:
    image: semitechnologies/weaviate:1.25
    ports: ["8080:8080"]
    environment:
      - QUERY_DEFAULTS_LIMIT=25
      - AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true
      - PERSISTENCE_DATA_PATH=/var/lib/weaviate
    volumes:
      - weaviate_data:/var/lib/weaviate
    networks:
      - bmad_net

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    ports: ["9000:9000", "9001:9001"]
    environment:
      - MINIO_ROOT_USER=bmad
      - MINIO_ROOT_PASSWORD=bmad_secret
    volumes:
      - minio_data:/data
    networks:
      - bmad_net

  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes:
      - ollama_models:/root/.ollama
    networks:
      - bmad_net

  n8n:
    image: n8nio/n8n:latest
    ports: ["5678:5678"]
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin
    volumes:
      - n8n_data:/home/node/.n8n
    networks:
      - bmad_net

volumes:
  pg_data:
  redis_data:
  weaviate_data:
  minio_data:
  ollama_models:
  n8n_data:

networks:
  bmad_net:
    driver: bridge
```

### 6.2 Kubernetes Architecture

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: supervisor-agent
  namespace: bmad
spec:
  replicas: 2
  selector:
    matchLabels:
      app: supervisor
  template:
    metadata:
      labels:
        app: supervisor
    spec:
      containers:
      - name: supervisor
        image: bmad/supervisor:latest
        ports:
        - containerPort: 4000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: bmad-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: bmad-secrets
              key: redis-url
        livenessProbe:
          httpGet:
            path: /healthz
            port: 4000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 4000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: supervisor-hpa
  namespace: bmad
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: supervisor-agent
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 6.3 Network Architecture

```
                    Internet
                       │
                       ▼
              ┌────────────────┐
              │  Load Balancer │
              │   (Nginx/HAProxy)│
              └────────┬───────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
   │ Frontend│   │   API   │   │ WebSocket│
   │  Pods   │   │  Pods   │   │   Pods   │
   └────┬────┘   └────┬────┘   └────┬────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
              ┌────────▼────────┐
              │  Service Mesh   │
              │   (Linkerd)     │
              └────────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
   │ Agent   │   │ Storage │   │  AI/ML  │
   │ Cluster │   │ Layer   │   │ Services│
   └─────────┘   └─────────┘   └─────────┘
```

---

## 7. Security Architecture

### 7.1 Defense in Depth

```
┌─────────────────────────────────────────────┐
│         Layer 7: Application Security       │
│  - Input validation - Output encoding       │
│  - CSRF protection - SQL injection prevent  │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│         Layer 6: Authentication & AuthZ     │
│  - JWT tokens - RBAC - OAuth 2.0           │
│  - Session management - MFA                 │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│         Layer 5: API Security               │
│  - Rate limiting - API key validation       │
│  - Request signing - TLS enforcement        │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│         Layer 4: Transport Security         │
│  - mTLS - Certificate pinning              │
│  - Network policies - Service mesh          │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│         Layer 3: Data Security              │
│  - Encryption at rest - Field-level crypto  │
│  - Key rotation - Secure deletion          │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│         Layer 2: Infrastructure Security    │
│  - Container scanning - Secrets management  │
│  - Network segmentation - Firewalls         │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│         Layer 1: Physical Security          │
│  - Data center access - Hardware security   │
│  - Geographic redundancy                    │
└─────────────────────────────────────────────┘
```

### 7.2 Secrets Management (Vault)

```hcl
# vault.hcl
storage "file" {
  path = "/vault/data"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = false
  tls_cert_file = "/vault/tls/cert.pem"
  tls_key_file  = "/vault/tls/key.pem"
}

seal "transit" {
  address = "https://vault.example.com"
  disable_renewal = false
  key_name = "bmad-unseal"
  mount_path = "transit/"
}

ui = true
```

**Secret Access Pattern:**
```typescript
// Agent secret retrieval
import Vault from 'node-vault';

const vault = Vault({
  endpoint: process.env.VAULT_ADDR,
  token: process.env.VAULT_TOKEN
});

const secrets = await vault.read('secret/bmad/database');
const dbPassword = secrets.data.password;
```

### 7.3 RBAC Model

```yaml
# rbac/roles.yaml
roles:
  - name: system_admin
    permissions:
      - '*'
    
  - name: model_manager
    permissions:
      - models:read
      - models:write
      - content:read
      - content:approve
      - analytics:read
    
  - name: model_user
    permissions:
      - models:read:self
      - content:read:self
      - analytics:read:self
    
  - name: auditor
    permissions:
      - audit:read
      - compliance:read
      - '*:read'
```

---

## 8. Integration Architecture

### 8.1 External API Integration

```typescript
// integration/instagram.ts
export class InstagramPublisher {
  private readonly baseURL = 'https://graph.facebook.com/v18.0';
  
  async publishPost(opts: PublishOptions): Promise<PublishResult> {
    const { accessToken, imageUrl, caption } = opts;
    
    // Step 1: Create media container
    const container = await this.createContainer({
      image_url: imageUrl,
      caption,
      access_token: accessToken
    });
    
    // Step 2: Publish container
    const result = await this.publishContainer({
      creation_id: container.id,
      access_token: accessToken
    });
    
    // Step 3: Store in ledger
    await this.ledger.record({
      platform: 'instagram',
      post_id: result.id,
      timestamp: new Date()
    });
    
    return result;
  }
}
```

### 8.2 Event-Driven Integration

```typescript
// Message bus integration
import { connect } from 'amqplib';

export class EventBus {
  private connection: Connection;
  private channel: Channel;
  
  async publish(event: Event): Promise<void> {
    const exchange = 'bmad.events';
    const routingKey = event.type;
    
    await this.channel.publish(
      exchange,
      routingKey,
      Buffer.from(JSON.stringify(event)),
      {
        persistent: true,
        timestamp: Date.now(),
        messageId: event.job_id
      }
    );
  }
  
  async subscribe(
    pattern: string,
    handler: EventHandler
  ): Promise<void> {
    const queue = await this.channel.assertQueue('', {
      exclusive: true
    });
    
    await this.channel.bindQueue(
      queue.queue,
      'bmad.events',
      pattern
    );
    
    this.channel.consume(queue.queue, async (msg) => {
      if (msg) {
        const event = JSON.parse(msg.content.toString());
        await handler(event);
        this.channel.ack(msg);
      }
    });
  }
}
```

---

## 9. Deployment Architecture

### 9.1 CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: BMAD CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Lint
        run: npm run lint
      
      - name: Unit tests
        run: npm run test:unit
      
      - name: Integration tests
        run: npm run test:integration
      
      - name: Coverage report
        run: npm run test:coverage
      
      -