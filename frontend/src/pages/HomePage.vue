<template>
  <main class="min-h-screen pb-20">
    <div class="container mx-auto max-w-6xl px-4">
      <div class="flex flex-col gap-[var(--section-gap)]">
        <div id="start" data-reveal class="flex flex-col gap-6 -mt-10 sm:-mt-14 lg:-mt-16">
          <div class="fade-up delay-1 relative z-10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 rounded-2xl glass-card px-4 py-3 text-xs sm:text-sm text-gray-600 dark:text-gray-300">
            <div class="flex items-center gap-2">
              <span class="font-semibold text-gray-900 dark:text-gray-100">当前积分</span>
              <span>{{ creditsLabel }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="font-semibold text-gray-900 dark:text-gray-100">每次消耗</span>
              <span>{{ costPerSummary }} 积分</span>
            </div>
          </div>
          <UrlInputCard 
            :is-loading="isLoading" 
            @submit="handleSummarize" 
            @bulk="openFavoritesImport"
          />
          <div
            v-if="!user"
            class="rounded-2xl border border-blue-100/80 bg-blue-50/80 px-4 py-3 text-sm text-blue-700 dark:border-blue-500/40 dark:bg-blue-950/40 dark:text-blue-200"
          >
            <div class="font-semibold">请先登录</div>
            <div class="mt-1 text-xs opacity-80">登录后才可生成总结并使用云端同步与积分体系。</div>
            <button
              class="mt-2 inline-flex text-xs font-semibold text-primary hover:underline"
              @click="openLogin"
            >
              去登录
            </button>
          </div>
          <div
            v-if="phase === 'error'"
            class="rounded-2xl border border-red-200/80 bg-red-50/80 px-4 py-3 text-sm text-red-700 dark:border-red-500/40 dark:bg-red-950/40 dark:text-red-200"
          >
            <div class="font-semibold">{{ status || '请求失败' }}</div>
            <div class="mt-1 text-xs opacity-80">{{ hint || '请稍后再试' }}</div>
            <div v-if="detail" class="mt-1 text-xs opacity-70">{{ detail }}</div>
            <div v-if="errorCode === 'CREDITS_EXCEEDED'" class="mt-1 text-xs opacity-70">
              若你使用管理员账号但仍受限，请确认服务端已配置 `ADMIN_EMAILS`。
            </div>
            <button
              v-if="errorCode === 'CREDITS_EXCEEDED'"
              class="mt-2 inline-flex text-xs font-semibold text-primary hover:underline"
              @click="openPricing"
            >
              去升级以获取更多积分
            </button>
            <button
              v-if="errorCode === 'AUTH_REQUIRED' || errorCode === 'AUTH_INVALID'"
              class="mt-2 inline-flex text-xs font-semibold text-primary hover:underline"
              @click="openLogin"
            >
              去登录
            </button>
          </div>
        </div>

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

        <div v-if="result.summary || result.transcript" class="results-section flex flex-col gap-8" data-reveal>
          <MindmapViewer
            v-if="extractedMindmap"
            ref="mindmapRef"
            :diagram="extractedMindmap"
            @export-svg="exportMindmap('svg')"
            @export-png="exportMindmap('png')"
          />

          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div class="lg:col-span-1">
              <TranscriptPanel
                :content="result.transcript"
                :video-url="currentVideoUrl"
                :video-file="result.videoFile"
                :video-info="videoInfo"
                @copy="copyTranscript"
              />
            </div>

            <div class="lg:col-span-2 space-y-6">
                <SummaryCard
                  :content="result.summary"
                  :loading="isLoading"
                  @copy="copySummary"
                  @refresh="handleResummarize"
                  @tts="showTTS = true"
                />
                
                <ExportBar @export="handleExport" @share="openShareCard" />
                
                <AudioPlayer 
                  v-if="showTTS" 
                  :text="result.summary" 
                  @close="showTTS = false" 
                />
              </div>
          </div>
          
          <ChatPanel
            v-if="result.summary"
            :summary="result.summary"
            :transcript="result.transcript || ''"
          />
        </div>

        <ShareCardModal
          :show="showShareCard"
          :title="videoInfo?.title || extractTitle(result.summary)"
          :summary="result.summary"
          :thumbnail="videoInfo?.thumbnail || ''"
          @close="showShareCard = false"
        />

        <FavoritesImportModal
          :show="showFavoritesImport"
          :cost-per-summary="costPerSummary"
          @close="showFavoritesImport = false"
          @import-started="fetchDashboard"
        />

        <div data-reveal data-delay="200">
          <HistoryList
            :items="displayHistory"
            @select="loadFromHistory"
            @clear="clearHistory"
            @guide="openUsageGuide"
            @share="shareHistoryItem"
          />
        </div>

        </div>

        <!-- Section: Product Features -->
        <section id="features" class="pt-10 pb-6 space-y-8 border-t border-gray-100 dark:border-gray-800/50" data-reveal>
          <div class="text-center space-y-3">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 tracking-tight">核心特性</h2>
            <p class="text-gray-500 dark:text-gray-400 text-sm">专为 B 站长视频打造的智能总结工具</p>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
            <button class="page-card card-action hover:translate-y-[-4px] transition-transform duration-300" type="button" @click="scrollToStart">
              <div class="icon-chip bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-300 mb-4">
                <BoltIcon class="h-4 w-4" />
              </div>
              <div class="text-base font-semibold text-gray-900 dark:text-gray-100">结构化总结</div>
              <div class="mt-2 text-sm text-gray-500 leading-relaxed">AI 智能提取视频核心观点，生成层级分明的笔记，通过大纲快速把握重点。</div>
              <div class="mt-4 text-xs text-primary font-semibold">开始总结 →</div>
            </button>
            <button class="page-card card-action hover:translate-y-[-4px] transition-transform duration-300" type="button" @click="scrollToStart">
              <div class="icon-chip bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-300 mb-4">
                <DocumentTextIcon class="h-4 w-4" />
              </div>
              <div class="text-base font-semibold text-gray-900 dark:text-gray-100">自动转录</div>
              <div class="mt-2 text-sm text-gray-500 leading-relaxed">提供精准的逐字稿与时间戳，支持一键定位播放，不错过任何细节。</div>
              <div class="mt-4 text-xs text-primary font-semibold">立即试用 →</div>
            </button>
            <button class="page-card card-action hover:translate-y-[-4px] transition-transform duration-300 page-card--accent" type="button" @click="scrollToStart">
              <div class="icon-chip bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-300 mb-4">
                <MapIcon class="h-4 w-4" />
              </div>
              <div class="text-base font-semibold text-gray-900 dark:text-gray-100">思维导图</div>
              <div class="mt-2 text-sm text-gray-500 leading-relaxed">自动分析逻辑脉络，生成可视化思维导图，支持导出 SVG/PNG，便于复习与分享。</div>
              <div class="mt-4 text-xs text-primary font-semibold">立即生成 →</div>
            </button>
          </div>
        </section>

        <!-- Section: Pricing -->
        <section id="pricing" class="pt-10 pb-6 space-y-8 border-t border-gray-100 dark:border-gray-800/50" data-reveal>
          <div class="text-center space-y-3">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 tracking-tight">灵活方案</h2>
            <p class="text-gray-500 dark:text-gray-400 text-sm">按需付费，余额永久有效</p>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div class="page-card hover:border-primary/30 transition-colors cursor-pointer group" @click="openPricing">
              <div class="flex justify-between items-start">
                <div>
                  <div class="text-base font-semibold text-gray-900 dark:text-gray-100">Starter</div>
                  <div class="mt-1 text-xs text-gray-500">尝鲜体验</div>
                </div>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300">¥1</span>
              </div>
              <div class="mt-4 flex items-baseline gap-1">
                <span class="text-2xl font-bold text-gray-900 dark:text-gray-100">30</span>
                <span class="text-sm text-gray-500">积分</span>
              </div>
              <div class="mt-4 pt-4 border-t border-gray-100 dark:border-gray-800 flex items-center text-xs text-primary font-medium group-hover:underline">
                立即购买 <span class="ml-1">→</span>
              </div>
            </div>
            <div class="page-card hover:border-primary/30 transition-colors cursor-pointer group page-card--accent" @click="openPricing">
              <div class="flex justify-between items-start">
                <div>
                  <div class="text-base font-semibold text-gray-900 dark:text-gray-100">Pro Pack</div>
                  <div class="mt-1 text-xs text-gray-500">高频总结</div>
                </div>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-primary/10 text-primary">¥3</span>
              </div>
              <div class="mt-4 flex items-baseline gap-1">
                <span class="text-2xl font-bold text-gray-900 dark:text-gray-100">120</span>
                <span class="text-sm text-gray-500">积分</span>
              </div>
              <div class="mt-4 pt-4 border-t border-gray-100 dark:border-gray-800 flex items-center text-xs text-primary font-medium group-hover:underline">
                立即购买 <span class="ml-1">→</span>
              </div>
            </div>
            <div class="page-card hover:border-primary/30 transition-colors cursor-pointer group" @click="openPricing">
              <div class="flex justify-between items-start">
                <div>
                  <div class="text-base font-semibold text-gray-900 dark:text-gray-100">Pro Plan</div>
                  <div class="mt-1 text-xs text-gray-500">无限次使用</div>
                </div>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-300">¥29.9/月</span>
              </div>
              <div class="mt-4 flex items-baseline gap-1">
                <span class="text-2xl font-bold text-gray-900 dark:text-gray-100">∞</span>
                <span class="text-sm text-gray-500">无限量</span>
              </div>
              <div class="mt-4 pt-4 border-t border-gray-100 dark:border-gray-800 flex items-center text-xs text-primary font-medium group-hover:underline">
                订阅 Pro <span class="ml-1">→</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Section: User Account Management -->
        <section id="user-management" class="grid grid-cols-1 md:grid-cols-3 gap-5 pt-6 pb-6 border-t border-gray-100 dark:border-gray-800/50" data-reveal>
          <div class="page-card group hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors flex flex-col gap-4">
            <div class="flex items-center gap-4">
              <div class="icon-chip bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-300 group-hover:scale-110 transition-transform">
                <ChartBarIcon class="h-5 w-5" />
              </div>
              <div>
                <div class="text-base font-semibold text-gray-900 dark:text-gray-100">仪表盘</div>
                <div class="mt-1 text-sm text-gray-500">查看使用趋势与剩余积分</div>
              </div>
            </div>
            <button @click="requireAuth(openDashboard)" class="mt-auto text-xs text-primary font-semibold hover:underline text-left">立即查看 →</button>
          </div>
          
          <div class="page-card group hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors flex flex-col gap-4">
            <div class="flex items-center gap-4">
              <div class="icon-chip bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-300 group-hover:scale-110 transition-transform">
                <ReceiptPercentIcon class="h-5 w-5" />
              </div>
              <div>
                <div class="text-base font-semibold text-gray-900 dark:text-gray-100">账单与发票</div>
                <div class="mt-1 text-sm text-gray-500">管理订阅记录与查看发票</div>
              </div>
            </div>
            <button @click="requireAuth(openBilling)" class="mt-auto text-xs text-primary font-semibold hover:underline text-left">立即管理 →</button>
          </div>

          <div class="page-card group hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors flex flex-col gap-4">
            <div class="flex items-center gap-4">
              <div class="icon-chip bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-300 group-hover:scale-110 transition-transform">
                <GiftIcon class="h-5 w-5" />
              </div>
              <div>
                <div class="text-base font-semibold text-gray-900 dark:text-gray-100">邀请好友</div>
                <div class="mt-1 text-sm text-gray-500">分享邀请码，赢取积分奖励</div>
              </div>
            </div>
            <button @click="requireAuth(openInvite)" class="mt-auto text-xs text-primary font-semibold hover:underline text-left">获取邀请码 →</button>
          </div>
        </section>

        <!-- Section: Developer & Resources -->
        <section id="resources" class="grid grid-cols-1 md:grid-cols-2 gap-5 pt-6 pb-10 border-t border-gray-100 dark:border-gray-800/50" data-reveal>
          <button @click="requireAuth(() => $router.push('/developer'))" class="page-card group hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors flex items-center gap-4 text-left">
            <div class="icon-chip bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 group-hover:scale-110 transition-transform">
              <WrenchScrewdriverIcon class="h-5 w-5" />
            </div>
            <div>
              <div class="text-base font-semibold text-gray-900 dark:text-gray-100">开发者 API</div>
              <div class="mt-1 text-sm text-gray-500">将总结能力集成到你的应用中</div>
            </div>
            <div class="ml-auto text-gray-400 group-hover:translate-x-1 transition-transform">→</div>
          </button>
          <RouterLink to="/docs" class="page-card group hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors flex items-center gap-4">
            <div class="icon-chip bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 group-hover:scale-110 transition-transform">
              <BookOpenIcon class="h-5 w-5" />
            </div>
            <div>
              <div class="text-base font-semibold text-gray-900 dark:text-gray-100">使用文档</div>
              <div class="mt-1 text-sm text-gray-500">查看详细功能介绍与常见问题</div>
            </div>
            <div class="ml-auto text-gray-400 group-hover:translate-x-1 transition-transform">→</div>
          </RouterLink>
        </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, inject, onMounted, onBeforeUnmount } from 'vue'
