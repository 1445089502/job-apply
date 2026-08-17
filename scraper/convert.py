"""把 raw 智联数据集转换为 job-apply 可导入格式。

原始数据：scraper/data/*.json（blackyau/zhaopin 智联爬取，真实岗位列表）
输出：scraper/output/zhaopin_jobs.json（app 的 /api/jobs/import 格式）
"""
import glob
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW = BASE / "data"
OUT = BASE / "output"


def _text(rec: dict) -> str:
    """由真实字段合成 jd_text（原始数据集无完整 JD，用真实字段拼接）。"""
    parts = [
        rec.get("jobName", ""),
        "公司：" + rec.get("company", {}).get("name", ""),
        "行业：" + (rec.get("industry", {}).get("name", "") if isinstance(rec.get("industry"), dict) else ""),
        "学历：" + (rec.get("eduLevel", {}).get("name", "") if isinstance(rec.get("eduLevel"), dict) else ""),
        "经验：" + (rec.get("workingExp", {}).get("name", "") if isinstance(rec.get("workingExp"), dict) else ""),
        "福利：" + "、".join(rec.get("welfare", []) if isinstance(rec.get("welfare"), list) else []),
    ]
    return " ".join(p for p in parts if p)


def convert() -> dict:
    OUT.mkdir(exist_ok=True)
    jobs: list[dict] = []
    seen: set[str] = set()
    for path in sorted(glob.glob(str(RAW / "*.json"))):
        data = json.loads(path and open(path, encoding="utf-8").read() or "{}")
        for page in data.get("all_data", []):
            for rec in page.get("data", {}).get("results", []):
                job_id = str(rec.get("number", ""))
                if not job_id or job_id in seen:
                    continue
                seen.add(job_id)
                jobs.append(
                    {
                        "platform": "zhaopin",
                        "job_id": job_id,
                        "title": rec.get("jobName", ""),
                        "company": rec.get("company", {}).get("name", ""),
                        "city": rec.get("city", {}).get("display", ""),
                        "salary": rec.get("salary", ""),
                        "language_req": "",
                        "skills": [],
                        "jd_text": _text(rec),
                    }
                )

    out_file = OUT / "zhaopin_jobs.json"
    out_file.write_text(json.dumps(jobs, ensure_ascii=False), encoding="utf-8")
    return {"total": len(jobs), "output": str(out_file)}


if __name__ == "__main__":
    result = convert()
    print(json.dumps(result, ensure_ascii=False))
