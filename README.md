# MeetMind — Agentic AI Meeting Assistant

MeetMind transforms unstructured meeting conversations into structured
organizational knowledge and safely executes real-world follow-up actions
(Jira tickets, Slack recaps, calendar holds) with a human-in-the-loop
approval gate before anything touches an external system.

This repo is a scaffold generated from the project blueprint
(`docs/BLUEPRINT.md`). It contains the folder structure, core agent logic,
database schema, API surface, and infra config described there. Most
service bodies are stubbed with `TODO`s — see the blueprint for full
reference implementations of every agent.

## What separates MeetMind from a summarizer

| Summarizer | MeetMind (Agent) |
|---|---|
| Produces text | Makes decisions |
| One-shot LLM call | Multi-agent reasoning loop |
| No memory | Cross-meeting organizational memory |
| No actions | Executes in Jira, Slack, Calendar |
| No oversight | Human-in-the-loop approval gate |
| No confidence | Evidence-linked confidence scoring |
| Flat output | Knowledge graph across meetings |

## Quick start

```bash
cp .env.example .env        # fill in ANTHROPIC_API_KEY etc.
docker compose -f infrastructure/docker-compose.yml up --build
```

- API: http://localhost:8000
- Frontend: http://localhost:3000
- Qdrant: http://localhost:6333
- Neo4j browser: http://localhost:7474

## Repo layout

```
backend/     FastAPI + LangGraph agent pipeline
frontend/    Next.js approval dashboard & meeting UI
infrastructure/  Docker Compose, Helm, Terraform
scripts/     Demo data seeding, evaluation runner
docs/        Full architecture blueprint
.github/     CI/CD workflows
```

## Pipeline (12 agents)

Ingestion → Transcription → Diarization → Planning → Extraction →
Verification → Identity Resolution → Calendar Resolution → Memory →
Approval (HITL) → Integration → Audit

See `docs/BLUEPRINT.md` §4–5 for full agent specs and `backend/app/agents/`
for the code.

## License

MIT — see LICENSE.
