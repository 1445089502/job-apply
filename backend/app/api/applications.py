"""投递记录接口（人工确认后记录）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.models import JobApplication

router = APIRouter(prefix="/api", tags=["applications"])


@router.post("/applications")
def record_application(payload: dict, db: Session = Depends(get_db)) -> dict:
    application = JobApplication(
        user_id=1,
        job_id=payload["job_id"],
        status=payload.get("status", "CREATED"),
    )
    db.add(application)
    db.commit()
    return {"ok": True, "id": application.id, "status": application.status}
