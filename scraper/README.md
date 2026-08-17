# scraper · 招聘数据爬虫模块

> 独立于 backend/frontend 的爬虫模块，用于获取**真实岗位数据**并导入 job-apply。

## 目录
```
scraper/
├── platforms/
│   ├── base.py        # JobScraper 基类 + 统一 Job 模型
│   └── zhilian.py     # 智联招聘真实实现（fe-api）
├── run.py             # CLI：抓取真实岗位 → JSON
├── convert.py         # 把 raw 数据集转换为 app 导入格式
├── load_to_app.py     # 把转换后数据导入 job-apply 数据库
├── data/              # raw 智联数据集（blackyau/zhaopin，真实岗位 2.7万+）
└── output/            # 转换/抓取产物
```

## 一、使用已下载的真实数据集（推荐，即开即用）
已内置 `blackyau/zhaopin` 的**真实智联岗位数据**（2.7 万+ 条，覆盖北上广深等）。

```bash
# 1. 转换 raw 数据为 app 导入格式
cd job-apply
.\.venv\Scripts\python scraper/convert.py

# 2. 导入到 app 数据库
.\.venv\Scripts\python scraper/load_to_app.py
```

## 二、实时抓取（智联）
```bash
# 抓取 Java 岗位，北京(city=530)，3 页
.\.venv\Scripts\python -m scraper.run --kw Java --city 530 --pages 3
```
- 输出到 `scraper/output/live_Java_530.json`（app 导入格式，可用 `/api/jobs/import` 导入）
- 城市代码：北京 530 / 上海 538 / 广州 619 / 深圳 765（参考）
- **若返回空**：智联有 WAF 风控，需用登录后的 cookies：
  ```bash
  .\.venv\Scripts\python -m scraper.run --kw Java --city 530 --cookies-file cookies.json
  ```

## 三、合规提示
- 招聘平台爬取存在**风控/封号与 ToS 风险**，请：仅个人学习、控制频率（内置限速）、不使用自动投递。
- 数据仅用于个人求职分析，不公开转售。

## 四、导入到 app
```bash
# 方法一：脚本直连（推荐，大数据量）
.\.venv\Scripts\python scraper/load_to_app.py

# 方法二：走 API（小批量）
curl -X POST http://127.0.0.1:8000/api/jobs/import -H "Content-Type: application/json" -d '{"jobs":[...]}'
```
