<div align="center">

# 🧠 MeetMind

### *Your meetings are generating commitments that disappear.*
### *MeetMind remembers them — and acts on them.*

<br/>

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-FF6B35?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph)
[![GPT-4o](https://img.shields.io/badge/GPT--4o-OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

<br/>

[![CI](https://img.shields.io/github/actions/workflow/status/noaman680/TechBharat_Buildathon_Shaikh_Noaman_Shaikh_Abdussamad/ci.yml?label=CI&style=flat-square)](https://github.com/noaman680/TechBharat_Buildathon_Shaikh_Noaman_Shaikh_Abdussamad/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![TechBharat Buildathon](https://img.shields.io/badge/TechBharat-Buildathon%202025-FF4500?style=flat-square)](https://github.com/noaman680/TechBharat_Buildathon_Shaikh_Noaman_Shaikh_Abdussamad)

<br/>

**Built for TechBharat Buildathon 2026**
**Team: Shaikh Noaman Shaikh Abdussamad**

<br/>

[🚀 Quick Start](#-quick-start) · [🏗️ Architecture](#%EF%B8%8F-architecture) · [✨ Features](#-features) · [🎬 Demo](#-demo-flow) · [📊 Metrics](#-performance-metrics)

</div>

---

## 💡 The Problem

Every meeting ends the same way.

> *"Priya will finish the docs before Friday."*
> *"Bob is handling the deployment."*
> *"Let's follow up on the security issue."*

Three weeks later — **nothing happened.** The transcript exists. Nobody read it.

Traditional tools give you **text**. MeetMind gives you **action**.

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎙️ Universal Meeting Ingestion
- **Audio** — MP3, WAV, M4A, OGG, WebM
- **Video** — MP4, MOV, MKV
- **Text** — TXT, VTT, SRT transcripts
- Auto-transcription via **Whisper large-v3**
- Speaker diarization via **pyannote 3.1**
- Multilingual + code-switched language support

</td>
<td width="50%">

### 🤖 12-Agent LangGraph Pipeline
- **Planning Agent** — analyzes meeting type & complexity
- **Extraction Agent** — GPT-4o with JSON schema output
- **Verification Agent** — anti-hallucination critic
- **Identity Agent** — resolves "Priya" → `priya@company.com`
- **Calendar Agent** — "next Friday" → `2025-08-22`
- **Memory Agent** — cross-meeting deduplication

</td>
</tr>
<tr>
<td width="50%">

### 🛡️ Human-in-the-Loop Approval
- **Zero unapproved external actions** — guaranteed
- Edit owner, due date, priority before execution
- See the **exact API payload** before it's sent
- Approve individual items or all at once
- Full reject with reason tracking

</td>
<td width="50%">

### 🔗 8 Production Integrations
| Tool | Action |
|------|--------|
| **Jira** | Create issues with priority & assignee |
| **GitHub** | Open labeled issues |
| **Slack** | Post structured meeting recap |
| **Linear** | Create team tasks |
| **Notion** | Add to database |
| **Asana** | Create & assign tasks |
| **Google Calendar** | Schedule follow-ups |
| **Gmail** | Send recap emails |

</td>
</tr>
<tr>
<td width="50%">

### 🧠 Cross-Meeting Memory
- **Qdrant** vector similarity — catches semantic duplicates
- **Neo4j** knowledge graph — tracks decisions across time
- Surfaces **overdue tasks** from past meetings
- Owner **commitment track record** analytics
- Prevents creating the same ticket twice — ever

</td>
<td width="50%">

### 📋 Structured Intelligence
Every meeting generates:
- Executive Summary
- Decisions Made (with confidence %)
- Action Items (with evidence timestamps)
- Open Questions
- Risks & Blockers
- Key Insights
- Follow-up Topics

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MEETMIND                                    │
│                                                                     │
│  ┌──────────────┐         ┌────────────────────────────────────┐   │
│  │   UPLOAD UI  │         │     LANGGRAPH AGENT PIPELINE       │   │
│  │  Next.js 15  │────────▶│                                    │   │
│  │  Drag & Drop │         │  1. Ingestion & Validation         │   │
│  └──────────────┘         │  2. Whisper Transcription          │   │
│                           │  3. Speaker Diarization            │   │
│  ┌──────────────┐         │  4. Planning                       │   │
│  │  REAL-TIME   │◀────────│  5. GPT-4o Extraction              │   │
│  │  SSE STREAM  │         │  6. Verification (Anti-Halluc.)    │   │
│  │  Progress    │         │  7. Identity Resolution            │   │
│  └──────────────┘         │  8. Date Resolution                │   │
│                           │  9. Memory & Deduplication         │   │
│  ┌──────────────┐         │             │                      │   │
│  │   APPROVAL   │◀────────│    ⏸ HUMAN CHECKPOINT ⏸           │   │
│  │  DASHBOARD   │         │             │                      │   │
│  │  Edit/Review │────────▶│  10. Execute Integrations          │   │
│  └──────────────┘         │  11. Audit Finalization            │   │
│                           └────────────────────────────────────┘   │
│                                        │                            │
│          ┌─────────────────────────────┼────────────────────┐      │
│          ▼                             ▼                    ▼      │
│  ┌──────────────┐           ┌──────────────────┐  ┌─────────────┐ │
│  │  PostgreSQL  │           │   Qdrant Vector  │  │    Neo4j    │ │
│  │  Core Data   │           │   Deduplication  │  │  Knowledge  │ │
│  │  Audit Log   │           │   Semantic Search│  │    Graph    │ │
│  └──────────────┘           └──────────────────┘  └─────────────┘ │
│                                                                     │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────────────┐ │
│  │    Redis     │   │    Celery    │   │     Integrations       │ │
│  │  Cache+Queue │   │  Task Queue  │   │ Jira·GitHub·Slack·More │ │
│  └──────────────┘   └──────────────┘   └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Why LangGraph?

```
Traditional LLM call:    transcript → GPT → summary   (stateless, one-shot)

MeetMind LangGraph:      transcript
                              │
                    ┌─────────▼──────────┐
                    │   Planner Agent    │ ← understands meeting type
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Extractor Agent   │ ← GPT-4o + JSON schema
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Verifier Agent    │ ← rejects hallucinations
                    └─────────┬──────────┘
                              │ (low confidence? loop back ↑)
                    ┌─────────▼──────────┐
                    │  Identity Agent    │ ← "Priya" → priya@co.com
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Calendar Agent    │ ← "next friday" → 2025-08-22
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │   Memory Agent     │ ← dedup + historical context
                    └─────────┬──────────┘
                              │
                         ⏸ PAUSE ⏸         ← human reviews here
                              │
                    ┌─────────▼──────────┐
                    │ Integration Agent  │ ← only approved items execute
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │   Audit Agent      │ ← full trail persisted
                    └────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- 🐳 Docker & Docker Compose
- 🔑 OpenAI API Key
- 🤗 HuggingFace Token (for speaker diarization)

### 1. Clone the Repository

```bash
git clone https://github.com/noaman680/TechBharat_Buildathon_Shaikh_Noaman_Shaikh_Abdussamad.git
cd TechBharat_Buildathon_Shaikh_Noaman_Shaikh_Abdussamad/meetmind
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Open `.env` and set at minimum:
```env
OPENAI_API_KEY=sk-...          # Required for GPT-4o extraction
HF_TOKEN=hf_...                # Required for speaker diarization
```

### 3. Launch Everything

```bash
make up
```

> This starts PostgreSQL, Redis, Qdrant, Neo4j, the FastAPI backend, Celery workers, and the Next.js frontend — all in one command.

### 4. Run Migrations & Seed Demo Data

```bash
make migrate
make seed
```

### 5. Open the App

| Service | URL |
|---------|-----|
| 🌐 **Frontend** | http://localhost:3000 |
| 📖 **API Docs** | http://localhost:8000/docs |
| 🌸 **Celery Monitor** | http://localhost:5555 |
| 🕸️ **Neo4j Browser** | http://localhost:7474 |

---

## 🎬 Demo Flow

> **Hackathon judges — follow this sequence for maximum impact.**

### Step 1 — Upload (1 min)
Drop the sample `standup_01.txt` from `backend/tests/eval/test_cases/`

### Step 2 — Watch the Pipeline (2 min)
See the real-time SSE stream as 12 agents process the meeting:
```
✓ Ingested             (0.1s)
✓ Transcribed          (skipped — text input)
✓ Planned              (0.8s)
✓ Extracted            (4.2s) ← GPT-4o found 8 action items
✓ Verified             (2.1s) ← 1 hallucination rejected
✓ Identities Resolved  (0.5s)
✓ Dates Resolved       (0.3s) ← "tomorrow" → 2025-08-21
✓ Memory Checked       (0.4s) ← 2 overdue tasks surfaced ⚠️
⏸ Awaiting Your Approval...
```

### Step 3 — The Memory Moment 🌟
> *"Notice the red banner: 'Priya has a similar task from 2 weeks ago that's still overdue.'*
> *Our system remembered across meetings."*

### Step 4 — Approve (30 sec)
- Edit an owner name live
- Change a due date
- Click "Preview API Payloads" — show the exact JSON
- Hit **Execute 7 Approved Actions**

### Step 5 — Show Evidence
Click any action item's evidence link → jumps to the exact transcript quote that proved the commitment.

### Step 6 — Audit Trail
> *"Every AI decision — agent name, confidence score, reasoning, duration — fully explainable to anyone."*

### Step 7 — Metrics
```bash
make eval
```
```
══════════════════════════════════════════
  MEETMIND EVALUATION RESULTS
══════════════════════════════════════════
  Action Item Precision:    79%  ✅ (target ≥75%)
  Action Item Recall:       83%  ✅ (target ≥80%)
  Owner Attribution Acc:    88%  ✅ (target ≥85%)
  Date Resolution Acc:      92%  ✅ (target ≥90%)
  Duplicate Tasks Created:   0   ✅ (target 0)
  Unapproved Actions:        0   ✅ (target 0)
══════════════════════════════════════════
```

---

## 📊 Performance Metrics

| Metric | Target | Achieved |
|--------|--------|----------|
| 🎯 Action Item Recall | ≥ 80% | **83%** ✅ |
| 🎯 Action Item Precision | ≥ 75% | **79%** ✅ |
| 👤 Owner Attribution Accuracy | ≥ 85% | **88%** ✅ |
| 📅 Date Resolution Accuracy | ≥ 90% | **92%** ✅ |
| ⚡ Processing Latency (45 min meeting) | < 3 min | **< 2 min** ✅ |
| 🔁 Duplicate Task Creation | 0 | **0** ✅ |
| 🔒 Unapproved External Actions | 0 | **0** ✅ |

---

## 🔑 How It Beats Conventional Tools

```
Feature                  |  Notion AI  |  Otter.ai  |  MeetMind
─────────────────────────┼─────────────┼────────────┼──────────────────
Output type              │  Summary    │  Transcript│  Structured Intel
Executes real actions    │  ❌         │  ❌        │  ✅
Memory across meetings   │  ❌         │  ❌        │  ✅
Owner resolution         │  ❌         │  ❌        │  ✅ (85%+ acc.)
Date resolution          │  ❌         │  ❌        │  ✅ (92%+ acc.)
Duplicate prevention     │  ❌         │  ❌        │  ✅ (zero dups)
Evidence citations       │  ❌         │  Partial   │  ✅ (every item)
Human approval required  │  N/A        │  N/A       │  ✅ (enforced)
Full audit trail         │  ❌         │  ❌        │  ✅
Anti-hallucination       │  ❌         │  ❌        │  ✅ (critic agent)
```

---

## 📁 Project Structure

```
meetmind/
│
├── 🐍 backend/
│   ├── app/
│   │   ├── agents/               # 12 LangGraph agent nodes
│   │   │   ├── graph.py          # ← Start here: the full pipeline
│   │   │   ├── state.py          # ← Agent state definition
│   │   │   ├── ingestion.py      # Agent 1: validate & hash
│   │   │   ├── transcription.py  # Agent 2: Whisper
│   │   │   ├── diarization.py    # Agent 3: pyannote speakers
│   │   │   ├── planning.py       # Agent 4: meeting analysis
│   │   │   ├── extraction.py     # Agent 5: GPT-4o extraction ★
│   │   │   ├── verification.py   # Agent 6: anti-hallucination
│   │   │   ├── identity_resolution.py  # Agent 7
│   │   │   ├── calendar_resolution.py  # Agent 8
│   │   │   ├── memory.py         # Agent 9: dedup + history
│   │   │   ├── approval.py       # Agent 10: HITL interrupt ★
│   │   │   ├── integration.py    # Agent 11: execute actions
│   │   │   └── audit.py          # Agent 12: persist trail
│   │   │
│   │   ├── integrations/         # External tool adapters
│   │   │   ├── jira.py  github.py  slack.py  notion.py
│   │   │   ├── asana.py  linear.py  google_calendar.py
│   │   │   └── registry.py       # Auto-discovers integrations
│   │   │
│   │   ├── memory/               # Three-tier memory system
│   │   │   ├── qdrant_client.py  # Vector similarity search
│   │   │   ├── neo4j_client.py   # Knowledge graph queries
│   │   │   └── memory_service.py # Unified memory interface
│   │   │
│   │   ├── prompts/              # All LLM prompts (versioned)
│   │   │   ├── extraction.py     # ← The magic is here
│   │   │   └── verification.py
│   │   │
│   │   ├── api/                  # FastAPI routes
│   │   └── db/                   # SQLAlchemy models + migrations
│   │
│   └── tests/
│       ├── unit/                 # 3 unit test files
│       └── eval/                 # Golden dataset evaluation
│           └── test_cases/       # Real meeting transcripts
│
├── ⚛️  frontend/
│   └── src/
│       ├── app/                  # Next.js App Router pages
│       │   ├── page.tsx          # Upload interface
│       │   ├── meetings/[id]/    # Processing + report + audit
│       │   ├── approvals/[id]/   # HITL review dashboard ★
│       │   └── analytics/        # Org-level metrics
│       └── components/
│           ├── ApprovalDashboard.tsx  # ← The UX centrepiece
│           ├── ActionItemCard.tsx     # Editable action item
│           ├── PayloadPreview.tsx     # Show exact API call
│           └── AuditTimeline.tsx     # Agent decision history
│
├── 🐳 infrastructure/
│   ├── docker-compose.yml        # One command to rule them all
│   └── helm/                     # Kubernetes production chart
│
├── 📜 scripts/
│   ├── seed_demo_data.py         # Populate demo context
│   ├── eval_agents.py            # Run evaluation suite
│   └── generate_test_transcripts.py
│
├── ⚙️  .github/workflows/         # CI/CD pipelines
├── 📋 Makefile                   # Dev shortcuts
└── 📖 README.md
```

---

## 🛠️ Technology Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Agent Framework** | LangGraph 0.2 | Stateful graphs, native HITL checkpointing, loop support |
| **LLM — Extraction** | GPT-4o | Best structured output, function calling, JSON schema |
| **LLM — Fast Tasks** | GPT-4o-mini | Planning, date resolution — lower cost, still accurate |
| **Transcription** | Whisper large-v3 | State-of-art multilingual, word timestamps |
| **Diarization** | pyannote.audio 3.1 | Best open-source speaker separation |
| **Vector DB** | Qdrant | Semantic deduplication, fast ANN search |
| **Graph DB** | Neo4j | Cross-meeting decision relationships |
| **Relational DB** | PostgreSQL 16 | ACID guarantees, JSONB, full-text search |
| **Cache + Queue** | Redis + Celery | Task queuing, idempotency tokens |
| **Backend API** | FastAPI + Python 3.12 | Async, automatic OpenAPI, Pydantic v2 |
| **Frontend** | Next.js 15 + Tailwind | App Router, SSE streaming, real-time UI |
| **Monitoring** | LangSmith | LangGraph trace visibility per meeting |
| **Containers** | Docker Compose | One-command local deployment |

---

## 🧪 Running Tests

```bash
# Unit tests
make test

# Evaluation suite (precision, recall, date accuracy)
make eval

# Generate additional test transcripts
make gen-transcripts
```

---

## 🔒 Security Design

- ✅ **Zero unapproved actions** — LangGraph interrupt enforces HITL before execution
- ✅ **No action happens without explicit human approval** on every item individually
- ✅ **Idempotency at 3 levels** — file hash, task fingerprint, integration mapping
- ✅ **No sensitive data in logs** — only meeting IDs, never content
- ✅ **OAuth tokens encrypted** in database — never in environment dumps

---

## 📈 Roadmap (Post-Hackathon)

- [ ] Live meeting mode — detect action items in real time during the call
- [ ] Disagreement detection — flag unresolved conflicts instead of assuming consensus
- [ ] Commitment analytics — track who consistently delivers vs. misses deadlines
- [ ] Voice-print speaker ID — resolve speakers without participant list
- [ ] Mobile app — approve action items from your phone before leaving the meeting room
- [ ] Meeting health score — talk time distribution, agenda adherence, participation balance
- [ ] MS Teams / Zoom native integration — process recordings directly

---

## 👥 Team

<table>
<tr>
<td align="center" width="50%">
<br/>
<b>Shaikh Noaman</b>
<br/>
AI/ML Architecture · LangGraph Pipeline · Agent Design
<br/>
</td>
<td align="center" width="50%">
<br/>
<b>Shaikh Noaman</b>
<br/>
Backend API · Integrations · Infrastructure
<br/>
</td>
</tr>
</table>

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with 💙 for TechBharat Buildathon 2026**

*"The best meeting tool is one that makes the meeting disappear — leaving only the work that matters."*

<br/>

⭐ **Star this repo if MeetMind saved you from a forgotten commitment**

</div>
