<template>
  <div id="app" class="relative">
    <div class="absolute inset-0 pointer-events-none">
      <div class="absolute -top-24 left-1/2 h-80 w-[60rem] -translate-x-1/2 rounded-full bg-gradient-to-r from-[#ffd66b]/30 via-[#4f46e5]/25 to-[#06b6d4]/25 blur-3xl"></div>
      <div class="absolute top-40 right-10 h-48 w-48 rounded-full bg-[#4f46e5]/20 blur-2xl"></div>
      <div class="absolute top-72 left-16 h-60 w-60 rounded-full bg-[#06b6d4]/20 blur-2xl"></div>
    </div>

    <header class="relative z-40">
      <div class="sticky top-0 z-40 backdrop-blur-xl bg-white/70 dark:bg-slate-900/70 border-b border-gray-200/70 dark:border-slate-800/70">
        <div class="container mx-auto max-w-6xl px-4">
          <div class="flex items-center justify-between h-16">
            <div class="flex items-center gap-3">
              <div class="flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-cyan-400 text-white font-semibold">✨</div>
              <div class="text-lg font-semibold tracking-tight text-gray-900 dark:text-gray-100">Bili-Summarizer</div>
            </div>

            <nav class="hidden lg:flex items-center gap-6 text-sm text-gray-600 dark:text-gray-300">
              <div class="relative group">
                <button class="hover:text-gray-900 dark:hover:text-white transition-colors">产品</button>
                <div class="absolute left-0 top-full mt-4 w-72 rounded-2xl border border-gray-200/70 dark:border-slate-700/80 bg-white/95 dark:bg-slate-900/95 shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                  <div class="p-4 space-y-2">
                    <div class="text-sm font-semibold text-gray-900 dark:text-gray-100">核心能力</div>
                    <p class="text-xs text-gray-500">总结 · 转录 · 思维导图 · AI 追问</p>
                    <div class="text-xs text-gray-400">一站式视频信息提炼与复盘。</div>
                  </div>
                </div>
              </div>
              <button @click="showPricingModal = true" class="hover:text-gray-900 dark:hover:text-white transition-colors">方案</button>
              <button @click="showUsageGuide = true" class="hover:text-gray-900 dark:hover:text-white transition-colors">使用文档</button>
              <button v-if="user" @click="openDashboard" class="hover:text-gray-900 dark:hover:text-white transition-colors">仪表盘</button>
              <button v-if="user" @click="openBilling" class="hover:text-gray-900 dark:hover:text-white transition-colors">账单</button>
              <button v-if="user" @click="showInviteModal = true" class="hover:text-gray-900 dark:hover:text-white transition-colors">邀请好友</button>
              <button v-if="user" @click="showApiKeyModal = true" class="hover:text-gray-900 dark:hover:text-white transition-colors">开发者 API</button>
            </nav>

            <div class="flex items-center gap-3">
              <button
                @click="toggleTheme"
                class="w-9 h-9 flex items-center justify-center rounded-full bg-gray-100 dark:bg-slate-800 text-lg hover:scale-105 transition-transform"
                title="切换主题"
              >
                {{ isDark ? '☀️' : '🌙' }}
              </button>

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
                    class="w-9 h-9 rounded-full border-2 border-white/30 hover:border-primary transition-colors shadow-md"
                    @error="(e: Event) => { (e.target as HTMLImageElement).src = 'https://ui-avatars.com/api/?name=U&background=4f46e5&color=fff' }"
                  />
                </button>
                
                <div
                  v-show="showUserMenu"
                  class="absolute top-full right-0 mt-2 w-52 bg-white dark:bg-gray-800 rounded-xl shadow-xl overflow-hidden border border-gray-100 dark:border-gray-700 z-50"
                  role="menu"
                >
                  <div class="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                    <p class="text-sm font-medium text-gray-900 dark:text-gray-200 truncate">{{ user.email }}</p>
                    <div class="flex items-center gap-2 mt-1">
                      <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">{{ planLabel }}</span>
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
                    @click="openDashboard"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    仪表盘
                  </button>
                  <button
                    @click="openBilling"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    账单与发票
                  </button>
                  <button
                    @click="showInviteModal = true; showUserMenu = false"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    邀请好友
                  </button>
                  <button 
                    @click="showApiKeyModal = true; showUserMenu = false"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    开发者 API
                  </button>
                  <button
                    @click="showUsageGuide = true; showUserMenu = false"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    使用文档
                  </button>
                  <button 
                    @click="handleLogout"
                    class="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    退出登录
                  </button>
                </div>
              </div>

              <button 
                v-else
                @click="showLoginModal = true" 
                class="px-4 py-2 rounded-full bg-gray-900 text-white text-sm font-medium hover:shadow-lg transition-all"
              >
                登录 / 注册
              </button>

              <button
                class="lg:hidden w-9 h-9 flex items-center justify-center rounded-full bg-gray-100 dark:bg-slate-800"
                @click="showMobileMenu = !showMobileMenu"
              >
                ☰
              </button>
            </div>
          </div>
          <div v-if="showMobileMenu" ref="mobileMenuRef" class="lg:hidden pb-4">
            <div class="rounded-2xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 space-y-2 text-sm text-gray-700 dark:text-gray-200">
              <button class="w-full text-left" @click="showPricingModal = true; showMobileMenu = false">方案</button>
              <button class="w-full text-left" @click="showUsageGuide = true; showMobileMenu = false">使用文档</button>
              <button v-if="user" class="w-full text-left" @click="openDashboard">仪表盘</button>
              <button v-if="user" class="w-full text-left" @click="openBilling">账单与发票</button>
              <button v-if="user" class="w-full text-left" @click="showInviteModal = true; showMobileMenu = false">邀请好友</button>
              <button v-if="user" class="w-full text-left" @click="showApiKeyModal = true; showMobileMenu = false">开发者 API</button>
            </div>
          </div>
        </div>
      </div>

      <div class="container mx-auto max-w-6xl px-4 py-16">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
          <div class="space-y-6">
            <span class="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-primary">
              <span class="w-6 h-[2px] bg-primary"></span>
              视频理解新方式
            </span>
            <h1 class="text-4xl md:text-5xl font-semibold text-gray-900 dark:text-gray-100 leading-tight">
              用 AI 把长视频拆成可执行的知识模块
            </h1>
            <p class="text-base md:text-lg text-gray-600 dark:text-gray-300">
              一键总结、结构化思维导图与时间戳转录，把 B 站内容变成可复盘的工作流。
            </p>
            <div class="flex flex-wrap gap-3">
              <button
                @click="scrollToStart"
                class="px-6 py-3 rounded-full bg-primary text-white text-sm font-medium shadow-lg shadow-primary/20 hover:-translate-y-0.5 transition"
              >
                立即开始
              </button>
              <button
                @click="showUsageGuide = true"
                class="px-6 py-3 rounded-full border border-gray-300 dark:border-slate-700 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-slate-800 transition"
              >
                了解使用方式
              </button>
            </div>
            <div class="flex flex-wrap gap-6 text-xs text-gray-500 dark:text-gray-400">
              <span>⚡ 平均 1 分钟出结果</span>
              <span>🧠 思维导图自动生成</span>
              <span>📄 支持 PDF/PNG 导出</span>
            </div>
          </div>
          <div class="relative">
            <div class="absolute -top-8 -left-6 h-24 w-24 rounded-2xl bg-primary/10 blur-xl"></div>
            <div class="rounded-3xl border border-gray-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-6 shadow-2xl">
              <div class="text-sm text-gray-500 mb-3">实时流程预览</div>
              <div class="space-y-3 text-sm">
                <div class="flex items-center justify-between rounded-2xl bg-gray-50 dark:bg-slate-800 px-4 py-3">
                  <span>字幕识别</span>
                  <span class="text-primary font-semibold">✔</span>
                </div>
                <div class="flex items-center justify-between rounded-2xl bg-gray-50 dark:bg-slate-800 px-4 py-3">
                  <span>结构化总结</span>
                  <span class="text-primary font-semibold">进行中</span>
                </div>
                <div class="flex items-center justify-between rounded-2xl bg-gray-50 dark:bg-slate-800 px-4 py-3">
                  <span>思维导图渲染</span>
                  <span class="text-gray-400">等待</span>
                </div>
              </div>
              <div class="mt-4 text-xs text-gray-400">支持云端历史与多端同步</div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main class="min-h-screen pb-20">
      <div class="container mx-auto max-w-6xl px-4">
        <!-- URL Input Card -->
        <div id="start">
        <UrlInputCard 
          :is-loading="isLoading" 
          @submit="handleSummarize" 
        />
        </div>

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
            ref="mindmapRef"
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
                :loading="isLoading"
                @copy="copySummary"
                @refresh="handleResummarize"
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
          @guide="showUsageGuide = true"
          @share="shareHistoryItem"
        />
      </div>
    </main>

    <LoginModal :show="showLoginModal" @close="showLoginModal = false" />
    <PricingModal :show="showPricingModal" @close="showPricingModal = false" />
    <ApiKeyModal :show="showApiKeyModal" @close="showApiKeyModal = false" />
    <DashboardModal
      :show="showDashboard"
      :loading="dashboardLoading"
      :error="dashboardError"
      :data="dashboardData"
      :subscription="subscriptionData"
      @close="showDashboard = false"
      @refresh="fetchDashboard"
      @upgrade="showPricingModal = true"
    />
    <InviteModal
      :show="showInviteModal"
      @close="showInviteModal = false"
      @refreshed="fetchDashboard"
    />
    <BillingModal
      :show="showBillingModal"
      :loading="billingLoading"
      :error="billingError"
      :items="billingItems"
      @close="showBillingModal = false"
    />
    <UsageGuideModal :show="showUsageGuide" @close="showUsageGuide = false" />

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
import { marked } from 'marked'
import html2pdf from 'html2pdf.js'
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
import DashboardModal from './components/DashboardModal.vue'
import BillingModal from './components/BillingModal.vue'
import InviteModal from './components/InviteModal.vue'
import UsageGuideModal from './components/UsageGuideModal.vue'
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
const showDashboard = ref(false)
const showBillingModal = ref(false)
const showInviteModal = ref(false)
const showUsageGuide = ref(false)
const showUserMenu = ref(false)
const showMobileMenu = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)
const mobileMenuRef = ref<HTMLElement | null>(null)
const currentVideoUrl = ref('')
type VideoInfo = {
  title: string
  thumbnail: string
  duration: number
  uploader: string
  view_count: number
}

