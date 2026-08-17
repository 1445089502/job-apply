"""异步任务：采集 / 投递 / 向量索引构建（骨架）。

依赖幂等与状态机兜底：at-least-once，外部副作用靠业务幂等保证不重复。
"""
from app.collectors.registry import registry
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def collect_jobs_task(self, platform: str, keyword: str, page: int = 1):
    """采集岗位任务。"""
    adapter = registry.get(platform)
    jobs = adapter.fetch_jobs(keyword, page)
    # TODO: 标准化入库（去重 + 唯一键）
    return {"platform": platform, "count": len(jobs)}


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def apply_job_task(self, platform: str, job_id: str, resume_path: str):
    """全自动投递任务（受控）。"""
    adapter = registry.get(platform)
    # 先检查幂等（唯一键 (platform, job_id, user)）
    # 状态机：QUEUED -> APPLYING -> SUBMITTED_UNCONFIRMED ...
    status = adapter.apply(job_id, resume_path)
    return {"platform": platform, "job_id": job_id, "status": status}


@celery_app.task
def build_vector_index_task():
    """向量索引构建/重建任务（embedding 版本 + manifest）。"""
    # TODO: 读取 job_embedding 表 -> 生成向量 -> 重建 FAISS -> 更新 manifest
    return {"index": "job_index"}
