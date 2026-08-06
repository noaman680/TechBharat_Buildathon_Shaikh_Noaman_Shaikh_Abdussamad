"""Neo4j knowledge graph client."""
from neo4j import AsyncGraphDatabase
from app.config import settings


def get_driver():
    return AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )


async def create_meeting_node(meeting_id: str, org_id: str, date: str, summary: str):
    async with get_driver() as driver:
        async with driver.session() as session:
            await session.run(
                """
                MERGE (m:Meeting {id: $id})
                SET m.org_id = $org_id, m.date = $date, m.summary = $summary
                """,
                id=meeting_id, org_id=org_id, date=date, summary=summary,
            )


async def create_task_node(task_id: str, meeting_id: str, title: str,
                            owner_email: str, due_date: str, status: str):
    async with get_driver() as driver:
        async with driver.session() as session:
            await session.run(
                """
                MERGE (t:Task {id: $task_id})
                SET t.title = $title, t.due_date = $due_date, t.status = $status
                WITH t
                MATCH (m:Meeting {id: $meeting_id})
                MERGE (t)-[:EXTRACTED_FROM]->(m)
                WITH t
                MERGE (p:Person {email: $owner_email})
                MERGE (p)-[:OWNS]->(t)
                """,
                task_id=task_id, meeting_id=meeting_id, title=title,
                owner_email=owner_email, due_date=due_date or "", status=status,
            )


async def get_overdue_tasks(org_id: str, owner_emails: list[str]) -> list[dict]:
    async with get_driver() as driver:
        async with driver.session() as session:
            result = await session.run(
                """
                MATCH (p:Person)-[:OWNS]->(t:Task)-[:EXTRACTED_FROM]->(m:Meeting)
                WHERE m.org_id = $org_id
                  AND p.email IN $emails
                  AND t.status IN ['pending', 'approved']
                  AND t.due_date < date()
                RETURN t.id as id, t.title as title, t.due_date as due_date,
                       p.email as owner, m.date as meeting_date
                ORDER BY t.due_date
                LIMIT 10
                """,
                org_id=org_id, emails=owner_emails,
            )
            return [dict(r) async for r in result]
