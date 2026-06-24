from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    PROVIDER_LLM: str = "openai"
    AWS_BEARER_TOKEN_BEDROCK: str | None = None
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""

    REDIS_URL: str = "redis://:myredissecret@localhost:6379/0"

    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "http://localhost:3000"

    @field_validator("DB_PORT", mode="before")
    @classmethod
    def parse_db_port(cls, v):
        if v == "" or v is None:
            return 5432
        return int(v)


settings = Settings()
