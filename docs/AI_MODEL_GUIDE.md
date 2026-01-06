# AI 模型配置指南

## 当前使用的模型

**重要**: 本项目使用 **Gemini 3 Flash Preview** (`gemini-3-flash-preview`) 作为 AI 总结模型。

### 模型标识符
```
gemini-3-flash-preview
```

### 完整模型路径
```python
models/gemini-3-flash-preview
```

## 为什么使用 Flash 3.0?

Gemini 3 Flash 是 Google 最新的快速模型，相比 2.0 版本具有：
- ✅ **更强的理解能力**
- ✅ **更准确的总结质量**
- ✅ **更好的中文支持**
- ✅ **保持快速响应**

## 代码中的使用

所有 AI 相关功能均已配置为使用 `gemini-3-flash-preview`：

### 1. 视频总结 (`summarizer_gemini.py`)
```python
model = genai.GenerativeModel(model_name="models/gemini-3-flash-preview")
```

### 2. 追问功能 (`main.py`)
```python
model = genai.GenerativeModel(model_name="models/gemini-3-flash-preview")
```

### 3. 视频对比 (`compare.py`)
```python
model = genai.GenerativeModel("gemini-3-flash-preview")
```

## ⚠️ 重要提醒

**给未来的 AI Agent / 开发者**：

如果需要修改或新增 AI 功能，请确保使用：
```python
genai.GenerativeModel(model_name="models/gemini-3-flash-preview")
```

**不要使用**：
- ❌ `gemini-2.0-flash`（旧版本）
- ❌ `gemini-2.0-flash-exp`（实验版本）
- ❌ `gemini-pro`（已过时）

## API 配置

模型通过 Google AI API 访问，需要配置：

```bash
# .env 文件
GOOGLE_API_KEY=your_api_key_here
```

获取 API Key：https://aistudio.google.com/apikey

## 相关文件

需要修改 AI 模型时，检查以下文件：
- `web_app/summarizer_gemini.py` - 核心总结逻辑
- `web_app/main.py` - 追问和流式响应
- `web_app/compare.py` - 视频对比功能

## 验证模型版本

启动后端后，查看 Google AI Studio 的使用统计：
https://aistudio.google.com/apikey

应该看到 `gemini-3-flash-preview` 的请求记录。
