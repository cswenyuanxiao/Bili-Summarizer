<template>
  <div v-if="show" class="loading-overlay bg-white dark:bg-slate-800 rounded-3xl shadow-lg p-8 mb-8 text-center border border-gray-200 dark:border-gray-700">
    <div class="text-6xl mb-6">☕</div>
    <p class="text-xl font-medium text-gray-900 dark:text-gray-100 mb-2">
      {{ status || '正在连接服务器...' }}
    </p>
    <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
      {{ hint || '正在为您冲泡一杯好内容，请稍候...' }}
    </p>
    <div class="progress-bar-container max-w-md mx-auto h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
      <div 
        class="progress-bar h-full bg-gradient-to-r from-primary to-blue-400 rounded-full transition-all duration-500"
        :style="{ width: progress + '%' }"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  show: boolean
  status?: string
  hint?: string
  progress?: number
}>()
</script>
