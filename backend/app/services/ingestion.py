"""岗位导入：清洗标准化 + 去重 + 入库 + 向量化。"""
import json
import re

from sqlalchemy.orm import Session

from app.models.models import Company, Job
from app.services.embedding import Embedder
from app.services.vector_index import VectorIndex


def parse_salary(raw: str) -> tuple[int, int]:
    """解析 "15-25K" / "15000-25000" / "15-25千" 等 → (min, max) 单位 千/月。"""
    if not raw:
        return 0, 0
    nums = [int(x) for x in re.findall(r"\d+", raw)]
    if not nums:
        return 0, 0
    lo, hi = nums[0], nums[-1] if len(nums) > 1 else nums[0]
    is_k = ("k" in raw.lower()) or ("千" in raw) or (hi <= 100)
    if not is_k and hi > 100:
        lo, hi = lo // 1000, hi // 1000
    return lo, hi


def _key(platform: str, job_id: str) -> str:
    return f"{platform}:{job_id}"


def import_jobs(db: Session, raw_jobs: list[dict], embedder: Embedder, index: VectorIndex) -> dict:
    added = updated = dup = 0
    for raw in raw_jobs:
        platform = raw.get("platform", "import")
        job_id = str(raw.get("job_id") or "")
        if not job_id:
            continue
        existing = db.query(Job).filter_by(platform=platform, job_id=job_id).first()
        if existing:
            dup += 1
            continue

        lo, hi = parse_salary(raw.get("salary", ""))
        company = (
            db.query(Company).filter_by(name=raw.get("company", "")).first()
            or Company(name=raw.get("company", ""))
        )
        db.add(company)
        db.flush()

        jd_text = raw.get("jd_text") or raw.get("jd", "")
        job = Job(
            platform=platform,
            job_id=job_id,
            company_id=company.id,
            title=raw.get("title", ""),
            jd_text=jd_text,
            city=raw.get("city", ""),
            salary_min=lo,
            salary_max=hi,
            experience_req=raw.get("experience_req", ""),
            education_req=raw.get("education_req", ""),
            language_req=raw.get("language_req", ""),
            skills_json=json.dumps(raw.get("skills", []), ensure_ascii=False),
            embedding=json.dumps(embedder.embed(jd_text)),
        )
        db.add(job)
        index.add(_key(platform, job_id), json.loads(job.embedding))
        added += 1
    db.commit()
    return {"added": added, "updated": updated, "dup": dup}
