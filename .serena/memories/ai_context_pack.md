# AI_CONTEXT 速记

来源：docs/AI_CONTEXT.md

## 必读顺序（优先级）
1. docs/START_HERE.md
2. docs/DEVELOPER_GUIDE.md
3. docs/API_REFERENCE.md
4. docs/ENGINEERING_STANDARDS.md
5. docs/CONFIGURATION.md
6. docs/DEPLOYMENT.md
7. docs/CHANGELOG.md

## 变更后必须同步的文档
- 改 API/SSE：docs/API_REFERENCE.md + docs/CHANGELOG.md
- 改配置项：docs/CONFIGURATION.md + docs/CHANGELOG.md
- 改部署流程：docs/DEPLOYMENT.md
- 改架构/模块边界：docs/DEVELOPER_GUIDE.md
- 改工程规范：docs/ENGINEERING_STANDARDS.md

## 统一术语
- 思维导图：Markdown 无序列表 + Markmap 渲染
- CoT：Chain of Thought（思维链）
- SSE：Server-Sent Events（流式推送）
- 总结：summary
- 转录：transcript
- 思维导图面板：mindmap panel

## 文档治理
- Tier A 只允许一个“文档整合者”落盘
- 其他协作者只给补丁建议
- docs/memo/ 可并行草稿，合并后再升级