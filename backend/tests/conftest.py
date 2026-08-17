"""pytest 共享 fixtures：内存数据库 + stub embedder + 向量索引。"""
import pytest

from app.core.db import SessionLocal, init_db
from app.services.embedding import StubEmbedder
from app.services.vector_index import VectorIndex


@pytest.fixture()
def db():
    init_db("sqlite:///:memory:")
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture()
def embedder():
    return StubEmbedder()


@pytest.fixture()
def index(embedder):
    return VectorIndex(dim=embedder.dim)


@pytest.fixture()
def sample_jobs():
    return [
        {
            "platform": "import",
            "job_id": "1001",
            "company": "某日系IT公司",
            "title": "对日Java开发工程师",
            "city": "大连",
            "salary": "15-25K",
            "language_req": "N2",
            "jd_text": "对日Java项目开发，要求日语N2，能读写式样书，熟悉Spring",
        },
        {
            "platform": "import",
            "job_id": "1002",
            "company": "某互联网公司",
            "title": "Python后端工程师",
            "city": "深圳",
            "salary": "20-30K",
            "language_req": "",
            "jd_text": "Python后端服务开发，使用FastAPI，有SQL基础",
        },
        {
            "platform": "import",
            "job_id": "1003",
            "company": "某日资贸易公司",
            "title": "IT系统担当",
            "city": "深圳",
            "salary": "8-12K",
            "language_req": "N1",
            "jd_text": "公司IT系统运维、AD域控管理，要求日语N1商务水平",
        },
    ]
