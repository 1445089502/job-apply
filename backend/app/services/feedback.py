"""用户反馈：写入反馈表并更新行为偏好向量（影响后续排序）。"""
import json

import numpy as np
from sqlalchemy.orm import Session

from app.models.models import Job, UserJobFeedback, UserPreference

# 行为反馈权重（doc/10 §10.4.4）
ACTION_WEIGHTS = {"view": 0.2, "collect": 0.6, "apply": 1.0, "dislike": -0.8}


def _norm(v: list[float]) -> list[float]:
    arr = np.asarray(v, dtype=np.float32)
    n = float(np.linalg.norm(arr))
    return (arr / n).tolist() if n > 0 else v


def _recompute_behavior(db: Session) -> list[float]:
    """按全部反馈加权平均岗位向量，正反馈加、负反馈减。"""
    rows = db.query(UserJobFeedback).filter_by(user_id=1).all()
    vec = [0.0] * 64
    dim = 64
    for row in rows:
        job = db.query(Job).filter_by(id=row.job_id).first()
        if job is None or not job.embedding:
            continue
        jv = json.loads(job.embedding)
        dim = len(jv)
        vec = [v + row.weight * x for v, x in zip(vec, jv, strict=True)]
    return _norm(vec) if any(vec) else [0.0] * dim


def apply_feedback(db: Session, job_id: int, action: str) -> dict:
    if action not in ACTION_WEIGHTS:
        raise ValueError(f"不支持的行为: {action}")
    weight = ACTION_WEIGHTS[action]
    db.add(UserJobFeedback(user_id=1, job_id=job_id, action=action, weight=weight))
    db.flush()

    behavior = _recompute_behavior(db)
    pref = db.query(UserPreference).filter_by(user_id=1).first()
    if pref is None:
        pref = UserPreference(user_id=1, behavior_embedding=json.dumps(behavior))
        db.add(pref)
    else:
        pref.behavior_embedding = json.dumps(behavior)
    db.commit()
    return {"job_id": job_id, "action": action, "weight": weight, "ok": True}
