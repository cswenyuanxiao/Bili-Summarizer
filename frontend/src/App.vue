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
          <div v-if="user" class="relative group">
            <button class="flex items-center gap-2 focus:outline-none">
              <img 
                :src="user.user_metadata?.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.email?.charAt(0) || 'U')}&background=4f46e5&color=fff`" 
                :alt="user.email"
                class="w-10 h-10 rounded-full border-2 border-white/30 hover:border-white transition-colors shadow-md"
                @error="(e: Event) => { (e.target as HTMLImageElement).src = 'https://ui-avatars.com/api/?name=U&background=4f46e5&color=fff' }"
              />
            </button>
            
            <!-- Dropdown Menu -->
            <div class="absolute top-full right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-xl shadow-xl overflow-hidden hidden group-hover:block border border-gray-100 dark:border-gray-700 z-50">
              <div class="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                <p class="text-sm font-medium text-gray-900 dark:text-gray-200 truncate">{{ user.email }}</p>
                <div class="flex items-center gap-2 mt-1">
                  <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">免费版</span>
                  <button @click="showPricingModal = true" class="text-xs text-primary hover:underline">升级</button>
                </div>
              </div>
              <button 
                @click="showPricingModal = true"
                class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center justify-between group/item"
              >
                <span>升级 Pro</span>
                <span class="text-xs bg-gradient-to-r from-primary to-purple-500 text-white px-1.5 py-0.5 rounded">HOT</span>
              </button>
              <button 
                @click="showApiKeyModal = true"
                class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                开发者 API
              </button>
              <button 
                @click="logout" 
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
          :progress="progress"
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
import { ref, computed, onMounted } from 'vue'
import UrlInputCard from './components/UrlInputCard.vue'
import LoadingOverlay from './components/LoadingOverlay.vue'
import SummaryCard from './components/SummaryCard.vue'
import TranscriptPanel from './components/TranscriptPanel.vue'
import MindmapViewer from './components/MindmapViewer.vue'
import ExportBar from './components/ExportBar.vue'
import HistoryList from './components/HistoryList.vue'
import LoginModal from './components/LoginModal.vue'
import PricingModal from './components/PricingModal.vue'
import ApiKeyModal from './components/ApiKeyModal.vue'
import { useSummarize } from './composables/useSummarize'
import { useTheme } from './composables/useTheme'
import { useAuth } from './composables/useAuth'
import type { SummarizeRequest } from './types/api'

// Theme management
const { isDark, toggleTheme, initTheme } = useTheme()
onMounted(() => { initTheme() })

// Auth management
const { user, logout } = useAuth()
const showLoginModal = ref(false)
const showPricingModal = ref(false)
const showApiKeyModal = ref(false)

// Summarization logic
const { isLoading, status, progress, result, summarize } = useSummarize()

// History
const historyItems = ref<any[]>([])

const handleSummarize = async (request: SummarizeRequest) => {
  await summarize(request)
  
  // Save to history after completion
  if (result.value.summary) {
    historyItems.value.unshift({
      id: Date.now().toString(),
      title: extractTitle(result.value.summary),
      mode: request.mode,
      timestamp: Date.now(),
      url: request.url,
      summary: result.value.summary,
      transcript: result.value.transcript,
    })
    
    // Keep only last 10 items
    historyItems.value = historyItems.value.slice(0, 10)
    localStorage.setItem('history', JSON.stringify(historyItems.value))
  }
}

const extractTitle = (summary: string) => {
  const firstLine = summary.split('\n')[0]
  return firstLine?.replace(/^#+ /, '').trim() || '未命名总结'
}

const extractedMindmap = computed(() => {
  if (!result.value.summary) return ''
  // Extract mermaid diagram from summary
  const match = result.value.summary.match(/```mermaid\n([\s\S]*?)\n```/)
  return match ? match[1] : ''
})

const copySummary = () => {
  navigator.clipboard.writeText(result.value.summary)
  alert('已复制总结到剪贴板')
}

const copyTranscript = () => {
  navigator.clipboard.writeText(result.value.transcript)
  alert('已复制转录到剪贴板')
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
}

const clearHistory = () => {
  if (confirm('确定要清空所有历史记录吗？')) {
    historyItems.value = []
    localStorage.removeItem('history')
  }
}

// Load history on mount
const savedHistory = localStorage.getItem('history')
if (savedHistory) {
  try {
    historyItems.value = JSON.parse(savedHistory)
  } catch (e) {
    console.error('Failed to parse history', e)
  }
}
</script>
