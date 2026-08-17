"""采集适配器抽象：统一各平台的岗位采集/投递/状态接口。"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Job:
    """标准化岗位模型（对比前提）。"""

    platform: str
    job_id: str
    title: str
    company: str
    jd_text: str
    city: str = ""
    district: str = ""
    salary_min: int | None = None  # 归一为 千/月
    salary_max: int | None = None
    experience_req: str = ""
    education_req: str = ""
    language_req: str = ""
    skills: list[str] = field(default_factory=list)
    url: str = ""

    @property
    def unique_key(self) -> tuple[str, str]:
        return (self.platform, self.job_id)


class ChannelAdapter(ABC):
    """平台适配器基类。每平台实现：采集 / 投递 / 状态查询。"""

    platform: str = ""
    # 熔断路由状态（简化版，生产用独立熔断器）
    _breaker_open: bool = False

    @abstractmethod
    def fetch_jobs(self, keyword: str, page: int = 1) -> list[Job]:
        """按关键词采集岗位列表（Plan C：API 优先 + 浏览器兜底）。"""

    @abstractmethod
    def apply(self, job: Job, resume_path: str) -> str:
        """自动投递，返回状态标识。"""

    @abstractmethod
    def get_status(self, job_id: str) -> str:
        """查询投递结果状态。"""
