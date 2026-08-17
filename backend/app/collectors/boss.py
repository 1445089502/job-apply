"""BOSS 直聘适配器：浏览器优先 + API 兜底 + 熔断路由（Plan C）。"""
import random
import time

from app.collectors.base import ChannelAdapter, Job


class BOSSAdapter(ChannelAdapter):
    platform = "boss"

    def fetch_jobs(self, keyword: str, page: int = 1) -> list[Job]:
        if self._breaker_open:
            # 熔断降级：返回空或抛错，由上层处理
            return []
        # 实现要点：
        # 1) 浏览器优先：Playwright 打开搜索页，解析列表+详情
        # 2) 反检测：真实UA、随机延时、关闭 webdriver 特征
        # 3) 验证码/滑块 → 抛 NEEDS_HUMAN
        # 4) API 兜底：requests + 签名复现
        # 5) 数据校验 + 统一 Job 模型
        # （骨架：演示随机延时，真实逻辑后续实现）
        time.sleep(random.uniform(1, 3))
        raise NotImplementedError("BOSS 采集逻辑待实现")

    def apply(self, job: Job, resume_path: str) -> str:
        # 自动投递：打开岗位页 → 上传简历 → 提交 → 确认结果
        raise NotImplementedError("BOSS 自动投递待实现")

    def get_status(self, job_id: str) -> str:
        raise NotImplementedError("BOSS 状态查询待实现")
