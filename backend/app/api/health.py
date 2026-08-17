"""健康检查接口。"""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "job-apply",
        "version": "0.1.0",
    }
