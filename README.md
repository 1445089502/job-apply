# job-apply · 求职自动化系统

> AI 辅助·半自动求职推荐与投递记录系统
> 定位：理解用户想要什么，稳定推荐值得投的岗位；自动采集/投递作为受控外围能力（后置）

## 文档
见 [`docs/`](docs/README.md)（架构、检查报告、实施说明、本机方案）。

## 功能
- **岗位库**：JSON/CSV 导入 + 清洗去重 + 向量化
- **推荐**：硬过滤（城市/薪资/语言）+ 向量召回 + 推荐理由
- **反馈学习**：收藏/投递/不感兴趣 影响后续排序
- **投递记录**：人工确认后记录状态
- **报表**：岗位数 / 投递漏斗可视化（ECharts）

## 技术栈
FastAPI + SQLAlchemy(SQLite) + numpy 向量索引 + Vue/Vite(占位, 现为静态 SPA) + Celery(增强分支)

## 目录结构
```
job-apply/
├── docs/            # 架构与计划文档（01-13）
├── backend/
│   ├── app/
│   │   ├── main.py          # 应用入口（含静态托管）
│   │   ├── core/            # 配置 / 数据库
│   │   ├── api/             # jobs/recommend/feedback/applications/statistics/health
│   │   ├── models/          # SQLAlchemy 模型
│   │   ├── services/        # 导入/匹配/反馈/embedding/向量索引
│   │   ├── collectors/      # 平台采集适配器（增强分支）
│   │   ├── workers/         # Celery 任务（增强分支）
│   │   └── ...
│   ├── alembic/             # 数据库迁移
│   ├── tests/               # pytest
│   └── scripts/verify_minimal.py  # 端到端闭环验证
├── frontend/static/  # 前端静态看板（HTML+JS+ECharts）
└── data/            # SQLite 数据 + 样本岗位
```

## 本地运行
```powershell
# 1. 创建虚拟环境 + 安装依赖
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

# 2. 启动后端（含前端看板，端口 8000）
cd backend
..\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000

# 3. 浏览器打开 http://127.0.0.1:8000
```

## API 一览
| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 健康检查 |
| GET | `/api/jobs` | 岗位列表（可 keyword 过滤）|
| POST | `/api/jobs/import` | 批量导入 `{jobs:[...]}` |
| POST | `/api/jobs/import-csv` | CSV 导入 `{csv:"..."}` |
| POST | `/api/recommend` | 推荐 `{resume, preference, prefs, top_k}` |
| POST | `/api/feedback` | 反馈 `{job_id, action}` |
| POST | `/api/applications` | 记录投递 |
| GET | `/api/applications` | 投递列表 |
| GET | `/api/statistics` | 报表统计 |

## 测试与规范
```powershell
..\.venv\Scripts\python -m pytest -q
..\.venv\Scripts\python -m ruff check backend
```

## 最低可验证闭环
```powershell
..\.venv\Scripts\python backend/scripts/verify_minimal.py
# 导入→推荐→反馈→再推荐(排序变化)→投递记录
```

## 分支
- `main`：合规 MVP（S0-S1）
- `feat/automation-ha`：自动化增强版（采集适配器/扩展状态机/Celery/HA compose/最低可验证 MVP）
