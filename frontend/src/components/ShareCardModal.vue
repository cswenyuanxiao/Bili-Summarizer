<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content share-card-modal">
      <header class="modal-header">
        <h3>生成分享卡片</h3>
        <button class="close-btn" @click="$emit('close')">×</button>
      </header>
      
      <div class="modal-body">
        <!-- 预览区域 -->
        <div class="preview-area">
          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>正在渲染卡片...</p>
          </div>
          <img v-else-if="cardUrl" :src="cardUrl" class="card-preview-img" />
          <div v-else class="preview-placeholder">
            选择模板并点击「生成」
          </div>
        </div>
        
        <!-- 侧边设置 -->
        <div class="settings-area">
          <div class="setting-group">
            <label>卡片模板</label>
            <div class="template-selector">
              <button 
                v-for="t in templates" 
                :key="t.id"
                class="template-option"
                :class="{ active: currentTemplate === t.id }"
                @click="currentTemplate = t.id"
              >
                {{ t.name }}
              </button>
            </div>
          </div>
          
          <div class="actions">
            <button class="btn-primary" @click="generate" :disabled="loading">
              {{ cardUrl ? '重新生成' : '生成卡片' }}
            </button>
            
            <template v-if="cardUrl">
              <button class="btn-secondary" @click="download">
                <span class="inline-flex items-center gap-1.5">
                  <span class="icon-chip-inline text-gray-500">
                    <ArrowDownTrayIcon class="h-3.5 w-3.5" />
                  </span>
                  下载图片
                </span>
              </button>
              <button class="btn-secondary" @click="copyLink">
                <span class="inline-flex items-center gap-1.5">
                  <span class="icon-chip-inline text-gray-500">
                    <LinkIcon class="h-3.5 w-3.5" />
                  </span>
                  复制链接
                </span>
              </button>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArrowDownTrayIcon, LinkIcon } from '@heroicons/vue/24/outline'

const props = defineProps<{
  show: boolean
  title: string
  summary: string
  thumbnail: string
}>()

defineEmits(['close'])

const loading = ref(false)
const cardUrl = ref('')
const currentTemplate = ref('default')

const templates = [
  { id: 'default', name: '清爽白' },
  { id: 'dark', name: '深邃夜' },
  { id: 'gradient', name: '极光渐变' },
  { id: 'minimal', name: '极简横版' }
]

async function generate() {
  loading.value = true
  try {
    const response = await fetch('/api/share/card', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('supabase_token') || ''}`
      },
      body: JSON.stringify({
        title: props.title,
        summary: props.summary,
        thumbnail_url: props.thumbnail,
        template: currentTemplate.value
      })
    })
    
    if (!response.ok) throw new Error('生成失败')
    
    const data = await response.json()
    cardUrl.value = data.image_url
  } catch (error) {
    console.error('Share card generation failed:', error)
    alert('卡片生成失败，请重试')
  } finally {
    loading.value = false
  }
}

async function download() {
  if (!cardUrl.value) return
  
  try {
    const response = await fetch(cardUrl.value)
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `summary-card-${Date.now()}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Download failed:', error)
    alert('下载失败')
  }
}

function copyLink() {
  const fullUrl = window.location.origin + cardUrl.value
  navigator.clipboard.writeText(fullUrl)
  alert('链接已复制')
}
</script>

<style scoped>
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
  width: 90%;
  max-width: 900px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
}

.modal-header {
  padding: 16px 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}

.modal-body {
  display: grid;
  grid-template-columns: 1fr 300px;
  height: 600px;
}

.preview-area {
  background: #f1f5f9;
  padding: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.card-preview-img {
  max-width: 100%;
  max-height: 100%;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  border-radius: 8px;
}

.preview-placeholder {
  color: #94a3b8;
  font-style: italic;
}

.settings-area {
  padding: 24px;
  border-left: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.template-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 8px;
}

.template-option {
  padding: 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.template-option.active {
  border-color: #4f46e5;
  color: #4f46e5;
  background: #eef2ff;
}

.actions {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-primary {
  background: #4f46e5;
  color: white;
  padding: 12px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f8fafc;
  color: #475569;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  cursor: pointer;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .modal-body {
    grid-template-columns: 1fr;
    height: auto;
    max-height: 80vh;
    overflow-y: auto;
  }
  .settings-area {
    border-left: none;
    border-top: 1px solid #e2e8f0;
  }
}
</style>
