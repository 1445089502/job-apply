"""向量化：可插拔 Embedder。stub 用于离线验证，真实模型可选。"""
import hashlib
from abc import ABC, abstractmethod

from app.core.config import settings


class Embedder(ABC):
    dim: int

    @abstractmethod
    def embed(self, text: str) -> list[float]: ...


class StubEmbedder(Embedder):
    """确定性哈希向量：无需下载模型，用于测试与离线验证。"""

    dim = 64

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in text.lower().split():
            h = hashlib.md5(token.encode("utf-8")).digest()
            idx = int.from_bytes(h[:4], "little") % self.dim
            vec[idx] += 1.0
        norm = sum(x * x for x in vec) ** 0.5
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec


class SentenceTransformerEmbedder(Embedder):
    """真实语义向量（需联网下载模型）。"""

    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5") -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)
        self.dim = self._model.get_sentence_embedding_dimension()

    def embed(self, text: str) -> list[float]:
        return self._model.encode([text])[0].tolist()


def get_embedder() -> Embedder:
    name = (settings.embedding_model or "stub").lower()
    if name in ("sentence-transformers", "bge-m3", "bge"):
        return SentenceTransformerEmbedder()
    return StubEmbedder()
