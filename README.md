# Bili-Summarizer (B站视频总结助手)

Bili-Summarizer 是一个旨在帮助用户快速获取 Bilibili 视频核心内容的自动化工具。用户只需提供一个 Bilibili 视频链接，该工具即可自动完成视频下载、上传至 Google AI Studio 进行分析，并最终生成一份简洁、准确的视频内容摘要文本。

---

## 需求文档 (Product Requirements Document)

**1. 核心功能 (Features)**
*   **视频链接输入:** 支持用户输入标准的 Bilibili 视频链接。
*   **自动视频下载:** 工具后台自动将原始视频文件保存到本地。
*   **调用 AI 总结:** 自动将下载好的视频通过 Google AI Studio (Gemini API) 请求视频内容总结服务。
*   **文本摘要输出:** 在终端清晰地展示由 AI 生成的视频摘要。
*   **状态反馈:** 在处理过程中向用户提供明确的状态提示。

**2. 用户流程 (User Flow)**
1.  用户通过命令行启动 Bili-Summarizer。
2.  根据提示，输入一个 Bilibili 视频的 URL。
3.  应用界面显示“正在下载视频...”。
4.  下载完成后，界面显示“正在上传并分析视频...”。
5.  分析完成后，界面显示最终的视频内容摘要。

**3. 输入与输出 (Input & Output)**
*   **输入:** 一个有效的 Bilibili 视频 URL。
*   **输出:** 一段格式化好的视频摘要文本。

---

## 技术文档 (Technical Specification)

**1. 系统架构 (System Architecture)**
本工具将采用模块化的单体应用架构，主要由一个主程序（Orchestrator）调度三个核心模块完成任务。

`用户 -> CLI -> 主程序 (main.py)`
    `-> 1. 下载模块 (downloader.py)`
    `-> 2. AI总结模块 (summarizer_gemini.py)`
    `-> 3. 输出模块 (display.py)`

**2. 技术选型 (Technology Stack)**
*   **编程语言:** Python 3
*   **视频下载:** `yt-dlp`
*   **API 交互:** `google-generativeai` (Google官方Python SDK)
*   **依赖管理:** `requirements.txt`
*   **AI 服务:** Google AI Studio (Gemini 2.5 Pro / Flash API)

**3. 核心组件**
*   **`main.py`**: 主程序，负责调度和流程控制。
*   **`downloader.py`**: 下载模块，负责调用 `yt-dlp` 下载视频。
*   **`summarizer_gemini.py`**: AI总结模块，负责与 Gemini API 交互。
*   **`display.py`**: 输出模块，负责在终端格式化并显示文本。
*   **`.env`**: 配置文件，用于存储 `GOOGLE_API_KEY`。

---

## 如何获得在线访问链接 (部署到云端)

目前的程序运行在您的本地电脑（Localhost）。如果您想获得一个像 `https://your-app.railway.app` 这样可以直接打开的链接，通常需要将其部署到“云服务器”上。

### 推荐部署方案：Railway.app (最快最简单)
Railway 是一个支持 FastAPI 的云平台，自动处理 HTTPS 和域名。

1.  **准备代码**：将代码上传到您的 **GitHub** 私有仓库。
2.  **关联 Railway**：
    *   登录 [Railway.app](https://railway.app/)。
    *   点击 **New Project** -> **Deploy from GitHub repo**，选择您的仓库。
3.  **配置环境变量**：
    *   在 Railway 的项目设置中找到 **Variables**。
    *   添加 `GOOGLE_API_KEY`（必填）。
4.  **开启公开访问**：
    *   在 **Settings** -> **Networking** 中点击 **Generate Domain**。
    *   您将获得一个以 `.up.railway.app` 结尾的 **公开链接**。

### 为什么需要这样做？
*   **24/7 在线**：云服务器不会断电，任何人随时可以访问。
*   **固定链接**：提供一个全球可访问的 HTTPS 网址，而不仅仅是本地的 `127.0.0.1`。
*   **环境一致性**：我已经为您创建了 `Dockerfile`，它会告诉云服务器如何安装 `ffmpeg` 等视频处理所需的组件。

