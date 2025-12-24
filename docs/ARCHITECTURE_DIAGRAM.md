# Bili-Summarizer 项目结构图

> 生成日期: 2025-12-25

---

## 🏗️ 系统总览架构

```mermaid
flowchart TB
    subgraph Client["🌐 客户端"]
        Browser["浏览器"]
    end
    
    subgraph Frontend["📱 前端 (Vue 3 + Vite)"]
        VueApp["Vue SPA"]
        Router["Vue Router"]
        Composables["Composables<br/>(useSummarize, useAuth, etc.)"]
        Components["UI 组件<br/>(UrlInput, ShareCard, etc.)"]
    end
    
    subgraph Backend["⚙️ 后端 (FastAPI)"]
        MainAPI["main.py API 路由层"]
        subgraph Core["核心逻辑"]
            Auth["auth.py 鉴权"]
            Credits["credits.py 积分"]
            Downloader["downloader.py 下载"]
            Summarizer["summarizer_gemini.py AI"]
        end
        subgraph V2Features["v2.0 增强模块"]
            Teams["teams.py 团队"]
            Templates["templates.py 模板"]
            TTS["tts.py 语音"]
            Push["notifications.py 推送"]
            Compare["compare.py 对比"]
            Scheduler["scheduler.py 定时任务"]
            Favorites["favorites.py 收藏夹"]
            ShareCard["share_card.py 分享卡"]
        end
        DB["db.py 数据库抽象"]
    end
    
    subgraph External["☁️ 外部服务"]
        Bilibili["Bilibili API"]
        Gemini["Google Gemini"]
        Supabase["Supabase Auth/DB"]
        Email["SMTP Server"]
        PushService["Web Push Service"]
    end
    
    Browser --> VueApp
    VueApp --> MainAPI
    MainAPI --> Core
    MainAPI --> V2Features
    
    Core --> External
    V2Features --> External
    Core --> DB
    V2Features --> DB
```

---

## 📂 项目目录结构

```
bili-summarizer/
├── 📁 frontend/                    # Vue 3 前端应用
│   ├── 📁 src/
│   │   ├── App.vue                 # 主入口 (包含总结核心逻辑)
│   │   ├── 📁 pages/               # 路由页面 (12个)
│   │   │   ├── HomePage.vue        # 首页
│   │   │   ├── TeamsPage.vue       # [v2.0] 团队协作
│   │   │   ├── ComparePage.vue     # [v2.0] 总结对比
│   │   │   ├── TemplatesPage.vue   # [v2.0] 模板管理
│   │   │   ├── SubscriptionsPage.vue # [v2.0] UP主订阅
│   │   │   ├── DashboardPage.vue   # 仪表盘
│   │   │   └── ...
│   │   ├── 📁 components/          # UI 组件
│   │   │   ├── ShareCardModal.vue  # [v2.0] 分享卡片弹窗
│   │   │   ├── FavImportModal.vue  # [v2.0] 收藏夹导入弹窗
│   │   │   ├── AudioPlayer.vue     # [v2.0] 语音播放器
│   │   │   └── ...
│   │   └── ...
│   └── ...
│
├── 📁 web_app/                     # FastAPI 后端
│   ├── main.py                     # 核心 API 与路由 (2800+ 行)
│   ├── teams.py                    # [v2.0] 团队逻辑
│   ├── compare.py                  # [v2.0] 对比逻辑
│   ├── tts.py                      # [v2.0] 语音播报
│   ├── templates.py                # [v2.0] 模板管理
│   ├── subscriptions.py            # [v2.0] 订阅管理
│   ├── notifications.py            # [v2.0] 通知推送
│   ├── scheduler.py                # [v2.0] 任务调度
│   ├── share_card.py               # [v2.0] 卡片渲染
│   ├── favorites.py                # [v2.0] 收藏夹解析
│   ├── auth.py                     # 鉴权
│   ├── db.py                       # 数据库
│   └── ...
│
├── 📁 docs/                        # 项目文档
├── 📁 videos/                      # 临时视频缓存
├── 📁 feedback/                    # 用户反馈
└── ...
```


---

## 🔄 核心业务流程

### 视频总结流程 (SSE)

