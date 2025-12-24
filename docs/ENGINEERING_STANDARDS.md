# 工程规范（验收条款）

Last updated: 2025-12-24  
Owner: Core Eng

## 日志标准
- 必须包含：`request_id`、`user_id`、`video_id`、`latency_ms`、`status`

## 超时与重试
- Gemini：设置超时 + 失败返回 `UPSTREAM_FAILED`
- 下载：失败允许一次重试

## 限流建议
- 按用户限制并发与每日调用
- 对 API Key 使用单独配额

## 测试与验收
- 新增 API 必须有错误码覆盖（401/403/5xx）
- 支付回调必须幂等
- SSE 事件类型不破坏兼容
