<template>
  <div class="transcript-panel glass-card card-hover-elevate rounded-3xl overflow-hidden">
    <div class="card-header flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 px-4 sm:px-6 py-4 border-b border-gray-200/70 dark:border-gray-700/70 bg-white/60 dark:bg-slate-900/50">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
        📜 视频转录
      </h3>
      <button
        @click="$emit('copy')"
        class="px-3 py-1.5 text-xs sm:text-sm btn-ghost hover:bg-white/70 dark:hover:bg-slate-800/70 transition-colors"
        title="复制转录"
      >
        📋 复制
      </button>
    </div>
    <div v-if="videoUrl" class="px-4 sm:px-6 pt-5 sm:pt-6">
      <div
        class="relative rounded-2xl overflow-hidden bg-slate-100 dark:bg-slate-700 cursor-pointer group"
        @click="openVideoPlayer(0)"
      >
        <img
          v-if="videoInfo?.thumbnail"
          :src="videoInfo.thumbnail"
          :alt="videoInfo?.title || '视频回放'"
          class="w-full h-40 object-cover"
        />
        <div class="absolute inset-0 bg-black/30 flex items-center justify-center">
          <div class="w-12 h-12 rounded-full bg-white/90 text-slate-900 flex items-center justify-center text-xl group-hover:scale-105 transition-transform">
            ▶
          </div>
        </div>
      </div>
      <div class="mt-3">
        <p class="text-sm font-semibold text-gray-900 dark:text-gray-100">
          {{ videoInfo?.title || '视频回放' }}
        </p>
        <p v-if="videoMeta" class="text-xs text-gray-500 dark:text-gray-400">
          {{ videoMeta }}
        </p>
      </div>
    </div>

    <div ref="listRef" class="transcript-container max-h-[600px] overflow-y-auto p-4 sm:p-6">
      <p v-if="!content" class="text-gray-500 dark:text-gray-400">暂无转录内容。</p>
      <div v-else class="space-y-2">
        <div
          v-for="(line, index) in parsedLines"
          :key="index"
          :ref="setLineRef"
          class="transcript-line flex gap-3 p-2 rounded-lg transition-colors"
          :class="{
            'hover:bg-primary-light/20 dark:hover:bg-primary/10': line.seconds !== null,
            'cursor-pointer': line.seconds !== null,
            'bg-primary-light/30 dark:bg-primary/20 border-l-2 border-primary': activeLineIndex === index
          }"
          @click="handleLineClick(line)"
        >
          <span v-if="line.timestamp" class="transcript-time text-primary font-medium text-sm flex-shrink-0">
            {{ line.timestamp }}
          </span>
          <span class="text-gray-700 dark:text-gray-300">{{ line.text }}</span>
        </div>
      </div>
    </div>

    <div v-if="showVideoModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click="closeVideoPlayer">
      <div class="bg-white dark:bg-slate-900 w-[92%] max-w-3xl rounded-2xl overflow-hidden shadow-2xl" @click.stop>
        <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100">视频回放</h4>
          <button
            class="w-8 h-8 rounded-full hover:bg-gray-100 dark:hover:bg-slate-800 text-gray-600 dark:text-gray-300"
            @click="closeVideoPlayer"
          >
            ×
          </button>
        </div>
        <div class="relative w-full pt-[56.25%] bg-black">
          <video
            v-if="videoFile"
            ref="videoRef"
            :src="videoSrc"
            controls
            class="absolute inset-0 w-full h-full"
            @timeupdate="handleTimeUpdate"
            @loadedmetadata="handleMetadataLoaded"
          ></video>
          <iframe
            v-else
            class="absolute inset-0 w-full h-full"
            :src="iframeSrc"
            allowfullscreen
          ></iframe>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick, onBeforeUpdate, type ComponentPublicInstance } from 'vue'

const props = defineProps<{
  content: string
  videoUrl?: string
  videoFile?: string | null
  videoInfo?: {
    title: string
    thumbnail: string
    duration: number
    uploader: string
    view_count: number
  } | null
}>()

defineEmits<{
  copy: []
}>()

const showVideoModal = ref(false)
const videoRef = ref<HTMLVideoElement | null>(null)
const listRef = ref<HTMLElement | null>(null)
const lineRefs = ref<HTMLElement[]>([])
const activeSeconds = ref<number | null>(null)
const pendingSeekSeconds = ref(0)
const iframeSrc = ref('')

