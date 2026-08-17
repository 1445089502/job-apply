# job-apply · 求职自动化系统

> AI 辅助·半自动求职推荐与投递记录系统
> 定位：理解用户想要什么，稳定推荐值得投的岗位；自动采集/投递作为受控外围能力（后置）

## 文档
见 [`docs/`](docs/README.md)（架构、检查报告、实施说明、本机方案）。

## 当前阶段
- S1 项目骨架（本阶段）
- 按 `docs/11` 的 Git 提交阶段推进：S1 骨架 → S2 数据模型 → S3 岗位导入 → S4 匹配引擎 → ...

## 目录结构
```
job-apply/
├── docs/          # 架构与计划文档（01-12）
├── backend/       # FastAPI 后端
│   ├── app/
│   │   ├── main.py       # 应用入口
│   │   ├── core/         # 配置
│   │   ├── api/          # 路由
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── schemas/      # Pydantic 模式
│   │   ├── services/     # 业务逻辑
│   │   └── repositories/ # 数据访问
│   └── tests/            # pytest
├── frontend/      # Vue 前端（后续阶段）
└── data/          # SQLite 数据
```

## 本地开发（Windows 原生，按 docs/12）
```powershell
# 1. 创建虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. 安装依赖
pip install -r backend/requirements.txt

# 3. 运行后端
uvicorn app.main:app --reload --port 8000

# 4. 测试
pytest backend/tests
```
