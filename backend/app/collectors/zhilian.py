"""智联招聘适配器：API 优先 + 浏览器兜底（Plan C）。"""
from app.collectors.base import ChannelAdapter, Job


class ZhilianAdapter(ChannelAdapter):
    platform = "zhilian"

    def fetch_jobs(self, keyword: str, page: int = 1) -> list[Job]:
        # 智联接口较开放：API 优先（requests + cookie + token）
        # 被风控/改版 → 熔断 → 浏览器兜底
        raise NotImplementedError("智联采集逻辑待实现")

    def apply(self, job: Job, resume_path: str) -> str:
        raise NotImplementedError("智联自动投递待实现")

    def get_status(self, job_id: str) -> str:
        raise NotImplementedError("智联状态查询待实现")
