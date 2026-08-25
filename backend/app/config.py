"""Application configuration using pydantic-settings."""
from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "MeetMind"
    app_env: Literal["development", "staging", "production"] = "development"
    secret_key: str = "change-me"
    debug: bool = True

    # Database
    database_url: str = "sqlite+aiosqlite:///./meetmind.db"
    redis_url: str = "redis://localhost:6379/0"

    # AI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_fast_model: str = "gpt-4o-mini"
    hf_token: str = ""

    # Vector DB
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "meetmind"

    # Graph DB
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "meetmind123"

    # Storage
    local_storage_path: str = "./uploads"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    s3_bucket: str = "meetmind-uploads"
    use_s3: bool = False

    # LangSmith
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "meetmind"

    # Integrations
    jira_base_url: str = ""
    jira_email: str = ""
    jira_api_token: str = ""
    jira_project_key: str = "MEET"

    github_token: str = ""
    github_repo: str = ""

    slack_bot_token: str = ""
    slack_channel_id: str = ""

    notion_api_key: str = ""
    notion_database_id: str = ""

    asana_access_token: str = ""
    asana_workspace_gid: str = ""

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Auth
    clerk_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
