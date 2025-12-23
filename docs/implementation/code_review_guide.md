# 代码审查快速参考指南

## 📋 审查优先级

### ⭐ P0 - 必须审查（安全和核心逻辑）

| 文件 | 行号范围 | 审查要点 | 功能 |
|------|---------|---------|------|
| [`web_app/auth.py`](file:///Users/wenyuan/Desktop/summarizer/web_app/auth.py) | 全文 ~80行 | • API Key vs Token 优先级<br>• 哈希验证逻辑<br>• 错误处理 | 统一鉴权 |
| [`web_app/main.py`](file:///Users/wenyuan/Desktop/summarizer/web_app/main.py) | 50-80 | • 表结构正确性<br>• 索引设计<br>• 迁移安全性 | 数据库初始化 |
| [`web_app/main.py`](file:///Users/wenyuan/Desktop/summarizer/web_app/main.py) | 263-350 | • 密钥生成安全性<br>• 哈希算法<br>• 用户所有权验证 | API Key CRUD |
| [`frontend/src/composables/useHistorySync.ts`](file:///Users/wenyuan/Desktop/summarizer/frontend/src/composables/useHistorySync.ts) | 36-118 | • 去重算法<br>• 冲突解决策略<br>• 数据丢失风险 | 云端同步核心 |

---

### ⚠️ P1 - 建议审查（功能实现）

| 文件 | 行号范围 | 审查要点 | 功能 |
|------|---------|---------|------|
| [`web_app/main.py`](file:///Users/wenyuan/Desktop/summarizer/web_app/main.py) | 628-690 | • 上下文截断逻辑<br>• SSE 格式正确性<br>• 错误处理 | AI Chat 端点 |
| [`web_app/main.py`](file:///Users/wenyuan/Desktop/summarizer/web_app/main.py) | 694-791 | • Supabase 连接<br>• RLS 策略配合<br>• 批量上传性能 | History API |
| [`frontend/src/components/ChatPanel.vue`](file:///Users/wenyuan/Desktop/summarizer/frontend/src/components/ChatPanel.vue) | 95-195 | • SSE 解析逻辑<br>• 消息历史管理<br>• 自动滚动 | AI 聊天 UI |
| [`frontend/src/App.vue`](file:///Users/wenyuan/Desktop/summarizer/frontend/src/App.vue) | 220-231 | • 格式转换正确性<br>• 类型安全 | 历史格式适配 |

---

### ✅ P2 - 可选审查（UI 和集成）

| 文件 | 行号范围 | 审查要点 | 功能 |
|------|---------|---------|------|
| [`frontend/src/components/ApiKeyModal.vue`](file:///Users/wenyuan/Desktop/summarizer/frontend/src/components/ApiKeyModal.vue) | 全文 ~200行 | • 用户体验流程<br>• 错误提示 | API Key UI |
| [`frontend/src/App.vue`](file:///Users/wenyuan/Desktop/summarizer/frontend/src/App.vue) | 143-148 | • Props 传递<br>• 组件显示逻辑 | ChatPanel 集成 |

---

## 🔍 关键审查点

### Phase 8.1: API Key 系统

#### 安全性检查
```python
# web_app/main.py 约270-280行
def create_api_key():
    # ✅ 检查: 使用 secrets.token_urlsafe (CSPRNG)
    raw_key = secrets.token_urlsafe(32)
    
    # ✅ 检查: SHA256 哈希，非明文存储
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    
    # ✅ 检查: 密钥仅返回一次
    return {"key": raw_key}  # 后续不再显示
```

#### 鉴权逻辑检查
```python
# web_app/auth.py 约40-60行
async def get_current_user():
    # ⚠️ 检查: API Key 优先级 > Session Token
    if api_key_header:
        # 验证 API Key
        return await verify_api_key(api_key)
    elif authorization_header:
        # 验证 Supabase Token
        return await verify_supabase_token(token)
```

---

### Phase 10.2: AI 追问功能

#### 上下文管理
```python
# web_app/main.py 约640-650行
# ⚠️ 检查: transcript 截断防止 token 超限
system_prompt = f"""
基于以下视频总结和部分转录内容回答用户问题...
转录内容（节选）: {request.transcript[:5000]}
"""
```

#### SSE 格式
```python
# web_app/main.py 约660-680行
# ✅ 检查: 正确的 SSE 格式
yield f"data: {json.dumps({'content': chunk})}\n\n"
yield f"data: {json.dumps({'done': True})}\n\n"
```

---

### Phase 9.2: 云端历史同步

#### 去重策略
```typescript
// frontend/src/composables/useHistorySync.ts 约65-75行
// ✅ 检查: 唯一键设计合理性
const key = `${item.video_url}|${item.mode}|${item.focus}`

// ⚠️ 审查: 冲突解决逻辑
if (localTime > cloudTime) {
  toUpload.push(item)  // 上传本地版本覆盖云端
}
```

#### 错误降级
```typescript
// frontend/src/composables/useHistorySync.ts 约110-115行
// ✅ 检查: 同步失败时不影响本地功能
catch (error) {
  console.error('Sync failed:', error)
  return getLocalHistory()  // 降级到本地
}
```

---

## 📝 审查检查清单

### 文件完整性检查
- [ ] 所有新增文件都已提交
- [ ] 所有修改文件都已保存
- [ ] 没有遗留的 TODO 或 FIXME

### 代码质量检查
- [ ] 没有硬编码的敏感信息
- [ ] 错误处理覆盖所有关键路径
- [ ] 日志记录适当且不泄露敏感信息
- [ ] TypeScript 类型定义完整

### 安全性检查
- [ ] API Key 使用 SHA256 哈希
- [ ] 用户数据有所有权验证
- [ ] Supabase RLS 策略已启用
- [ ] 没有 SQL 注入风险

### 性能检查
- [ ] 没有 N+1 查询
- [ ] 大数据集有分页或限制
- [ ] 前端没有不必要的重渲染

---

## 🚀 快速审查流程

### 30分钟快速审查
1. **安全审查** (10min): `auth.py` + API Key 哈希逻辑
2. **核心逻辑** (10min): History 同步算法
3. **API 端点** (10min): 错误处理和数据库操作

### 1小时深度审查
1. **P0 文件** (25min): 全部必查文件
2. **P1 文件** (25min): Chat 和 History API
3. **集成测试** (10min): 端到端流程验证

### 完整代码审查
1. **P0** →  **P1** → **P2** 按优先级逐个审查
2. 每个文件都运行 TypeScript/Python 类型检查
3. 手动测试所有用户交互流程

---

## 📚 相关文档

- [三个Phase综合总结](file:///Users/wenyuan/.gemini/antigravity/brain/a105074a-5d5c-4121-bf9d-d3369971a3f1/three_phases_summary.md) - 完整实现细节
- [Phase 8.1 Walkthrough](file:///Users/wenyuan/.gemini/antigravity/brain/a105074a-5d5c-4121-bf9d-d3369971a3f1/phase8_1_walkthrough.md)
- [Phase 10.2 Walkthrough](file:///Users/wenyuan/.gemini/antigravity/brain/a105074a-5d5c-4121-bf9d-d3369971a3f1/phase10_2_walkthrough.md)
- [Phase 9.2 Walkthrough](file:///Users/wenyuan/.gemini/antigravity/brain/a105074a-5d5c-4121-bf9d-d3369971a3f1/phase9_2_walkthrough.md)
- [浏览器测试报告](file:///Users/wenyuan/.gemini/antigravity/brain/a105074a-5d5c-4121-bf9d-d3369971a3f1/browser_test_report.md)
