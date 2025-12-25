<template>
  <div class="trending-page min-h-screen pb-20">
    <div class="container mx-auto max-w-6xl px-4 py-8">
      <header class="mb-10 text-center">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2 flex items-center justify-center gap-2">
          <span class="icon-chip text-rose-500/80">
            <FireIcon class="h-5 w-5" />
          </span>
          热门推荐
        </h1>
        <p class="text-gray-500 dark:text-gray-400">B站当前最热门的视频，一键AI总结</p>
      </header>

      <!-- 加载状态 -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-20">
        <span class="icon-chip text-gray-400 mb-4">
          <ArrowPathIcon class="h-5 w-5 animate-spin" />
        </span>
        <p class="text-gray-500">正在拉取热门视频...</p>
      </div>

      <!-- 视频列表 -->
      <div v-else-if="videos.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="video in videos" 
          :key="video.bvid"
          class="bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-white/40 dark:border-slate-800/50 shadow-xl rounded-2xl overflow-hidden hover:shadow-2xl transition-all duration-300 group"
        >
          <!-- 封面 -->
          <div class="relative aspect-video overflow-hidden">
            <img 
              :src="getProxyUrl(video.cover)" 
              :alt="video.title"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
            <div class="absolute bottom-2 right-2 px-2 py-1 bg-black/70 text-white text-xs rounded">
              {{ video.duration }}
            </div>
            <div class="absolute top-2 left-2 flex gap-2">
              <span class="px-2 py-1 bg-red-500/90 text-white text-xs rounded">热门</span>
            </div>
          </div>

          <!-- 信息 -->
          <div class="p-4">
            <a 
              :href="video.url" 
              target="_blank"
              class="block mb-2 hover:text-primary transition"
            >
              <h3 class="font-bold text-gray-900 dark:text-gray-100 line-clamp-2 leading-snug">
                {{ video.title }}
              </h3>
            </a>

            <!-- UP主信息 -->
            <div class="flex items-center gap-2 mb-3">
              <img 
                :src="getProxyUrl(video.owner.face)" 
                class="w-6 h-6 rounded-full"
                :alt="video.owner.name"
              />
              <span class="text-xs text-gray-600 dark:text-gray-400">{{ video.owner.name }}</span>
            </div>

            <!-- 统计数据 -->
            <div class="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400 mb-4">
              <span class="inline-flex items-center gap-1">
                <span class="icon-chip-inline text-gray-400">
                  <EyeIcon class="h-3.5 w-3.5" />
                </span>
                {{ formatNumber(video.view) }}
              </span>
              <span class="inline-flex items-center gap-1">
                <span class="icon-chip-inline text-gray-400">
                  <HandThumbUpIcon class="h-3.5 w-3.5" />
                </span>
                {{ formatNumber(video.like) }}
              </span>
              <span class="inline-flex items-center gap-1">
                <span class="icon-chip-inline text-gray-400">
                  <ChatBubbleLeftRightIcon class="h-3.5 w-3.5" />
                </span>
                {{ formatNumber(video.danmaku) }}
              </span>
            </div>

            <!-- 操作按钮 -->
            <button 
              class="w-full px-4 py-2 bg-gradient-to-r from-primary to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all"
              @click="summarizeVideo(video.url)"
            >
              <span class="inline-flex items-center justify-center gap-2">
                <span class="icon-chip-inline text-white/90">
                  <SparklesIcon class="h-3.5 w-3.5" />
                </span>
                AI 总结
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="text-center py-20">
        <div class="mx-auto mb-4 icon-chip text-primary/80">
          <InboxIcon class="h-5 w-5" />
        </div>
        <p class="text-gray-500">暂无热门视频</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  ArrowPathIcon,
  ChatBubbleLeftRightIcon,
  EyeIcon,
  FireIcon,
  HandThumbUpIcon,
  InboxIcon,
  SparklesIcon,
} from '@heroicons/vue/24/outline'
import { useRouter } from 'vue-router'

interface Video {
  bvid: string
  title: string
  cover: string
  duration: string
  view: number
  like: number
  danmaku: number
  url: string
  owner: {
    name: string
    mid: string
    face: string
  }
  pubdate: number
  desc: string
}

const router = useRouter()
const videos = ref<Video[]>([])
const loading = ref(true)

onMounted(async () => {
  await fetchTrendingVideos()
})

async function fetchTrendingVideos() {
  loading.value = true
  try {
    const res = await fetch('/api/trending/videos?limit=30')
    const data = await res.json()
    videos.value = data.videos || []
  } catch (err) {
    console.error('Fetch trending failed:', err)
  } finally {
    loading.value = false
  }
}

function summarizeVideo(url: string) {
  // 跳转回首页并传递视频URL
  router.push({ path: '/', query: { url } })
}

function formatNumber(num: number): string {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toString()
}

function getProxyUrl(url: string) {
  if (!url) return ''
  const cleanUrl = url.replace(/^https?:\/\//, '')
  return `https://images.weserv.nl/?url=${cleanUrl}&w=400&h=300&fit=cover`
}
</script>
