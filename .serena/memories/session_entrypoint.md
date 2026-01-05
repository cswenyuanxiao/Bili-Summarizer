# 会话入口速览

来源：docs/SESSION_ENTRYPOINT.md

## 必读顺序（只读这些即可）
1. docs/START_HERE.md（项目目标与硬约束）
2. docs/AI_CONTEXT.md（上下文包与同步规则）
3. docs/DEVELOPER_GUIDE.md（架构与模块分工）
4. docs/API_REFERENCE.md（接口与 SSE 协议）
5. docs/CONFIGURATION.md（配置项）

## 功能完成后的必更清单
- 新增/变更 API 或 SSE：更新 docs/API_REFERENCE.md + docs/CHANGELOG.md
- 新增/变更配置项：更新 docs/CONFIGURATION.md + docs/CHANGELOG.md
- 影响部署流程：更新 docs/DEPLOYMENT.md
- 影响工程规范/质量门槛：更新 docs/ENGINEERING_STANDARDS.md
- 影响架构/模块边界：更新 docs/DEVELOPER_GUIDE.md

## 维护规则
- 每完成一个功能/阶段性任务：检查本入口文档“阅读顺序/必更清单”是否仍准确，并同步更新