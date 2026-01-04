# 🐛 Bug Report: 思维链 (CoT) 无法显示

**创建时间**: 2026-01-04  
**状态**: 待修复  
**优先级**: High (核心 AI 增强功能失效)

## 1. 问题描述
在前端勾选 "🧠 显示思考过程" 并生成总结后，界面未显示 "AI 分析思路" 面板，但图表生成功能（强制模式下）正常工作。这表明 API 的 `usage` 数据字段传递机制是正常的，问题可能出在 CoT 内容的生成或解析环节。

## 2. 现象分析
- **正常**: 图表生成正常 -> `usage.charts` 数据正确传递到了前端 `HomePage.vue` 并被 `ChartPanel.vue`渲染。
- **异常**: CoT 面板未显示 -> `usage.cot_steps` 为空，或前端组件渲染条件未满足。

## 3. 怀疑原因 (Hypothesis)

### H1: Prompt 注入失效 (后端)
`enable_cot` 参数可能在传递过程中丢失，导致 Prompt 中根本没有加入 `[COT_START]` 相关的指令。
- **检查点**: `web_app/summarizer_gemini.py` 中的 `if enable_cot:` 分支是否被执行。

### H2: 模型输出格式不匹配 (后端)
Gemini 虽然生成了思考过程，但格式与正则表达式不匹配，导致解析失败。
- **当前正则**: `r'### 步骤 (\d+): (.+?)\n\[思考\]: (.+?)(?=\n\n|\n###|\[COT_END\])'`
- **风险点**: 如果模型输出少了一个换行符，或者使用了中文冒号 `：`，正则就会匹配失败，导致 `cot_steps` 为 `None`。

### H3: 解析逻辑异常 (后端)
`summarizer_gemini.py` 中的 `try-except` 块捕获了解析错误并静默处理（只打印了 warning），导致外层只看到了没有 CoT 的结果。

## 4. 排查指南 (Code Review Guide)

请审查以下核心文件：

### 后端逻辑
- **文件**: [`web_app/summarizer_gemini.py`](../../web_app/summarizer_gemini.py)
- **关键函数**: `summarize_content`
- **关注点**:
  1. 第 214 行: `cot_instruction` 是否正确拼接到 `prompt_text`？
  2. 第 325 行: `re.findall` 的正则表达式是否过于严格？建议放宽匹配规则（如兼容中文冒号）。
  3. 第 300 行: 新增的 Debug 日志输出是什么？（查看 `AI 响应前 500 字符`）。

### 前端逻辑
- **文件**: [`frontend/src/pages/HomePage.vue`](../../frontend/src/pages/HomePage.vue)
- **关注点**: `watch(() => result.value.usage)` 是否正确提取了 `cot_steps`。

## 5. 参考文档

在 Debug 过程中，请参考以下文档了解设计意图：

1.  **[docs/cot_design.md](../cot_design.md)**
    - CoT 的设计与提示词规范。

2.  **[docs/API_REFERENCE.md](../API_REFERENCE.md)**
    - 查看 `usage` 字段的 API 契约定义。

3.  **[docs/CHANGELOG.md](../CHANGELOG.md)**
    - 查看 v2.3.0 的变更记录，了解前后端修改范围。

## 6. 建议修复方案

1.  **查看日志**: 检查后端控制台输出的 `AI 响应前 500 字符`，确认模型实际输出的格式。
2.  **优化正则**: 如果模型输出了 CoT 但正则没匹配到，请优化正则。例如：
    ```python
    # 更宽容的正则
    re.findall(r'步骤\s*(\d+)[:：]\s*(.+?)\s*\[思考\][:：]\s*(.+?)(?=\n|\[COT_END\])', cot_content, re.DOTALL)
    ```
3.  **前端兜底**: 即使解析失败，也可以考虑将原始 CoT 文本返回用于调试（如果 `enable_cot` 为真且解析为空）。
