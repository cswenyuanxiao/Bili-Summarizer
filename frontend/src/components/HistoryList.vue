<template>
  <section class="history-section fade-up delay-2">
    <div class="section-header flex justify-between items-center mb-6 px-2">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
        <span class="icon-chip-sm text-primary/80">
          <ArchiveBoxIcon class="h-4 w-4" />
        </span>
        历史记录
      </h2>
      <button
        v-if="items.length > 0"
        @click="$emit('clear')"
        class="px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
      >
        清空所有
      </button>
    </div>

    <div v-if="items.length === 0" class="rounded-2xl glass-card card-hover-elevate p-6 sm:p-8 text-center">
      <div class="mx-auto mb-3 icon-chip text-primary/80">
        <InboxIcon class="h-5 w-5" />
      </div>
      <p class="text-sm text-gray-500 dark:text-gray-400">完成一次总结后，历史记录会出现在这里。</p>
      <button
        @click="$emit('guide')"
        class="mt-4 inline-flex items-center justify-center px-4 py-2 text-sm bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
      >
        查看使用文档
      </button>
    </div>

    <div v-else class="history-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      <div
        v-for="item in items"
        :key="item.id"
        @click="$emit('select', item)"
        class="history-item glass-card card-hover-elevate rounded-2xl p-5 cursor-pointer"
      >
        <div class="history-item-title font-semibold text-gray-900 dark:text-gray-100 mb-2 line-clamp-2">
          {{ item.title || '未命名视频' }}
        </div>
        <div class="history-item-meta text-sm text-gray-500 dark:text-gray-400 flex items-center gap-2">
          <span>{{ item.mode === 'smart' ? '智能模式' : '视频模式' }}</span>
          <span>·</span>
          <span>{{ formatTime(item.timestamp) }}</span>
        </div>
        <div class="mt-4 flex items-center justify-between text-xs text-gray-400">
          <span>快速访问</span>
          <button
            @click.stop="$emit('share', item)"
            class="px-2 py-1 text-xs border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-700 transition-colors"
          >
            分享
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ArchiveBoxIcon, InboxIcon } from '@heroicons/vue/24/outline'
interface HistoryItem {
  id: string
  title: string
  mode: 'smart' | 'video'
  timestamp: number
  url: string
  summary: string
  transcript: string
  mindmap?: string
}

defineProps<{
  items: HistoryItem[]
}>()

defineEmits<{
  select: [item: HistoryItem]
  clear: []
  guide: []
  share: [item: HistoryItem]
}>()

const formatTime = (timestamp: number) => {
  const now = Date.now()
  const diff = now - timestamp
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 0) return `${days}天前`
  if (hours > 0) return `${hours}小时前`
  if (minutes > 0) return `${minutes}分钟前`
  return '刚刚'
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
