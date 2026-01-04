---
status: stable
owner: Core Eng
last_reviewed: 2026-01-05
applies_to: main
---

# AI Context Pack

本文件是 AI/IDE/CLI 的统一入口，所有模型必须先读完本文件再读其他文档。

## 必读清单（按优先级）
1. `docs/START_HERE.md`
2. `docs/DEVELOPER_GUIDE.md`
3. `docs/API_REFERENCE.md`
4. `docs/ENGINEERING_STANDARDS.md`
5. `docs/CONFIGURATION.md`
6. `docs/DEPLOYMENT.md`
7. `docs/CHANGELOG.md`

## 变更后必须同步的文档
- 改 API/SSE：`docs/API_REFERENCE.md` + `docs/CHANGELOG.md`
- 改配置项：`docs/CONFIGURATION.md` + `docs/CHANGELOG.md`
- 改部署流程：`docs/DEPLOYMENT.md`
- 改架构/模块边界：`docs/DEVELOPER_GUIDE.md`
- 改工程规范：`docs/ENGINEERING_STANDARDS.md`

## 术语表（统一用词）
- 思维导图：Markdown 无序列表 + Markmap 渲染
- CoT：Chain of Thought（思维链）
- SSE：Server-Sent Events（流式推送）
- 总结：summary
- 转录：transcript
- 思维导图面板：mindmap panel

## 文档写入协议
1. Tier A 文档只允许一个“文档整合者”落盘。
2. 其他协作者只给补丁建议，不直接改 Tier A。
3. `docs/memo/` 允许并行草稿，合并后再升级为 Tier A/B。
