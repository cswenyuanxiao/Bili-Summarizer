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
            v-model="currentVideoUrl"
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
          <CoTPanel
            v-if="cotSteps && cotSteps.length > 0"
            :steps="cotSteps"
            @close="cotSteps = []"
          />
          
          <MindmapViewerMarkmap
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
          
          <ChartPanel
            v-if="chartData && chartData.length > 0"
            :charts="chartData"
          />

          <WordCloudPanel
            v-if="keywordData && keywordData.length > 0"
            :keywords="keywordData"
          />
          
          <ChatPanel
            v-if="result.summary"
            :key="chatKey"
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

        <transition name="badge-toast">
          <div v-if="badgeToast" class="fixed right-6 bottom-6 z-50">
            <div class="badge-toast-card">
              <div class="badge-toast-icon">🏆</div>
              <div class="badge-toast-body">
                <div class="badge-toast-title">成就解锁</div>
                <div class="badge-toast-text">{{ badgeToast.title }}</div>
              </div>
              <div class="badge-toast-glow"></div>
            </div>
          </div>
        </transition>

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
import { useRoute, useRouter } from 'vue-router'
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
import MindmapViewerMarkmap from '../components/MindmapViewerMarkmap.vue'
import ChatPanel from '../components/ChatPanel.vue'
import ExportBar from '../components/ExportBar.vue'
import AudioPlayer from '../components/AudioPlayer.vue'
import ShareCardModal from '../components/ShareCardModal.vue'
import FavoritesImportModal from '../components/FavoritesImportModal.vue'
import HistoryList from '../components/HistoryList.vue'
import CoTPanel from '../components/CoTPanel.vue'
import ChartPanel from '../components/ChartPanel.vue'
import WordCloudPanel from '../components/WordCloudPanel.vue'
import { useSummarize } from '../composables/useSummarize'
import { useAuth } from '../composables/useAuth'
import { useHistorySync } from '../composables/useHistorySync'
import { useReveal } from '../composables/useReveal'
import { useBadges } from '../composables/useBadges'
import type { SummarizeRequest } from '../types/api'
import { isSupabaseConfigured, supabase } from '../supabase'
import confetti from 'canvas-confetti'

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
const route = useRoute()
const router = useRouter()

const { isLoading, status, hint, detail, progress, phase, elapsedSeconds, errorCode, result, summarize } = useSummarize()

const cotSteps = ref<any[]>([])
const chartData = ref<any[]>([])
const keywordData = ref<any[]>([])
const badgeToast = ref<{ title: string } | null>(null)
const lastCelebratedSummary = ref('')

const { checkAndUnlockBadges } = useBadges()

// 监听 usage 变化，提取 CoT 和图表数据
watch(() => result.value.usage, (newUsage) => {
  if (newUsage) {
    cotSteps.value = newUsage.cot_steps || []
    chartData.value = newUsage.charts || []
    keywordData.value = newUsage.keywords || []
  } else {
    cotSteps.value = []
    chartData.value = []
    keywordData.value = []
  }
}, { deep: true })

const triggerConfetti = () => {
  if (typeof window === 'undefined') return
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  confetti({
    particleCount: 120,
    spread: 70,
    origin: { y: 0.6 }
  })
  confetti({
    particleCount: 80,
    spread: 120,
    origin: { y: 0.2 },
    ticks: 200
  })
}

const showBadgeToast = (title: string) => {
  badgeToast.value = { title }
  window.setTimeout(() => {
    badgeToast.value = null
  }, 2500)
}

watch(() => result.value.summary, (newVal) => {
  if (newVal) {
    nextTick(() => {
      refreshReveal()
    })
  }
})

