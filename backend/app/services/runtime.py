"""运行时单例：embedder + 向量索引 + 从库重建索引。"""
import json

from sqlalchemy.orm import Session

from app.models.models import Job
from app.services.embedding import Embedder, get_embedder
from app.services.vector_index import VectorIndex

embedder: Embedder = get_embedder()
index: VectorIndex = VectorIndex(dim=embedder.dim)


def rebuild_index(db: Session) -> None:
    """从数据库岗位重建内存向量索引。"""
    for job in db.query(Job).all():
        if job.embedding:
            index.add(f"{job.platform}:{job.job_id}", json.loads(job.embedding))
