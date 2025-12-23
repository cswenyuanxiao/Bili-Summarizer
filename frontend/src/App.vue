<template>
  <div id="app" class="relative">
    <!-- Header Background Layer: Low z-index -->
    <div class="absolute inset-x-0 top-0 h-64 bg-gradient-to-r from-[#4f46e5] to-[#0ea5e9] pointer-events-none"></div>

    <!-- Header Content Layer: High z-index, no background -->
    <header class="relative z-30 text-white py-16 px-4 text-center">
      <div class="container mx-auto max-w-4xl px-4 relative">
        
        <!-- Top Right Controls -->
        <div class="absolute top-4 right-4 flex items-center gap-4">
          <!-- User Profile -->
          <div v-if="user" ref="userMenuRef" class="relative">
            <button
              class="flex items-center gap-2 focus:outline-none"
              :aria-expanded="showUserMenu"
              aria-haspopup="menu"
              @click="toggleUserMenu"
            >
              <img 
                :src="user.user_metadata?.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.email?.charAt(0) || 'U')}&background=4f46e5&color=fff`" 
                :alt="user.email"
                class="w-10 h-10 rounded-full border-2 border-white/30 hover:border-white transition-colors shadow-md"
                @error="(e: Event) => { (e.target as HTMLImageElement).src = 'https://ui-avatars.com/api/?name=U&background=4f46e5&color=fff' }"
              />
            </button>
            
            <!-- Dropdown Menu -->
            <div
              v-show="showUserMenu"
              class="absolute top-full right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-xl shadow-xl overflow-hidden border border-gray-100 dark:border-gray-700 z-50"
              role="menu"
            >
              <div class="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                <p class="text-sm font-medium text-gray-900 dark:text-gray-200 truncate">{{ user.email }}</p>
                <div class="flex items-center gap-2 mt-1">
                  <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">免费版</span>
                  <button @click="showPricingModal = true; showUserMenu = false" class="text-xs text-primary hover:underline">升级</button>
                </div>
              </div>
              <button 
                @click="showPricingModal = true; showUserMenu = false"
                class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center justify-between group/item"
              >
                <span>升级 Pro</span>
                <span class="text-xs bg-gradient-to-r from-primary to-purple-500 text-white px-1.5 py-0.5 rounded">HOT</span>
              </button>
              <button 
                @click="showApiKeyModal = true; showUserMenu = false"
                class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                开发者 API
              </button>
              <button 
                @click="handleLogout"
                class="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                退出登录
              </button>
            </div>
          </div>

          <!-- Login Button -->
          <button 
            v-else
            @click="showLoginModal = true" 
            class="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-full backdrop-blur-sm text-sm font-medium transition-all"
          >
            登录
          </button>

          <!-- Theme Toggle -->
          <button
            @click="toggleTheme"
            class="text-2xl cursor-pointer hover:scale-110 transition-transform ml-2"
            title="切换主题"
          >
            {{ isDark ? '☀️' : '🌙' }}
          </button>
        </div>

        <h1 class="text-4xl md:text-5xl font-bold mb-3">✨ Bili-Summarizer</h1>
        <p class="text-lg opacity-95">AI 视频总结 · 思维导图 · 转录文本 — 一键获取</p>
      </div>
    </header>

    <main class="min-h-screen pb-20">
      <div class="container mx-auto max-w-6xl px-4">
        <!-- URL Input Card -->
        <UrlInputCard 
          :is-loading="isLoading" 
          @submit="handleSummarize" 
        />

        <!-- Loading Overlay -->
    <LoadingOverlay
      :show="isLoading"
      :status="status"
      :hint="hint"
      :detail="detail"
      :progress="progress"
      :steps="loadingSteps"
      :active-step="activeStep"
      :elapsed="elapsedSeconds"
      :phase-note="phaseNote"
    />

        <!-- Results -->
        <div v-if="result.summary || result.transcript" class="results-section">
          <!-- Mermaid Mindmap -->
          <MindmapViewer
            v-if="extractedMindmap"
            :diagram="extractedMindmap"
            @export-svg="exportMindmap('svg')"
            @export-png="exportMindmap('png')"
          />

          <!-- Two Column Layout -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Left Column: Transcript -->
            <div class="lg:col-span-1">
              <TranscriptPanel
                :content="result.transcript"
                :video-url="currentVideoUrl"
                :video-file="result.videoFile"
                :video-info="videoInfo"
                @copy="copyTranscript"
              />
            </div>

            <!-- Right Column: Summary -->
            <div class="lg:col-span-2 space-y-6">
              <SummaryCard
                :content="result.summary"
                @copy="copySummary"
              />
              
              <ExportBar @export="handleExport" />
            </div>
          </div>
          
          <!-- AI 追问面板 -->
          <ChatPanel
            v-if="result.summary"
            :summary="result.summary"
            :transcript="result.transcript || ''"
            class="mt-8"
          />
        </div>

        <!-- History -->
        <HistoryList
          :items="historyItems"
          @select="loadFromHistory"
          @clear="clearHistory"
        />
      </div>
    </main>

    <LoginModal :show="showLoginModal" @close="showLoginModal = false" />
    <PricingModal :show="showPricingModal" @close="showPricingModal = false" />
    <ApiKeyModal :show="showApiKeyModal" @close="showApiKeyModal = false" />

    <footer class="bg-gray-100 dark:bg-gray-800 py-6 text-center text-sm text-gray-600 dark:text-gray-400">
      <div class="container mx-auto">
        <p>
          Powered by <a href="https://ai.google.dev/" target="_blank" class="text-primary hover:underline">Google Gemini</a> · Built with ❤️
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import UrlInputCard from './components/UrlInputCard.vue'
import LoadingOverlay from './components/LoadingOverlay.vue'
import SummaryCard from './components/SummaryCard.vue'
import TranscriptPanel from './components/TranscriptPanel.vue'
import MindmapViewer from './components/MindmapViewer.vue'
import ChatPanel from './components/ChatPanel.vue'
import ExportBar from './components/ExportBar.vue'
import HistoryList from './components/HistoryList.vue'
import LoginModal from './components/LoginModal.vue'
import PricingModal from './components/PricingModal.vue'
import ApiKeyModal from './components/ApiKeyModal.vue'
import { useSummarize } from './composables/useSummarize'
import { useTheme } from './composables/useTheme'
import { useAuth } from './composables/useAuth'
import { useHistorySync } from './composables/useHistorySync'
import type { SummarizeRequest } from './types/api'

