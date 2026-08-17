"""岗位接口：列表查询 + 批量导入。"""
from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.models import Job
from app.services.ingestion import import_jobs
from app.services.runtime import embedder, index

router = APIRouter(prefix="/api", tags=["jobs"])


@router.get("/jobs")
def list_jobs(keyword: str = "", db: Session = Depends(get_db)) -> dict:
    q = db.query(Job)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(or_(Job.title.contains(like), Job.jd_text.contains(like)))
    rows = q.limit(50).all()
    return {
        "jobs": [
            {
                "id": r.id,
                "platform": r.platform,
                "title": r.title,
                "city": r.city,
                "salary": f"{r.salary_min}-{r.salary_max}K",
            }
            for r in rows
        ]
    }


@router.post("/jobs/import")
def import_jobs_api(payload: dict, db: Session = Depends(get_db)) -> dict:
    return import_jobs(db, payload.get("jobs", []), embedder, index)
