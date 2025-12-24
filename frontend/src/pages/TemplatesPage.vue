<template>
  <div class="templates-page container mx-auto max-w-5xl px-4 py-8">
    <header class="page-header flex justify-between items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">总结模板</h1>
        <p class="text-sm text-gray-500 mt-1">自定义 AI 总结的结构与关注重点</p>
      </div>
      <button class="btn-primary flex items-center gap-2" @click="openCreateModal">
        <span>+</span> 新建模板
      </button>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="tmpl in templates" 
        :key="tmpl.id" 
        class="template-card glass-card hover-elevate p-6 flex flex-col"
      >
        <div class="flex justify-between items-start mb-4">
          <span 
            class="px-2 py-0.5 rounded text-[10px] font-bold"
            :class="tmpl.is_preset ? 'bg-blue-100 text-blue-600' : 'bg-purple-100 text-purple-600'"
          >
            {{ tmpl.is_preset ? '预设' : '自定义' }}
          </span>
          <div v-if="!tmpl.is_preset" class="actions flex gap-2">
            <button class="icon-btn" @click="editTemplate(tmpl)">✎</button>
            <button class="icon-btn text-red-500" @click="deleteTmpl(tmpl.id)">🗑</button>
          </div>
        </div>
        
        <h3 class="font-bold text-lg mb-2">{{ tmpl.name }}</h3>
        <p class="text-sm text-gray-500 flex-1 mb-4">{{ tmpl.description }}</p>
        
        <div class="template-footer pt-4 border-t border-gray-100 dark:border-gray-800">
          <button class="w-full py-2 bg-gray-50 dark:bg-gray-800 rounded-lg text-xs font-semibold hover:bg-gray-100 transition-colors" @click="showPreview(tmpl)">
            预览 Prompt
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑/新建弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content max-w-2xl w-full">
        <header class="modal-header">
          <h3>{{ editingId ? '编辑模板' : '创建新模板' }}</h3>
          <button class="close-btn" @click="showModal = false">×</button>
        </header>
        <div class="modal-body space-y-4">
          <div class="form-group">
            <label>模板名称</label>
            <input v-model="form.name" type="text" placeholder="例如：深度学习路线" />
          </div>
          <div class="form-group">
            <label>简单描述</label>
            <input v-model="form.description" type="text" placeholder="描述该模板的适用场景" />
          </div>
          <div class="form-group">
            <label>Prompt 模板</label>
            <textarea 
              v-model="form.prompt_template" 
              rows="8" 
              placeholder="请输入你希望 AI 遵循的总结指令..."
            ></textarea>
            <p class="hint">提示：这里定义的文字将作为 AI 总结的核心指令。</p>
          </div>
          <div class="actions flex justify-end gap-3 pt-4">
            <button class="btn-ghost" @click="showModal = false">取消</button>
            <button class="btn-primary" @click="saveTemplate" :disabled="saving">
              {{ saving ? '保存中...' : '确定保存' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 预览弹窗 -->
    <div v-if="previewTmpl" class="modal-overlay" @click.self="previewTmpl = null">
      <div class="modal-content max-w-xl w-full">
        <header class="modal-header">
          <h3>Prompt 预览: {{ previewTmpl.name }}</h3>
          <button class="close-btn" @click="previewTmpl = null">×</button>
        </header>
        <div class="modal-body">
          <pre class="prompt-preview">{{ previewTmpl.prompt_template }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'

const templates = ref<any[]>([])
const showModal = ref(false)
const previewTmpl = ref<any>(null)
const editingId = ref<string | null>(null)
const saving = ref(false)

const form = reactive({
  name: '',
  description: '',
  prompt_template: '',
  output_format: 'markdown',
  sections: []
})

async function fetchTemplates() {
  const res = await fetch('/api/templates', {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('supabase_token') || ''}`
    }
  })
  templates.value = await res.json()
}

function openCreateModal() {
  editingId.value = null
  form.name = ''
  form.description = ''
  form.prompt_template = ''
  showModal.value = true
}

function editTemplate(tmpl: any) {
  editingId.value = tmpl.id
  form.name = tmpl.name
  form.description = tmpl.description
  form.prompt_template = tmpl.prompt_template
  showModal.value = true
}

async function saveTemplate() {
  if (!form.name || !form.prompt_template) {
    alert('请填写名称和 Prompt')
    return
  }
  
  saving.value = true
  try {
    const url = editingId.value ? `/api/templates/${editingId.value}` : '/api/templates'
    const method = editingId.value ? 'PATCH' : 'POST'
    
    const res = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('supabase_token') || ''}`
      },
      body: JSON.stringify(form)
    })
    
    if (!res.ok) throw new Error('保存失败')
    
    await fetchTemplates()
    showModal.value = false
  } catch (error) {
    alert('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

async function deleteTmpl(id: string) {
  if (!confirm('确定要删除这个模板吗？')) return
  
  try {
    const res = await fetch(`/api/templates/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('supabase_token') || ''}`
      }
    })
    if (!res.ok) throw new Error('删除失败')
    templates.value = templates.value.filter(t => t.id !== id)
  } catch (error) {
    alert('删除失败')
  }
}

function showPreview(tmpl: any) {
  previewTmpl.value = tmpl
}

onMounted(fetchTemplates)
</script>

<style scoped>
.template-card {
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: white;
  transition: all 0.3s ease;
}

.dark .template-card {
  border-color: #2d3748;
  background: #1a202c;
}

.icon-btn {
  padding: 4px 8px;
  border-radius: 6px;
  background: #f7fafc;
  font-size: 14px;
}

.dark .icon-btn {
  background: #2d3748;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
  padding: 24px;
}

.dark .modal-content {
  background: #1a202c;
  color: #e2e8f0;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 700;
}

.close-btn {
  font-size: 24px;
  cursor: pointer;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}

.form-group input, .form-group textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
}

.dark .form-group input, .dark .form-group textarea {
  background: #2d3748;
  border-color: #4a5568;
}

.prompt-preview {
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  font-family: monospace;
  font-size: 13px;
  white-space: pre-wrap;
}

.dark .prompt-preview {
  background: #1a202c;
}
</style>
