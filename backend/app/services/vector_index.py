"""内存向量索引（numpy 余弦相似度）。小规模够用，后续可换 FAISS。"""
from __future__ import annotations

import numpy as np


class VectorIndex:
    def __init__(self, dim: int = 64) -> None:
        self.dim = dim
        self._vectors: dict[str, np.ndarray] = {}

    def add(self, job_id: str, vector: list[float]) -> None:
        v = np.asarray(vector, dtype=np.float32)
        if v.shape[0] != self.dim:
            raise ValueError(f"向量维度不匹配: {v.shape[0]} != {self.dim}")
        self._vectors[job_id] = v

    def remove(self, job_id: str) -> None:
        self._vectors.pop(job_id, None)

    def size(self) -> int:
        return len(self._vectors)

    def search(self, query_vector: list[float], top_k: int = 10) -> list[tuple[str, float]]:
        q = np.asarray(query_vector, dtype=np.float32)
        scored: list[tuple[str, float]] = []
        for jid, v in self._vectors.items():
            dot = float(np.dot(q, v))
            scored.append((jid, dot))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
