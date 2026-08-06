# 🧠 MeetMind — Agentic AI Meeting Assistant

> **National Hackathon Project** | TechBharat Buildathon 2025
> **Team:** Shaikh Noaman & Shaikh Abdussamad

MeetMind transforms raw meeting audio, video, or transcripts into **structured organizational intelligence** and **safely executes follow-up actions** — creating Jira tickets, Slack recaps, and calendar invites — but only after human approval.

---

## 🏆 What Makes This Different

| Feature | Traditional Tool | MeetMind |
|---------|-----------------|---------|
| Output | Text summary | Structured intelligence + executed actions |
| Memory | None | Cross-meeting knowledge graph |
| Ownership | Guessed | Resolved with 85%+ accuracy |
| Dates | Copied verbatim | Resolved to exact calendar dates |
| Duplicates | Creates new every run | Zero duplicates, idempotent by design |
| Human control | None | Full approval dashboard before ANY action |
| Explainability | Black box | Every decision cited, confidence-scored, timestamped |
| Execution | None | Real Jira tickets, Slack messages, calendar invites |

---

## 🏗️ Architecture

```
User Upload (Audio/Video/TXT/VTT/SRT)
       │
       ▼
LangGraph Multi-Agent Pipeline
  ├── Agent 1:  Ingestion & Validation
  ├── Agent 2:  Transcription (Whisper large-v3)
  ├── Agent 3:  Speaker Diarization (pyannote 3.1)
  ├── Agent 4:  Planning
  ├── Agent 5:  Extraction (GPT-4o + JSON Schema)
  ├── Agent 6:  Verification (anti-hallucination)
  ├── Agent 7:  Identity Resolution
  ├── Agent 8:  Calendar/Date Resolution
  ├── Agent 9:  Memory Enrichment (Qdrant + Neo4j)
  ├── Agent 10: ⏸ HUMAN APPROVAL CHECKPOINT
  ├── Agent 11: Integration Execution
  └── Agent 12: Audit Finalization
       │
       ▼
Integrations: Jira │ GitHub │ Slack │ Google Calendar │ Notion │ Asana
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Node.js 20+
- OpenAI API Key

### 1. Clone & Configure

```bash
git clone https://github.com/noaman680/TechBharat_Buildathon_Shaikh_Noaman_Shaikh_Abdussamad.git
cd TechBharat_Buildathon_Shaikh_Noaman_Shaikh_Abdussamad/meetmind
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start All Services

```bash
docker compose -f infrastructure/docker-compose.yml up -d
```

### 3. Run Database Migrations

```bash
docker compose exec backend alembic upgrade head
```

### 4. Seed Demo Data

```bash
docker compose exec backend python scripts/seed_demo_data.py
```

### 5. Open the App

- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Celery Monitor:** http://localhost:5555
- **Neo4j Browser:** http://localhost:7474

---

## 📁 Project Structure

```
meetmind/
├── backend/           FastAPI + LangGraph agents
├── frontend/          Next.js 15 + Tailwind + shadcn/ui
├── infrastructure/    Docker Compose + Helm + Terraform
├── scripts/           Demo seeding + evaluation
└── .github/           CI/CD workflows
```

---

## 🧪 Running Evaluations

```bash
cd backend
python tests/eval/evaluate.py
# Expected: Recall ≥80%, Precision ≥75%, Date Accuracy ≥90%
```

---

## 🔑 Environment Variables

See `.env.example` for all required variables.

Key variables:
- `OPENAI_API_KEY` — GPT-4o for extraction & reasoning
- `HF_TOKEN` — HuggingFace token for pyannote diarization
- `PINECONE_API_KEY` — Vector similarity search
- `NEO4J_URI` / `NEO4J_PASSWORD` — Knowledge graph

---

## 📊 Target Metrics

| Metric | Target |
|--------|--------|
| Action Item Recall | ≥ 80% |
| Action Item Precision | ≥ 75% |
| Owner Attribution Accuracy | ≥ 85% |
| Date Resolution Accuracy | ≥ 90% |
| Processing Latency (45-min meeting) | < 3 min |
| Duplicate Task Creation | 0 |
| Unapproved External Actions | 0 |

---

## 👥 Team

- **Shaikh Noaman** — AI/ML & LangGraph Architecture
- **Shaikh Noaman** — Backend API & Integrations

---

*Built for TechBharat Buildathon 2026*
