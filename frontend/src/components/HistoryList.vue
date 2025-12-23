<template>
  <section v-if="items.length > 0" class="history-section mt-8">
    <div class="section-header flex justify-between items-center mb-6 px-2">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
        📚 历史记录
      </h2>
      <button
        @click="$emit('clear')"
        class="px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
      >
        清空所有
      </button>
    </div>

    <div class="history-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      <div
        v-for="item in items"
        :key="item.id"
        @click="$emit('select', item)"
        class="history-item bg-white dark:bg-slate-800 rounded-xl p-5 shadow-sm border border-gray-200 dark:border-gray-700 cursor-pointer hover:shadow-md hover:border-primary hover:-translate-y-1 transition-all"
      >
        <div class="history-item-title font-semibold text-gray-900 dark:text-gray-100 mb-2 line-clamp-2">
          {{ item.title || '未命名视频' }}
        </div>
        <div class="history-item-meta text-sm text-gray-500 dark:text-gray-400 flex items-center gap-2">
          <span>{{ item.mode === 'smart' ? '智能模式' : '视频模式' }}</span>
          <span>·</span>
          <span>{{ formatTime(item.timestamp) }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
interface HistoryItem {
  id: string
  title: string
  mode: 'smart' | 'video'
  timestamp: number
  url: string
  summary: string
  transcript: string
}

defineProps<{
  items: HistoryItem[]
}>()

defineEmits<{
  select: [item: HistoryItem]
  clear: []
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