```mermaid
sequenceDiagram
    participant User as 用户
    participant Frontend as Vue 前端
    participant API as FastAPI
    participant Cache as 缓存模块
    participant Downloader as yt-dlp
    participant Gemini as Google Gemini
    participant DB as 数据库
    
    User->>Frontend: 粘贴视频链接
    Frontend->>API: GET /api/summarize (SSE)
    
    API->>Cache: 检查缓存
    alt 缓存命中
        Cache-->>API: 返回缓存结果
        API-->>Frontend: SSE: summary_complete (不扣分)
    else 缓存未命中
        API-->>Frontend: SSE: status (开始处理)
        
        API->>Downloader: 下载字幕/视频
        Downloader->>Downloader: yt-dlp 抓取
        Downloader-->>API: 文件路径 + 类型
        
        API-->>Frontend: SSE: status (AI 分析中)
        
        API->>Gemini: 上传文件 + 分析
        Gemini-->>API: 结构化总结 + 思维导图
        
        API-->>Frontend: SSE: transcript_complete
        API-->>Frontend: SSE: summary_complete
        
        API->>Cache: 保存结果
        API->>DB: 扣减用户积分
    end
    
    Frontend->>User: 渲染结果
```

---

## 🔐 认证与鉴权流程

```mermaid
flowchart LR
    subgraph Request["📨 请求"]
        Header["HTTP Headers"]
    end
    
    subgraph Auth["🔐 auth.py"]
        Check1{"x-api-key?"}
        Check2{"Bearer Token?"}
        VerifyKey["verify_api_key()"]
        VerifySession["verify_session_token()"]
    end
    
    subgraph Result["✅ 结果"]
        User["用户信息"]
        Error401["401 未认证"]
    end
    
    Header --> Check1
    Check1 -->|有| VerifyKey
    Check1 -->|无| Check2
    Check2 -->|有| VerifySession
    Check2 -->|无| Error401
    
    VerifyKey --> User
    VerifySession --> User
```

**鉴权优先级**:
1. `x-api-key` (开发者 API)
2. `Authorization: Bearer <token>` (Supabase Session)

---

## 💾 数据模型

```mermaid
erDiagram
    user_credits {
        TEXT user_id PK
        INTEGER credits
        INTEGER total_used
        TEXT created_at
        TEXT updated_at
    }
    
    credit_events {
        INTEGER id PK
        TEXT user_id FK
        TEXT event_type
        INTEGER cost
        TEXT created_at
    }
    
    video_cache {
        INTEGER id PK
        TEXT video_id
        TEXT url
        TEXT mode
        TEXT focus
        TEXT cache_key UK
        TEXT summary
        TEXT transcript
        TEXT usage_data
        TIMESTAMP created_at
    }
    
    api_keys {
        TEXT id PK
        TEXT user_id FK
        TEXT name
        TEXT key_hash
        BOOLEAN is_active
        TEXT last_used_at
        TEXT created_at
    }
    
    payment_orders {
        TEXT id PK
        TEXT user_id FK
        TEXT plan_id
        TEXT provider
        TEXT status
        TEXT created_at
    }
    
    summaries {
        TEXT id PK
        TEXT user_id FK
        TEXT video_id
        TEXT mode
        TEXT focus
        TEXT summary
        TEXT transcript
        TEXT mindmap
        TEXT created_at
    }
    
    user_credits ||--o{ credit_events : "has"
    user_credits ||--o{ api_keys : "owns"
    user_credits ||--o{ payment_orders : "places"
    user_credits ||--o{ summaries : "creates"
```

---

## 🌐 API 端点清单

### 核心业务

| 方法 | 路径 | 描述 | 鉴权 |
|------|------|------|------|
| `GET` | `/api/summarize` | SSE 视频总结 | ✅ |
| `POST` | `/api/chat` | AI 追问 | ✅ |
| `GET` | `/api/dashboard` | 用户仪表盘 | ✅ |
| `GET` | `/api/video-info` | 视频元信息 | ❌ |
| `GET` | `/api/image-proxy` | 图片代理 | ❌ |

### 历史与缓存

| 方法 | 路径 | 描述 | 鉴权 |
|------|------|------|------|
| `GET` | `/api/history` | 获取云端历史 | ✅ |
| `POST` | `/api/history` | 同步历史 | ✅ |
| `DELETE` | `/api/history/{id}` | 删除历史 | ✅ |
| `GET` | `/api/cache/stats` | 缓存统计 | ❌ |