onBeforeUpdate(() => {
  lineRefs.value = []
})

const setLineRef = (el: Element | ComponentPublicInstance | null) => {
  if (!el) return
  const node = (el as ComponentPublicInstance).$el ?? el
  if (node instanceof Element) {
    lineRefs.value.push(node as HTMLElement)
  }
}

const parsedLines = computed(() => {
  if (!props.content) return []
  
  const lines = props.content.split('\n').filter(line => line.trim())
  return lines.map(line => {
    const timestampMatch = line.match(/^\[?(\d{1,2}:\d{2}(?::\d{2})?)\]?/)
    if (timestampMatch) {
      const timeLabel = timestampMatch[1] || ''
      const seconds = timeLabel ? parseTime(timeLabel) : null
      return {
        timestamp: timeLabel,
        seconds,
        text: line.replace(timestampMatch[0], '').trim()
      }
    }
    return {
      timestamp: null,
      seconds: null,
      text: line
    }
  })
})

const activeLineIndex = computed(() => {
  if (activeSeconds.value === null) return -1
  let index = -1
  const currentSeconds = activeSeconds.value ?? -1
  parsedLines.value.forEach((line, i) => {
    if (line.seconds !== null && line.seconds <= currentSeconds) {
      index = i
    }
  })
  return index
})

const videoMeta = computed(() => {
  if (!props.videoInfo) return ''
  const duration = formatDuration(props.videoInfo.duration)
  const views = typeof props.videoInfo.view_count === 'number'
    ? `${props.videoInfo.view_count.toLocaleString()} 播放`
    : ''
  return [props.videoInfo.uploader, duration, views].filter(Boolean).join(' · ')
})

const videoSrc = computed(() => {
  if (!props.videoFile) return ''
  return `/videos/${props.videoFile}`
})

const openVideoPlayer = async (startTime: number) => {
  pendingSeekSeconds.value = startTime
  if (props.videoFile) {
    showVideoModal.value = true
    await nextTick()
    if (videoRef.value) {
      videoRef.value.currentTime = startTime
      videoRef.value.play().catch(() => undefined)
    }
  } else {
    const bvid = extractBvid(props.videoUrl || '')
    if (!bvid) return
    iframeSrc.value = `https://player.bilibili.com/player.html?bvid=${bvid}&high_quality=1&autoplay=1&t=${startTime}`
    showVideoModal.value = true
  }
}

const closeVideoPlayer = () => {
  showVideoModal.value = false
  activeSeconds.value = null
  if (videoRef.value) {
    videoRef.value.pause()
    videoRef.value.currentTime = 0
  }
  iframeSrc.value = ''
}

const handleLineClick = (line: { seconds: number | null }) => {
  if (line.seconds === null) return
  openVideoPlayer(line.seconds)
}

const handleTimeUpdate = () => {
  if (!videoRef.value) return
  activeSeconds.value = videoRef.value.currentTime
}

const handleMetadataLoaded = () => {
  if (!videoRef.value) return
  if (pendingSeekSeconds.value > 0) {
    videoRef.value.currentTime = pendingSeekSeconds.value
  }
  videoRef.value.play().catch(() => undefined)
}

watch(activeLineIndex, async (index) => {
  if (index < 0) return
  await nextTick()
  const el = lineRefs.value[index]
  if (el && listRef.value) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
})

const parseTime = (timeStr: string) => {
  const parts = timeStr.split(':').map(part => Number(part))
  const first = parts[0] ?? 0
  const second = parts[1] ?? 0
  const third = parts[2] ?? 0
  if (parts.length === 2) return first * 60 + second
  if (parts.length === 3) return first * 3600 + second * 60 + third
  return 0
}

const formatDuration = (seconds: number) => {
  if (!Number.isFinite(seconds)) return ''
  const total = Math.max(0, Math.floor(seconds))
  const min = Math.floor(total / 60)
  const sec = total % 60
  return `${min}:${String(sec).padStart(2, '0')}`
}

const extractBvid = (url: string) => {
  const match = url.match(/BV[\w]+/)
  return match ? match[0] : ''
}
</script>
