"""爬虫 CLI：抓取真实岗位并保存为 JSON（可导入 job-apply）。

用法：
    python -m scraper.run --kw Java --city 530 --pages 3
    python -m scraper.run --kw Java --city 530 --out data/live_zhaopin.json
可选：
    --cookies-file cookies.json   登录后导出的 cookies（提升成功率/绕过风控）
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # job-apply 根

from scraper.platforms.zhilian import ZhilianScraper  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="智联招聘爬虫")
    p.add_argument("--kw", required=True, help="搜索关键词，如 Java")
    p.add_argument("--city", default="", help="城市代码，如 530(北京) 538(上海) 765(深圳)")
    p.add_argument("--pages", type=int, default=1, help="抓取页数")
    p.add_argument("--page-size", type=int, default=90)
    p.add_argument("--out", default="", help="输出 JSON 路径")
    p.add_argument("--cookies-file", default="", help="cookies JSON 文件路径")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cookies = {}
    if args.cookies_file:
        cookies = json.loads(Path(args.cookies_file).read_text(encoding="utf-8"))

    scraper = ZhilianScraper(cookies=cookies)
    all_jobs = []
    for page in range(1, args.pages + 1):
        try:
            jobs = scraper.search(args.kw, args.city, page, args.page_size)
        except Exception as exc:  # noqa: BLE001
            print(f"第 {page} 页失败: {exc}", file=sys.stderr)
            break
        all_jobs.extend(jobs)
        print(f"第 {page} 页: {len(jobs)} 条")
        if len(jobs) < args.page_size:
            break

    out = args.out or str(Path(__file__).resolve().parent / "output" / f"live_{args.kw}_{args.city}.json")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps([j.to_dict() for j in all_jobs], ensure_ascii=False), encoding="utf-8")
    print(f"共 {len(all_jobs)} 条，已保存: {out}")


if __name__ == "__main__":
    main()
