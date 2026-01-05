# API_REFERENCE 速记

来源：docs/API_REFERENCE.md

## 基础
- Base URL：dev `http://localhost:8000`
- 格式：JSON
- 认证：Bearer Token（需与 START_HERE 里的 x-api-key 描述统一）

## 总结接口
- POST `/api/summarize`：url/mode/focus/skip_cache/output_language/enable_cot
- SSE(GET `/api/summarize`) 事件：
  - transcript_complete
  - summary_complete（含 usage：cot_steps/charts/keywords 等可选）
  - status
  - error

## 订阅
- GET `/api/subscriptions/search` 搜索 UP 主
- GET `/api/subscriptions` 列表（需认证）
- POST `/api/subscriptions` 订阅（需认证）
- DELETE `/api/subscriptions/{id}` 取消
- GET `/api/subscriptions/videos` 最新视频

## 其他
- GET `/api/trending/videos` 热门
- GET/POST `/api/templates` 模板（需认证）
- GET `/api/dashboard` 仪表盘（需认证）

## 错误与外部依赖
- 标准错误：`{"detail":"..."}`
- B站错误码：-352/-412 等
- 外部：Bilibili API、Gemini API、Supabase Auth/DB