### 支付与订阅

| 方法 | 路径 | 描述 | 鉴权 |
|------|------|------|------|
| `GET` | `/api/plans` | 获取套餐 | ❌ |
| `POST` | `/api/payments` | 创建支付 | ✅ |
| `GET` | `/api/payments/status` | 支付状态 | ✅ |
| `GET` | `/api/subscription` | 订阅状态 | ✅ |
| `GET` | `/api/billing` | 账单历史 | ✅ |

### 开发者 API

| 方法 | 路径 | 描述 | 鉴权 |
|------|------|------|------|
| `GET` | `/api/keys` | 列出 API Key | ✅ |
| `POST` | `/api/keys` | 创建 API Key | ✅ |
| `DELETE` | `/api/keys/{id}` | 删除 API Key | ✅ |

### 邀请与分享

| 方法 | 路径 | 描述 | 鉴权 |
|------|------|------|------|
| `GET` | `/api/invite` | 邀请信息 | ✅ |
| `POST` | `/api/invite/code` | 创建邀请码 | ✅ |
| `POST` | `/api/invite/redeem` | 兑换邀请码 | ✅ |
| `POST` | `/api/share` | 创建分享链接 | ✅ |
| `GET` | `/share/{id}` | 查看分享 | ❌ |

---

## 📱 前端路由结构

```mermaid
flowchart TB
    subgraph AppShell["AppShell.vue (导航壳)"]
        Header["Header 导航栏"]
        Footer["Footer"]
    end
    
    subgraph Routes["路由页面"]
        Home["/  首页<br/>HomePage.vue"]
        Product["/product  产品<br/>ProductPage.vue"]
        Pricing["/pricing  定价<br/>PricingPage.vue"]
        Docs["/docs  文档<br/>DocsPage.vue"]
        Dashboard["/dashboard  仪表盘<br/>DashboardPage.vue"]
        Billing["/billing  账单<br/>BillingPage.vue"]
        Invite["/invite  邀请<br/>InvitePage.vue"]
        Developer["/developer  开发者<br/>DeveloperPage.vue"]
    end
    
    subgraph Modals["弹窗组件"]
        LoginModal["登录弹窗"]
        PricingModal["定价弹窗"]
        DashboardModal["仪表盘弹窗"]
        ApiKeyModal["API Key 弹窗"]
    end
    
    AppShell --> Routes
    Routes --> Modals
```

---

## ⚡ 技术栈总结

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端框架** | Vue 3 + Composition API | SFC + TypeScript |
| **构建工具** | Vite | HMR 热更新 |
| **样式** | Tailwind CSS | 流光渐变主题 |
| **状态管理** | Pinia | 轻量级 |
| **路由** | Vue Router | 8 条路由 |
| **后端框架** | FastAPI | 异步 Python |
| **AI 模型** | Google Gemini 2.0 Flash | 视频理解 |
| **视频下载** | yt-dlp | B 站抓取 |
| **认证** | Supabase | OAuth + JWT |
| **数据库** | PostgreSQL / SQLite | 生产/开发 |
| **实时通信** | SSE | 进度推送 |
| **容器化** | Docker Compose | 一键部署 |

---

## 🔗 模块依赖关系

```mermaid
flowchart TB
    subgraph Backend["后端模块"]
        main["main.py<br/>API 入口"]
        auth["auth.py"]
        credits["credits.py"]
        cache["cache.py"]
        downloader["downloader.py"]
        summarizer["summarizer_gemini.py"]
        payments["payments.py"]
        db["db.py"]
    end
    
    main --> auth
    main --> credits
    main --> cache
    main --> downloader
    main --> summarizer
    main --> payments
    
    auth --> db
    credits --> db
    cache --> db
    payments --> db
    
    summarizer --> downloader
```

---

## 📊 文件规模统计

| 模块 | 文件数 | 最大文件 | 总代码量 |
|------|--------|----------|----------|
| **后端 web_app/** | 15 | main.py (64KB, 1857行) | ~100KB |
| **前端 pages/** | 8 | HomePage.vue (23KB) | ~45KB |
| **前端 components/** | 15 | PricingModal.vue (15KB) | ~80KB |
| **前端 composables/** | 5 | useSummarize.ts (9KB) | ~23KB |
| **文档 docs/** | 14 | - | ~17KB |
