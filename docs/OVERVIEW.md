# 项目总览

Last updated: 2025-12-24  
Owner: Core Eng

## 项目定位
Bili-Summarizer 是一个面向 B 站内容学习与复盘的 AI 总结工具，提供结构化总结、转录、思维导图与导出能力。

## 目标用户
- B 站高频学习者、知识型 UP 观众
- 内容从业者与研究人员
- 需要高频总结与复盘的团队

## 核心功能
- URL 总结（SSE 实时进度）
- 自动转录与时间戳
- 思维导图渲染与导出
- 结果导出（MD/TXT/PDF/SVG/PNG）
- 积分体系与订阅（支付接口）
- 云端历史同步（Supabase）
- API Key 管理（开发者 API）

## 技术框架
- 前端：Vue 3 + Vite + Tailwind + TypeScript
- 后端：FastAPI + SSE
- AI：Google Gemini
- 下载：yt-dlp
- 存储：SQLite（开发）/ PostgreSQL（生产推荐）
- Auth：Supabase（可选）

## 近期关键决策
- Render 免费实例无持久化磁盘，生产使用外部 Postgres（`DATABASE_URL`）。
- 前端改为路由化页面（`AppShell.vue` + `vue-router`）。
- 价格统一由 `docs/COMMERCIAL.md` 作为单一来源。
- 调试与支付开关统一见 `docs/CONFIGURATION.md`。

## 技术边界与约束
- Render 免费层不可挂载磁盘，SQLite 数据会在部署后丢失。
- 支付宝/微信正式支付需要平台资质，沙箱无法完全替代生产。
- Supabase 未配置时，登录与云端能力会降级。

## 不在范围内 / 不支持
- 非 B 站链接的稳定支持（目前仅保证 B 站 URL）。
- 超长视频或极高并发的 SLA 保证。
- 无字幕视频的结果质量保证（会尝试视频转录，可能较慢）。

## 数据合规提示
- 用户需确保对视频/字幕拥有合法使用权限并遵守平台条款。
- 本项目仅提供技术工具，不承担内容授权责任。

## 配置矩阵（摘要）
- 完整配置请参考 `docs/CONFIGURATION.md`。

## 相关文档
- 入口与硬约束：`docs/START_HERE.md`
- 系统架构：`docs/ARCHITECTURE.md`
- API 契约：`docs/API_CONTRACT.md`
- 配置参考：`docs/CONFIGURATION.md`
- 数据模型：`docs/DATA_MODEL.md`
- 安全与鉴权：`docs/SECURITY_AUTH.md`
- 部署与运维：`docs/RUNBOOK.md`
- 产品/UI 规范：`docs/PRODUCT_UI.md`
- 商业化与支付：`docs/COMMERCIAL.md`
- 进度与路线图：`docs/ROADMAP.md`
