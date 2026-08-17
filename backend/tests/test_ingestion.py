"""岗位导入测试：薪资解析 + 去重 + 入库。"""
from app.models.models import Job
from app.services.ingestion import import_jobs, parse_salary


def test_parse_salary():
    assert parse_salary("15-25K") == (15, 25)
    assert parse_salary("15000-25000") == (15, 25)
    assert parse_salary("8-12K") == (8, 12)
    assert parse_salary("") == (0, 0)


def test_import_dedup(db, embedder, index, sample_jobs):
    r1 = import_jobs(db, sample_jobs, embedder, index)
    assert r1["added"] == len(sample_jobs)
    assert r1["dup"] == 0

    # 重复导入应全部去重
    r2 = import_jobs(db, sample_jobs, embedder, index)
    assert r2["added"] == 0
    assert r2["dup"] == len(sample_jobs)

    assert db.query(Job).count() == len(sample_jobs)
    assert index.size() == len(sample_jobs)
