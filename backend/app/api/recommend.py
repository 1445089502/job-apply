"""推荐接口：简历 + 偏好 → 岗位推荐列表。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.matching import recommend
from app.services.runtime import embedder, index

router = APIRouter(prefix="/api", tags=["recommend"])


@router.post("/recommend")
def recommend_api(payload: dict, db: Session = Depends(get_db)) -> dict:
    resume = payload.get("resume", "")
    preference = payload.get("preference", "")
    prefs = payload.get("prefs", {}) or {}
    top_k = int(payload.get("top_k", 5))
    recs = recommend(db, embedder, index, resume, preference, prefs, top_k)
    return {"recommendations": recs}
