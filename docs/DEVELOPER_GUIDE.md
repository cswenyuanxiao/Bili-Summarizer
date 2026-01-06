# Developer Guide

> **快速开始**: 建议先阅读 [START_HERE.md](START_HERE.md)  
> **最后更新**: 2025-12-26

---

## 📖 目录

1. [项目概览](#项目概览)
2. [系统架构](#系统架构)
3. [项目结构](#项目结构)
4. [数据模型](#数据模型)
5. [开发流程](#开发流程)

---

## 项目概览

**Bili-Summarizer** 是一个基于AI的B站视频总结工具，支持：
- 视频智能总结（摘要+要点提取）
- 自动字幕转录（带时间戳）
- 思维导图生成（Markdown 列表 + Markmap 渲染）
- UP主订阅与推送
- 批量处理与收藏管理

### 技术栈

**后端**:
- FastAPI (Python 3.10+)
- Supabase (PostgreSQL + Auth)
- APScheduler (定时任务)
- Google Gemini API (AI总结)

**前端**:
- Vue 3 + TypeScript
- Vue Router + Pinia
- Vite (构建工具)
- Markmap (思维导图渲染)

**部署**:
- Render (后端托管)
- Vercel (前端托管)
- Supabase (数据库)

---

## 系统架构

### 整体架构图

```
┌─────────────┐
│  用户浏览器  │
└──────┬──────┘
       │ HTTPS
       ↓
┌─────────────────────────────────┐
│  前端 (Vue + Vite)              │
│  - 路由: Vue Router             │
│  - 状态: Pinia                  │
│  - UI: 自定义样式+Heroicons     │
└──────────────┬──────────────────┘
               │ API (Proxy)
               ↓
┌──────────────────────────────────────┐
│  后端 (FastAPI)                      │
│  ┌────────────────────────────────┐  │
│  │  Routers (模块化)              │  │
│  │  - /api/summarize              │  │
│  │  - /api/subscriptions          │  │
│  │  - /api/trending               │  │
│  │  - /api/payments               │  │
│  │  - /api/templates              │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │  Services                      │  │
│  │  - services/history_service.py │  │
│  │  - services/subscriptions_service.py │  │
│  │  - clients/bilibili_client.py  │  │
│  │  - wbi.py (签名)               │  │
│  │  - db.py (SQLite)              │  │
│  │  - scheduler.py (定时任务)     │  │
│  └────────────────────────────────┘  │
└──────┬────────────┬─────────────┬────┘
       │            │             │
       ↓            ↓             ↓
  ┌─────────┐ ┌──────────┐ ┌───────────┐
  │Supabase │ │Bilibili  │ │Google     │
  │ (Auth)  │ │  API     │ │Gemini API │
  └─────────┘ └──────────┘ └───────────┘
```

### 核心流程

#### 1. 视频总结流程
```
用户输入URL
  ↓
提取BV号
  ↓
调用B站API获取视频信息
  ↓
下载字幕/音频
  ↓
Gemini API生成总结+思维导图
  ↓
返回前端展示
  ↓
保存到历史记录（Supabase）
```

#### 2. 订阅推送流程
```
用户订阅UP主
  ↓
存入subscriptions表
  ↓
定时任务(每小时)
  ↓
遍历订阅列表
  ↓
调用B站API获取新视频(WBI签名)
  ↓
检测到新视频 → 推送通知
```

---

## 项目结构

```
summarizer/
├── web_app/                 # 后端代码
│   ├── main.py              # FastAPI入口（仅实例化+注册路由）
│   ├── app_setup.py         # 中间件与静态资源挂载
│   ├── lifecycle.py         # 启动/关闭生命周期
│   ├── exceptions.py        # 全局异常处理注册
│   ├── legacy_main.py       # 历史路由聚合（APIRouter）
│   ├── routers/             # API路由模块
│   │   ├── subscriptions.py # 订阅相关
│   │   ├── trending.py      # 热门视频
│   │   ├── payments.py      # 支付
│   │   └── templates.py     # 自定义模板
│   ├── services/            # 业务服务层
│   │   ├── history_service.py
│   │   └── subscriptions_service.py
│   ├── clients/             # 第三方客户端
│   │   └── bilibili_client.py
│   ├── subscriptions.py     # 兼容层（历史导入路径）
│   ├── wbi.py               # B站WBI签名
│   ├── db.py                # 数据库操作
│   └── scheduler.py         # 定时任务调度
│
├── frontend/                # 前端代码
│   ├── src/
│   │   ├── pages/           # 页面组件
│   │   │   ├── HomePage.vue
│   │   │   ├── TrendingPage.vue
│   │   │   ├── FavoritesPage.vue
│   │   │   ├── BatchPage.vue
│   │   │   ├── SubscriptionsPage.vue
│   │   │   ├── ComparePage.vue
│   │   │   └── TemplatesPage.vue
│   │   ├── components/      # 公共组件
│   │   ├── composables/     # 组合式API
│   │   │   ├── useAuth.ts
│   │   │   └── useSummarize.ts
│   │   ├── router/          # 路由配置
│   │   └── App.vue          # 根组件
│   └── vite.config.ts       # Vite配置
│
├── docs/                    # 文档
├── .env                     # 环境变量
└── requirements.txt         # Python依赖
```

---

## 数据模型

### Supabase表

#### 1. users (Supabase Auth自动管理)
```sql
- id: uuid (主键)
- email: string
- created_at: timestamp
```

#### 2. summaries (总结历史)
```sql
CREATE TABLE summaries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id),
  video_url text NOT NULL,
  video_title text,
  video_thumbnail text,
  mode text,  -- 'smart' | 'video'
  focus text,
  summary text,
  transcript text,
  mindmap text,
  created_at timestamp DEFAULT now()
);

-- RLS策略
ALTER TABLE summaries ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own summaries"
  ON summaries FOR SELECT
  USING (auth.uid() = user_id);
```

#### 3. up_subscriptions (本地SQLite)
```sql
CREATE TABLE up_subscriptions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    up_mid TEXT NOT NULL,
    up_name TEXT NOT NULL,
    up_avatar TEXT,
    notify_methods TEXT,  -- JSON: ["browser", "email"]
    created_at TEXT NOT NULL,
    last_checked_at TEXT,
    last_video_bvid TEXT
);
```

### 前端数据模型 (TypeScript)

```typescript
// 订阅项
interface Subscription {
  id: string
  up_mid: string
  up_name: string
  up_avatar: string
  created_at: string
  videos?: Video[]
  videosLoading?: boolean
}

// 视频
interface Video {
  bvid: string
  title: string
  pic: string
  created: number
  length: number
  url: string
}

// 总结请求
interface SummarizeRequest {
  url: string
  mode: 'smart' | 'video'
  focus?: string
  skip_cache?: boolean
}

// 总结结果
interface SummarizeResult {
  summary: string
  transcript?: string
  mindmap?: string
  videoFile?: string
}
```

---

## 开发流程

### 1. 环境搭建

```bash
# 克隆项目
cd /path/to/summarizer

# 后端
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 前端
cd frontend
npm install

# 配置环境变量
cp .env.example .env
# 编辑.env，填入API密钥
```

### 2. 本地开发

```bash
# 终端1: 启动后端
python -m uvicorn web_app.main:app --reload --port 8000

# 终端2: 启动前端
cd frontend
npm run dev -- --port 5173

# 访问 http://localhost:5173
```

### 3. 添加新功能

遵循模块化原则（参考 [ENGINEERING_STANDARDS.md](ENGINEERING_STANDARDS.md)）：

1. **后端API**: 在 `web_app/routers/` 创建新模块
2. **前端页面**: 在 `frontend/src/pages/` 创建Vue组件
3. **路由配置**: 更新 `frontend/src/router/index.ts`
4. **更新文档**: 在本文档添加新功能说明

### 4. 调试技巧

**后端**:
```python
# 在代码中添加日志
import logging
logger = logging.getLogger(__name__)
logger.info(f"Debug: {variable}")
```

**前端**:
```javascript
// 在Vue组件中
console.log('Debug:', data)

// 在浏览器开发者工具查看:
// - Network: API请求
// - Console: 日志输出
// - Vue DevTools: 组件状态
```

**B站API风控调试**:
```bash
# 检查SESSDATA是否生效
tail -f logs/app.log | grep "Using SESSDATA"

# 手动测试API
curl 'http://localhost:8000/api/subscriptions/videos?up_mid=123456&count=1'
```

---

## 常见问题

### Q: B站API返回-352风控错误？
A: 确保`.env`中配置了`BILIBILI_SESSDATA`（从B站Cookies中获取）

### Q: 前端API请求失败？
A: 检查Vite代理配置（`frontend/vite.config.ts`）是否指向正确的后端端口（默认8000）

### Q: Supabase Auth不工作？
A: 确认`.env`中`SUPABASE_URL`和`SUPABASE_ANON_KEY`配置正确

### Q: 定时任务不执行？
A: 检查`web_app/scheduler.py`是否在`main.py`启动时初始化

---

## 参考资料

- [配置参考](CONFIGURATION.md)
- [工程规范](ENGINEERING_STANDARDS.md)
- [API参考](API_REFERENCE.md)
- [部署手册](DEPLOYMENT.md)
- [变更日志](CHANGELOG.md)