import {
  BookOpenIcon,
  BoltIcon,
  ChartBarIcon,
  DocumentTextIcon,
  GiftIcon,
  MapIcon,
  ReceiptPercentIcon,
  WrenchScrewdriverIcon,
} from '@heroicons/vue/24/outline'
import { exportToPdf } from '../utils/pdfExporter'
import UrlInputCard from '../components/UrlInputCard.vue'
import LoadingOverlay from '../components/LoadingOverlay.vue'
import SummaryCard from '../components/SummaryCard.vue'
import TranscriptPanel from '../components/TranscriptPanel.vue'
import MindmapViewer from '../components/MindmapViewer.vue'
import ChatPanel from '../components/ChatPanel.vue'
import ExportBar from '../components/ExportBar.vue'
import AudioPlayer from '../components/AudioPlayer.vue'
import ShareCardModal from '../components/ShareCardModal.vue'
import FavoritesImportModal from '../components/FavoritesImportModal.vue'
import HistoryList from '../components/HistoryList.vue'
import { useSummarize } from '../composables/useSummarize'
import { useAuth } from '../composables/useAuth'
import { useHistorySync } from '../composables/useHistorySync'
import { useReveal } from '../composables/useReveal'
import type { SummarizeRequest } from '../types/api'
import { isSupabaseConfigured, supabase } from '../supabase'

