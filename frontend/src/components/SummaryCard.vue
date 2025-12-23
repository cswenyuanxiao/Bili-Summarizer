<template>
  <div class="summary-card bg-white dark:bg-slate-800 rounded-3xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
    <div class="card-header flex justify-between items-center px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-slate-900/50">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
        📝 智能总结
      </h3>
      <div class="flex gap-2">
        <button
          @click="$emit('copy')"
          class="px-3 py-1.5 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
          title="复制总结"
        >
          📋 复制
        </button>
      </div>
    </div>
    <div class="p-6">
      <div 
        v-if="content" 
        class="summary-content prose dark:prose-invert max-w-none"
        v-html="renderedContent"
      ></div>
      <p v-else class="text-gray-500 dark:text-gray-400">暂无总结内容。</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps<{
  content: string
}>()

defineEmits<{
  copy: []
}>()

const renderedContent = computed(() => {
  if (!props.content) return ''
  return marked(props.content)
})
</script>

<style scoped>
.summary-content :deep(h1),
.summary-content :deep(h2),
.summary-content :deep(h3) {
  @apply font-bold text-gray-900 dark:text-gray-100 mt-6 mb-3;
}

.summary-content :deep(h1) {
  @apply text-2xl;
}

.summary-content :deep(h2) {
  @apply text-xl;
}

.summary-content :deep(h3) {
  @apply text-lg;
}

.summary-content :deep(p) {
  @apply mb-4 text-gray-700 dark:text-gray-300;
}

.summary-content :deep(ul),
.summary-content :deep(ol) {
  @apply pl-6 mb-4;
}

.summary-content :deep(li) {
  @apply mb-2 text-gray-700 dark:text-gray-300;
}

.summary-content :deep(strong) {
  @apply font-semibold text-gray-900 dark:text-gray-100;
}

.summary-content :deep(code) {
  @apply bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded text-sm;
}
</style>
