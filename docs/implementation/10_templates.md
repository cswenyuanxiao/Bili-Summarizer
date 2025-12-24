# 总结模板自定义实施计划

> 优先级: P2 | 预估工作量: 10h | 依赖: 无

---

## 1. 功能概述

用户可自定义 AI 总结的输出格式和重点提取方向，保存为个人模板复用。

### 用户故事

1. 用户在「模板管理」页面创建自定义模板
2. 定义输出格式（段落/列表）、必含章节（要点/金句/行动项）
3. 总结时可选择已保存的模板
4. 系统提供 4 个预设模板供参考

### 预设模板

| 模板 | 章节组成 | 适用场景 |
|------|----------|----------|
| 学习笔记 | 知识点 + 重点标记 + 复习问题 | 教程、课程 |
| 会议纪要 | 议题 + 决议 + 行动项 | 会议录像 |
| 产品分析 | 功能点 + 优劣势 + 竞品对比 | 产品评测 |
| 读书笔记 | 核心观点 + 金句 + 读后感 | 书评、解读 |

---

## 2. 技术方案

### 2.1 数据模型

#### 数据库表: `summary_templates`

```sql
-- 在 init_database 中添加
CREATE TABLE IF NOT EXISTS summary_templates (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    prompt_template TEXT NOT NULL,
    output_format TEXT DEFAULT 'markdown',
    sections TEXT,  -- JSON 数组: ["要点", "金句", "行动项"]
    is_preset BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_templates_user ON summary_templates(user_id);
```

---

### 2.2 后端实现

#### 新增文件: `web_app/templates.py`

