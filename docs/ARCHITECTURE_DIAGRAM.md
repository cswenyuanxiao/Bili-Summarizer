# Bili-Summarizer 项目结构图

> 生成日期: 2024-12-24

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
        Composables["Composables"]
        Components["UI 组件"]
    end
    
    subgraph Backend["⚙️ 后端 (FastAPI)"]
        MainAPI["main.py<br/>API 路由层"]
        Auth["auth.py<br/>鉴权模块"]
        Credits["credits.py<br/>积分系统"]
        Cache["cache.py<br/>缓存模块"]
        Downloader["downloader.py<br/>视频下载"]
        Summarizer["summarizer_gemini.py<br/>AI 总结"]
        Payments["payments.py<br/>支付处理"]
        DB["db.py<br/>数据库抽象"]
    end
    
    subgraph External["☁️ 外部服务"]
        Bilibili["Bilibili API"]
        Gemini["Google Gemini"]
        Supabase["Supabase Auth"]
        PostgreSQL["PostgreSQL"]
        SQLite["SQLite (开发)"]
    end
    
    Browser --> VueApp
    VueApp --> MainAPI
    MainAPI --> Auth
    MainAPI --> Credits
    MainAPI --> Cache
    MainAPI --> Downloader
    MainAPI --> Summarizer
    MainAPI --> Payments
    
    Auth --> Supabase
    Auth --> DB
    Credits --> DB
    Cache --> DB
    Downloader --> Bilibili
    Summarizer --> Gemini
    DB --> PostgreSQL
    DB --> SQLite
```

---

## 📂 项目目录结构

```
bili-summarizer/
├── 📁 frontend/                    # Vue 3 前端应用
│   ├── 📁 src/
│   │   ├── App.vue                 # 主应用 (48KB, 总结核心逻辑)
│   │   ├── AppShell.vue            # 路由壳组件 (导航/弹窗)
│   │   ├── main.ts                 # 入口文件
│   │   ├── supabase.ts             # Supabase 客户端配置
│   │   ├── style.css               # 全局样式 (流光渐变主题)
│   │   │
│   │   ├── 📁 router/              # Vue Router
│   │   │   └── index.ts            # 8 条路由配置
│   │   │
│   │   ├── 📁 pages/               # 路由页面 (8个)
│   │   │   ├── HomePage.vue        # 首页 (总结入口)
│   │   │   ├── ProductPage.vue     # 产品介绍
│   │   │   ├── PricingPage.vue     # 定价方案
│   │   │   ├── DocsPage.vue        # 使用文档
│   │   │   ├── DashboardPage.vue   # 用户仪表盘
│   │   │   ├── BillingPage.vue     # 账单页面
│   │   │   ├── InvitePage.vue      # 邀请系统
│   │   │   └── DeveloperPage.vue   # 开发者 API
│   │   │
│   │   ├── 📁 components/          # UI 组件 (15个)
│   │   │   ├── UrlInputCard.vue    # URL 输入卡片
│   │   │   ├── SummaryCard.vue     # 总结卡片
│   │   │   ├── MindmapViewer.vue   # 思维导图
│   │   │   ├── TranscriptPanel.vue # 转录面板
│   │   │   ├── ChatPanel.vue       # AI 追问
│   │   │   ├── HistoryList.vue     # 历史列表
│   │   │   ├── ExportBar.vue       # 导出工具栏
│   │   │   ├── LoadingOverlay.vue  # 加载遮罩
│   │   │   ├── LoginModal.vue      # 登录弹窗
│   │   │   ├── PricingModal.vue    # 定价弹窗
│   │   │   ├── DashboardModal.vue  # 仪表盘弹窗
│   │   │   ├── BillingModal.vue    # 账单弹窗
│   │   │   ├── InviteModal.vue     # 邀请弹窗
│   │   │   ├── ApiKeyModal.vue     # API Key 弹窗
│   │   │   └── UsageGuideModal.vue # 使用指南
│   │   │
│   │   ├── 📁 composables/         # 组合式函数 (5个)
│   │   │   ├── useAuth.ts          # 认证逻辑
│   │   │   ├── useSummarize.ts     # 总结 SSE 逻辑
│   │   │   ├── useHistorySync.ts   # 云端历史同步
│   │   │   ├── useTheme.ts         # 主题切换
│   │   │   └── useReveal.ts        # 动画效果
│   │   │
│   │   └── 📁 types/               # TypeScript 类型
│   │       └── api.ts              # API 接口类型
│   │
│   ├── Dockerfile                  # 前端 Docker 镜像
│   ├── nginx.conf                  # Nginx 配置
│   └── vite.config.ts              # Vite 配置
│
├── 📁 web_app/                     # FastAPI 后端
│   ├── main.py                     # 核心 API (1857行, 64KB)
│   ├── auth.py                     # 鉴权模块
│   ├── credits.py                  # 积分系统
│   ├── cache.py                    # 缓存模块
│   ├── db.py                       # 数据库抽象层
│   ├── downloader.py               # yt-dlp 视频下载
│   ├── summarizer_gemini.py        # Gemini AI 调用
│   ├── payments.py                 # 支付处理
│   ├── ppt_generator.py            # PPT 生成
│   ├── history_sync_endpoints.py   # 历史同步 API
│   ├── telemetry.py                # 遥测日志
│   └── display.py                  # 显示工具
│
├── 📁 docs/                        # 项目文档 (14个)
│   ├── START_HERE.md               # 入口文档
│   ├── ARCHITECTURE.md             # 系统架构
│   ├── API_CONTRACT.md             # API 契约
│   ├── DATA_MODEL.md               # 数据模型
│   ├── PRODUCT_UI.md               # UI 规范
│   ├── COMMERCIAL.md               # 商业化
│   ├── CONFIGURATION.md            # 配置说明
│   ├── SECURITY_AUTH.md            # 安全认证
│   ├── RUNBOOK.md                  # 运维手册
│   └── ROADMAP.md                  # 路线图
│
├── 📁 scripts/                     # 工具脚本
├── docker-compose.yml              # 生产环境
├── docker-compose.dev.yml          # 开发环境
├── Dockerfile.backend              # 后端镜像
├── requirements.txt                # Python 依赖
└── AGENTS.md                       # 开发约束
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
