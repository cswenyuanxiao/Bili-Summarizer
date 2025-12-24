# 安全与鉴权

Last updated: 2025-12-24  
Owner: Backend

## 鉴权优先级
1) `x-api-key`  
2) `Authorization: Bearer <token>`

同时存在：以 `x-api-key` 为准。

## 权限模型
- API Key：仅允许 API 能力（summarize/history/share）。
- Bearer：允许账号能力（billing/subscription/dashboard）。

## 401 / 403 条件
- 401：缺少或无效凭证。
- 403：凭证有效但权限不足。

## 会话与安全建议
- Supabase session 需持久化并支持刷新。
- 发现 session 异常时清理本地 session 并提示重试。