```python
"""
总结模板管理服务
"""
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from .db import get_connection

logger = logging.getLogger(__name__)

# 预设模板定义
PRESET_TEMPLATES = [
    {
        "id": "preset_learning",
        "name": "学习笔记",
        "description": "适合教程、课程类视频，提取知识点和复习问题",
        "prompt_template": """请按照以下格式总结视频内容：

## 📚 核心知识点
（列出 3-5 个最重要的知识点，每个用 1-2 句话解释）

## 🔑 重点标记
（用 > 引用标记视频中最关键的表述）

## ❓ 复习问题
（生成 3 个可用于自测的问题）

## 📝 学习总结
（100 字以内的总体评价和学习建议）""",
        "output_format": "markdown",
        "sections": ["核心知识点", "重点标记", "复习问题", "学习总结"],
        "is_preset": True
    },
    {
        "id": "preset_meeting",
        "name": "会议纪要",
        "description": "适合会议录像，提取议题、决议和行动项",
        "prompt_template": """请按照以下格式总结会议内容：

## 📋 会议概要
- 会议主题：
- 主要参与者：
- 时长：

## 💬 讨论议题
（列出本次会议讨论的主要议题）

## ✅ 决议事项
（列出达成共识的决议）

## 🎯 行动项
| 任务 | 负责人 | 截止时间 |
|------|--------|----------|
（如果视频中有提及）

## 📌 待跟进事项
（未解决或需要后续讨论的问题）""",
        "output_format": "markdown",
        "sections": ["会议概要", "讨论议题", "决议事项", "行动项", "待跟进事项"],
        "is_preset": True
    },
    {
        "id": "preset_product",
        "name": "产品分析",
        "description": "适合产品评测、开箱视频",
        "prompt_template": """请按照以下格式分析视频中的产品：

## 🏷️ 产品信息
- 产品名称：
- 品牌/厂商：
- 价格区间：

## ✨ 核心功能
（列出产品的主要功能和特点）

## 👍 优势
（视频中提到的产品优点）

## 👎 不足
（视频中提到的产品缺点或改进空间）

## 🆚 竞品对比
（如有提及其他竞品，列出对比要点）

## 💡 购买建议
（基于视频内容给出购买建议）""",
        "output_format": "markdown",
        "sections": ["产品信息", "核心功能", "优势", "不足", "竞品对比", "购买建议"],
        "is_preset": True
    },
    {
        "id": "preset_reading",
        "name": "读书笔记",
        "description": "适合书评、解读类视频",
        "prompt_template": """请按照以下格式总结这本书/文章的内容：

## 📖 基本信息
- 书名/标题：
- 作者：
- 主题领域：

## 💡 核心观点
（提取 3-5 个核心观点，每个配以简要解释）

## ✨ 金句摘录
（提取视频中引用的精彩句子，用 > 格式）

## 🤔 个人思考
（基于视频内容，提出 2-3 个值得思考的问题）

## 📝 读后感
（100 字以内的总体感悟）""",
        "output_format": "markdown",
        "sections": ["基本信息", "核心观点", "金句摘录", "个人思考", "读后感"],
        "is_preset": True
    }
]


def init_preset_templates():
    """初始化预设模板（如果不存在）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    for template in PRESET_TEMPLATES:
        cursor.execute(
            "SELECT id FROM summary_templates WHERE id = ?",
            (template["id"],)
        )
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO summary_templates 
                (id, user_id, name, description, prompt_template, output_format, sections, is_preset, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template["id"],
                "system",
                template["name"],
                template["description"],
                template["prompt_template"],
                template["output_format"],
                json.dumps(template["sections"]),
                True,
                datetime.utcnow().isoformat()
            ))
    
    conn.commit()
    conn.close()


def get_user_templates(user_id: str, include_presets: bool = True) -> List[Dict[str, Any]]:
    """获取用户的模板列表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if include_presets:
        cursor.execute("""
            SELECT id, name, description, prompt_template, output_format, sections, 
                   is_preset, is_default, created_at
            FROM summary_templates
            WHERE user_id = ? OR is_preset = TRUE
            ORDER BY is_preset DESC, created_at DESC
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT id, name, description, prompt_template, output_format, sections,
                   is_preset, is_default, created_at
            FROM summary_templates
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    templates = []
    for row in rows:
        templates.append({
            "id": row["id"],
            "name": row["name"],
            "description": row["description"],
            "prompt_template": row["prompt_template"],
            "output_format": row["output_format"],
            "sections": json.loads(row["sections"]) if row["sections"] else [],
            "is_preset": bool(row["is_preset"]),
            "is_default": bool(row["is_default"]),
            "created_at": row["created_at"]
        })
    
    return templates


def get_template_by_id(template_id: str) -> Optional[Dict[str, Any]]:
    """根据 ID 获取模板"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, user_id, name, description, prompt_template, output_format, 
               sections, is_preset, is_default, created_at
        FROM summary_templates
        WHERE id = ?
    """, (template_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "name": row["name"],
        "description": row["description"],
        "prompt_template": row["prompt_template"],
        "output_format": row["output_format"],
        "sections": json.loads(row["sections"]) if row["sections"] else [],
        "is_preset": bool(row["is_preset"]),
        "is_default": bool(row["is_default"]),
        "created_at": row["created_at"]
    }


def create_template(
    user_id: str,
    name: str,
    prompt_template: str,
    description: str = "",
    output_format: str = "markdown",
    sections: List[str] = None
) -> Dict[str, Any]:
    """创建用户模板"""
    template_id = f"tmpl_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO summary_templates 
        (id, user_id, name, description, prompt_template, output_format, sections, is_preset, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, FALSE, ?, ?)
    """, (
        template_id,
        user_id,
        name,
        description,
        prompt_template,
        output_format,
        json.dumps(sections or []),
        now,
        now
    ))
    
    conn.commit()
    conn.close()
    
    return {
        "id": template_id,
        "user_id": user_id,
        "name": name,
        "description": description,
        "prompt_template": prompt_template,
        "output_format": output_format,
        "sections": sections or [],
        "is_preset": False,
        "is_default": False,
        "created_at": now
    }


def update_template(
    template_id: str,
    user_id: str,
    **updates
) -> bool:
    """更新用户模板"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 检查权限
    cursor.execute(
        "SELECT is_preset FROM summary_templates WHERE id = ? AND user_id = ?",
        (template_id, user_id)
    )
    row = cursor.fetchone()
    
    if not row or row["is_preset"]:
        conn.close()
        return False
    
    # 构建更新语句
    set_clauses = []
    params = []
    
    for key in ["name", "description", "prompt_template", "output_format"]:
        if key in updates:
            set_clauses.append(f"{key} = ?")
            params.append(updates[key])
    
    if "sections" in updates:
        set_clauses.append("sections = ?")
        params.append(json.dumps(updates["sections"]))
    
    if not set_clauses:
        conn.close()
        return False
    
    set_clauses.append("updated_at = ?")
    params.append(datetime.utcnow().isoformat())
    params.append(template_id)
    
    cursor.execute(
        f"UPDATE summary_templates SET {', '.join(set_clauses)} WHERE id = ?",
        params
    )
    
    conn.commit()
    affected = cursor.rowcount > 0
    conn.close()
    
    return affected


def delete_template(template_id: str, user_id: str) -> bool:
    """删除用户模板"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM summary_templates 
        WHERE id = ? AND user_id = ? AND is_preset = FALSE
    """, (template_id, user_id))
    
    conn.commit()
    affected = cursor.rowcount > 0
    conn.close()
    
    return affected


def set_default_template(template_id: str, user_id: str) -> bool:
    """设置默认模板"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 先清除之前的默认
    cursor.execute(
        "UPDATE summary_templates SET is_default = FALSE WHERE user_id = ?",
        (user_id,)
    )
    
    # 设置新默认
    cursor.execute("""
        UPDATE summary_templates SET is_default = TRUE
        WHERE id = ? AND (user_id = ? OR is_preset = TRUE)
    """, (template_id, user_id))
    
    conn.commit()
    affected = cursor.rowcount > 0
    conn.close()
    
    return affected
```

