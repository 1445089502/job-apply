"""Celery 应用：异步任务基础设施（自动化增强版）。

MVP 用单机可恢复；生产引入 RabbitMQ + 多 worker。
"""
from celery import Celery

# 从环境变量读取，MVP 可用 Redis，生产切 RabbitMQ
broker_url = "redis://127.0.0.1:6379/0"
result_backend = "redis://127.0.0.1:6379/1"

celery_app = Celery(
    "job_apply",
    broker=broker_url,
    backend=result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    task_acks_late=True,  # at-least-once 语义
    worker_prefetch_multiplier=1,
)
