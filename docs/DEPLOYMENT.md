# Deployment Guide

> **最后更新**: 2025-12-26

---

## 📖 目录

1. [快速部署](#快速部署)
2. [环境配置](#环境配置)
3. [部署到生产环境](#部署到生产环境)
4. [安全与认证](#安全与认证)
5. [故障排查](#故障排查)

---

## 快速部署

### 本地开发

```bash
# 1. 克隆项目
git clone <repo-url>
cd summarizer

# 2. 配置环境变量
cp .env.example .env
# 编辑.env，填入必要的API密钥

# 3. 安装依赖
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 4. 启动服务
# 终端1 - 后端
python -m uvicorn web_app.main:app --reload --port 8000

# 终端2 - 前端
cd frontend && npm run dev -- --port 5173
```

访问: http://localhost:5173

---

## 环境配置

### 必需的环境变量

```bash
# .env文件

# Google AI (必需)
GOOGLE_API_KEY="AIzaSyC8_a9y9Hx..."

# Supabase (必需)
SUPABASE_URL="https://xxx.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJI..."

# JWT密钥 (必需)
JWT_SECRET_KEY="随机生成的长字符串"

# Bilibili SESSDATA (强烈推荐)
BILIBILI_SESSDATA="c933235f%2C1777226620%2C..."

# PayPal (可选，商业化时需要)
PAYPAL_CLIENT_ID="your_client_id"
PAYPAL_CLIENT_SECRET="your_secret"
```

### 获取API密钥

#### Google Gemini API
1. 访问 https://ai.google.dev/
2. 创建或选择项目
3. 启用Gemini API
4. 创建API密钥
5. 复制到`.env`的`GOOGLE_API_KEY`

#### Supabase
1. 访问 https://supabase.com
2. 创建新项目
3. 进入Settings → API
4. 复制`URL`和`anon/public key`
5. 粘贴到`.env`

#### Bilibili SESSDATA (提升成功率95%)
1. 登录 https://www.bilibili.com
2. 按F12打开开发者工具
3. Application → Cookies → bilibili.com
4. 复制`SESSDATA`的值
5. 粘贴到`.env`

---

## 部署到生产环境

### 选项1: Render (推荐)

#### 后端部署

1. **连接GitHub仓库**
2. **创建Web Service**
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn web_app.main:app --host 0.0.0.0 --port $PORT`
3. **配置环境变量**
   - 添加所有`.env`中的变量
4. **部署**

#### 前端部署 (Vercel)

```bash
cd frontend
npm run build  # 构建静态文件

# 部署到Vercel
npx vercel --prod
```

**Vite配置** (`frontend/vite.config.ts`):
```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'https://your-backend.onrender.com',  // 修改为实际后端URL
        changeOrigin: true
      }
    }
  }
})
```

---

### 选项2: Docker

#### 构建镜像

```bash
# 后端
docker build -f Dockerfile.backend -t bili-summarizer-backend .

# 前端
cd frontend
docker build -t bili-summarizer-frontend .
```

#### 使用Docker Compose

```bash
# 开发环境
docker-compose -f docker-compose.dev.yml up

# 生产环境
docker-compose up -d
```

---

## 安全与认证

### Supabase Row Level Security (RLS)

#### summaries表

```sql
-- 启用RLS
ALTER TABLE summaries ENABLE ROW LEVEL SECURITY;

-- 用户只能查看自己的总结
CREATE POLICY "Users can view own summaries"
  ON summaries FOR SELECT
  USING (auth.uid() = user_id);

-- 用户只能插入自己的总结
CREATE POLICY "Users can insert own summaries"
  ON summaries FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- 用户只能删除自己的总结
CREATE POLICY "Users can delete own summaries"
  ON summaries FOR DELETE
  USING (auth.uid() = user_id);
```

### API认证流程

```
请求发起
  ↓
优先检查: x-api-key
  ↓
若存在则直接验证 API Key
  ↓
若不存在，则走 Bearer Token:
用户登录 → Supabase返回JWT → 前端存储Token (localStorage)
  ↓
每次请求携带: Authorization: Bearer <token>
  ↓
后端验证Token
  ↓
