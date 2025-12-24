<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content fav-import-modal">
      <header class="modal-header">
        <h3>导入 B 站收藏夹</h3>
        <button class="close-btn" @click="$emit('close')">×</button>
      </header>
      
      <div class="modal-body">
        <!-- URL 输入区域 -->
        <div class="input-section">
          <label>收藏夹链接</label>
          <div class="url-input-group">
            <input 
              v-model="url" 
              type="text" 
              placeholder="粘贴收藏夹链接，例如: https://www.bilibili.com/medialist/detail/ml123..."
              @keyup.enter="fetchInfo"
            />
            <button class="btn-primary" :disabled="loadingInfo" @click="fetchInfo">
              {{ loadingInfo ? '获取中...' : '解析' }}
            </button>
          </div>
          <p class="hint">支持公开的收藏夹或播放列表</p>
        </div>

        <!-- 收藏夹预览 -->
        <div v-if="favInfo" class="fav-preview">
          <div class="fav-header">
            <img :src="favInfo.cover" class="fav-cover" />
            <div class="fav-meta">
              <h4>{{ favInfo.title }}</h4>
              <p>创建者: {{ favInfo.owner }} | 视频数: {{ favInfo.media_count }}</p>
            </div>
          </div>

          <div class="video-preview-list">
            <div class="list-header">
              <label>
                <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" />
                全选 ({{ selectedBvids.length }} / {{ videos.length }})
              </label>
              <span>预计消耗: {{ totalCost }} 积分</span>
            </div>
            
            <div class="video-items">
              <div v-for="video in videos" :key="video.bvid" class="video-item">
                <input 
                  type="checkbox" 
                  :value="video.bvid" 
                  v-model="selectedBvids"
                />
                <img :src="video.cover" class="video-thumb" />
                <div class="video-info">
                  <p class="video-title">{{ video.title }}</p>
                  <span class="video-duration">{{ video.duration }}</span>
                </div>
              </div>
            </div>
            
            <div v-if="hasMore" class="load-more">
              <button class="btn-text" @click="fetchVideos(page + 1)">加载更多...</button>
            </div>
          </div>
        </div>

        <!-- 导入选项 -->
        <div v-if="favInfo" class="import-options">
          <div class="option-row">
            <label>总结模式</label>
            <select v-model="mode">
              <option value="smart">智能总结 (推荐)</option>
              <option value="video">完整总结 (详细)</option>
            </select>
          </div>
          <div class="option-row">
            <label>关注重点</label>
            <select v-model="focus">
              <option value="default">综合全貌</option>
              <option value="logic">逻辑脉络</option>
              <option value="detail">细节挖掘</option>
            </select>
          </div>
          <button 
            class="btn-primary btn-import" 
            :disabled="importing || selectedBvids.length === 0"
            @click="handleImport"
          >
            {{ importing ? '正在启动...' : `开始批量总结 (${selectedBvids.length} 个视频)` }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{
  show: boolean
  costPerSummary: number
}>()

const emit = defineEmits(['close', 'import-started'])

const url = ref('')
const loadingInfo = ref(false)
const favInfo = ref<any>(null)
const videos = ref<any[]>([])
const selectedBvids = ref<string[]>([])
const page = ref(1)
const hasMore = ref(false)
const mode = ref('smart')
const focus = ref('default')
const importing = ref(false)

const isAllSelected = computed(() => {
  return videos.value.length > 0 && selectedBvids.value.length === videos.value.length
})

const totalCost = computed(() => {
  return selectedBvids.value.length * props.costPerSummary
})

async function fetchInfo() {
  if (!url.value) return
  loadingInfo.value = true
  favInfo.value = null
  videos.value = []
  selectedBvids.value = []
  page.value = 1
  
  try {
    const res = await fetch(`/api/favorites/info?url=${encodeURIComponent(url.value)}`)
    if (!res.ok) throw new Error('获取失败')
    favInfo.value = await res.json()
    await fetchVideos(1)
  } catch (error) {
    alert('解析失败，请检查链接是否正确且收藏夹是否公开')
  } finally {
    loadingInfo.value = false
  }
}

async function fetchVideos(p: number) {
  try {
    const res = await fetch(`/api/favorites/videos?url=${encodeURIComponent(url.value)}&page=${p}`)
    if (!res.ok) throw new Error('获取视频失败')
    const data = await res.json()
    
    if (p === 1) {
      videos.value = data.videos
    } else {
      videos.value = [...videos.value, ...data.videos]
    }
    
    // 默认全选新加载的视频
    data.videos.forEach((v: any) => {
      if (!selectedBvids.value.includes(v.bvid)) {
        selectedBvids.value.push(v.bvid)
      }
    })
    
    page.value = p
    hasMore.value = data.has_more
  } catch (error) {
    console.error(error)
  }
}

function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedBvids.value = []
  } else {
    selectedBvids.value = videos.value.map(v => v.bvid)
  }
}

async function handleImport() {
  if (selectedBvids.value.length === 0) return
  importing.value = true
  
  try {
    const response = await fetch('/api/favorites/import', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('supabase_token') || ''}`
      },
      body: JSON.stringify({
        favorites_url: url.value,
        mode: mode.value,
        focus: focus.value,
        selected_bvids: selectedBvids.value
      })
    })
    
    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || '导入失败')
    }
    
    const data = await response.json()
    emit('import-started', data.job_id)
    emit('close')
    alert(`已启动批量总结任务，共 ${selectedBvids.value.length} 个视频`)
  } catch (error: any) {
    alert(error.message)
  } finally {
    importing.value = false
  }
}

watch(() => props.show, (newVal) => {
  if (!newVal) {
    url.value = ''
    favInfo.value = null
    videos.value = []
    selectedBvids.value = []
  }
})
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
  max-width: 700px;
  border-radius: 16px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
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
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.input-section label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  margin-bottom: 8px;
}

.url-input-group {
  display: flex;
  gap: 12px;
}

.url-input-group input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
}

.hint {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.fav-preview {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.fav-header {
  display: flex;
  gap: 16px;
  align-items: center;
}

.fav-cover {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  object-fit: cover;
}

.fav-meta h4 {
  margin: 0;
  font-size: 16px;
}

.fav-meta p {
  margin: 4px 0 0;
  font-size: 12px;
  color: #64748b;
}

.video-preview-list {
  background: #f8fafc;
  border-radius: 8px;
  padding: 12px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #475569;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e2e8f0;
}

.video-items {
  max-height: 240px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.video-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  background: white;
  border-radius: 6px;
  border: 1px solid #f1f5f9;
}

.video-thumb {
  width: 60px;
  height: 40px;
  border-radius: 4px;
  object-fit: cover;
}

.video-info {
  flex: 1;
  min-width: 0;
}

.video-title {
  font-size: 13px;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.video-duration {
  font-size: 11px;
  color: #94a3b8;
}

.load-more {
  text-align: center;
  margin-top: 12px;
}

.import-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.option-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.option-row label {
  width: 80px;
  font-size: 14px;
  color: #475569;
}

.option-row select {
  flex: 1;
  padding: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
}

.btn-import {
  margin-top: 8px;
  padding: 14px;
  font-size: 15px;
  font-weight: 600;
}

.btn-primary {
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-text {
  background: none;
  border: none;
  color: #4f46e5;
  font-size: 13px;
  cursor: pointer;
}

.btn-text:hover {
  text-decoration: underline;
}
</style>
