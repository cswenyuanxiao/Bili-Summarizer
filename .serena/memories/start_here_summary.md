# START_HERE 速记

来源：docs/START_HERE.md

## 一句话
Bili‑Summarizer：B 站视频 AI 总结工具，输出结构化总结/转录/思维导图，支持导出与积分计费。

## Golden Path
1) 打开 `/` → 粘贴 B 站链接
2) SSE 总结 → 等待 `summary_complete`
3) 结果渲染 → 导出/分享/入库

## 系统三要素
- 计算：yt-dlp → Gemini → 结构化摘要
- 存储：Postgres（生产）/ SQLite（开发）
- 鉴权：x-api-key 优先，Bearer 其次（需与 API_REFERENCE 统一）

## 10 条硬约束（摘要）
- SSE 事件协议兼容不可破坏
- 扣分：仅 `summary_complete` 成功时扣
- 支付回调需幂等
- UI 交互约束：卡片需真实事件、Modal 可关闭/可滚动、z-index 使用 token
- 新增接口需结构化日志字段
- 新增配置/API/SSE/价格需同步对应文档

## 最小闭环验证
1) 配 `GOOGLE_API_KEY`
2) 后端：`uvicorn web_app.main:app --reload --port 7860`
3) 前端：`cd frontend && npm install && npm run dev`
4) 访问：`http://localhost:5173`
5) SSE 收到 `summary_complete` 且页面渲染成功