# ✨ Bili-Summarizer

> **AI 视频总结助手** — 一键获取 Bilibili 视频的智能总结、思维导图和完整转录

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

![Preview](https://img.shields.io/badge/Design-Luminous%20Flow-4f46e5?style=for-the-badge)

---

## 🎬 产品预览

<div align="center">
  <img src="https://via.placeholder.com/800x450/4f46e5/ffffff?text=Bili-Summarizer+Preview" alt="产品预览" width="100%">
</div>

---

## ✨ 核心功能

| 功能 | 描述 |
|------|------|
| 🤖 **AI 智能总结** | 使用 Google Gemini 2.0 Flash 模型深度分析视频内容 |
| 🧠 **思维导图** | 自动生成 Mermaid 格式的知识结构图，可导出 SVG/PNG |
| 📜 **完整转录** | 提取视频字幕，或通过 AI 分析画面生成转录 |
| 💬 **AI 追问** | 基于视频内容的智能问答，深入挖掘细节 |
| 🎬 **视频回放** | 点击封面即可在应用内观看 Bilibili 原视频 |
| ♻️ **重新总结** | 一键强制重算总结，跳过缓存 |
| 📊 **仪表盘** | 查看积分、使用次数与账号概况 |
| 📱 **流体响应式** | 完美适配从 iPhone SE 到 iPad Pro 的所有设备 |
| 🌙 **暗色模式** | 支持亮色/暗色主题一键切换 |
| 📥 **多格式导出** | Markdown、TXT、PDF、SVG、PNG 多格式导出 |
| 🕐 **本地历史** | 自动保存总结历史，随时回顾 |

### v2.0 新增功能

| 功能 | 描述 |
|------|------|
| 🎨 **分享卡片** | 4 种精美模板，一键生成社交分享图片 |
| 📂 **收藏夹导入** | 解析 B 站收藏夹 URL，批量导入视频总结 |
| 📝 **自定义模板** | 预设学习/会议/产品模板，支持完全自定义 Prompt |
| 🔊 **语音播报** | Edge TTS 集成，6 种中文语音，随时听总结 |
| 🔔 **每日推送** | 订阅 UP 主，新视频自动推送浏览器/邮件通知 |
| ⚖️ **总结对比** | 2-4 视频 AI 深度对比，提炼差异与共识 |
| 👥 **团队协作** | 创建团队、共享总结、评论讨论 |

---


## 🎨 设计系统

本项目采用 **"流光智汇 (Luminous Flow)"** 设计语言：

- **极光渐变**：Indigo → Cyan 的智能渐变背景
- **磨砂玻璃**：Glassmorphism 半透明卡片效果
- **微重力交互**：按钮悬浮、点击下沉的 3D 反馈
- **流体排版**：使用 `clamp()` 实现字体和间距的无级缩放
- **8px 网格**：严格遵循设计规范的间距系统

**色彩体系**：
```css
--primary: #4f46e5;    /* Indigo 600 */
--bg: #f8fafc;         /* Slate 50 */
--text-main: #0f172a;  /* Slate 900 */
```

---

## 🚀 快速开始

### 方案 1: Docker Compose（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/cswenyuanxiao/Bili-Summarizer.git
cd Bili-Summarizer

# 2. 创建环境变量文件
cp .env.example .env
# 编辑 .env 并填入您的 GOOGLE_API_KEY

# 3. 启动前后端服务
docker-compose up -d

# 4. 访问应用
open http://localhost


# 5.更新docker
docker-compose up -d --build
```


> 💡 Docker Compose 会自动启动前端 (Nginx) 和后端 (FastAPI) 两个容器

### 方案 2: 本地开发

```bash
# 终端 1: 启动后端
pip install -r requirements.txt
brew install ffmpeg  # macOS
export GOOGLE_API_KEY="你的密钥"
uvicorn web_app.main:app --reload --port 7860

# 终端 2: 启动前端
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

### 方案 3: 临时分享（Localtunnel）

```bash
# 启动应用后，运行以下命令生成公网链接
npx localtunnel --port 7860
```

---

## ☁️ 云端部署

### Render（推荐，完全免费）

1. Fork 本仓库到您的 GitHub
2. 访问 [Render Dashboard](https://dashboard.render.com/)
3. 点击 **New** → **Web Service**
4. 连接 GitHub 仓库
5. 添加环境变量 `GOOGLE_API_KEY`
6. 等待自动部署完成

> ⚠️ 免费版 15 分钟无活动会休眠，首次访问需等待 30-50 秒唤醒
> ⚠️ Render 免费实例不支持持久化磁盘，生产环境建议使用外部 Postgres（如 Supabase/Neon），配置 `DATABASE_URL` 以持久化积分与订单数据。

### 更多平台

详见 [DEPLOYMENT.md](./DEPLOYMENT.md) 获取 Railway、Fly.io 部署指南。

---

## 📋 环境变量

| 变量名 | 必填 | 说明 | 获取方式 |
|--------|------|------|----------|
| `GOOGLE_API_KEY` | ✅ | Google Gemini API 密钥 | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `DATABASE_URL` | ❌ | 外部 Postgres 连接字符串（生产建议配置） | Supabase/Neon 控制台 |
| `PG_POOL_MIN` | ❌ | Postgres 连接池最小连接数 | 默认 1 |
| `PG_POOL_MAX` | ❌ | Postgres 连接池最大连接数 | 默认 5 |
| `DEBUG_API` | ❌ | 调试接口开关（1=开启） | 生产默认关闭 |
| `PAYMENT_MOCK` | ❌ | 支付 Mock 开关（1=开启） | 默认关闭 |

---

## 🎯 使用方法

### 1. 输入视频链接

支持以下格式：
```
https://www.bilibili.com/video/BV1xx411c7mD
https://b23.tv/xxxxxx
```

### 2. 选择分析模式

| 模式 | 适用场景 |
|------|----------|
| **智能模式** | 优先使用字幕，速度快，推荐日常使用 |
| **视频模式** | AI 分析画面，适合无字幕或需要深度分析 |

### 3. 选择分析视角

| 视角 | 描述 |
|------|------|
| 🎯 综合总结 | 全面客观的内容概述 |
| 📚 深度学习 | 提取知识点、要点清单 |
| 😄 趣味互动 | 轻松幽默的表达风格 |
| 💼 商业洞察 | 商业模式、市场分析 |

### 4. 查看结果

- **📝 智能总结**：结构化的视频内容摘要
- **🧠 思维导图**：可视化的知识结构
- **📜 视频转录**：完整的文字内容
- **🎬 视频播放**：点击封面在线观看
- **💬 AI 追问**：深入探讨特定话题

---

## 🛠️ 技术栈

### 后端
- **FastAPI** - 高性能异步 Web 框架
- **Google Gemini 2.0 Flash** - 最新 AI 模型
- **yt-dlp** - 视频信息提取
- **httpx** - 现代 HTTP 客户端
- **Python 3.10** - 运行环境

### 前端
- **Vue 3** - 渐进式前端框架 (Composition API)
- **Vite** - 极速构建工具
- **TypeScript** - 类型安全
- **Tailwind CSS** - 工具类 CSS (Build 版)
- **Pinia** - 轻量级状态管理
- **Mermaid.js** - 思维导图渲染
- **Marked.js** - Markdown 解析
- **html2pdf.js** - 前端 PDF 导出

### 基础设施
- **Docker Compose** - 容器编排
- **Nginx** - 反向代理 + 静态文件服务
- **SSE (Server-Sent Events)** - 实时进度推送

---

## 📂 项目结构

```
bili-summarizer/
├── frontend/                    # Vue 3 前端应用
│   ├── src/
│   │   ├── App.vue              # 主应用组件（总结核心逻辑）
│   │   ├── AppShell.vue         # 路由壳组件（导航/弹窗）
│   ├── main.ts              # 应用入口
│   │   ├── supabase.ts          # Supabase 客户端配置
│   │   ├── router/              # Vue Router (11 条路由)
│   │   ├── pages/               # 路由页面 (11 个)
│   │   ├── components/          # UI 组件 (20+ 个)
│   │   ├── composables/         # 组合式函数 (5 个)
│   │   ├── styles/              # 样式系统 (shadows/animations/polish)
│   │   ├── data/                # 静态数据 (apiDocs.ts)
│   │   └── types/               # TypeScript 类型定义
│   ├── Dockerfile               # 前端镜像（Node + Nginx）
│   ├── nginx.conf               # Nginx 反向代理配置
│   └── vite.config.ts           # Vite 构建配置
│
├── web_app/                     # FastAPI 后端
│   ├── main.py                  # API 路由入口 (2200+ 行)
│   ├── auth.py                  # 鉴权模块（API Key/JWT）
│   ├── credits.py               # 积分系统
│   ├── cache.py                 # 缓存模块
│   ├── db.py                    # 数据库抽象层（SQLite/PG）
│   ├── downloader.py            # yt-dlp 视频下载
│   ├── summarizer_gemini.py     # Gemini AI 总结
│   ├── payments.py              # 支付全链路处理
│   ├── idempotency.py           # 幂等性管理器
│   ├── reconciliation.py        # 对账服务
│   ├── batch_summarize.py       # 批量总结服务
│   ├── queue_manager.py         # 任务队列管理
│   ├── rate_limiter.py          # 请求限流
│   ├── ppt_generator.py         # PPT 生成
│   └── telemetry.py             # 遥测与错误记录
│
├── docs/                        # 项目文档 (14 个)
│   ├── START_HERE.md            # 入口文档（10 条硬约束）
│   ├── ARCHITECTURE.md          # 系统架构
│   ├── API_CONTRACT.md          # API 契约（SSE 事件协议）
│   ├── DATA_MODEL.md            # 数据模型
│   ├── PRODUCT_UI.md            # UI/UX 规范
│   ├── COMMERCIAL.md            # 定价与支付
│   └── CONFIGURATION.md         # 环境变量配置
│
├── scripts/                     # 工具脚本
├── Dockerfile.backend           # 后端镜像
├── docker-compose.yml           # 生产环境编排
├── docker-compose.dev.yml       # 开发环境配置
├── requirements.txt             # Python 依赖
├── AGENTS.md                    # 开发硬约束（UI/路由/交互）
└── DEPLOYMENT.md                # 部署完整指南
```

### 核心模块职责

| 模块 | 职责 |
|------|------|
| `main.py` | API 路由、SSE 总结流程、支付/订阅/API Key 管理 |
| `auth.py` | 统一鉴权（x-api-key 优先，Bearer Token 其次） |
| `credits.py` | 积分扣减/充值、首次总结奖励 |
| `cache.py` | 缓存命中检查、结果持久化 |
| `summarizer_gemini.py` | Gemini 文件上传、AI 分析、思维导图生成 |
| `downloader.py` | yt-dlp 字幕/视频下载、格式转换 |

## 📎 维护上下文

新开会话入口：`docs/START_HERE.md`。

---

## 🧭 系统分析与流程图

系统流程与数据路径见：`docs/ARCHITECTURE.md`。

---

## 🧩 项目上下文

文档索引：`docs/README.md`。

---

## 🐛 常见问题

<details>
<summary><strong>Q: 视频下载失败（403 错误）</strong></summary>

B 站可能限制了您的 IP，尝试：
1. 使用代理（在 `downloader.py` 中配置 `proxy`）
2. 降低请求频率
3. 切换网络环境
</details>

<details>
<summary><strong>Q: 封面图片加载失败</strong></summary>

已实现后端图片代理，如仍失败请检查：
1. 网络连接是否正常
2. B 站是否可访问
</details>

<details>
<summary><strong>Q: 账号功能不可用</strong></summary>

请确认已配置 `VITE_SUPABASE_URL` 与 `VITE_SUPABASE_ANON_KEY`。未配置时登录/订阅/API Key 会被禁用。
</details>

<details>
<summary><strong>Q: AI 分析超时</strong></summary>

1. 使用字幕模式（更快）
2. 检查 Gemini API 密钥配额
3. 视频过长可尝试分段处理
</details>

<details>
<summary><strong>Q: 云端部署后爬取失败</strong></summary>

云服务器 IP 可能被限制：
1. 考虑使用代理池
2. 联系云服务商更换 IP
3. 本地运行 + Localtunnel 分享
</details>

---

## 🗺️ 开发路线图

### v1.0 ✅ 已完成
- [x] 核心总结功能
- [x] 思维导图生成
- [x] 视频播放集成
- [x] 暗色模式
- [x] 响应式设计
- [x] 云端部署支持

### v1.1 ✅ 已完成 (2024-12-24)
- [x] 完整 API 文档 (`/api-docs`)
- [x] 服务条款页面 (`/terms`)
- [x] 隐私政策页面 (`/privacy`)
- [x] 用户反馈功能 (浮动按钮 + 表单)
- [x] UI/UX 优化 (阴影系统 + 动画统一)
- [x] 单元测试框架 (Vitest)
- [x] 页面内容丰富 (Product/Pricing/Docs)

### v1.2 ✅ 已完成 (2025-12-25)
- [x] 订阅与支付全链路（支付宝/微信）
- [x] 支付回调幂等处理
- [x] 订单/账单/积分一致性对账
- [x] 批量视频总结 (最多 20 个/批次)
- [x] PDF 导出稳定性优化
- [x] 任务队列与 Worker 架构
- [x] 请求限流机制

### v2.0 ✅ 已完成 (2025-12-25)
- [x] **分享卡片生成** - 4 种精美模板，一键下载分享
- [x] **收藏夹导入** - 解析 B 站收藏夹，批量导入视频
- [x] **总结模板自定义** - 预设模板 + 完全自定义 Prompt
- [x] **语音播报 (TTS)** - Edge TTS 集成，6 种中文语音
- [x] **每日总结推送** - UP 主订阅，新视频自动浏览器/邮件推送
- [x] **总结对比** - 2-4 视频 AI 深度对比分析
- [x] **团队协作** - 团队创建、内容共享、评论系统

### v2.1 ✅ 已上线 (Foundation)
- [x] **API 开放平台** - 支持 API Key 管理、用量统计与接口文档
- [x] **多语言支持 (i18n)** - 支持中英切换，已集成 vue-i18n

### v2.2+ 📋 规划中
- [ ] 浏览器插件
- [ ] 移动端 PWA


---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 开源协议

本项目采用 [MIT 协议](./LICENSE)

---

## 🙏 致谢

- [Google Gemini](https://ai.google.dev/) - AI 模型
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 视频下载
- [Mermaid](https://mermaid.js.org/) - 思维导图
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架
- [Tailwind CSS](https://tailwindcss.com/) - CSS 框架

---

<div align="center">
  <strong>⭐ 如果这个项目对您有帮助，请给个 Star！</strong>
  <br><br>
  Made with ❤️ by <a href="https://github.com/cswenyuanxiao">cswenyuanxiao</a>
</div>