const appActions = inject<{
  openLogin: () => void
  openPricing: () => void
  openUsageGuide: () => void
  openDashboard: () => void
  openBilling: () => void
  openInvite: () => void
}>('appActions')

const openLogin = () => appActions?.openLogin()
const openPricing = () => appActions?.openPricing()
const openUsageGuide = () => appActions?.openUsageGuide()
const openDashboard = () => appActions?.openDashboard()
const openBilling = () => appActions?.openBilling()
const openInvite = () => appActions?.openInvite()

const requireAuth = (action: () => any) => {
  if (!user.value) {
    openLogin()
    return
  }
  action()
}

const { refresh: refreshReveal } = useReveal()
const { user } = useAuth()

const { isLoading, status, hint, detail, progress, phase, elapsedSeconds, errorCode, result, summarize } = useSummarize()

watch(() => result.value.summary, (newVal) => {
  if (newVal) {
    nextTick(() => {
      refreshReveal()
    })
  }
})

const { syncToCloud, addHistoryItem, getLocalHistory, clearHistory: clearHistorySync } = useHistorySync()
const lastRequest = ref<SummarizeRequest | null>(null)

const rawHistory = ref(getLocalHistory())

const refreshHistory = async () => {
  if (user.value) {
    try {
      await syncToCloud()
    } catch (e) {
      console.error('History sync failed:', e)
    }
  }
  rawHistory.value = getLocalHistory()
}

