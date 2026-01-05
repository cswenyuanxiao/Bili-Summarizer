# 新对话起始句模板

> 目的：让新对话先读 serena 记忆，再按需补读文档，避免全量扫描。

## 推荐起始句（复制即用）

```
请先读取 serena 记忆：session_entrypoint、ai_context_pack、start_here_summary、developer_guide_summary、api_reference_core、configuration_reference。 
然后用表格给我：1) 你理解的项目目标（3 行内）2) 你认为的关键模块与入口文件 3) 可能的风险/冲突点。
若记忆与文档冲突，请只回读最小必要文档并标出冲突来源。
```

## 可选补充句（按需追加）

- “本次任务与 API 相关，请回读 docs/API_REFERENCE.md 的相关段落。”
- “本次任务与配置/部署相关，请回读 docs/CONFIGURATION.md 或 docs/DEPLOYMENT.md 的相关段落。”
