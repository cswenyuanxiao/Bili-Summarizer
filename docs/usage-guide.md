# 使用说明（前端/后端/Docker/Render）

## 你看到“无历史记录”的原因
- 历史记录只在完成过至少一次总结后才会显示。
- 历史是存储在浏览器的 localStorage 里，按“域名 + 端口”隔离。
  - `http://localhost:5173` 和 `http://127.0.0.1:5173` 是两个不同的存储空间。
  - `http://localhost:5173` 与 `http://localhost:7860` 也互不共享历史。
- 所以：切换访问地址、端口或清空浏览器存储后，历史会显示为空。

建议：确定一个固定入口访问（如下文的“推荐访问链接”）。

---

## 额度说明
- 新注册用户赠送 30 积分（约 3 次总结）。
- 每次总结默认消耗 10 积分。
- 访问“仪表盘”可查看剩余积分与已使用次数。
- 首次完成总结会额外奖励 10 积分。
- 邀请好友成功双方各得 10 积分。

---

## 订阅与支付
- 升级入口：右上角头像菜单 → “升级 Pro” 或 “方案”。
- 支付方式：支付宝 / 微信（需要配置支付环境变量）。
- 如果支付未配置，界面会提示“暂未开放”。

---

## 分享链接
- 历史记录卡片支持“分享”，会生成只读链接并自动复制。
- 分享链接会展示总结与转录内容。

---

## 1) 本地开发（推荐）

适合开发调试，热更新最快。

### 后端
```bash
export GOOGLE_API_KEY="你的密钥"
uvicorn web_app.main:app --reload --port 7860
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

### 访问链接（推荐）
- `http://localhost:5173`

说明：前端 dev server 会通过 Vite 代理请求后端 API（见 `frontend/vite.config.ts`），所以只需要打开 5173 即可。历史记录也会保存在 5173 这个域名/端口下。

---

## 2) 本地构建 + 后端直出

适合接近线上部署的本地验证。

### 构建前端
```bash
cd frontend
npm run build
```

### 启动后端（会自动托管 frontend/dist）
```bash
export GOOGLE_API_KEY="你的密钥"
uvicorn web_app.main:app --reload --port 7860
```

### 访问链接
- `http://localhost:7860`

说明：如果 `frontend/dist` 不存在，会回退到 legacy UI（历史/新功能可能不全）。

---

## 3) Docker Compose

适合本地一键启动与多服务验证。

```bash
docker-compose up -d
```

### 访问链接（推荐）
- `http://localhost`

说明：Nginx 会统一代理前端静态资源与后端 API。

---

## 4) Render / 云端部署

适合对外分享或正式发布。

### 访问链接
- Render 给出的服务 URL（例如 `https://xxx.onrender.com`）

说明：Render 部署后只需访问服务 URL；不要再用本地端口。

---

## 推荐访问入口（总结）

1. 开发调试：`http://localhost:5173`
2. 本地准上线：`http://localhost:7860`
3. Docker：`http://localhost`
4. Render：`https://<your-service>.onrender.com`

只要固定使用一个入口，历史记录就能稳定显示。 
