"""最低可验证闭环：岗位导入 → 推荐 → 反馈 → 再推荐 → 投递记录。

运行：
    python backend/scripts/verify_minimal.py
"""
import json
import sys
from pathlib import Path

# 使 backend 可导入
BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from app.core.db import SessionLocal, init_db  # noqa: E402
from app.models.models import JobApplication  # noqa: E402
from app.services.feedback import apply_feedback  # noqa: E402
from app.services.ingestion import import_jobs  # noqa: E402
from app.services.matching import recommend  # noqa: E402
from app.services.runtime import embedder, index  # noqa: E402

SAMPLE = Path(__file__).resolve().parent.parent.parent / "data" / "sample_jobs.json"


def main() -> None:
    print("=" * 56)
    print("job-apply 最低可验证闭环")
    print("embedding:", type(embedder).__name__, "| dim:", embedder.dim)
    print("=" * 56)

    init_db()
    with SessionLocal() as db:
        # 1. 岗位导入（幂等去重）
        jobs = json.loads(SAMPLE.read_text(encoding="utf-8"))
        res = import_jobs(db, jobs, embedder, index)
        print(f"[1] 岗位导入: 新增={res['added']} 重复={res['dup']} 索引={index.size()}")

        # 2. 推荐
        resume = "熟悉Java和日语N1，做过全栈开发，希望从事对日开发或日企IT"
        prefs = {"city": "深圳", "min_salary": 8}
        recs = recommend(db, embedder, index, resume, "对日开发/日企IT", prefs, top_k=3)
        print("[2] 初始推荐:")
        for r in recs:
            print(
                f"     {r['title']} | {r['company']} | {r['city']} | {r['salary']} "
                f"| 分={r['score']} | 理由={r['reasons']}"
            )
        if not recs:
            print("     （无推荐，请检查数据）")

        # 3. 反馈：对 top1 标记不感兴趣
        if recs:
            top_id = recs[0]["job_id"]
            apply_feedback(db, top_id, "dislike")
            print(f"[3] 反馈: 对 job_id={top_id} 标记 dislike")

        # 4. 再推荐（应看到排序变化）
        recs2 = recommend(db, embedder, index, resume, "对日开发/日企IT", prefs, top_k=3)
        print("[4] 反馈后推荐:")
        for r in recs2:
            print(f"     {r['title']} | {r['city']} | 分={r['score']}")
        if recs and recs2:
            changed = recs2[0]["job_id"] != recs[0]["job_id"]
            print(f"     top1 是否变化: {'是 ✅' if changed else '否 ⚠️'}")

        # 5. 投递记录
        if recs2:
            app_row = JobApplication(user_id=1, job_id=recs2[0]["job_id"], status="CREATED")
            db.add(app_row)
            db.commit()
            print(f"[5] 投递记录: id={app_row.id} job_id={app_row.job_id} status={app_row.status}")

        print("=" * 56)
        print("闭环验证完成 ✅" if recs and recs2 else "闭环未走通 ⚠️")


if __name__ == "__main__":
    main()
