"""
Seed demo organization, users, and pre-processed historical meetings so the
hackathon demo can show cross-meeting memory / RAG Q&A immediately.
See docs/BLUEPRINT.md §24 "Pre-baked Demo Assets".

Usage: python scripts/seed_demo_data.py
"""
import asyncio

DEMO_ORG = {"name": "Acme Robotics", "slug": "acme-robotics", "timezone": "Asia/Kolkata"}

DEMO_USERS = [
    {"full_name": "Priya Shah", "email": "priya@acme.dev", "aliases": ["Priya", "PS"]},
    {"full_name": "Rahul Kumar", "email": "rahul@acme.dev", "aliases": ["Rahul", "RK"]},
    # TODO: add the remaining 8 team members referenced in the blueprint demo script
]


async def seed():
    raise NotImplementedError(
        "TODO: insert DEMO_ORG/DEMO_USERS into Postgres, then run the ingestion "
        "pipeline against the 5 historical meeting fixtures so memory_agent has "
        "something to retrieve during the live demo"
    )


if __name__ == "__main__":
    asyncio.run(seed())
