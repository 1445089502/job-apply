"""报表统计接口：岗位/投递漏斗/反馈概览。"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.models import Job, JobApplication, UserJobFeedback

router = APIRouter(prefix="/api", tags=["statistics"])


@router.get("/statistics")
def statistics(db: Session = Depends(get_db)) -> dict:
    total_jobs = db.query(Job).count()

    status_rows = db.query(JobApplication.status, func.count()).group_by(JobApplication.status).all()
    applications_by_status = {status: count for status, count in status_rows}

    feedback_rows = db.query(UserJobFeedback.action, func.count()).group_by(UserJobFeedback.action).all()
    feedback_by_action = {action: count for action, count in feedback_rows}

    # 漏斗：浏览(点击) → 投递(申请) → 已投递成功
    funnel = {
        "viewed": feedback_by_action.get("view", 0) + feedback_by_action.get("collect", 0),
        "applied": applications_by_status.get("CREATED", 0),
        "total_jobs": total_jobs,
    }
    return {
        "total_jobs": total_jobs,
        "applications_by_status": applications_by_status,
        "feedback_by_action": feedback_by_action,
        "funnel": funnel,
    }
