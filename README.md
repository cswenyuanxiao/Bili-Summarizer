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
| 📱 **流体响应式** | 完美适配从 iPhone SE 到 iPad Pro 的所有设备 |
| 🌙 **暗色模式** | 支持亮色/暗色主题一键切换 |
| 📥 **多格式导出** | Markdown、TXT、SVG、PNG 多格式导出 |
| 🕐 **本地历史** | 自动保存总结历史，随时回顾 |

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

### 方案 1: Docker（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/cswenyuanxiao/Bili-Summarizer.git
cd Bili-Summarizer

# 2. 创建环境变量文件
cp .env.example .env
# 编辑 .env 并填入您的 GOOGLE_API_KEY

# 3. 启动服务
docker-compose up -d

# 4. 访问应用
open http://localhost:7860
```

### 方案 2: 本地开发

```bash
# 1. 安装 Python 依赖
pip install -r requirements.txt

# 2. 安装 FFmpeg（macOS）
brew install ffmpeg

# 3. 配置环境变量
export GOOGLE_API_KEY="你的密钥"

# 4. 启动开发服务器
uvicorn web_app.main:app --reload --port 7860
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

### 更多平台

详见 [DEPLOYMENT.md](./DEPLOYMENT.md) 获取 Railway、Fly.io 部署指南。

---

## 📋 环境变量

| 变量名 | 必填 | 说明 | 获取方式 |
|--------|------|------|----------|
| `GOOGLE_API_KEY` | ✅ | Google Gemini API 密钥 | [Google AI Studio](https://aistudio.google.com/app/apikey) |

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

### 前端
- **Vanilla JavaScript** - 无框架依赖，极致性能
- **Mermaid.js** - 思维导图渲染
- **Marked.js** - Markdown 解析
- **Tailwind CSS** - 工具类 CSS
- **Inter + Noto Sans SC** - 中西文排版字体

### 基础设施
- **Docker** - 容器化部署
- **SSE (Server-Sent Events)** - 实时进度推送

---

## 📂 项目结构

```
bili-summarizer/
├── web_app/
│   ├── main.py              # FastAPI 主应用 & 路由
│   ├── downloader.py        # 视频下载 & 字幕提取
│   ├── summarizer_gemini.py # Gemini AI 总结模块
│   ├── templates/
│   │   └── index.html       # 主页面（含完整 CSS）
│   └── static/
│       └── script.js        # 前端交互逻辑
├── Dockerfile               # Docker 构建配置
├── docker-compose.yml       # Docker Compose 编排
├── requirements.txt         # Python 依赖
├── railway.json             # Railway 部署配置
├── render.yaml              # Render 部署配置
├── fly.toml                 # Fly.io 部署配置
├── deploy.sh                # 快速部署脚本
├── DEPLOYMENT.md            # 部署完整指南
├── CHANGELOG.md             # 版本更新日志
└── README.md                # 本文件
```

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

### v1.1 🔜 即将推出
- [ ] 批量视频总结
- [ ] 总结模板自定义
- [ ] 导出为 PDF
- [ ] 分享卡片生成

### v2.0 📋 规划中
- [ ] 用户账号系统
- [ ] 云端历史同步
- [ ] 浏览器插件
- [ ] API 开放

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
