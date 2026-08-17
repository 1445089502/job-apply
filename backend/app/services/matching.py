"""匹配推荐：硬过滤 + 向量召回 + 综合分 + 理由。"""
import json

import numpy as np
from sqlalchemy.orm import Session

from app.models.models import Job, UserPreference
from app.services.embedding import Embedder
from app.services.vector_index import VectorIndex


def _norm(v: list[float]) -> list[float]:
    arr = np.asarray(v, dtype=np.float32)
    n = float(np.linalg.norm(arr))
    return (arr / n).tolist() if n > 0 else v


def hard_filter(job: Job, prefs: dict) -> tuple[bool, list[str]]:
    """硬过滤：城市 / 最低薪资 / 语言 / 黑名单。返回 (是否通过, 命中理由)。"""
    reasons: list[str] = []
    city = prefs.get("city")
    if city and job.city and job.city != city:
        return False, [f"城市不匹配: {job.city}"]

    min_salary = prefs.get("min_salary")
    if min_salary and job.salary_max and job.salary_max < min_salary:
        return False, [f"薪资低于底线: {job.salary_min}-{job.salary_max}K"]

    language = prefs.get("language")
    if language and job.language_req and language not in job.language_req:
        return False, [f"语言要求不满足: {job.language_req}"]

    if job.city:
        reasons.append(f"城市: {job.city}")
    if job.salary_max:
        reasons.append(f"薪资: {job.salary_min}-{job.salary_max}K")
    return True, reasons


def _get_behavior_vector(db: Session, embedder: Embedder) -> list[float]:
    pref = db.query(UserPreference).filter_by(user_id=1).first()
    if pref and pref.behavior_embedding:
        return json.loads(pref.behavior_embedding)
    return [0.0] * embedder.dim


def recommend(
    db: Session,
    embedder: Embedder,
    index: VectorIndex,
    resume_text: str,
    preference_text: str,
    prefs: dict | None = None,
    top_k: int = 5,
) -> list[dict]:
    prefs = prefs or {}
    resume_vec = embedder.embed(resume_text)
    behavior_vec = _get_behavior_vector(db, embedder)
    # user_profile_vector = 0.6*resume + 0.4*behavior（MVP 简化权重）
    query_vec = _norm([0.6 * a + 0.4 * b for a, b in zip(resume_vec, behavior_vec, strict=True)])

    candidates = index.search(query_vec, top_k * 3)
    results: list[dict] = []
    for key, vec_score in candidates:
        platform, _, job_id = key.partition(":")
        job = db.query(Job).filter_by(platform=platform, job_id=job_id).first()
        if job is None:
            continue
        ok, reasons = hard_filter(job, prefs)
        if not ok:
            continue
        final = round(0.7 * vec_score + 0.3 * 1.0, 4)  # 硬过滤通过即给满分权重
        results.append(
            {
                "job_id": job.id,
                "platform": job.platform,
                "title": job.title,
                "company": job.company.name if job.company_id else "",
                "city": job.city,
                "salary": f"{job.salary_min}-{job.salary_max}K",
                "score": final,
                "reasons": reasons,
                "jd": job.jd_text[:200],
            }
        )
        if len(results) >= top_k:
            break
    return results
