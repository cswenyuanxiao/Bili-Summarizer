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
              />
              
              <ExportBar @export="handleExport" />
            </div>
          </div>
          
          <ChatPanel
            v-if="result.summary"
            :summary="result.summary"
            :transcript="result.transcript || ''"
          />
        </div>

        <div data-reveal data-delay="200">
          <HistoryList
            :items="historyItems"
            @select="loadFromHistory"
            @clear="clearHistory"
            @guide="openUsageGuide"
            @share="shareHistoryItem"
          />
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, inject } from 'vue'
import html2pdf from 'html2pdf.js'
import UrlInputCard from '../components/UrlInputCard.vue'
import LoadingOverlay from '../components/LoadingOverlay.vue'
import SummaryCard from '../components/SummaryCard.vue'
import TranscriptPanel from '../components/TranscriptPanel.vue'
import MindmapViewer from '../components/MindmapViewer.vue'
import ChatPanel from '../components/ChatPanel.vue'
import ExportBar from '../components/ExportBar.vue'
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
}>('appActions')

const openLogin = () => appActions?.openLogin()
const openPricing = () => appActions?.openPricing()
const openUsageGuide = () => appActions?.openUsageGuide()

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

const historyItems = displayHistory

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

watch(user, () => {
  fetchDashboard().catch(() => undefined)
})

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
    rawHistory.value = getLocalHistory()
    if (user.value) {
      syncToCloud().catch(err => console.error('Sync failed:', err))
    }
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

const phaseNote = computed(() => {
  if (phase.value === 'error') return '发生错误'
  if (phase.value === 'complete') return '完成'
  return ''
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
  await mindmapRef.value.exportAs(format)
}

const handleExport = async (type: 'pdf' | 'png') => {
  const element = document.getElementById('summary-card')
  if (!element) return
  const options = {
    margin: 0.5,
    filename: `summary.${type}`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2, useCORS: true },
    jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
  }
  if (type === 'pdf') {
    await html2pdf().set(options).from(element).save()
  } else {
    const canvas = await html2pdf().set(options).from(element).outputImg()
    const link = document.createElement('a')
    link.href = canvas.src
    link.download = 'summary.png'
    link.click()
  }
}
</script>
