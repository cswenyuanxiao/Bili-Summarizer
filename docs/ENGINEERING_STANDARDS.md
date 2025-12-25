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

## CI 基线（必过）
- Backend 依赖安装 + `pip check`
- Frontend `npm run build` 成功

---

## 🛡️ 模块化与解耦最佳实践

### 原则 1: 单一职责 (SRP)
- main.py 仅负责应用初始化 (~150行)
- 业务逻辑放到 routers/ 和 services/
- 配置常量统一在 config.py

### 原则 2: "超过100行就拆分"
- 单个文件 >300行 → 立即拆分
- 单个router >100行 → 按功能分解

### 原则 3: 依赖注入
- 使用 FastAPI Depends 避免全局导入
- 避免循环依赖

### 原则 4: 定期审查
```bash
# 每月检查最大文件
find web_app -name "*.py" -exec wc -l {} \; | sort -rn | head -10
```

**详细指南**: 见 [REFACTORING_CLEANUP_GUIDE.md](./REFACTORING_CLEANUP_GUIDE.md)