#### 修改文件: `web_app/main.py`

添加模板 API 端点：

```python
# === 模板管理相关 ===
from .templates import (
    init_preset_templates,
    get_user_templates,
    get_template_by_id,
    create_template,
    update_template,
    delete_template,
    set_default_template
)

# 在 startup 事件中初始化预设模板
@app.on_event("startup")
async def init_templates():
    init_preset_templates()

class CreateTemplateRequest(BaseModel):
    name: str
    prompt_template: str
    description: str = ""
    output_format: str = "markdown"
    sections: List[str] = []

class UpdateTemplateRequest(BaseModel):
    name: Optional[str] = None
    prompt_template: Optional[str] = None
    description: Optional[str] = None
    output_format: Optional[str] = None
    sections: Optional[List[str]] = None

@app.get("/api/templates")
async def list_templates(request: Request, include_presets: bool = True):
    """获取用户的模板列表"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    templates = get_user_templates(user["user_id"], include_presets)
    return {"templates": templates}

@app.get("/api/templates/{template_id}")
async def get_template(template_id: str, request: Request):
    """获取单个模板详情"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    template = get_template_by_id(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # 预设模板对所有人可见，自定义模板只对创建者可见
    if not template["is_preset"] and template["user_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return template

@app.post("/api/templates")
async def create_user_template(request: Request, body: CreateTemplateRequest):
    """创建用户模板"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    if not body.name or not body.prompt_template:
        raise HTTPException(status_code=400, detail="Name and prompt_template are required")
    
    if len(body.prompt_template) > 5000:
        raise HTTPException(status_code=400, detail="Prompt template too long (max 5000 chars)")
    
    template = create_template(
        user_id=user["user_id"],
        name=body.name,
        prompt_template=body.prompt_template,
        description=body.description,
        output_format=body.output_format,
        sections=body.sections
    )
    
    return template

@app.put("/api/templates/{template_id}")
async def update_user_template(template_id: str, request: Request, body: UpdateTemplateRequest):
    """更新用户模板"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    updates = body.dict(exclude_none=True)
    
    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")
    
    success = update_template(template_id, user["user_id"], **updates)
    
    if not success:
        raise HTTPException(status_code=404, detail="Template not found or not editable")
    
    return {"message": "Template updated"}

@app.delete("/api/templates/{template_id}")
async def delete_user_template(template_id: str, request: Request):
    """删除用户模板"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    success = delete_template(template_id, user["user_id"])
    
    if not success:
        raise HTTPException(status_code=404, detail="Template not found or cannot be deleted")
    
    return {"message": "Template deleted"}

@app.post("/api/templates/{template_id}/default")
async def set_default(template_id: str, request: Request):
    """设置默认模板"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    success = set_default_template(template_id, user["user_id"])
    
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {"message": "Default template set"}
```

#### 修改文件: `web_app/summarizer_gemini.py`

在总结函数中支持模板：

