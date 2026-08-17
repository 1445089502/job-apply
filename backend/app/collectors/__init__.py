"""多平台岗位采集适配器（自动化增强版）。"""
from app.collectors.base import ChannelAdapter, Job
from app.collectors.registry import AdapterRegistry, registry

__all__ = ["ChannelAdapter", "Job", "AdapterRegistry", "registry"]
