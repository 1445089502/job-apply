"""数据库引擎 / 会话 / 建表。MVP 默认 SQLite。"""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _create_engine(url: str):
    connect_args = {"check_same_thread": False}
    if url.startswith("sqlite") and ":memory:" in url:
        from sqlalchemy.pool import StaticPool

        return create_engine(url, connect_args=connect_args, poolclass=StaticPool)
    return create_engine(url, connect_args=connect_args)


engine = _create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db(url: str | None = None) -> None:
    """建表；测试可传 sqlite:///:memory:。"""
    global engine, SessionLocal
    target = url or settings.database_url
    engine = _create_engine(target)
    SessionLocal.configure(bind=engine)
    if target.startswith("sqlite"):
        db_path = target.removeprefix("sqlite:///")
        if db_path and db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    import app.models.models  # noqa: F401  确保模型注册

    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI 依赖：提供数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