const videoInfo = ref<VideoInfo | null>(null)
const mindmapRef = ref<InstanceType<typeof MindmapViewer> | null>(null)
const dashboardLoading = ref(false)
const dashboardError = ref('')
const dashboardData = ref<{
  credits: number
  total_used: number
  cost_per_summary: number
  daily_usage?: { day: string; count: number }[]
  email?: string | null
} | null>(null)
const subscriptionData = ref<{
  plan: string
  status: string
  current_period_end?: string | null
} | null>(null)
const billingLoading = ref(false)
const billingError = ref('')
const billingItems = ref<Array<{
  id: string
  amount_cents: number
  currency: string
  status: string
  period_start?: string | null
  period_end?: string | null
  invoice_url?: string | null
  created_at?: string | null
}>>([])

// Summarization logic
const { isLoading, status, hint, detail, progress, phase, elapsedSeconds, errorCode, result, summarize } = useSummarize()

// Cloud history sync
const { syncToCloud, addHistoryItem, getLocalHistory, clearHistory: clearHistorySync } = useHistorySync()
const lastRequest = ref<SummarizeRequest | null>(null)

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
    transcript: item.transcript || '',
    mindmap: item.mindmap || ''
  }))
})

const historyItems = displayHistory // Alias for compatibility

const handleSummarize = async (request: SummarizeRequest) => {
  lastRequest.value = request
  currentVideoUrl.value = request.url
  videoInfo.value = null
  fetchVideoInfo(request.url)
  await summarize(request)
  
  // Save to history after completion
  if (result.value.summary) {
    const currentInfo = videoInfo.value as VideoInfo | null
    addHistoryItem({
      video_url: request.url,
      video_title: currentInfo?.title || '',
      video_thumbnail: currentInfo?.thumbnail || '',
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

const handleResummarize = async () => {
  if (!lastRequest.value || isLoading.value) return
  await summarize({ ...lastRequest.value, skip_cache: true })
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
  if (standardMatch?.[1]) return standardMatch[1].trim()
  
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

const handleMobileMenuClick = (event: MouseEvent) => {
  if (!showMobileMenu.value || !mobileMenuRef.value) return
  const target = event.target as Node | null
  if (target && mobileMenuRef.value.contains(target)) return
  showMobileMenu.value = false
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
  showDashboard.value = false
  showBillingModal.value = false
  showInviteModal.value = false
  showUsageGuide.value = false
  showLoginModal.value = false
  } catch (error: any) {
    alert(`退出登录失败: ${error?.message || '未知错误'}`)
  }
}

const fetchDashboard = async () => {
  if (!user.value) {
    dashboardData.value = null
    return
  }
  dashboardLoading.value = true
  dashboardError.value = ''
  try {
    const token = (await import('./supabase').then(m => m.supabase.auth.getSession())).data.session?.access_token
    if (!token) throw new Error('未获取到登录凭证')
    const response = await fetch('/api/dashboard', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.ok) throw new Error('获取仪表盘失败')
    dashboardData.value = await response.json()
  } catch (error: any) {
    dashboardError.value = error?.message || '获取仪表盘失败'
  } finally {
    dashboardLoading.value = false
  }
}

const fetchSubscription = async () => {
  if (!user.value) {
    subscriptionData.value = null
    return
  }
  try {
    const token = (await import('./supabase').then(m => m.supabase.auth.getSession())).data.session?.access_token
    if (!token) throw new Error('未获取到登录凭证')
    const response = await fetch('/api/subscription', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.ok) throw new Error('获取订阅信息失败')
    subscriptionData.value = await response.json()
  } catch (error) {
    subscriptionData.value = null
  }
}

const fetchBilling = async () => {
  if (!user.value) {
    billingItems.value = []
    return
  }
  billingLoading.value = true
  billingError.value = ''
  try {
    const token = (await import('./supabase').then(m => m.supabase.auth.getSession())).data.session?.access_token
    if (!token) throw new Error('未获取到登录凭证')
    const response = await fetch('/api/billing', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.ok) throw new Error('获取账单失败')
    billingItems.value = await response.json()
  } catch (error: any) {
    billingError.value = error?.message || '获取账单失败'
  } finally {
    billingLoading.value = false
  }
}

const openDashboard = async () => {
  showUserMenu.value = false
  showMobileMenu.value = false
  showDashboard.value = true
  await fetchDashboard()
}

const openBilling = async () => {
  showUserMenu.value = false
  showMobileMenu.value = false
  showBillingModal.value = true
  await fetchBilling()
}

const shareHistoryItem = async (item: {
  title: string
  summary: string
  transcript: string
  mindmap?: string
}) => {
  if (!user.value) {
    showLoginModal.value = true
    return
  }
  try {
    const token = (await import('./supabase').then(m => m.supabase.auth.getSession())).data.session?.access_token
    if (!token) throw new Error('未获取到登录凭证')
    const response = await fetch('/api/share', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: item.title,
        summary: item.summary,
        transcript: item.transcript,
        mindmap: item.mindmap
      })
    })
    if (!response.ok) throw new Error('生成分享链接失败')
    const data = await response.json()
    const shareUrl = `${window.location.origin}${data.share_url}`
    await navigator.clipboard.writeText(shareUrl)
    alert('分享链接已复制')
  } catch (error: any) {
    alert(error?.message || '分享失败')
  }
}

const scrollToStart = () => {
  document.getElementById('start')?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  document.addEventListener('click', handleMobileMenuClick)
  document.addEventListener('keydown', handleDocumentKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
  document.removeEventListener('click', handleMobileMenuClick)
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
    fetchDashboard().catch(() => undefined)
    fetchSubscription().catch(() => undefined)
    return
  }
  
  showUserMenu.value = false
  showPricingModal.value = false
  showApiKeyModal.value = false
  showDashboard.value = false
  showBillingModal.value = false
  showInviteModal.value = false
})