// 添加定时刷新:每30秒从云端同步一次历史记录
let refreshInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  // 立即刷新一次
  refreshHistory()
  
  // 设置定时刷新(仅当用户已登录时)
  if (user.value) {
    refreshInterval = setInterval(() => {
      if (user.value) {
        refreshHistory()
      }
    }, 30000) // 30秒刷新一次
  }
})

// 监听用户登录状态变化
watch(user, (newUser) => {
  fetchDashboard().catch(() => undefined)
  refreshHistory()
  
  // 如果用户登出,清除定时器
  if (!newUser && refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
  // 如果用户登录,启动定时器
  else if (newUser && !refreshInterval) {
    refreshInterval = setInterval(() => {
      if (user.value) {
        refreshHistory()
      }
    }, 30000)
  }
})

// 组件卸载时清除定时器
onBeforeUnmount(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
})
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
const showShareCard = ref(false)
const showTTS = ref(false)
const showFavoritesImport = ref(false)

const openShareCard = () => {
  showShareCard.value = true
}

const openFavoritesImport = () => {
  showFavoritesImport.value = true
}

const dashboardData = ref<{
  credits: number
  total_used: number
  cost_per_summary: number
} | null>(null)

const getSupabaseToken = async () => {
  if (!isSupabaseConfigured || !supabase) return null
  const { data } = await supabase.auth.getSession()
  return data.session?.access_token ?? null
}

