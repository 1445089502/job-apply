"""CSV 岗位导入（真实数据源）。"""
import csv
import io

from sqlalchemy.orm import Session

from app.services.embedding import Embedder
from app.services.ingestion import import_jobs
from app.services.vector_index import VectorIndex

CSV_COLUMNS = {
    "platform": "platform",
    "job_id": "job_id",
    "id": "job_id",
    "title": "title",
    "company": "company",
    "city": "city",
    "salary": "salary",
    "language_req": "language_req",
    "experience_req": "experience_req",
    "education_req": "education_req",
    "skills": "skills",
    "jd_text": "jd_text",
    "jd": "jd_text",
}


def import_jobs_csv(
    db: Session,
    csv_text: str,
    embedder: Embedder,
    index: VectorIndex,
    platform: str = "csv",
) -> dict:
    reader = csv.DictReader(io.StringIO(csv_text))
    raw_jobs: list[dict] = []
    for row in reader:
        skills = [s.strip() for s in row.get("skills", "").split(",") if s.strip()]
        raw_jobs.append(
            {
                "platform": row.get("platform") or platform,
                "job_id": row.get("job_id") or row.get("id") or "",
                "title": row.get("title", ""),
                "company": row.get("company", ""),
                "city": row.get("city", ""),
                "salary": row.get("salary", ""),
                "language_req": row.get("language_req", ""),
                "experience_req": row.get("experience_req", ""),
                "education_req": row.get("education_req", ""),
                "skills": skills,
                "jd_text": row.get("jd_text") or row.get("jd", ""),
            }
        )
    return import_jobs(db, raw_jobs, embedder, index)