watch(errorCode, (code) => {
  if (code === 'CREDITS_EXCEEDED') {
    showPricingModal.value = true
  }
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

const planLabel = computed(() => {
  if (subscriptionData.value?.plan === 'pro' && subscriptionData.value?.status === 'active') {
    return 'Pro'
  }
  return '免费版'
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

const downloadBlob = (blob: Blob, filename: string) => {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

const stripMarkdown = (content: string) => {
  return content
    .replace(/```[\s\S]*?```/g, '')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/!\[[^\]]*]\([^)]+\)/g, '')
    .replace(/\[([^\]]+)]\([^)]+\)/g, '$1')
    .replace(/^\s{0,3}#{1,6}\s?/gm, '')
    .replace(/^\s{0,3}[-*+]\s+/gm, '')
    .replace(/^\s{0,3}\d+\.\s+/gm, '')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/__([^_]+)__/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/_([^_]+)_/g, '$1')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

const exportSummaryPdf = async () => {
  if (!result.value.summary) {
    alert('暂无可导出的总结内容')
    return
  }

  const container = document.createElement('div')
  container.style.position = 'fixed'
  container.style.left = '0'
  container.style.top = '0'
  container.style.width = '800px'
  container.style.padding = '24px'
  container.style.background = '#ffffff'
  container.style.color = '#111827'
  container.style.fontFamily = '"Noto Sans SC", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif'
  container.style.opacity = '0'
  container.style.pointerEvents = 'none'
  container.style.zIndex = '-1'

  const html = marked.parse(cleanedSummary.value)
  container.innerHTML = `
    <div style="font-size: 22px; font-weight: 700; margin-bottom: 16px;">视频总结</div>
    <div style="font-size: 14px; line-height: 1.7;">${html}</div>
  `

  document.body.appendChild(container)
  try {
    await new Promise<void>(resolve => {
      requestAnimationFrame(() => requestAnimationFrame(() => resolve()))
    })
    await html2pdf().set({
      margin: 10,
      filename: 'summary.pdf',
      html2canvas: { scale: 2, useCORS: true, backgroundColor: '#ffffff' },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    }).from(container).save()
  } finally {
    container.remove()
  }
}

const handleExport = async (format: 'md' | 'txt' | 'pdf') => {
  if (!result.value.summary) {
    alert('暂无可导出的总结内容')
    return
  }

  if (format === 'pdf') {
    await exportSummaryPdf()
    return
  }

  const content = format === 'md'
    ? result.value.summary
    : stripMarkdown(cleanedSummary.value)
  const mime = format === 'md' ? 'text/markdown' : 'text/plain'
  downloadBlob(new Blob([content], { type: `${mime};charset=utf-8` }), `summary.${format}`)
}

const getSvgSize = (svg: SVGSVGElement) => {
  const widthAttr = svg.getAttribute('width')
  const heightAttr = svg.getAttribute('height')
  let width = widthAttr ? parseFloat(widthAttr) : 0
  let height = heightAttr ? parseFloat(heightAttr) : 0
  if ((!width || !height) && svg.getAttribute('viewBox')) {
    const viewBox = svg.getAttribute('viewBox')?.split(/\s+/).map(Number) || []
    if (viewBox.length === 4) {
      width = viewBox[2] || 0
      height = viewBox[3] || 0
    }
  }
  return {
    width: width || 1200,
    height: height || 800
  }
}

const buildSvgExport = () => {
  const svgEl = mindmapRef.value?.getSvgElement()
  const svgMarkup = mindmapRef.value?.getSvgMarkup()
  if (svgMarkup) {
    const parser = new DOMParser()
    const doc = parser.parseFromString(svgMarkup, 'image/svg+xml')
    const parsedSvg = doc.querySelector('svg')
    if (parsedSvg) {
      return parsedSvg as SVGSVGElement
    }
  }
  return svgEl
}

const exportMindmap = async (format: 'svg' | 'png') => {
  const svgEl = buildSvgExport()
  if (!svgEl) {
    alert('暂无可导出的思维导图')
    return
  }

  const serializer = new XMLSerializer()
  let svgText = serializer.serializeToString(svgEl)
  if (!svgText.includes('xmlns=')) {
    svgText = svgText.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')
  }
  if (!svgText.includes('xmlns:xlink=')) {
    svgText = svgText.replace('<svg', '<svg xmlns:xlink="http://www.w3.org/1999/xlink"')
  }

  if (format === 'svg') {
    downloadBlob(new Blob([svgText], { type: 'image/svg+xml;charset=utf-8' }), 'mindmap.svg')
    return
  }

  const { width, height } = getSvgSize(svgEl)
  const svgBlob = new Blob([svgText], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(svgBlob)
  const img = new Image()
  img.onload = () => {
    const canvas = document.createElement('canvas')
    canvas.width = width
    canvas.height = height
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.fillStyle = '#ffffff'
      ctx.fillRect(0, 0, width, height)
      ctx.drawImage(img, 0, 0, width, height)
      canvas.toBlob((blob) => {
        if (blob) {
          downloadBlob(blob, 'mindmap.png')
        } else {
          alert('导出 PNG 失败，请重试')
        }
        URL.revokeObjectURL(url)
      }, 'image/png')
    } else {
      URL.revokeObjectURL(url)
      alert('导出 PNG 失败，请重试')
    }
  }
  img.onerror = () => {
    URL.revokeObjectURL(url)
    alert('导出 PNG 失败，请重试')
  }
  img.decoding = 'async'
  img.src = url
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
