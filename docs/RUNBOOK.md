# 部署与运维手册

Last updated: 2025-12-24  
Owner: Ops

## 本地开发
```bash
# 后端
export GOOGLE_API_KEY="..."
uvicorn web_app.main:app --reload --port 7860

# 前端
cd frontend
npm install
npm run dev
```

## Docker
```bash
docker-compose up -d
```

### Docker Compose 最小说明
- 后端服务：FastAPI（默认 7860）
- 前端服务：Vite 开发或静态 `dist`（生产）
- 如修改 compose，确保端口映射与前端代理一致

## Render 部署
1) 连接 GitHub 仓库
2) 设置环境变量：
   - `GOOGLE_API_KEY`
   - `DATABASE_URL`（生产推荐）
3) 等待构建完成

## 关键环境变量
完整列表见：`docs/CONFIGURATION.md`

## 健康检查与观测（建议）
- `/healthz`：只检查进程存活
- `/readyz`：检查数据库与外部依赖可用性
- 日志建议字段：request_id、user_id、video_id、latency、token_usage
- 告警关注：支付回调失败率、Gemini 错误率、下载失败率、DB 连接耗尽

## 静态前端托管说明
- 生产使用 `frontend/dist` 由 FastAPI 静态托管。
- 确保构建步骤包含 `npm run build`。
- History 路由需重写到 `index.html`。

## 密钥管理与轮换
- `GOOGLE_API_KEY`、支付私钥、Webhook secret 必须使用环境变量。
- 更换密钥后需重启服务生效。

## 常见问题
- **Render 重启后数据丢失**：说明还在用 SQLite，需配置 `DATABASE_URL`。
- **前端找不到 vue-router**：在 `frontend/` 执行 `npm install vue-router@4`。
