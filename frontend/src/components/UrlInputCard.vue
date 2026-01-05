<template>
  <div class="input-section relative z-20 fade-up delay-2">
    <div class="container mx-auto max-w-4xl px-4">
      <div class="input-card glass-card card-hover-elevate rounded-3xl p-6 sm:p-8 lg:p-10">
        <form @submit.prevent="handleSubmit">
          <!-- URL Input Row -->
          <div class="url-input-row flex flex-col md:flex-row gap-3 md:gap-4 mb-5 sm:mb-6">
            <input
              v-model="formData.url"
              type="text"
              id="video-url"
              class="flex-1 px-4 sm:px-6 input-base text-base sm:text-lg"
              placeholder="粘贴 Bilibili 视频链接，例如: https://www.bilibili.com/video/BV..."
              required
            />
            <button
              type="button"
              class="px-4 btn-ghost rounded-xl text-sm font-semibold hover:bg-gray-50/80 dark:hover:bg-gray-800/80 transition-colors flex items-center justify-center"
              @click="handleLuckyPick"
              title="手气不错"
            >
              <span class="icon-chip-inline text-gray-500">
                <BoltIcon class="h-3.5 w-3.5" />
              </span>
            </button>
            <button
              type="submit"
              :disabled="isLoading"
              class="px-6 sm:px-8 btn-primary transition-all flex items-center justify-center gap-2 w-full md:w-auto"
            >
              <span class="icon-chip-inline text-white/90">
                <SparklesIcon class="h-3.5 w-3.5" />
              </span>
              生成总结
            </button>
            <button
              type="button"
              class="px-5 btn-ghost rounded-xl text-sm font-medium hover:bg-gray-50/80 dark:hover:bg-gray-800/80 transition-colors"
              @click="$emit('bulk')"
            >
              <span class="icon-chip-inline text-gray-500 mr-1">
                <Squares2X2Icon class="h-3.5 w-3.5" />
              </span>
              批量导入
            </button>
          </div>

          <!-- Options Row -->
          <div class="options-row flex flex-col md:flex-row gap-3 md:gap-6">
            <div class="option-group flex flex-col md:flex-row md:items-center gap-2 md:gap-3 w-full md:w-auto">
              <label for="summarize-mode" class="text-sm font-semibold text-gray-600 dark:text-gray-400 whitespace-nowrap">
                模式
              </label>
              <select
                v-model="formData.mode"
                id="summarize-mode"
                class="px-4 py-2 border border-gray-300/80 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 cursor-pointer w-full md:w-auto"
              >
                <option value="smart">智能 (优先字幕)</option>
                <option value="video">视频 (画面分析)</option>
              </select>
            </div>

            <div class="option-group flex flex-col md:flex-row md:items-center gap-2 md:gap-3 w-full md:w-auto">
              <label for="summary-template" class="text-sm font-semibold text-gray-600 dark:text-gray-400 whitespace-nowrap">
                模板
              </label>
              <select
                v-model="formData.template_id"
                id="summary-template"
                class="px-4 py-2 border border-gray-300/80 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 cursor-pointer w-full md:w-auto min-w-[120px]"
              >
                <option :value="null">默认总结</option>
                <option v-for="t in templates" :key="t.id" :value="t.id">
                  {{ t.name }}
                </option>
              </select>
            </div>

            <div class="option-group flex flex-col md:flex-row md:items-center gap-2 md:gap-3 w-full md:w-auto">
              <label for="output-language" class="text-sm font-semibold text-gray-600 dark:text-gray-400 whitespace-nowrap">
                语言
              </label>
              <select
                v-model="formData.output_language"
                id="output-language"
                class="px-4 py-2 border border-gray-300/80 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 cursor-pointer w-full md:w-auto min-w-[140px]"
              >
                <option value="zh">🇨🇳 中文</option>
                <option value="en">🇺🇸 English</option>
                <option value="ja">🇯🇵 日本語</option>
                <option value="ko">🇰🇷 한국어</option>
                <option value="es">🇪🇸 Español</option>
                <option value="fr">🇫🇷 Français</option>
              </select>
            </div>
          </div>
          
          <!-- Advanced Options -->
          <div class="advanced-options flex flex-wrap gap-4 mt-4 pt-4 border-t border-gray-100 dark:border-gray-800">
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                v-model="formData.enable_cot"
                type="checkbox"
                class="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary cursor-pointer"
              />
              <span class="text-sm text-gray-600 dark:text-gray-400 inline-flex items-center gap-2">
                <span class="icon-chip-inline text-gray-500">
                  <LightBulbIcon class="h-3.5 w-3.5" />
                </span>
                显示思考过程
              </span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                v-model="autoRunLucky"
                type="checkbox"
                class="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary cursor-pointer"
              />
              <span class="text-sm text-gray-600 dark:text-gray-400 inline-flex items-center gap-2">
                <span class="icon-chip-inline text-gray-500">
                  <BoltIcon class="h-3.5 w-3.5" />
                </span>
                手气不错后自动开始
              </span>
            </label>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted, ref, watch } from 'vue'
