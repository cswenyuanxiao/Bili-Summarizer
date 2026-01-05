# API Reference

> **最后更新**: 2026-01-05

---

## 📖 目录

1. [后端API](#后端api)
2. [外部依赖API](#外部依赖api)
3. [认证方式](#认证方式)

---

## 后端API

### 基础信息

- **Base URL**: `http://localhost:8000` (开发) / `https://your-domain.com` (生产)
- **数据格式**: JSON
- **认证**: `x-api-key` 优先，其次 `Authorization: Bearer <token>` (Supabase JWT)

---

### 1. 视频总结

#### POST `/api/summarize`

**请求**:
```json
{
  "url": "https://www.bilibili.com/video/BV1xx",
  "mode": "smart",  // "smart" | "video"
  "focus": "技术要点",  // 可选
  "skip_cache": false,  // 可选
  "output_language": "zh",  // "zh" | "en" | "ja" | "ko" | "es" | "fr"
  "enable_cot": false  // 可选：启用思维链展示
}
```

**响应**:
```json
{
  "summary": "# 视频总结\n...",
  "transcript": "00:00 开场...",
  "mindmap": "- 核心主题\n  - 分支 1\n  - 分支 2",
  "videoFile": "/videos/xxx.mp4"  // 可选
}
```

**需要认证**: ✅

#### SSE 事件（GET `/api/summarize`）

事件类型：
- `transcript_complete`: `{ "type": "transcript_complete", "transcript": "..." }`
- `summary_complete`: `{ "type": "summary_complete", "summary": "...", "usage": { ... }, "transcript": "..." }`
- `status`: `{ "type": "status", "status": "..." }`
- `error`: `{ "type": "error", "code": "...", "error": "..." }`

`summary_complete.usage` 关键字段（可选）：
- `cot_steps`: `[{ "step": 1, "title": "...", "thinking": "..." }]`
- `charts`: `[{ "type": "bar", "title": "...", "data": { "labels": [], "values": [] } }]`
- `keywords`: `[{ "text": "AI", "value": 10 }]`

---

### 2. 订阅管理

#### GET `/api/subscriptions/search`

搜索UP主

**参数**:
- `keyword`: 搜索关键词

**响应**:
```json
{
  "users": [
    {
      "mid": "123456",
      "name": "UP主名称",
      "avatar": "https://...",
      "fans": 100000,
      "videos": 500,
      "sign": "个性签名"
    }
  ]
}
```

#### GET `/api/subscriptions`

获取订阅列表

**需要认证**: ✅

**响应**:
```json
{
  "subscriptions": [
    {
      "id": "uuid",
      "up_mid": "123456",
      "up_name": "名称",
      "up_avatar": "https://...",
      "created_at": "2025-12-26T00:00:00",
      "notify_methods": ["browser"]
    }
  ]
}
```

#### POST `/api/subscriptions`

订阅UP主

**需要认证**: ✅

**请求**:
```json
{
  "up_mid": "123456",
  "up_name": "UP主名称",
  "up_avatar": "https://...",
  "notify_methods": ["browser", "email"]
}
```

#### DELETE `/api/subscriptions/{subscription_id}`

取消订阅

**需要认证**: ✅

#### GET `/api/subscriptions/videos`

获取UP主最新视频

**参数**:
- `up_mid`: UP主ID
- `count`: 视频数量 (默认2)

**响应**:
```json
{
  "up_mid": "123456",
  "videos": [
    {
      "bvid": "BV1xx",
      "title": "视频标题",
      "cover": "https://...",
      "duration": "10:30",
      "created": 1703001600,
      "url": "https://www.bilibili.com/video/BV1xx"
    }
  ]
}
```

---

### 3. 热门视频

#### GET `/api/trending/videos`

获取B站热门视频

**响应**:
```json
{
  "videos": [
    {
      "bvid": "BV1xx",
      "title": "标题",
      "pic": "https://...",
      "owner_name": "UP主",
      "owner_mid": "123456",
      "owner_face": "https://...",
      "duration": 630,
      "view": 100000,
      "like": 5000,
      "danmaku": 1000,
      "url": "https://www.bilibili.com/video/BV1xx"
    }
  ]
}
```

---

### 4. 自定义模板

#### GET `/api/templates`

获取模板列表

**需要认证**: ✅

#### POST `/api/templates`

创建模板

**需要认证**: ✅

**请求**:
```json
{
  "name": "技术分析模板",
  "prompt": "请按以下格式总结...",
  "is_public": false
}
```

---

### 5. 用户管理

#### GET `/api/dashboard`

获取用户仪表盘数据

**需要认证**: ✅

**响应**:
```json
{
  "credits": 100,
  "total_used": 50,
  "cost_per_summary": 1,
  "daily_usage": [
    {"day": "2025-12-25", "count": 10}
  ]
}
```

---

## 外部依赖API

### 1. Bilibili API

#### 搜索UP主
```
GET https://api.bilibili.com/x/web-interface/search/type
参数:
  - keyword: 搜索词
  - search_type: bili_user
  - page: 页码
  - page_size: 每页数量
```

#### 获取UP主视频 (需要WBI签名)
```
GET https://api.bilibili.com/x/space/wbi/arc/search
参数:
  - mid: UP主ID
  - pn: 页码
  - ps: 每页数量
  - order: pubdate
  - wts: 时间戳
  - w_rid: WBI签名
```

**WBI签名流程**:
1. 调用 `/x/web-interface/nav` 获取 `wbi_img.img_url` 和 `wbi_img.sub_url`
2. 提取文件名（去除扩展名）
3. 使用 `wbi.py` 中的 `sign_wbi()` 函数生成签名

#### 热门视频
```
GET https://api.bilibili.com/x/web-interface/popular
参数:
  - ps: 每页数量 (默认20)
  - pn: 页码
```

**重要提示**:
- 所有请求必须添加真实User-Agent
- 建议配置`BILIBILI_SESSDATA`环境变量（成功率95%+）
- 遇到-352错误时，代码会自动重试

---

### 2. Google Gemini API

#### 文本生成
```python
import google.generativeai as genai

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

response = model.generate_content(prompt)
```

**环境变量**: `GOOGLE_API_KEY`

**官方文档**: https://ai.google.dev/

---

### 3. Supabase

#### 认证
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
)

// 登录
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password'
})

