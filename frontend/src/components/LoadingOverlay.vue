<template>
  <div v-if="show" class="loading-overlay bg-white dark:bg-slate-800 rounded-3xl shadow-lg p-8 mb-8 text-center border border-gray-200 dark:border-gray-700">
    <div class="text-6xl mb-6">☕</div>
    <p class="text-xl font-medium text-gray-900 dark:text-gray-100 mb-2">
      {{ status || '正在连接服务器...' }}
    </p>
    <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
      {{ hint || '正在为您冲泡一杯好内容，请稍候...' }}
    </p>
    <div v-if="steps?.length" class="flex flex-wrap items-center justify-center gap-2 mb-4">
      <span
        v-for="(step, index) in steps"
        :key="step"
        class="text-xs px-2.5 py-1 rounded-full border"
        :class="index <= (activeStep ?? -1)
          ? 'bg-primary text-white border-primary'
          : 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-300 border-gray-200 dark:border-gray-600'"
      >
        {{ step }}
      </span>
    </div>
    <div
      v-if="phaseNote"
      class="max-w-md mx-auto mb-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-slate-900/50 px-4 py-3 text-left"
    >
      <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ phaseNote.title }}</p>
      <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">{{ phaseNote.body }}</p>
    </div>
    <div class="progress-bar-container max-w-md mx-auto h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
      <div 
        class="progress-bar h-full bg-gradient-to-r from-primary to-blue-400 rounded-full transition-all duration-500"
        :style="{ width: progress + '%' }"
      ></div>
    </div>
    <div class="mt-4 text-xs text-gray-500 dark:text-gray-400">
      <span v-if="elapsed !== undefined">已等待 {{ formatElapsed(elapsed) }}</span>
      <span v-if="detail"> · {{ detail }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  show: boolean
  status?: string
  hint?: string
  progress?: number
  steps?: string[]
  activeStep?: number
  elapsed?: number
  detail?: string
  phaseNote?: {
    title: string
    body: string
  } | null
}>()

const formatElapsed = (seconds: number) => {
  if (!Number.isFinite(seconds)) return '0s'
  const min = Math.floor(seconds / 60)
  const sec = Math.floor(seconds % 60)
  return min > 0 ? `${min}m ${String(sec).padStart(2, '0')}s` : `${sec}s`
}
</script>
