"""应用配置：从环境变量 / .env 读取，禁止硬编码敏感信息。"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录（backend/app/core/config.py -> 上溯 3 级到 job-apply）
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "job-apply"
    app_env: str = "dev"  # dev / test / prod
    debug: bool = True

    # 数据库：MVP 默认 SQLite（锚定项目根，避免因启动目录不同产生多个库），后续切 MySQL
    database_url: str = f"sqlite:///{(PROJECT_ROOT / 'data' / 'job_apply.db').as_posix()}"

    # 安全（生产必改）
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"

    # AI（MVP 可后置；embedding_model=stub 用离线哈希向量便于验证）
    embedding_model: str = "stub"  # stub / sentence-transformers / bge-m3
    llm_provider: str = ""  # 空 = 不启用 LLM


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
