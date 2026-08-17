"""异步任务：采集导入 / 投递 / 向量索引（接线真实服务）。

依赖幂等与状态机兜底：at-least-once，外部副作用靠业务幂等保证不重复。
"""
from app.core.db import SessionLocal
from app.services.ingestion import import_jobs
from app.services.runtime import embedder, index, rebuild_index
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def collect_jobs_task(self, jobs: list[dict]):
    """岗位导入任务（幂等去重）。"""
    with SessionLocal() as db:
        result = import_jobs(db, jobs, embedder, index)
    return result


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def apply_job_task(self, platform: str, job_id: str, resume_path: str):
    """全自动投递任务（受控）。"""
    # TODO: 对接真实平台投递（registry.get(platform).apply(...)）；当前仅为受控占位
    return {"platform": platform, "job_id": job_id, "status": "SUBMITTED_UNCONFIRMED"}


@celery_app.task
def build_vector_index_task():
    """从数据库重建向量索引（embedding 版本 + manifest 待补）。"""
    with SessionLocal() as db:
        rebuild_index(db)
    return {"index_size": index.size()}
