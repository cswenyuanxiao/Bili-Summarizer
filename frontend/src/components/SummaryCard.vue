<template>
  <div class="summary-card glass-card card-hover-elevate rounded-3xl overflow-hidden">
    <div class="card-header flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 px-4 sm:px-6 py-4 border-b border-gray-200/70 dark:border-gray-700/70 bg-white/60 dark:bg-slate-900/50">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
        <span class="icon-chip-sm text-primary/80">
          <DocumentTextIcon class="h-4 w-4" />
        </span>
        智能总结
      </h3>
      <div class="flex flex-wrap gap-2">
        <button
          @click="$emit('copy')"
          class="px-3 py-1.5 text-xs sm:text-sm btn-ghost hover:bg-white/70 dark:hover:bg-slate-800/70 transition-colors"
          title="复制总结"
        >
          <span class="inline-flex items-center gap-1.5">
            <span class="icon-chip-inline text-gray-500">
              <ClipboardDocumentIcon class="h-3.5 w-3.5" />
            </span>
            复制
          </span>
        </button>
        <button
          @click="$emit('tts')"
          :disabled="loading"
          class="px-3 py-1.5 text-xs sm:text-sm btn-ghost hover:bg-white/80 dark:hover:bg-slate-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title="语音播报"
        >
          <span class="inline-flex items-center gap-1.5">
            <span class="icon-chip-inline text-gray-500">
              <SpeakerWaveIcon class="h-3.5 w-3.5" />
            </span>
            语音播报
          </span>
        </button>
        <button
          @click="$emit('refresh')"
          :disabled="loading"
          class="px-3 py-1.5 text-xs sm:text-sm btn-ghost hover:bg-white/80 dark:hover:bg-slate-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title="重新总结"
        >
          <span class="inline-flex items-center gap-1.5">
            <span class="icon-chip-inline text-gray-500">
              <ArrowPathIcon class="h-3.5 w-3.5" />
            </span>
            重新总结
          </span>
        </button>
      </div>
    </div>
    <div class="p-4 sm:p-6">
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
import {
  ArrowPathIcon,
  ClipboardDocumentIcon,
  DocumentTextIcon,
  SpeakerWaveIcon,
} from '@heroicons/vue/24/outline'
import { marked } from 'marked'

const props = defineProps<{
  content: string
  loading?: boolean
}>()

defineEmits<{
  copy: []
  refresh: []
  tts: []
}>()

const renderedContent = computed(() => {
  if (!props.content) return ''
  return marked(props.content)
})
</script>

<style scoped>
.summary-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.summary-content :deep(> *) {
  margin: 0;
}

.summary-content :deep(h1),
.summary-content :deep(h2),
.summary-content :deep(h3) {
  @apply font-bold text-gray-900 dark:text-gray-100;
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
  @apply text-gray-700 dark:text-gray-300;
}

.summary-content :deep(ul),
.summary-content :deep(ol) {
  @apply pl-6;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-content :deep(li) {
  @apply text-gray-700 dark:text-gray-300;
}

.summary-content :deep(strong) {
  @apply font-semibold text-gray-900 dark:text-gray-100;
}

.summary-content :deep(code) {
  @apply bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded text-sm;
}
</style>
