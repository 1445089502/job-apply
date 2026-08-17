"""冒烟黑盒测试：对运行中的服务（http://127.0.0.1:8000）逐项探测。

先启动服务，再运行本脚本：
    start.bat          （或手动 uvicorn）
    python backend/scripts/smoke_test.py
"""
import json
import sys
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8000"
SAMPLE = Path(__file__).resolve().parent.parent.parent / "data" / "sample_jobs.json"

results: list[tuple[str, bool, str]] = []


def check(name: str, fn) -> None:
    try:
        detail = fn()
        results.append((name, True, detail))
    except Exception as exc:  # noqa: BLE001
        results.append((name, False, str(exc)))


def main() -> None:
    with httpx.Client(base_url=BASE, timeout=10) as client:
        # 1. 健康检查
        check("GET /api/health", lambda: client.get("/api/health").json()["status"])

        # 2. 前端首页
        check("GET / (前端)", lambda: "job-apply" in client.get("/").text)

        # 3. 导入样本岗位（幂等：重复导入应去重）
        jobs = json.loads(SAMPLE.read_text(encoding="utf-8"))

        def import_once():
            r = client.post("/api/jobs/import", json={"jobs": jobs})
            data = r.json()
            assert r.status_code == 200, data
            return f"added={data['added']} dup={data['dup']}"

        check("POST /api/jobs/import", import_once)

        # 4. 推荐（应返回带理由的推荐）
        def recommend():
            r = client.post(
                "/api/recommend",
                json={
                    "resume": "熟悉Java和日语N1，做过全栈开发",
                    "preference": "想找对日开发或日企IT",
                    "prefs": {"city": "深圳"},
                },
            )
            data = r.json()
            assert r.status_code == 200 and len(data.get("recommendations", [])) > 0, data
            return f"{len(data['recommendations'])} 条推荐"

        check("POST /api/recommend", recommend)

        # 5. 报表
        check("GET /api/statistics", lambda: f"total_jobs={client.get('/api/statistics').json()['total_jobs']}")

        # 6. 投递列表
        check("GET /api/applications", lambda: f"count={len(client.get('/api/applications').json()['applications'])}")

    print("=" * 52)
    print("job-apply 冒烟黑盒测试")
    print("=" * 52)
    all_ok = True
    for name, ok, detail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}  ->  {detail}")
        all_ok = all_ok and ok
    print("=" * 52)
    print("结果:", "全部通过 ✅" if all_ok else "存在失败 ❌")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