提取user_id → 执行业务逻辑
```

### 安全建议

1. **永远不要提交`.env`文件到Git**
2. **定期轮换API密钥**
3. **使用HTTPS** (生产环境必需)
4. **启用Supabase RLS** (防止数据泄露)
5. **限制CORS来源** (生产环境)

---

## 故障排查

### 常见问题

#### 1. 后端启动失败

**症状**: `ModuleNotFoundError` 或 `ImportError`

**解决**:
```bash
# 确认Python版本
python --version  # 应该 >= 3.10

# 重新安装依赖
pip install -r requirements.txt
```

---

#### 2. 前端API请求失败

**症状**: Network错误，CORS错误

**检查**:
1. 后端是否运行? `curl http://localhost:8000/`
2. Vite代理配置是否正确? (检查`vite.config.ts`)
3. 浏览器控制台有无错误?

**解决**:
```bash
# 确认后端端口
lsof -i:8000

# 重启前端
cd frontend
npm run dev -- --port 5173
```

---

#### 3. Supabase认证失败

**症状**: 401 Unauthorized

**检查**:
```javascript
// 前端
const { data: { session } } = await supabase.auth.getSession()
console.log('Session:', session)  // 应该有token
```

**解决**:
- 重新登录
- 检查`.env`中`SUPABASE_URL`和`SUPABASE_ANON_KEY`是否正确
- 确认Supabase Authentication已启用

---

#### 4. B站API风控(-352)

**症状**: 订阅页面显示"该UP主暂无视频"

**解决**:
1. 添加`BILIBILI_SESSDATA`到`.env`
2. 重启后端
3. 检查日志: `tail -f app.log | grep "Using SESSDATA"`

---

#### 5. 定时任务不执行

**症状**: 订阅的UP主有新视频但没有推送

**检查**:
```python
# web_app/main.py
# 确认scheduler已启动
from .scheduler import init_scheduler
init_scheduler()  # 应该在startup事件中
```

**解决**:
- 检查日志: `grep "Video check completed" app.log`
- 手动触发: 重启后端会立即执行一次

---

### 日志查看

#### 本地开发
```bash
# 后端日志
tail -f app.log

# 前端日志
# 浏览器控制台 (F12)
```

#### 生产环境 (Render)
1. 打开Render Dashboard
2. 选择服务
3. 点击"Logs"标签
4. 查看实时日志

---

### 性能优化

#### 后端
1. **使用缓存**: 已实现在`bilibili_cache.py`（需集成）
2. **限流**: 已实现在`bilibili_rate_limiter.py`（需集成）
3. **异步处理**: 使用`asyncio`处理耗时操作
4. **数据库索引**: 在`user_id`、`created_at`列上

#### 前端
1. **代码分割**: Vue Router懒加载
   ```javascript
   {
     path: '/trending',
     component: () => import('./pages/TrendingPage.vue')
   }
   ```
2. **图片优化**: 使用CDN (已使用`images.weserv.nl`)
3. **缓存策略**: Service Worker (可选)

---

## 监控与告警

### 推荐工具

#### 后端监控
- **Sentry**: 错误追踪
- **Prometheus + Grafana**: 性能监控
- **Render自带**: 基础监控

#### 前端监控
- **Google Analytics**: 用户行为
- **Sentry (JS)**: 前端错误
- **Lighthouse**: 性能评分

### 健康检查端点

```python
# web_app/main.py
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }
```

在Render中配置:
- Health Check Path: `/health`
- Expected HTTP Status: `200`

---

## 备份与恢复

### 数据库备份 (Supabase)

Supabase自动每日备份（Pro计划）。

手动备份:
```sql
-- 在Supabase SQL Editor执行
COPY summaries TO '/tmp/summaries_backup.csv' WITH CSV HEADER;
```

### 本地SQLite备份

```bash
# 备份订阅数据
cp summarizer.db summarizer.db.backup

# 定期备份（cron）
0 2 * * * cd /path/to/summarizer && cp summarizer.db backups/summarizer_$(date +\%Y\%m\%d).db
```

---

## 参考资料

- [开发者指南](DEVELOPER_GUIDE.md)
- [API参考](API_REFERENCE.md)
- [配置参考](CONFIGURATION.md)
- [工程规范](ENGINEERING_STANDARDS.md)