```python
def summarize_content(
    file_path: str,
    media_type: str,
    progress_callback=None,
    focus: str = "default",
    uploaded_file=None,
    template_id: str = None  # 新增参数
):
    """
    使用 Gemini 分析内容生成总结
    """
    # 如果指定了模板，获取模板内容
    custom_prompt = None
    if template_id:
        from .templates import get_template_by_id
        template = get_template_by_id(template_id)
        if template:
            custom_prompt = template["prompt_template"]
    
    # 构建 prompt
    if custom_prompt:
        base_prompt = custom_prompt
    else:
        base_prompt = get_default_prompt(focus)
    
    # ... 其余逻辑不变
```

---

### 2.3 前端实现

#### 新增文件: `frontend/src/pages/TemplatesPage.vue`

```vue
<template>
  <div class="templates-page">
    <header class="page-header">
      <h1>模板管理</h1>
      <button class="btn-primary" @click="showCreateModal = true">
        + 创建模板
      </button>
    </header>
    
    <!-- 预设模板 -->
    <section class="templates-section">
      <h2>预设模板</h2>
      <div class="templates-grid">
        <div 
          v-for="template in presetTemplates" 
          :key="template.id"
          class="template-card preset"
          :class="{ active: defaultTemplateId === template.id }"
          @click="selectTemplate(template)"
        >
          <div class="template-icon">📋</div>
          <h3>{{ template.name }}</h3>
          <p>{{ template.description }}</p>
          <div class="template-sections">
            <span v-for="s in template.sections.slice(0, 3)" :key="s">{{ s }}</span>
          </div>
          <button 
            v-if="defaultTemplateId !== template.id"
            class="btn-ghost btn-sm"
            @click.stop="setDefault(template.id)"
          >
            设为默认
          </button>
          <span v-else class="default-badge">默认</span>
        </div>
      </div>
    </section>
    
    <!-- 我的模板 -->
    <section class="templates-section">
      <h2>我的模板</h2>
      <div v-if="userTemplates.length === 0" class="empty-state">
        <p>你还没有创建自定义模板</p>
        <button class="btn-secondary" @click="showCreateModal = true">
          创建第一个模板
        </button>
      </div>
      <div v-else class="templates-grid">
        <div 
          v-for="template in userTemplates" 
          :key="template.id"
          class="template-card"
          :class="{ active: defaultTemplateId === template.id }"
        >
          <h3>{{ template.name }}</h3>
          <p>{{ template.description || '暂无描述' }}</p>
          <div class="template-actions">
            <button class="btn-ghost btn-sm" @click="editTemplate(template)">编辑</button>
            <button class="btn-ghost btn-sm" @click="deleteTemplate(template.id)">删除</button>
            <button 
              v-if="defaultTemplateId !== template.id"
              class="btn-ghost btn-sm"
              @click="setDefault(template.id)"
            >
              设为默认
            </button>
          </div>
        </div>
      </div>
    </section>
    
    <!-- 创建/编辑模态框 -->
    <TemplateEditorModal
      v-if="showCreateModal || editingTemplate"
      :template="editingTemplate"
      @close="closeEditor"
      @saved="handleSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import TemplateEditorModal from '@/components/TemplateEditorModal.vue'

interface Template {
  id: string
  name: string
  description: string
  prompt_template: string
  sections: string[]
  is_preset: boolean
  is_default: boolean
}

const templates = ref<Template[]>([])
const showCreateModal = ref(false)
const editingTemplate = ref<Template | null>(null)

const presetTemplates = computed(() => templates.value.filter(t => t.is_preset))
const userTemplates = computed(() => templates.value.filter(t => !t.is_preset))
const defaultTemplateId = computed(() => templates.value.find(t => t.is_default)?.id)

onMounted(async () => {
  await loadTemplates()
})

async function loadTemplates() {
  try {
    const response = await fetch('/api/templates', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('supabase_token') || ''}`
      }
    })
    const data = await response.json()
    templates.value = data.templates
  } catch (error) {
    console.error('Failed to load templates:', error)
  }
}

function selectTemplate(template: Template) {
  // 可以跳转到总结页面并预选该模板
}

function editTemplate(template: Template) {
  editingTemplate.value = template
}

async function deleteTemplate(id: string) {
  if (!confirm('确定删除该模板？')) return
  
  try {
    await fetch(`/api/templates/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('supabase_token') || ''}`
      }
    })
    await loadTemplates()
  } catch (error) {
    alert('删除失败')
  }
}

