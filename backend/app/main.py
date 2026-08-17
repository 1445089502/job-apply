"""FastAPI 应用入口。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.applications import router as applications_router
from app.api.feedback import router as feedback_router
from app.api.health import router as health_router
from app.api.jobs import router as jobs_router
from app.api.recommend import router as recommend_router
from app.core.config import settings
from app.core.db import SessionLocal, init_db
from app.services.runtime import rebuild_index


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    with SessionLocal() as db:
        rebuild_index(db)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.include_router(health_router)
    app.include_router(jobs_router)
    app.include_router(recommend_router)
    app.include_router(feedback_router)
    app.include_router(applications_router)
    return app


app = create_app()
