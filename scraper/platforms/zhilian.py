"""智联招聘爬虫：调 fe-api 搜索接口（真实实现，支持 Cookie 与反风控参数）。

说明：
- 智联有 WAF/风控，未登录或校验参数缺失时可能返回空结果或验证页。
- 可传入登录后的 cookies 提升成功率；被拦截时由上层决定是否用浏览器兜底。
- 请控制频率、仅个人学习使用。
"""
import random
import time
import uuid

import httpx

from scraper.platforms.base import Job, JobScraper


class ZhilianScraper(JobScraper):
    platform = "zhaopin"
    SEARCH_URL = "https://fe-api.zhaopin.com/c/i/sou"

    def __init__(self, cookies: dict | None = None, delay: float = 1.5, timeout: float = 15) -> None:
        self.cookies = cookies or {}
        self.delay = delay
        self.timeout = timeout

    def _headers(self) -> dict:
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.zhaopin.com/",
            "Accept": "application/json, text/plain, */*",
            "x-requested-with": "XMLHttpRequest",
        }

    def _params(self, keyword: str, city_id: str, page: int, page_size: int) -> dict:
        return {
            "start": (page - 1) * page_size,
            "pageSize": page_size,
            "cityId": city_id,
            "workExperience": -1,
            "education": -1,
            "companyType": -1,
            "employmentType": -1,
            "jobWelfareTag": -1,
            "kw": keyword,
            "kt": 3,
            "_v": f"0.{random.randint(0, 999999999):09d}",
            "x-zp-page-request-id": uuid.uuid4().hex,
        }

    def search(self, keyword: str, city_id: str = "", page: int = 1, page_size: int = 90) -> list[Job]:
        params = self._params(keyword, city_id, page, page_size)
        resp = httpx.get(
            self.SEARCH_URL,
            params=params,
            headers=self._headers(),
            cookies=self.cookies,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 200:
            return []
        results = data.get("data", {}).get("results", [])
        jobs = [self._to_job(r) for r in results if r.get("number")]
        time.sleep(self.delay)  # 限速，礼貌抓取
        return jobs

    @staticmethod
    def _to_job(r: dict) -> Job:
        company = r.get("company", {}) or {}
        city = r.get("city", {}) or {}
        salary = r.get("salary", "")
        parts = [
            r.get("jobName", ""),
            "公司：" + company.get("name", ""),
            "学历：" + ((r.get("eduLevel") or {}).get("name", "") or ""),
            "经验：" + ((r.get("workingExp") or {}).get("name", "") or ""),
            "福利：" + "、".join(r.get("welfare", []) if isinstance(r.get("welfare"), list) else []),
        ]
        return Job(
            platform="zhaopin",
            job_id=str(r.get("number", "")),
            title=r.get("jobName", ""),
            company=company.get("name", ""),
            city=city.get("display", ""),
            salary=salary,
            jd_text=" ".join(p for p in parts if p),
            language_req="",
            skills=[],
        )