async function setDefault(id: string) {
  try {
    await fetch(`/api/templates/${id}/default`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('supabase_token') || ''}`
      }
    })
    await loadTemplates()
  } catch (error) {
    alert('设置失败')
  }
}

function closeEditor() {
  showCreateModal.value = false
  editingTemplate.value = null
}

function handleSaved() {
  closeEditor()
  loadTemplates()
}
</script>
```

#### 新增文件: `frontend/src/components/TemplateEditorModal.vue`

```vue
<template>
  <Teleport to="body">
    <div class="editor-overlay" @click.self="$emit('close')">
      <div class="editor-modal">
        <header>
          <h3>{{ template ? '编辑模板' : '创建模板' }}</h3>
          <button class="close-btn" @click="$emit('close')">×</button>
        </header>
        
        <form @submit.prevent="save">
          <div class="form-group">
            <label>模板名称 *</label>
            <input v-model="form.name" placeholder="例如：技术分享笔记" required />
          </div>
          
          <div class="form-group">
            <label>描述</label>
            <input v-model="form.description" placeholder="简要描述模板用途" />
          </div>
          
          <div class="form-group">
            <label>Prompt 模板 *</label>
            <textarea 
              v-model="form.prompt_template" 
              rows="12"
              placeholder="请按照以下格式总结视频内容：

## 标题
（内容要求）

## 要点
（内容要求）"
              required
            ></textarea>
            <p class="hint">使用 Markdown 格式定义输出结构，AI 将按此格式生成总结</p>
          </div>
          
          <div class="form-group">
            <label>章节标签</label>
            <div class="sections-input">
              <input 
                v-model="newSection" 
                placeholder="输入章节名称后按回车"
                @keyup.enter.prevent="addSection"
              />
              <div class="sections-list">
                <span 
                  v-for="(s, i) in form.sections" 
                  :key="i"
                  class="section-tag"
                >
                  {{ s }}
                  <button type="button" @click="removeSection(i)">×</button>
                </span>
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="$emit('close')">取消</button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'

interface Template {
  id?: string
  name: string
  description: string
  prompt_template: string
  sections: string[]
}

const props = defineProps<{
  template?: Template | null
}>()

const emit = defineEmits(['close', 'saved'])

const form = reactive({
  name: '',
  description: '',
  prompt_template: '',
  sections: [] as string[]
})

const newSection = ref('')
const saving = ref(false)

// 编辑模式时填充表单
watch(() => props.template, (t) => {
  if (t) {
    form.name = t.name
    form.description = t.description
    form.prompt_template = t.prompt_template
    form.sections = [...t.sections]
  }
}, { immediate: true })

function addSection() {
  if (newSection.value.trim()) {
    form.sections.push(newSection.value.trim())
    newSection.value = ''
  }
}

function removeSection(index: number) {
  form.sections.splice(index, 1)
}

async function save() {
  saving.value = true
  
  try {
    const url = props.template?.id 
      ? `/api/templates/${props.template.id}`
      : '/api/templates'
    
    const method = props.template?.id ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('supabase_token') || ''}`
      },
      body: JSON.stringify(form)
    })
    
    if (!response.ok) {
      throw new Error('保存失败')
    }
    
    emit('saved')
  } catch (error) {
    alert('保存失败，请重试')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
/* 样式省略，与其他 Modal 类似 */
</style>
```

---

## 3. 实施步骤清单

| 序号 | 任务 | 文件 | 预估时间 |
|------|------|------|----------|
| 1 | 添加数据库表 | `web_app/main.py` | 30min |
| 2 | 创建 templates.py | `web_app/templates.py` | 2h |
| 3 | 添加 API 端点 | `web_app/main.py` | 1h |
| 4 | 修改 summarizer 支持模板 | `web_app/summarizer_gemini.py` | 1h |
| 5 | 创建 TemplatesPage | `frontend/src/pages/` | 2h |
| 6 | 创建 TemplateEditorModal | `frontend/src/components/` | 1.5h |
| 7 | 添加路由 | `frontend/src/router/` | 15min |
| 8 | 总结页面添加模板选择 | `frontend/src/pages/HomePage.vue` | 1h |
| 9 | 测试 | - | 1h |

---

## 4. 验收标准

- [ ] 4 个预设模板正确显示
- [ ] 可创建/编辑/删除自定义模板
- [ ] 可设置默认模板
- [ ] 总结时可选择模板
- [ ] 使用自定义模板的总结输出格式正确
- [ ] 预设模板不可编辑/删除
