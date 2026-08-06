# Agentic AI Meeting Assistant — Production Blueprint
### National Hackathon Edition | 36-Hour Build Plan

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Technology Stack](#3-technology-stack)
4. [Agent Architecture — LangGraph](#4-agent-architecture--langgraph)
5. [Multi-Agent Orchestration Design](#5-multi-agent-orchestration-design)
6. [Prompt Engineering Strategy](#6-prompt-engineering-strategy)
7. [Memory Architecture](#7-memory-architecture)
8. [Database Schema](#8-database-schema)
9. [Vector Database & RAG Strategy](#9-vector-database--rag-strategy)
10. [Knowledge Graph Design](#10-knowledge-graph-design)
11. [Tool Integration Architecture](#11-tool-integration-architecture)
12. [Human Approval Workflow](#12-human-approval-workflow)
13. [Idempotency Strategy](#13-idempotency-strategy)
14. [Audit Trail System](#14-audit-trail-system)
15. [API Design](#15-api-design)
16. [Event-Driven Architecture](#16-event-driven-architecture)
17. [Security & Authorization](#17-security--authorization)
18. [Deployment Architecture](#18-deployment-architecture)
19. [CI/CD Pipeline](#19-cicd-pipeline)
20. [Monitoring & Observability](#20-monitoring--observability)
21. [Testing & Evaluation Framework](#21-testing--evaluation-framework)
22. [Folder Structure](#22-folder-structure)
23. [Development Roadmap — 36 Hours](#23-development-roadmap--36-hours)
24. [Demo Flow — Hackathon Optimized](#24-demo-flow--hackathon-optimized)

---

## 1. Executive Summary

This blueprint defines **MeetMind** — a production-grade Agentic AI Meeting Assistant that transforms unstructured conversations into structured organizational knowledge and safely executes real-world follow-up actions.

**What separates MeetMind from a summarizer:**

| Summarizer | MeetMind (Agent) |
|---|---|
| Produces text | Makes decisions |
| One-shot LLM call | Multi-agent reasoning loop |
| No memory | Cross-meeting organizational memory |
| No actions | Executes in Jira, Slack, Calendar |
| No oversight | Human-in-the-loop approval gate |
| No confidence | Evidence-linked confidence scoring |
| Flat output | Knowledge graph across meetings |

**Core Value Proposition:**
> A meeting that ends without committed action is an expensive conversation. MeetMind ensures every commitment becomes a tracked, assigned, dated task — automatically, accurately, and safely.

---

## 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
│   Next.js Web App  ──  Chrome Extension  ──  Slack Bot Interface    │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTPS / WebSocket
┌────────────────────────────▼────────────────────────────────────────┐
│                         API GATEWAY                                 │
│            FastAPI (Python 3.12) + Redis Rate Limiting              │
│                JWT Auth ── RBAC ── Request Routing                  │
└──────┬─────────────┬──────────────┬────────────────┬───────────────┘
       │             │              │                │
┌──────▼──────┐ ┌───▼────┐  ┌──────▼──────┐  ┌────▼──────────────┐
│  INGESTION  │ │ AGENT  │  │  APPROVAL   │  │   INTEGRATION     │
│  SERVICE    │ │ORCHEST │  │  SERVICE    │  │   SERVICE         │
│  (Celery)   │ │(LGraph)│  │  (FastAPI)  │  │   (Tool Exec)     │
└──────┬──────┘ └───┬────┘  └──────┬──────┘  └────┬──────────────┘
       │             │              │                │
┌──────▼─────────────▼──────────────▼────────────────▼─────────────┐
│                       DATA LAYER                                   │
│  PostgreSQL   ──   Redis   ──  Qdrant   ──   Neo4j   ──  S3/GCS   │
│  (Core Data)    (Cache/Q)   (Vectors)    (KG)      (Media)        │
└───────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                    EXTERNAL INTEGRATIONS                             │
│   Jira  ──  GitHub  ──  Slack  ──  GCal  ──  Notion  ──  Linear    │
└─────────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                   OBSERVABILITY STACK                                │
│      Prometheus ── Grafana ── OpenTelemetry ── Sentry ── Langfuse   │
└─────────────────────────────────────────────────────────────────────┘
```

### Processing Pipeline (High Level)

```
Input (Audio/Video/Transcript)
        ↓
[1] INGESTION AGENT        → Normalize, hash, dedup check
        ↓
[2] TRANSCRIPTION AGENT    → Whisper STT + language detection
        ↓
[3] DIARIZATION AGENT      → Speaker segmentation + attribution
        ↓
[4] PLANNING AGENT         → Decompose meeting into analysis plan
        ↓
[5] EXTRACTION AGENT       → Decisions / Tasks / Risks / Questions
        ↓
[6] VERIFICATION AGENT     → Confidence scoring, hallucination check
        ↓
[7] IDENTITY AGENT         → Resolve owners to real people + emails
        ↓
[8] CALENDAR AGENT         → Resolve relative dates to exact dates
        ↓
[9] MEMORY AGENT           → Cross-meeting context enrichment
        ↓
[10] APPROVAL AGENT        → HITL dashboard, wait for user sign-off
        ↓
[11] INTEGRATION AGENT     → Execute approved actions in ext. systems
        ↓
[12] AUDIT AGENT           → Record full trace, results, and receipts
```

---

## 3. Technology Stack

### Backend

| Component | Technology | Justification |
|---|---|---|
| API Framework | FastAPI 0.115 | Async-native, OpenAPI auto-docs, Pydantic v2 validation |
| Agent Framework | LangGraph 0.2 | Stateful graph execution, cycles, human-in-the-loop, checkpointing |
| LLM — Primary | Claude claude-sonnet-4-6 | Superior reasoning, long context (200K tokens), low hallucination |
| LLM — Fast | Claude Haiku | Classification, quick entity extraction |
| Transcription | OpenAI Whisper v3 Large | Best-in-class accuracy, multilingual, timestamps |
| Diarization | Pyannote Audio 3.1 | State-of-the-art speaker segmentation |
| Task Queue | Celery + Redis | Async processing of heavy media files |
| Message Bus | Redis Streams | Event streaming between services |
| Embeddings | text-embedding-3-large | Semantic similarity for dedup and RAG |

### Data Layer

| Store | Technology | Purpose |
|---|---|---|
| Primary DB | PostgreSQL 16 + pgvector | All structured data, ACID guarantees |
| Cache | Redis 7.2 | Sessions, rate limits, task state |
| Vector DB | Qdrant | Semantic search over transcripts + tasks |
| Graph DB | Neo4j 5 | Cross-meeting knowledge graph |
| Object Storage | AWS S3 / GCS | Audio, video, transcript files |
| Search | Meilisearch | Full-text search over meetings |

### Frontend

| Component | Technology | Justification |
|---|---|---|
| Web App | Next.js 14 (App Router) | Server components, streaming, RSC |
| UI | Shadcn/UI + Tailwind | Rapid, polished, accessible |
| State | Zustand + React Query | Lightweight global state + server sync |
| Real-time | Server-Sent Events | Live progress during processing |
| Charts | Recharts | Meeting health analytics |
| Auth | Clerk / Supabase Auth | OAuth2, team management |

### Infrastructure

| Layer | Technology |
|---|---|
| Containerization | Docker + Docker Compose |
| Orchestration | Kubernetes (K8s 1.29) + Helm |
| CI/CD | GitHub Actions |
| IaC | Terraform |
| Secrets | HashiCorp Vault / AWS Secrets Manager |
| Observability | Prometheus + Grafana + OpenTelemetry + Langfuse |

---

## 23. Development Roadmap — 36 Hours

### Phase 1: Foundation (Hours 0–6)

**Goal:** Working end-to-end pipeline with mocked integrations

| Hour | Task | Owner |
|---|---|---|
| 0–1 | Project setup, Docker Compose, DB migrations | Backend |
| 1–2 | LangGraph state schema + graph skeleton (all nodes, no logic) | Backend |
| 2–3 | Ingestion Agent + file format detection | Backend |
| 3–4 | Transcription Agent (Whisper integration) | Backend |
| 4–5 | Diarization Agent (subtitle parsing + Pyannote) | Backend |
| 5–6 | Planning Agent (LLM-based) | Backend |
| 5–6 | Next.js app scaffold + upload UI | Frontend |

**Checkpoint:** Upload a TXT transcript → pipeline runs through Planning Agent

---

### Phase 2: Intelligence Core (Hours 6–14)

**Goal:** Full extraction, verification, resolution pipeline

| Hour | Task |
|---|---|
| 6–8 | Extraction Agent — main extraction prompt + few-shot examples |
| 8–9 | Verification Agent — quote existence check + LLM verification |
| 9–10 | Identity Resolution Agent — fuzzy matching + "I" resolution |
| 10–11 | Calendar Resolution Agent — natural language → dates |
| 11–12 | Memory Agent — Qdrant setup + semantic dedup |
| 12–14 | Processing progress API + WebSocket streaming |
| 12–14 | Meeting report UI + action items list |

**Checkpoint:** Upload meeting → get structured report + action items with confidence scores

---

### Phase 3: Agentic Capabilities (Hours 14–22)

**Goal:** HITL approval, integrations, audit trail, memory

| Hour | Task |
|---|---|
| 14–16 | Approval Agent + LangGraph interrupt_before |
| 16–17 | Approval Dashboard UI (edit/reject/merge) |
| 17–18 | Payload Preview UI (exact API call shown before execute) |
| 18–20 | Integration Agent — Jira + GitHub + Slack (real calls) |
| 20–21 | Audit Trail — complete logging + explainability endpoint |
| 21–22 | Idempotency — all 4 layers implemented |
| 21–22 | Audit Trail UI component |

**Checkpoint:** Full flow: upload → extract → approve → Jira ticket created → audit shows why

---

### Phase 4: Advanced Features (Hours 22–30)

**Goal:** Cross-meeting memory, knowledge graph, analytics, stretch goals

| Hour | Task |
|---|---|
| 22–23 | Neo4j knowledge graph — schema + update logic |
| 23–24 | Cross-meeting Q&A endpoint (RAG) |
| 24–25 | Meeting Health Analytics (talk time, decision density) |
| 25–26 | Disagreement Detection in extraction prompt |
| 26–27 | Repeat Commitment Detection |
| 27–28 | Code-switched language support (Hindi/English) |
| 28–29 | Knowledge Graph visualization in frontend |
| 29–30 | Follow-up Agent — overdue detection + reminders |

**Checkpoint:** Ask "What did we decide about X in past meetings?" → get cited answer

---

### Phase 5: Polish & Demo Prep (Hours 30–36)

**Goal:** Production-quality demo, evaluation, documentation

| Hour | Task |
|---|---|
| 30–31 | Load pre-baked demo meeting data (sprint planning + incident review) |
| 31–32 | Performance optimization — async everywhere, DB indexes |
| 32–33 | End-to-end evaluation run — verify all 7 metrics |
| 33–34 | Error handling + graceful degradation |
| 34–35 | Demo flow rehearsal + slide deck |
| 35–36 | Final polish, recording backup demo, README |

---

## 24. Demo Flow — Hackathon Optimized

### Demo Script (8 minutes)

**Minute 1: Hook** *(The Problem)*
> "Every week, your team holds 5 meetings. Each generates 30+ minutes of talk. What happens to the decisions? The commitments? They die in a transcript nobody reads."

**Minute 2: Upload & Processing** *(The Magic Begins)*
> Upload a pre-prepared 45-minute sprint planning meeting (audio). Show real-time WebSocket progress, 12 specialized AI agents running in sequence, transcript appearing with speaker labels.

**Minute 3: Structured Intelligence** *(More Than Summarization)*
> Show full meeting report: executive summary, decisions, open questions, risks, disagreement detection, key insights.

**Minute 4: Action Items with Evidence** *(The Core Value)*
> 7 action items with confidence scores, click-to-evidence in transcript, resolved owners/dates, one flagged as a repeat commitment.

**Minute 5: Human-in-the-Loop** *(Safety & Control)*
> Approval dashboard, edit an item, show payload preview before any external call, reject a hallucinated item, execute.

**Minute 6: Real Integrations** *(It Actually Works)*
> Jira ticket created with evidence link, Slack recap posted, every action traceable to the meeting moment that justified it.

**Minute 7: Cross-Meeting Memory** *(The Differentiator)*
> RAG Q&A over org history with citations, knowledge graph visualization, overdue commitment tracker.

**Minute 8: Architecture & Metrics** *(Credibility)*
> LangGraph pipeline visualization, Grafana dashboard, audit trail, 45-minute meeting processed in 2m 47s.

### Pre-baked Demo Assets (prepare before hackathon)

1. Primary demo transcript: 45-min sprint planning meeting (TXT, pre-labeled) — 8 action items, 3 decisions, 2 risks, 1 disagreement, 1 repeat commitment, one "next Diwali" date reference.
2. Secondary demo transcript: 30-min incident post-mortem (audio) — shows audio → transcription → diarization flow.
3. Historical meeting corpus: 5 past meetings already processed, for cross-meeting Q&A demo.
4. Pre-seeded org directory: 10 team members with emails, Slack IDs, Jira IDs.
5. Connected integrations: Jira sandbox + Slack test workspace + GitHub test repo.

---

*Full agent code, database schema, API design, and infra config referenced in
this blueprint are implemented under `backend/`, `frontend/`, and
`infrastructure/` in this repository. See each module's source for the
authoritative, up-to-date implementation — this document is the original
design reference and may drift from the code over time.*

*Blueprint version 1.0 — MeetMind — National Hackathon Build*
*Estimated build time: 36 hours*
