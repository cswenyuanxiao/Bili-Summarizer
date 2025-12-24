# 文档索引（精简版）

Last updated: 2025-12-25
Owner: Core Eng

## 适用对象
- 产品/业务：`docs/OVERVIEW.md`
- 工程实现：`docs/ARCHITECTURE.md`、`docs/API_CONTRACT.md`、`docs/DATA_MODEL.md`、`docs/SECURITY_AUTH.md`
- 运维部署：`docs/RUNBOOK.md`、`docs/CONFIGURATION.md`、`docs/ENGINEERING_STANDARDS.md`
- 设计与规范：`docs/PRODUCT_UI.md`
- 商业化：`docs/COMMERCIAL.md`
- 规划进度：`docs/ROADMAP.md`、`docs/CHANGELOG.md`

## 快速开始（最小闭环）
1) 设置环境变量：`GOOGLE_API_KEY`（必需），生产建议加 `DATABASE_URL`。  
2) 启动后端：`uvicorn web_app.main:app --reload --port 7860`  
3) 启动前端：`cd frontend && npm install && npm run dev`  
4) 访问：`http://localhost:5173`  
5) 验证：输入 B 站 URL，确认 SSE 输出 `summary_complete` 与 UI 渲染。

## 核心文档
1) `docs/START_HERE.md`（入口与硬约束）  
2) `docs/OVERVIEW.md`（项目概览、边界、用户背景）  
3) `docs/ARCHITECTURE.md`（系统架构、数据流、鉴权）  
4) `docs/API_CONTRACT.md`（API 契约与 SSE 事件）  
5) `docs/CONFIGURATION.md`（单一配置来源）  
6) `docs/DATA_MODEL.md`（数据模型与索引）  
7) `docs/SECURITY_AUTH.md`（安全与鉴权）  
8) `docs/ENGINEERING_STANDARDS.md`（工程验收条款）  
9) `docs/RUNBOOK.md`（部署与运维手册）  
10) `docs/PRODUCT_UI.md`（UI/交互规范）  
11) `docs/COMMERCIAL.md`（定价与支付）  
12) `docs/ROADMAP.md`（路线图与验收）  
13) `docs/CHANGELOG.md`（变更记录）  
14) `docs/EXTERNAL_DEPENDENCIES.md`（外部依赖与 API 文档链接）
