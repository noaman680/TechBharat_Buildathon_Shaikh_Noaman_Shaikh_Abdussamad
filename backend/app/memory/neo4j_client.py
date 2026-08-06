"""Neo4j driver + knowledge-graph update logic. See docs/BLUEPRINT.md §10."""
from neo4j import AsyncGraphDatabase

from app.config import settings

neo4j_driver = AsyncGraphDatabase.driver(
    settings.NEO4J_URL, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
)


async def update_knowledge_graph(meeting, state) -> None:
    """
    Upsert (:Person), (:Meeting), (:ActionItem), (:Decision), (:Project), (:Risk)
    nodes and the relationships between them for this meeting. See the Cypher
    schema in docs/BLUEPRINT.md #10 for node/relationship shapes.
    """
    raise NotImplementedError("TODO: write Cypher MERGE statements for this meeting's graph data")
