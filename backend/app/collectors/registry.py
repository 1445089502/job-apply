"""适配器注册表：按平台名获取对应适配器。"""
from app.collectors.base import ChannelAdapter


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, ChannelAdapter] = {}

    def register(self, adapter: ChannelAdapter) -> None:
        self._adapters[adapter.platform] = adapter

    def get(self, platform: str) -> ChannelAdapter:
        try:
            return self._adapters[platform]
        except KeyError:
            raise KeyError(f"不支持的平台: {platform}") from None

    def all(self) -> list[ChannelAdapter]:
        return list(self._adapters.values())


registry = AdapterRegistry()
