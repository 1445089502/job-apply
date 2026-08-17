# frontend

**当前实现**：静态单页看板（`static/`），由 FastAPI 直接托管，含 推荐 / 岗位 / 投递 / 报表 四个 Tab，使用原生 JS + ECharts(CDN) 调 `/api/*`。

**说明**：这是轻量可运行的前端。后续可升级为 Vue3 + Vite 工程（`frontend/` 下的工程化骨架），保持相同的 `/api/*` 接口即可。