// Theme management
const { isDark, toggleTheme, initTheme } = useTheme()
onMounted(() => { initTheme() })

// Auth management
const { user, logout } = useAuth()
const showLoginModal = ref(false)
const showPricingModal = ref(false)
const showApiKeyModal = ref(false)
const showUserMenu = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)
const currentVideoUrl = ref('')
const videoInfo = ref<{
  title: string
  thumbnail: string
  duration: number
  uploader: string
  view_count: number
} | null>(null)

// Summarization logic
const { isLoading, status, hint, detail, progress, phase, elapsedSeconds, result, summarize } = useSummarize()

// Cloud history sync
const { syncToCloud, addHistoryItem, getLocalHistory, clearHistory: clearHistorySync } = useHistorySync()

// History - convert cloud format to display format
const rawHistory = ref(getLocalHistory())
const displayHistory = computed(() => {
  return rawHistory.value.map(item => ({
    id: item.id || item.video_url,
    title: item.video_title || extractTitle(item.summary),
    mode: item.mode as 'smart' | 'video',
    timestamp: item.created_at ? new Date(item.created_at).getTime() : Date.now(),
    url: item.video_url,
    summary: item.summary,
    transcript: item.transcript || ''
  }))
})

const historyItems = displayHistory // Alias for compatibility

const handleSummarize = async (request: SummarizeRequest) => {
  currentVideoUrl.value = request.url
  videoInfo.value = null
  fetchVideoInfo(request.url)
  await summarize(request)
  
  // Save to history after completion
  if (result.value.summary) {
    addHistoryItem({
      video_url: request.url,
      video_title: videoInfo.value?.title || '',
      video_thumbnail: videoInfo.value?.thumbnail || '',
      mode: request.mode,
      focus: request.focus,
      summary: result.value.summary,
      transcript: result.value.transcript,
      mindmap: extractedMindmap.value || ''
    })
    
    // Refresh history display
    rawHistory.value = getLocalHistory()
    
    // Sync to cloud if logged in
    if (user.value) {
      syncToCloud().catch(err => console.error('Sync failed:', err))
    }
  }
}

