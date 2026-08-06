"""S3/GCS-backed object storage wrapper used by the ingestion agent."""


class _Storage:
    async def read(self, path: str) -> bytes:
        raise NotImplementedError("TODO: read raw bytes from S3/GCS at `path`")

    async def write(self, path: str, content: bytes) -> None:
        raise NotImplementedError("TODO: write bytes to S3/GCS at `path`")


storage = _Storage()