import { SparklesIcon, Squares2X2Icon, BoltIcon, LightBulbIcon } from '@heroicons/vue/24/outline'
import type { SummarizeRequest } from '../types/api'
import { FEATURED_VIDEOS, buildBilibiliUrl } from '../data/featuredVideos'

const props = defineProps<{
  isLoading?: boolean
  modelValue?: string
}>()

const emit = defineEmits<{
  submit: [request: SummarizeRequest]
  bulk: []
  'update:modelValue': [value: string]
}>()

const templates = ref<any[]>([])
const autoRunLucky = ref(false)
const trendingVideos = ref<TrendingVideo[]>([])
const trendingFetched = ref(false)
const luckyLoading = ref(false)

const formData = reactive<SummarizeRequest & { template_id?: string | null }>({
  url: props.modelValue || '',
  mode: 'smart',
  focus: 'default',
  template_id: null,
  output_language: 'zh',
  enable_cot: false
})

// 同步外部传入的 modelValue
watch(() => props.modelValue, (newVal) => {
  if (newVal !== undefined) {
    formData.url = newVal
  }
})

// 当本地 url 改变时通知外部
watch(() => formData.url, (newVal) => {
  emit('update:modelValue', newVal)
})

onMounted(async () => {
  try {
    const res = await fetch('/api/templates', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('supabase_token') || ''}`
      }
    })
    if (res.ok) {
      templates.value = await res.json()
    }
  } catch (err) {
    console.error('Failed to fetch templates:', err)
  }
})

const handleSubmit = () => {
  emit('submit', { ...formData } as any)
}

const handleLuckyPick = async () => {
  if (luckyLoading.value) return
  luckyLoading.value = true

  // 立即给出兜底，避免网络慢时无响应
  pickFromFeatured()

  try {
    if (!trendingFetched.value) {
      const res = await fetch('/api/trending/videos?limit=40')
      if (res.ok) {
        const data = await res.json()
        trendingVideos.value = (data.videos || []).filter((video: TrendingVideo) => {
          return getDurationSeconds(video.duration) <= 15 * 60
        })
      }
      trendingFetched.value = true
    }

    const candidates = trendingVideos.value
    const picked = candidates.length
      ? candidates[Math.floor(Math.random() * candidates.length)]
      : null

    if (picked?.url) {
      formData.url = picked.url
    }
  } catch (err) {
    console.error('Lucky pick failed:', err)
  } finally {
    luckyLoading.value = false
    if (formData.url && autoRunLucky.value && !props.isLoading) {
      handleSubmit()
    }
  }
}

const pickFromFeatured = () => {
  if (!FEATURED_VIDEOS.length) return
  const randomIndex = Math.floor(Math.random() * FEATURED_VIDEOS.length)
  const bvid = FEATURED_VIDEOS[randomIndex]
  if (bvid) {
    formData.url = buildBilibiliUrl(bvid)
  }
}

const getDurationSeconds = (duration: number | string | undefined) => {
  if (typeof duration === 'number') return duration
  if (typeof duration === 'string') {
    const parts = duration.split(':').map((p) => Number(p))
    if (parts.some((p) => Number.isNaN(p))) return Number.POSITIVE_INFINITY
    if (parts.length === 3) {
      const [h, m, s] = parts
      return h * 3600 + m * 60 + s
    }
    if (parts.length === 2) {
      const [m, s] = parts
      return m * 60 + s
    }
  }
  return Number.POSITIVE_INFINITY
}

interface TrendingVideo {
  bvid: string
  url: string
  duration: number | string
}
</script>
