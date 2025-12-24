# 外部依赖与工具文档

> 本文档列出项目所使用的所有外部 API、SDK 和第三方库，以及它们的官方文档链接，供开发时参考。

---

## 🤖 AI 与机器学习

### Google Gemini API
**用途**：视频/音频内容分析、转录提取、智能总结生成

| 资源 | 链接 |
|------|------|
| 官方文档 | https://ai.google.dev/docs |
| Python SDK | https://ai.google.dev/gemini-api/docs/quickstart?lang=python |
| API 参考 | https://ai.google.dev/api/python/google/generativeai |
| 定价 | https://ai.google.dev/pricing |
| 模型列表 | https://ai.google.dev/gemini-api/docs/models/gemini |

**项目中使用**：`web_app/summarizer_gemini.py`

---

## 🔐 身份认证与数据库

### Supabase
**用途**：用户认证、PostgreSQL 数据库、实时订阅

| 资源 | 链接 |
|------|------|
| 官方文档 | https://supabase.com/docs |
| Python SDK | https://supabase.com/docs/reference/python/introduction |
| JavaScript SDK | https://supabase.com/docs/reference/javascript/introduction |
| Auth 文档 | https://supabase.com/docs/guides/auth |
| Row Level Security | https://supabase.com/docs/guides/auth/row-level-security |
| Dashboard | https://app.supabase.com |

**项目中使用**：
- 后端：`web_app/auth.py`, `web_app/db.py`
- 前端：`frontend/src/supabase.ts`

---

## 📹 视频处理

### yt-dlp
**用途**：从 Bilibili、YouTube 等平台下载视频、音频和字幕

| 资源 | 链接 |
|------|------|
| GitHub | https://github.com/yt-dlp/yt-dlp |
| 文档 | https://github.com/yt-dlp/yt-dlp#readme |
| 支持的站点 | https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md |
| 选项参考 | https://github.com/yt-dlp/yt-dlp#usage-and-options |

**项目中使用**：`web_app/downloader.py`

---

## 💳 支付集成

### 支付宝 SDK
**用途**：支付宝扫码支付、订单管理

| 资源 | 链接 |
|------|------|
| 开放平台 | https://open.alipay.com |
| Python SDK | https://github.com/fzlee/alipay |
| 当面付文档 | https://opendocs.alipay.com/open/194/105072 |
| 沙箱环境 | https://opendocs.alipay.com/common/02kkv7 |

**项目中使用**：`web_app/payments.py`

### 微信支付
**用途**：微信扫码支付（Native 支付）

| 资源 | 链接 |
|------|------|
| 开发者文档 | https://pay.weixin.qq.com/wiki/doc/apiv3/index.shtml |
| Native 支付 | https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_4_1.shtml |
| Python SDK | https://github.com/wechatpay-apiv3/wechatpay-python |

**项目中使用**：`web_app/payments.py`

---

## 🖼️ 前端库

### Vue 3 生态

| 库 | 用途 | 文档链接 |
|-----|------|----------|
| Vue 3 | 前端框架 | https://vuejs.org/guide/introduction.html |
| Vue Router | 路由管理 | https://router.vuejs.org/ |
| Pinia | 状态管理 | https://pinia.vuejs.org/ |
| VueUse | 实用组合式函数 | https://vueuse.org/ |
| Vue I18n | 国际化 | https://vue-i18n.intlify.dev/ |

### UI 与样式

| 库 | 用途 | 文档链接 |
|-----|------|----------|
| Tailwind CSS | 原子化 CSS | https://tailwindcss.com/docs |
| Mermaid | 图表渲染 | https://mermaid.js.org/intro/ |
| html2pdf.js | PDF 导出 | https://ekoopmans.github.io/html2pdf.js/ |
| Marked | Markdown 解析 | https://marked.js.org/ |

### 开发工具

| 工具 | 用途 | 文档链接 |
|-----|------|----------|
| Vite | 构建工具 | https://vitejs.dev/guide/ |
| TypeScript | 类型系统 | https://www.typescriptlang.org/docs/ |
| Vitest | 单元测试 | https://vitest.dev/guide/ |
| Playwright | E2E 测试 | https://playwright.dev/docs/intro |

---

## 🐍 后端库

### Web 框架

| 库 | 用途 | 文档链接 |
|-----|------|----------|
| FastAPI | Web 框架 | https://fastapi.tiangolo.com/ |
| Uvicorn | ASGI 服务器 | https://www.uvicorn.org/ |
| Gunicorn | 生产部署 | https://docs.gunicorn.org/ |

### 数据与文档

| 库 | 用途 | 文档链接 |
|-----|------|----------|
| python-pptx | PPT 生成 | https://python-pptx.readthedocs.io/ |
| ReportLab | PDF 生成 | https://www.reportlab.com/docs/reportlab-userguide.pdf |
| Pillow | 图像处理 | https://pillow.readthedocs.io/ |
| qrcode | 二维码生成 | https://github.com/lincolnloop/python-qrcode |

### 数据库

| 库 | 用途 | 文档链接 |
|-----|------|----------|
| psycopg2 | PostgreSQL 驱动 | https://www.psycopg.org/docs/ |
| SQLite | 本地开发数据库 | https://www.sqlite.org/docs.html |

---

## ☁️ 部署与基础设施

### Render
**用途**：应用托管、自动部署

| 资源 | 链接 |
|------|------|
| 官方文档 | https://render.com/docs |
| Web Services | https://render.com/docs/web-services |
| 环境变量 | https://render.com/docs/environment-variables |

### Docker
**用途**：本地开发、容器化部署

| 资源 | 链接 |
|------|------|
| 官方文档 | https://docs.docker.com/ |
| Compose | https://docs.docker.com/compose/ |
| 最佳实践 | https://docs.docker.com/develop/dev-best-practices/ |

---

## 📝 使用指南

### 查阅文档时机

1. **添加新功能前**：查阅相关 SDK 的最新 API
2. **遇到错误时**：检查官方文档的 Troubleshooting 部分
3. **升级依赖时**：查看 Changelog 和迁移指南
4. **性能优化时**：参考官方最佳实践

### 版本管理

- 后端依赖版本：`requirements.txt`
- 前端依赖版本：`frontend/package.json`
- 建议定期检查依赖的安全更新

---

## 🔄 更新记录

| 日期 | 更新内容 |
|------|----------|
| 2025-12-25 | 初始版本，整理所有外部依赖文档链接 |
