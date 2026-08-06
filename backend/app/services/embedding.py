"""text-embedding-3-large wrapper used for RAG, dedup, and memory search."""


async def embed(text: str) -> list:
    raise NotImplementedError("TODO: call OpenAI embeddings API, return a 3072-dim vector")
