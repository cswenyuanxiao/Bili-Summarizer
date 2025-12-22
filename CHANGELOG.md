# 📝 更新日志

本文件记录 Bili-Summarizer 的所有重要更新。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.0.0] - 2024-12-23

### ✨ 新增
- **AI 智能总结**：使用 Google Gemini 2.0 Flash 模型分析视频内容
- **思维导图生成**：自动生成 Mermaid 格式的知识结构图
- **视频转录**：提取字幕或 AI 分析画面生成文本
- **AI 追问功能**：基于视频内容的智能问答
- **视频回放**：点击封面在应用内播放 Bilibili 视频
- **暗色模式**：支持亮色/暗色主题切换
- **本地历史**：自动保存总结历史记录
- **多格式导出**：支持 Markdown、TXT、SVG、PNG

### 🎨 设计
- **"流光智汇"设计系统**：
  - 极光渐变背景（Indigo → Cyan）
  - Glassmorphism 磨砂玻璃效果
  - 微重力交互动效
  - 流体响应式布局（clamp() 无级缩放）
  - 8px 网格间距系统
- **移动端优化**：
  - 触控友好的大按钮
  - 垂直堆叠输入布局
  - 超小屏安全模式（< 360px）

### 🔧 技术
- **后端**：FastAPI + Google Gemini + yt-dlp
- **前端**：Vanilla JS + Mermaid.js + Marked.js + Tailwind CSS
- **部署**：Docker + Railway/Render/Fly.io 支持
- **图片代理**：解决 Bilibili 封面防盗链问题
- **SSE 实时推送**：进度条实时更新

### 📚 文档
- 完整的 README 说明
- DEPLOYMENT.md 云端部署指南
- .env.example 环境变量示例

---

## [0.9.0] - 2024-12-22 (预发布)

### ✨ 新增
- 基础视频总结功能
- 字幕提取模块
- 简单的 Web 界面

### 🔧 修复
- 进度条显示优化（单向递增）
- 视频时长格式化修复

---

## 未来计划

### v1.1
- [ ] 批量视频总结
- [ ] 总结模板自定义
- [ ] PDF 导出
- [ ] 分享卡片生成

### v2.0
- [ ] 用户账号系统
- [ ] 云端历史同步
- [ ] 浏览器插件
- [ ] API 开放

---

[1.0.0]: https://github.com/cswenyuanxiao/Bili-Summarizer/releases/tag/v1.0.0
[0.9.0]: https://github.com/cswenyuanxiao/Bili-Summarizer/releases/tag/v0.9.0
