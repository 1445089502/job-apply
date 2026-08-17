"""应用配置：从环境变量 / .env 读取，禁止硬编码敏感信息。"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "job-apply"
    app_env: str = "dev"  # dev / test / prod
    debug: bool = True

    # 数据库：MVP 默认 SQLite，后续切 MySQL
    database_url: str = "sqlite:///./data/job_apply.db"

    # 安全（生产必改）
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"

    # AI（MVP 可后置）
    embedding_model: str = "bge-m3"
    llm_provider: str = ""  # 空 = 不启用 LLM


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
