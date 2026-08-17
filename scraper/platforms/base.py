"""爬虫基类与统一岗位模型。"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Job:
    """标准化岗位（与 job-apply 导入格式对齐）。"""

    platform: str
    job_id: str
    title: str
    company: str
    city: str
    salary: str
    jd_text: str
    language_req: str = ""
    skills: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "city": self.city,
            "salary": self.salary,
            "language_req": self.language_req,
            "skills": self.skills,
            "jd_text": self.jd_text,
        }


class JobScraper(ABC):
    platform: str = ""

    @abstractmethod
    def search(self, keyword: str, city_id: str = "", page: int = 1, page_size: int = 90) -> list[Job]:
        """按关键词 + 城市搜索岗位。"""