watch([() => phase.value, () => result.value.summary], ([nextPhase, summary]) => {
  if (nextPhase === 'complete' && summary && summary !== lastCelebratedSummary.value) {
    lastCelebratedSummary.value = summary
    triggerConfetti()
    const unlocked = checkAndUnlockBadges()
    if (unlocked.length > 0) {
      showBadgeToast(unlocked[0].title)
    }
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

const pendingAutoRun = ref(false)

onMounted(() => {
  // 检查 URL 参数（浏览器插件跳转支持）
  const urlParam = route.query.url as string
  const autoRun = route.query.auto_run as string
  
  if (urlParam) {
    // 自动填充 URL
    const decodedUrl = decodeURIComponent(urlParam)
    currentVideoUrl.value = decodedUrl
    
    // 如果指定了 auto_run，标记为待运行
    if (autoRun === 'true') {
      pendingAutoRun.value = true
      
      // 如果用户已经登录，直接触发
      if (user.value) {
        pendingAutoRun.value = false
        setTimeout(() => {
          handleSummarize({
            url: decodedUrl,
            mode: 'smart',
            focus: 'default'
          })
        }, 1000)
      }
    }

    // 移除 URL 参数，保持地址栏整洁
    router.replace({ query: {} })
  }

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
  
  // 处理自动运行逻辑：仅在用户刚登录且有 pending 任务时触发
  if (newUser && pendingAutoRun.value && currentVideoUrl.value) {
    pendingAutoRun.value = false
    setTimeout(() => {
      handleSummarize({
        url: currentVideoUrl.value,
        mode: 'smart',
        focus: 'default'
      })
    }, 800) // 略微增加延迟确保 Auth 系统完全就绪
  }
  
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
    mindmap: item.mindmap || '',
    thumbnail: item.video_thumbnail || '',
    video_title: item.video_title || ''
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
const mindmapRef = ref<InstanceType<typeof MindmapViewerMarkmap> | null>(null)
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

const chatKey = ref(0)

const handleSummarize = async (request: SummarizeRequest) => {
  if (!user.value) {
    openLogin()
    return
  }
  
  // 重置所有状态
  lastRequest.value = request
  currentVideoUrl.value = request.url
  videoInfo.value = null
  showTTS.value = false
  chatKey.value++ // 强制重建聊天窗口
  
  // 清空结果防止残留
  result.value.summary = ''
  result.value.transcript = ''
  
  fetchVideoInfo(request.url)
  
  // 如果启用了 CoT，自动跳过缓存以确保生成新的思考过程
  const finalRequest = request.enable_cot 
    ? { ...request, skip_cache: true }
    : request
  await summarize(finalRequest)
  
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
  chatKey.value++
  await summarize({ ...lastRequest.value, skip_cache: true })
}

const extractTitle = (summary: string) => {
  const firstLine = summary.split('\n')[0]
  return firstLine?.replace(/^#+ /, '').trim() || '未命名总结'
}

const cleanupMermaidLabel = (value: string) => {
  const normalized = value.replace(/::.+$/, '').trim()
  const match = normalized.match(/\(\((.+)\)\)|\[(.+)\]|\((.+)\)/)
  return (match?.[1] || match?.[2] || match?.[3] || normalized).replace(/^[-*+\s]+/, '').trim()
}

const convertMermaidToMarkdown = (source: string) => {
  const lines = source.split(/\r?\n/)
  const output: string[] = []
  lines.forEach((line) => {
    if (!line.trim()) return
    if (line.trim().startsWith('mindmap')) return
    const indent = line.match(/^\s*/)?.[0]?.length || 0
    const level = Math.max(0, Math.floor(indent / 4))
    const label = cleanupMermaidLabel(line.trim())
    if (!label) return
    output.push(`${'  '.repeat(level)}- ${label}`)
  })
  return output.join('\n').trim()
}

const normalizeListLine = (line: string) => {
  if (line.match(/^\s*\d+[.)]\s+/)) {
    return line.replace(/^(\s*)\d+[.)]\s+/, '$1- ')
  }
  return line
}

const takeListLines = (block: string) => {
  const lines = block.split(/\r?\n/)
  const listLines: string[] = []
  let started = false
  for (const rawLine of lines) {
    const line = normalizeListLine(rawLine)
    if (line.match(/^\s*[-*+]\s+/)) {
      started = true
      listLines.push(line)
      continue
    }
    if (started && line.match(/^\s{2,}\S/)) {
      listLines.push(line)
      continue
    }
    if (started && line.trim() === '') {
      listLines.push(line)
      continue
    }
    if (started) break
  }
  return listLines.join('\n').trim()
}

const extractSentencesForMindmap = (text: string) => {
  const cleaned = text
    .replace(/```[\s\S]*?```/g, '')
    .replace(/【思维导图】[\s\S]*$/g, '')
    .replace(/^\s*#+\s*思维导图[\s\S]*$/gm, '')
    .replace(/\r\n/g, '\n')
    .trim()

  const lines = cleaned.split('\n').map(line => line.trim()).filter(Boolean)
  const joined = lines.join(' ')
  const segments = joined
    .split(/(?<=[。！？!?])\s*/)
    .map(segment => segment.trim())
    .filter(Boolean)

  const title = lines.find(line => line.length >= 4 && line.length <= 24) || '视频要点'
  const uniqueSegments: string[] = []
  for (const segment of segments) {
    if (segment.length < 6) continue
    if (uniqueSegments.includes(segment)) continue
    uniqueSegments.push(segment)
    if (uniqueSegments.length >= 8) break
  }

  const bullets = uniqueSegments.length ? uniqueSegments : lines.slice(0, 6)
  if (!bullets.length) return ''

  return [
    `- ${title}`,
    ...bullets.map(item => `  - ${item}`)
  ].join('\n')
}

const extractMindmapList = (summary: string) => {
  if (!summary) return ''
  const normalized = summary.replace(/\r\n/g, '\n')
  const markerMatch = normalized.match(/【思维导图】[:：]?\n+([\s\S]*)$/)
  const headingMatch = normalized.match(/^\s*#+\s*思维导图.*\n([\s\S]*)$/m)
  const inlineMatch = normalized.match(/思维导图[:：]\n+([\s\S]*)$/)
  let listBlock = (markerMatch?.[1] || headingMatch?.[1] || inlineMatch?.[1] || '').trim()
  if (listBlock.includes('```json')) {
    listBlock = listBlock.split('```json')[0].trim()
  }
  if (!listBlock) {
    const mermaidMatch = normalized.match(/```mermaid[\s\S]*?\n([\s\S]*?)\n```/)
    if (mermaidMatch?.[1]) return convertMermaidToMarkdown(mermaidMatch[1])
    return ''
  }
  const listLines = takeListLines(listBlock)
  if (listLines) return listLines
  const fallbackList = takeListLines(normalized.split('```json')[0])
  if (fallbackList) return fallbackList
  return extractSentencesForMindmap(normalized)
}

const extractedMindmap = computed(() => extractMindmapList(result.value.summary))

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

const loadFromHistory = async (item: any) => {
  if (!item?.url) return
  
  // 1. 滚动到顶部
  scrollToStart()
  
  // 2. 设置当前 URL
  currentVideoUrl.value = item.url
  
  // 3. 重置状态
  chatKey.value++
  showTTS.value = false
  
  // 4. 从历史记录恢复已有的总结结果（不重新请求 API）
  result.value.summary = item.summary || ''
  result.value.transcript = item.transcript || ''
  result.value.usage = null // 历史记录通常不包含 usage
  result.value.videoFile = null
  
  // 5. 恢复视频信息（用于封面显示）
  if (item.thumbnail || item.video_title) {
    videoInfo.value = {
      title: item.video_title || item.title || '未知视频',
      thumbnail: item.thumbnail || '',
      duration: 0, // 历史记录暂未存时长，可用占位
      uploader: '',
      view_count: 0
    }
  } else {
    videoInfo.value = null
    // 仅在完全没信息时尝试重新获取
    fetchVideoInfo(item.url)
  }
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

<style scoped>
.badge-toast-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(226, 232, 240, 0.9);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.15);
  backdrop-filter: blur(8px);
  overflow: hidden;
}

.badge-toast-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(46, 131, 251, 0.2), rgba(46, 131, 251, 0.05));
  display: grid;
  place-items: center;
  font-size: 20px;
}

.badge-toast-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.badge-toast-title {
  font-size: 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(100, 116, 139, 0.9);
}

.badge-toast-text {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.badge-toast-glow {
  position: absolute;
  right: -20px;
  top: -20px;
  width: 80px;
  height: 80px;
  border-radius: 9999px;
  background: radial-gradient(circle, rgba(46, 131, 251, 0.18), transparent 70%);
}

.dark .badge-toast-card {
  background: rgba(15, 23, 42, 0.92);
  border-color: rgba(51, 65, 85, 0.8);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.5);
}

.dark .badge-toast-title {
  color: rgba(148, 163, 184, 0.9);
}

.dark .badge-toast-text {
  color: #e2e8f0;
}

.badge-toast-enter-active,
.badge-toast-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.badge-toast-enter-from,
.badge-toast-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
}
</style>
