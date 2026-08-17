"""匹配推荐测试：硬过滤 + 向量召回 + 反馈影响排序。"""
from app.services.feedback import apply_feedback
from app.services.ingestion import import_jobs
from app.services.matching import hard_filter, recommend


def test_hard_filter():
    class _J:
        city = "深圳"
        salary_min = 0
        salary_max = 12
        language_req = "N1"

    job = _J()
    ok, reasons = hard_filter(job, {"city": "深圳", "min_salary": 10, "language": "N1"})
    assert ok
    assert reasons

    ok, _ = hard_filter(job, {"city": "上海"})
    assert not ok


def test_recommend_filters_city(db, embedder, index, sample_jobs):
    import_jobs(db, sample_jobs, embedder, index)
    recs = recommend(
        db,
        embedder,
        index,
        resume_text="熟悉Java和日语，希望做对日开发",
        preference_text="想找日企IT岗位",
        prefs={"city": "大连"},
    )
    assert recs
    # 城市硬过滤后，所有推荐都应在可接受城市
    assert all(r["city"] in ("大连", "") for r in recs)


def test_feedback_changes_ranking(db, embedder, index, sample_jobs):
    import_jobs(db, sample_jobs, embedder, index)
    resume = "熟悉Java和日语N1，做过全栈开发"
    before = recommend(db, embedder, index, resume, "对日开发", prefs={})
    assert before

    top = before[0]["job_id"]
    # 对 top1 投"不感兴趣"，其排序应下降
    apply_feedback(db, top, "dislike")
    after = recommend(db, embedder, index, resume, "对日开发", prefs={})
    after_ids = [r["job_id"] for r in after]

    assert top not in after_ids[:2], "被标记不感兴趣的岗位不应仍排在前列"