const extractTitle = (summary: string) => {
  const firstLine = summary.split('\n')[0]
  return firstLine?.replace(/^#+ /, '').trim() || '未命名总结'
}

// Robust Mermaid Diagram Extraction
const extractedMindmap = computed(() => {
  if (!result.value.summary) return ''
  
  // 1. Standard pattern: ```mermaid ... ```
  const standardMatch = result.value.summary.match(/```mermaid[\s\S]*?\n([\s\S]*?)\n```/)
  if (standardMatch) return standardMatch[1].trim()
  
  // 2. Fallback: Check for graph/mindmap/pie keywords if backticks are missing
  const fallbackMatch = result.value.summary.match(/(graph\s+(?:TD|LR|TB|BT)[\s\S]*|mindmap[\s\S]*|pie[\s\S]*)/i)
  if (fallbackMatch) return fallbackMatch[0].trim()
  
  return ''
})

const loadingSteps = ['连接', '下载/字幕', 'AI 分析', '整理结果']
const activeStep = computed(() => {
  switch (phase.value) {
    case 'connecting':
      return 0
    case 'downloading':
    case 'transcript':
      return 1
    case 'summarizing':
      return 2
    case 'finalizing':
    case 'complete':
      return 3
    default:
      return -1
  }
})

const phaseNote = computed(() => {
  switch (phase.value) {
    case 'connecting':
      return { title: '建立连接', body: '正在创建会话并与服务器握手。' }
    case 'downloading':
      return { title: '获取素材', body: '拉取视频/音频与字幕，准备进入分析。' }
    case 'transcript':
      return { title: '生成字幕', body: '识别并整理可读的转录文本。' }
    case 'summarizing':
      return { title: 'AI 分析', body: '模型提炼重点并构建结构化内容。' }
    case 'finalizing':
      return { title: '整理结果', body: '汇总输出并渲染思维导图。' }
    case 'complete':
      return { title: '完成', body: '结果已就绪，可以开始查看。' }
    case 'error':
      return { title: '出现问题', body: '连接或处理失败，请稍后重试。' }
    default:
      return null
  }
})

const handleDocumentClick = (event: MouseEvent) => {
  if (!showUserMenu.value || !userMenuRef.value) return
  const target = event.target as Node | null
  if (target && userMenuRef.value.contains(target)) return
  showUserMenu.value = false
}

const handleDocumentKeydown = (event: KeyboardEvent) => {
  if (event.key !== 'Escape') return
  showUserMenu.value = false
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const handleLogout = async () => {
  try {
    await logout()
    showUserMenu.value = false
    showPricingModal.value = false
    showApiKeyModal.value = false
    showLoginModal.value = false
  } catch (error: any) {
    alert(`退出登录失败: ${error?.message || '未知错误'}`)
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  document.addEventListener('keydown', handleDocumentKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
  document.removeEventListener('keydown', handleDocumentKeydown)
})

// Auto-sync on login
watch(user, async (nextUser, prevUser) => {
  if (nextUser) {
    showLoginModal.value = false
    
    // Trigger cloud sync when user logs in
    if (!prevUser) {
      try {
        const synced = await syncToCloud()
        if (synced) {
          rawHistory.value = synced
        }
      } catch (error) {
        console.error('Auto-sync on login failed:', error)
      }
    }
    return
  }
  
  showUserMenu.value = false
  showPricingModal.value = false
  showApiKeyModal.value = false
})

// Cleaned summary (remove mermaid code from text display)
const cleanedSummary = computed(() => {
  if (!result.value.summary) return ''
  
  // Remove the standard block
  let cleaned = result.value.summary.replace(/```mermaid[\s\S]*?```/g, '')
  
  // If no backticks but we matched fallback, we should ideally not remove text 
  // unless we are sure it's the diagram. For now, only remove if explicitly in backticks.
  return cleaned.trim() || result.value.summary
})

const copySummary = () => {
  navigator.clipboard.writeText(result.value.summary)
  alert('已复制总结到剪贴板')
}

const copyTranscript = () => {
  navigator.clipboard.writeText(result.value.transcript)
  alert('已复制转录到剪贴板')
}

const fetchVideoInfo = async (url: string) => {
  if (!url) {
    videoInfo.value = null
    return
  }

  try {
    const response = await fetch('/api/video-info', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    })

    if (!response.ok) {
      videoInfo.value = null
      return
    }

    videoInfo.value = await response.json()
  } catch (error) {
    console.warn('Video info fetch failed:', error)
    videoInfo.value = null
  }
}

const handleExport = (format: 'md' | 'txt' | 'pdf') => {
  const content = result.value.summary
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `summary.${format === 'md' ? 'md' : 'txt'}`
  a.click()
  URL.revokeObjectURL(url)
}

const exportMindmap = (format: 'svg' | 'png') => {
  // TODO: Implement export logic
  console.log('Export mindmap as', format)
}

const loadFromHistory = (item: any) => {
  result.value.summary = item.summary
  result.value.transcript = item.transcript
  result.value.videoFile = null
  currentVideoUrl.value = item.url || ''
  fetchVideoInfo(currentVideoUrl.value)
}

const clearHistory = () => {
  if (confirm('确定要清空所有历史记录吗？')) {
    clearHistorySync()
    rawHistory.value = []
  }
}
</script>
