# 部署与运维手册

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

## Render 部署
1) 连接 GitHub 仓库
2) 设置环境变量：
   - `GOOGLE_API_KEY`
   - `DATABASE_URL`（生产推荐）
3) 等待构建完成

## 关键环境变量
- `GOOGLE_API_KEY`：必需
- `DATABASE_URL`：外部 Postgres（生产建议）
- `SUPABASE_URL` / `SUPABASE_ANON_KEY`：登录与云端历史
- `DEBUG_API=1`：打开调试接口
- `PAYMENT_MOCK=1`：支付联调

## 常见问题
- **Render 重启后数据丢失**：说明还在用 SQLite，需配置 `DATABASE_URL`。
- **前端找不到 vue-router**：在 `frontend/` 执行 `npm install vue-router@4`。
