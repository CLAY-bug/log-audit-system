# Log Audit System

初稿骨架：FastAPI + Vue，用于日志采集、告警、审计。

## 目录结构
- `backend/`：FastAPI 服务骨架（本周完成健康检查+配置/DB 框架）。
- `frontend/`：Vue 项目占位（待后续完善）。
- `docs/`：需求与设计文档。
- `sql/`：建表 SQL（初稿）。

## 后端快速启动（骨架版）
1. 创建虚拟环境并安装依赖（fastapi、uvicorn、sqlalchemy、pydantic 等）。
2. 运行：`uvicorn app.main:app --reload --app-dir backend`
3. 健康检查：`GET http://localhost:8000/health` 或 `GET http://localhost:8000/api/v1/ping`

## 约定
- 分支命名：`feature/<模块>`，如 `feature/logs-api`。
- 提交信息：`<type>: <summary>`，type 建议 `feat|fix|docs|chore|refactor`。
- 代码风格：
  - 后端使用 Black/flake8 规则（若未配置，至少保持 PEP8 命名）。
  - 前端遵循 ESLint 默认规则，组件/文件使用小写短横线或驼峰一致。

## 第 1 周交付小结
- 数据库设计文档：`docs/db-schema.md`
- API 设计文档：`docs/api-docs.md`
- 建表 SQL 初稿：`sql/init_schema.sql`
- FastAPI 骨架与测试接口：`/health`、`/api/v1/ping`
