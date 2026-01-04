# START HERE

Last updated: 2026-01-05  
Owner: Core Eng

## 一句话
Bili‑Summarizer 是面向 B 站视频的 AI 总结工具：输入视频链接，输出结构化总结/转录/思维导图，并支持导出与积分计费。

## Golden Path（最短用户路径）
1) 打开 `/` → 粘贴 B 站链接  
2) 触发 SSE 总结 → 等待 `summary_complete`  
3) 结果渲染 → 导出 / 分享 / 入库  

## 系统三要素速记
- 计算：yt-dlp → Gemini → 结构化摘要
- 存储：Postgres（生产推荐）/ SQLite（开发）
- 鉴权：x-api-key 优先，Bearer 其次

## 文档治理与协作规则（Doc-as-Code）
1) `docs/` 是系统约束与架构的唯一权威来源，任何行为变化必须同步更新文档。
2) Tier A 文档属于“规范/必须更新”：`API_REFERENCE`、`CONFIGURATION`、`ENGINEERING_STANDARDS`、`DEPLOYMENT`、`CHANGELOG`。
3) Tier C 文档属于“memo/草稿”，只放在 `docs/memo/`，禁止与 Tier A 混放。
4) 新对话必须先读 `docs/SESSION_ENTRYPOINT.md`，未读完不得开始实现。
5) 代码改动与文档更新必须同 PR 完成（若无文档变更，需在 PR 说明中写明原因）。
6) 任何新增配置项必须同步更新 `docs/CONFIGURATION.md` 与 `docs/CHANGELOG.md`。
7) 任何 API 或 SSE 变更必须同步更新 `docs/API_REFERENCE.md` 与 `docs/CHANGELOG.md`。
8) 任何部署流程变更必须同步更新 `docs/DEPLOYMENT.md`。
9) 文档入口以 `docs/AI_CONTEXT.md` 为唯一“可控上下文包”。

## 改代码必须遵守的 10 条（硬约束）
1) SSE 事件协议不可破坏兼容（见 `docs/API_REFERENCE.md`）。
2) 扣分时点固定：`summary_complete` 成功时扣，失败不扣（见 `docs/API_REFERENCE.md`）。
3) 支付回调必须幂等，重复回调不能重复发货（见 `docs/archived/COMMERCIAL.md`）。
4) 所有可点击卡片必须有真实事件（见 `docs/archived/PRODUCT_UI.md`）。
5) Modal 必须可关闭且移动端可滚动（见 `docs/archived/PRODUCT_UI.md`）。
6) z-index 必须使用 token（见 `docs/archived/PRODUCT_UI.md`）。
7) 新增接口必须有结构化日志字段（见 `docs/ENGINEERING_STANDARDS.md`）。
8) 新增配置必须进入 `docs/CONFIGURATION.md`。
9) 新增 API/SSE 字段必须更新 `docs/API_REFERENCE.md`。
10) 改价格只在 `docs/archived/COMMERCIAL.md` 修改。

## 最小闭环验证
1) 设置 `GOOGLE_API_KEY`  
2) 启动后端：`uvicorn web_app.main:app --reload --port 7860`  
3) 启动前端：`cd frontend && npm install && npm run dev`  
4) 访问：`http://localhost:5173`  
5) 验证：SSE 收到 `summary_complete`，页面渲染成功

## 文档地图（按角色）
- 前端：`docs/START_HERE.md` + `docs/API_REFERENCE.md` + `docs/ENGINEERING_STANDARDS.md`
- 后端：`docs/START_HERE.md` + `docs/DEVELOPER_GUIDE.md` + `docs/API_REFERENCE.md`
- 运维：`docs/DEPLOYMENT.md` + `docs/CONFIGURATION.md`
- 商业化：`docs/archived/COMMERCIAL.md`
