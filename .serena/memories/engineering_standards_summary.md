# ENGINEERING_STANDARDS 速记

来源：docs/ENGINEERING_STANDARDS.md

## 日志标准
- 必须包含：request_id / user_id / video_id / latency_ms / status

## 超时与重试
- Gemini：设置超时 + 失败返回 UPSTREAM_FAILED
- 下载：失败允许一次重试

## 限流建议
- 按用户限制并发与每日调用
- API Key 单独配额

## 测试与验收
- 新增 API：覆盖 401/403/5xx 错误码
- 支付回调必须幂等
- SSE 事件类型不可破坏兼容

## CI 基线
- Backend 安装依赖 + pip check
- Frontend npm run build

## 模块化/解耦
- main.py 仅初始化（~150 行）
- 业务逻辑进 routers/ 与 services/
- 配置常量进 config.py
- 文件 >300 行 / router >100 行必须拆分
- 使用 FastAPI Depends 避免循环依赖
- 每月检查最大文件：find web_app -name "*.py" -exec wc -l {} \; | sort -rn | head -10