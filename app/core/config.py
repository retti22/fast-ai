from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(
        "postgresql://postgres:1234@localhost:5432/postgres", env="DATABASE_URL"
    )
    openai_api_key: str | None = Field(default=None, env="OPENAI_API_KEY")
    text_embedding_model: str = Field(
        default="text-embedding-3-small", env="TEXT_EMBEDDING_MODEL"
    )
    chat_model: str = Field(default="gpt-4o-mini", env="CHAT_MODEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
