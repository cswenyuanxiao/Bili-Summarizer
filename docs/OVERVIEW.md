# 项目总览

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
- Render 免费实例无持久化磁盘，生产使用 `DATABASE_URL` 连接外部 Postgres。
- 前端改为路由化页面（`AppShell.vue` + `vue-router`）。
- 价格统一：Starter ¥1/30 积分，Pro Pack ¥3/120 积分，Pro 专业版 ¥29.9/月。
- 调试接口由 `DEBUG_API=1` 控制；`PAYMENT_MOCK` 默认关闭。

## 技术边界与约束
- Render 免费层不可挂载磁盘，SQLite 数据会在部署后丢失。
- 支付宝/微信正式支付需要平台资质，沙箱无法完全替代生产。
- Supabase 未配置时，登录与云端能力会降级。

## 相关文档
- 系统架构：`docs/ARCHITECTURE.md`
- 部署与运维：`docs/RUNBOOK.md`
- 产品/UI 规范：`docs/PRODUCT_UI.md`
- 商业化与支付：`docs/COMMERCIAL.md`
- 进度与路线图：`docs/ROADMAP.md`
