"""招聘平台爬虫适配器。"""
from scraper.platforms.base import Job, JobScraper
from scraper.platforms.zhilian import ZhilianScraper

__all__ = ["Job", "JobScraper", "ZhilianScraper"]
