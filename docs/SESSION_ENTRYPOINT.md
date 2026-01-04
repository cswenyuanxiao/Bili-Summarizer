---
status: stable
owner: Core Eng
last_reviewed: 2026-01-05
applies_to: main
---

# 会话入口文档（必读）

每次开启新对话，请先阅读本文件。本文件用于指导“下一步必须阅读哪些文档”以及“功能完成后需要更新哪些文档”。

## 快速阅读顺序（只读这些就够）
1. `docs/START_HERE.md`（项目目标与硬约束）
2. `docs/AI_CONTEXT.md`（上下文包与同步规则）
3. `docs/DEVELOPER_GUIDE.md`（架构与模块分工）
4. `docs/API_REFERENCE.md`（接口与 SSE 协议）
5. `docs/CONFIGURATION.md`（配置项）

## 功能完成后的必更清单（按变更类型）
- 新增/变更 API 或 SSE：更新 `docs/API_REFERENCE.md` + `docs/CHANGELOG.md`
- 新增/变更配置项：更新 `docs/CONFIGURATION.md` + `docs/CHANGELOG.md`
- 影响部署流程：更新 `docs/DEPLOYMENT.md`
- 影响工程规范/质量门槛：更新 `docs/ENGINEERING_STANDARDS.md`
- 影响架构/模块边界：更新 `docs/DEVELOPER_GUIDE.md`

## 本文档更新规则（必须）
每完成一个功能或阶段性任务，必须检查并更新本文件的“快速阅读顺序”和“必更清单”是否仍准确。
