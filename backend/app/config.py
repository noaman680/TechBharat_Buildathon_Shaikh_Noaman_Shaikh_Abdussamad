from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Core
    ENV: str = "development"
    DATABASE_URL: str = "postgresql://meetmind:meetmind@localhost:5432/meetmind"
    REDIS_URL: str = "redis://localhost:6379"
    QDRANT_URL: str = "http://localhost:6333"
    NEO4J_URL: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "meetmind"

    # LLM
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""  # Whisper + embeddings

    # Storage
    S3_BUCKET: str = "meetmind-media"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"

    # Auth
    JWT_SECRET: str = "change-me"
    JWT_EXPIRY_MINUTES: int = 15

    # Integrations (per-org overrides live in the `integrations` table)
    JIRA_BASE_URL: str = ""
    GITHUB_TOKEN: str = ""
    SLACK_BOT_TOKEN: str = ""

    # Observability
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    SENTRY_DSN: str = ""


settings = Settings()
