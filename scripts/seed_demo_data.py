"""Seed demo data for hackathon presentation."""
import asyncio
import json
from pathlib import Path
from datetime import datetime, timedelta


DEMO_MEETINGS = [
    {
        "id": "demo-meeting-001",
        "title": "Sprint 42 Planning",
        "date": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
        "summary": "Sprint 42 planning session. Team committed to API redesign, mobile UI updates, and DevOps pipeline improvements.",
        "action_items": [
            {"title": "API rate limiter implementation", "owner": "Raj Mehta",
             "email": "raj@demo.com", "due_date": "2025-08-01", "status": "overdue"},
            {"title": "Mobile UI accessibility audit", "owner": "Priya Shah",
             "email": "priya@demo.com", "due_date": "2025-08-05", "status": "overdue"},
        ],
        "decisions": [
            "Adopt microservices architecture for the new API",
            "Migrate CI/CD to GitHub Actions",
        ],
    },
    {
        "id": "demo-meeting-002",
        "title": "Design Review — Authentication Flow",
        "date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
        "summary": "Reviewed the new OAuth2 authentication flow design. JWT approach approved.",
        "action_items": [
            {"title": "Write JWT token management docs", "owner": "James Wilson",
             "email": "james@demo.com", "due_date": "2025-08-10", "status": "completed"},
        ],
        "decisions": [
            "Use JWT with refresh tokens for auth",
            "Drop XML support — REST + JSON only",
        ],
    },
    {
        "id": "demo-meeting-003",
        "title": "Quarterly OKR Review",
        "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
        "summary": "Q3 OKR review. Engineering team at 72% completion. Key risk: delayed API launch.",
        "action_items": [
            {"title": "Prepare Q3 engineering report", "owner": "Alice Chen",
             "email": "alice@demo.com", "due_date": "2025-08-25", "status": "pending"},
            {"title": "Update project timeline", "owner": "Sarah Patel",
             "email": "sarah@demo.com", "due_date": "2025-08-20", "status": "pending"},
        ],
        "decisions": ["Extend API launch deadline by 2 weeks"],
    },
]

DEMO_PARTICIPANTS = [
    {"name": "Alice Chen",   "email": "alice@demo.com",  "role": "Engineering Lead"},
    {"name": "Bob Kumar",    "email": "bob@demo.com",    "role": "Backend Engineer"},
    {"name": "Priya Shah",   "email": "priya@demo.com",  "role": "Mobile Engineer"},
    {"name": "Raj Mehta",    "email": "raj@demo.com",    "role": "DevOps Engineer"},
    {"name": "James Wilson", "email": "james@demo.com",  "role": "Backend Engineer"},
    {"name": "Sarah Patel",  "email": "sarah@demo.com",  "role": "Product Manager"},
]


async def seed():
    print("🌱 Seeding MeetMind demo data...")

    # Write demo context files
    demo_dir = Path("demo_data")
    demo_dir.mkdir(exist_ok=True)

    with open(demo_dir / "meetings.json", "w") as f:
        json.dump(DEMO_MEETINGS, f, indent=2)

    with open(demo_dir / "participants.json", "w") as f:
        json.dump(DEMO_PARTICIPANTS, f, indent=2)

    print(f"  ✅ {len(DEMO_MEETINGS)} historical meetings seeded")
    print(f"  ✅ {len(DEMO_PARTICIPANTS)} team members seeded")
    print(f"  ✅ {sum(len(m['action_items']) for m in DEMO_MEETINGS)} historical action items seeded")
    print(f"  ⚠️  2 overdue tasks seeded (will surface in cross-meeting memory)")
    print("\n🎯 Demo ready! Upload a meeting to see cross-meeting intelligence in action.")


if __name__ == "__main__":
    asyncio.run(seed())
