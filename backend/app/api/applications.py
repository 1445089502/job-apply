"""投递记录接口：记录 + 查询列表。"""
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


@router.get("/applications")
def list_applications(db: Session = Depends(get_db)) -> dict:
    rows = db.query(JobApplication).order_by(JobApplication.created_at.desc()).limit(50).all()
    return {
        "applications": [
            {"id": r.id, "job_id": r.job_id, "status": r.status, "created_at": str(r.created_at)}
            for r in rows
        ]
    }