// 获取session
const { data: { session } } = await supabase.auth.getSession()
```

#### 数据库操作
```javascript
// 查询
const { data, error } = await supabase
  .from('summaries')
  .select('*')
  .eq('user_id', userId)

// 插入
const { data, error } = await supabase
  .from('summaries')
  .insert({
    user_id: userId,
    video_url: url,
    summary: summary
  })
```

**环境变量**:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

**官方文档**: https://supabase.com/docs

---

## 认证方式

### API Key（x-api-key）

**请求头**:
```
x-api-key: sk-bili-***
```

**优先级**: 若同时提供 `x-api-key` 与 `Authorization: Bearer`，以 `x-api-key` 为准。

### Supabase JWT Bearer Token

**前端获取Token**:
```javascript
const { data: { session } } = await supabase.auth.getSession()
const token = session?.access_token
```

**前端发送请求**:
```javascript
fetch('/api/subscriptions', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

**后端验证**:
```python
from web_app.auth import verify_session_token

token = request.headers.get("Authorization", "").replace("Bearer ", "")
user = await verify_session_token(token)
# user = {"user_id": "xxx", "email": "xxx"}
```

---

## 错误处理

### 标准错误响应

```json
{
  "detail": "错误描述"
}
```

### 常见错误码

| HTTP状态码 | 含义 | 常见原因 |
|-----------|------|----------|
| 400 | Bad Request | 参数错误 |
| 401 | Unauthorized | 未登录或Token无效 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 参数验证失败 |
| 500 | Internal Server Error | 服务器错误 |

### B站API特殊错误

| code | message | 解决方案 |
|------|---------|----------|
| -352 | 风控校验失败 | 添加SESSDATA或减少请求频率 |
| -412 | 请求被拦截 | 检查User-Agent和Referer |
| 0 | 成功 | - |

---

## 开发工具

### Postman Collection

可以导入以下环境变量：
```json
{
  "base_url": "http://localhost:8000",
  "token": "your_supabase_jwt_token"
}
```

### cURL示例

```bash
# 搜索UP主
curl 'http://localhost:8000/api/subscriptions/search?keyword=技术'

# 获取订阅列表（需要token）
curl -H "Authorization: Bearer ${TOKEN}" \
  'http://localhost:8000/api/subscriptions'

# 视频总结
curl -X POST 'http://localhost:8000/api/summarize' \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.bilibili.com/video/BV1xx","mode":"smart"}'
```

---

## 参考资料

- [开发者指南](DEVELOPER_GUIDE.md)
- [配置参考](CONFIGURATION.md)
- [部署手册](DEPLOYMENT.md)
