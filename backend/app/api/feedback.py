"""反馈接口：收藏/投递/不感兴趣 等行为影响后续排序。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.feedback import apply_feedback

router = APIRouter(prefix="/api", tags=["feedback"])


@router.post("/feedback")
def feedback_api(payload: dict, db: Session = Depends(get_db)) -> dict:
    return apply_feedback(db, payload["job_id"], payload["action"])