const scrollToStart = () => {
  const target = document.getElementById('start')
  if (target) {
    target.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const fetchDashboard = async () => {
  if (!user.value) {
    dashboardData.value = null
    return
  }
  try {
    const token = await getSupabaseToken()
    if (!token) return
    const response = await fetch('/api/dashboard', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.ok) return
    dashboardData.value = await response.json()
  } catch {
    dashboardData.value = null
  }
}



const costPerSummary = computed(() => dashboardData.value?.cost_per_summary ?? 10)
const creditsLabel = computed(() => {
  if (!user.value) return '登录后可查看'
  if (!dashboardData.value) return '加载中...'
  return `${dashboardData.value.credits} 积分`
})

const handleSummarize = async (request: SummarizeRequest) => {
  if (!user.value) {
    openLogin()
    return
  }
  lastRequest.value = request
  currentVideoUrl.value = request.url
  videoInfo.value = null
  fetchVideoInfo(request.url)
  await summarize(request)
  
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
    // 立即更新本地历史显示
    rawHistory.value = getLocalHistory()
    // 后台同步到云端
    refreshHistory().catch(() => undefined)
    fetchDashboard().catch(() => undefined)
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

const extractedMindmap = computed(() => {
  if (!result.value.summary) return ''
  const standardMatch = result.value.summary.match(/```mermaid[\s\S]*?\n([\s\S]*?)\n```/)
  if (standardMatch?.[1]) return standardMatch[1].trim()
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
      return 0
  }
})

const phaseNote = computed<{ title: string; body: string } | null>(() => {
  if (phase.value === 'error') return { title: '发生错误', body: '请检查错误信息' }
  if (phase.value === 'complete') return { title: '完成', body: '总结已生成' }
  return null
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
  } catch {
    videoInfo.value = null
  }
}

const loadFromHistory = async (item: { url: string }) => {
  if (!item?.url) return
  currentVideoUrl.value = item.url
  await summarize({
    url: item.url,
    mode: 'smart',
    focus: 'default'
  })
}

const clearHistory = () => {
  clearHistorySync()
  rawHistory.value = []
}

const shareHistoryItem = async (item: { title: string; summary: string; transcript: string; mindmap?: string }) => {
  if (!user.value) {
    openLogin()
    return
  }
  try {
    const token = await getSupabaseToken()
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

const exportMindmap = async (format: 'svg' | 'png') => {
  if (!mindmapRef.value) return
  const svg = mindmapRef.value.getSvgElement()
  if (!svg) return
  
  if (format === 'svg') {
    const svgData = new XMLSerializer().serializeToString(svg)
    const blob = new Blob([svgData], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'mindmap.svg'
    link.click()
    URL.revokeObjectURL(url)
  } else {
    // PNG export via canvas
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    const svgData = new XMLSerializer().serializeToString(svg)
    const img = new Image()
    const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    
    img.onload = () => {
      canvas.width = img.width
      canvas.height = img.height
      ctx.drawImage(img, 0, 0)
      canvas.toBlob((pngBlob) => {
        if (!pngBlob) return
        const pngUrl = URL.createObjectURL(pngBlob)
        const link = document.createElement('a')
        link.href = pngUrl
        link.download = 'mindmap.png'
        link.click()
        URL.revokeObjectURL(pngUrl)
      })
      URL.revokeObjectURL(url)
    }
    img.src = url
  }
}

const handleExport = async (format: 'md' | 'txt' | 'pdf') => {
  if (format === 'md') {
    const blob = new Blob([result.value.summary], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'summary.md'
    link.click()
    URL.revokeObjectURL(url)
  } else if (format === 'txt') {
    const blob = new Blob([result.value.summary], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'summary.txt'
    link.click()
    URL.revokeObjectURL(url)
  } else {
    const element = document.getElementById('summary-card')
    if (!element) return
    
    // 使用新的稳定导出工具
    await exportToPdf(element, {
      filename: `${videoInfo.value?.title || 'summary'}.pdf`,
      imageQuality: 2
    })
  }
}
</script>
