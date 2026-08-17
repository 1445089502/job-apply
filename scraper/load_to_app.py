"""把转换后的真实数据导入 job-apply 数据库。

用法：
    cd backend
    ..\.venv\Scripts\python ..\scraper\load_to_app.py
"""
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))

from app.core.db import SessionLocal, init_db  # noqa: E402
from app.services.ingestion import import_jobs  # noqa: E402
from app.services.runtime import embedder, index  # noqa: E402

SOURCE = Path(__file__).resolve().parent / "output" / "zhaopin_jobs.json"


def main() -> None:
    init_db()
    jobs = json.loads(SOURCE.read_text(encoding="utf-8"))
    print(f"载入 {len(jobs)} 条真实岗位...")
    with SessionLocal() as db:
        result = import_jobs(db, jobs, embedder, index)
    print(f"导入完成: 新增={result['added']} 重复={result['dup']} 索引={index.size()}")


if __name__ == "__main__":
    main()
