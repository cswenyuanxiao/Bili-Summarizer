<template>
  <div class="transcript-panel bg-white dark:bg-slate-800 rounded-3xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
    <div class="card-header flex justify-between items-center px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-slate-900/50">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
        📜 视频转录
      </h3>
      <button
        @click="$emit('copy')"
        class="px-3 py-1.5 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
        title="复制转录"
      >
        📋 复制
      </button>
    </div>
    <div class="transcript-container max-h-[600px] overflow-y-auto p-6">
      <p v-if="!content" class="text-gray-500 dark:text-gray-400">暂无转录内容。</p>
      <div v-else class="space-y-2">
        <div
          v-for="(line, index) in parsedLines"
          :key="index"
          class="transcript-line flex gap-3 p-2 rounded-lg hover:bg-primary-light/20 dark:hover:bg-primary/10 transition-colors"
        >
          <span v-if="line.timestamp" class="transcript-time text-primary font-medium text-sm flex-shrink-0">
            {{ line.timestamp }}
          </span>
          <span class="text-gray-700 dark:text-gray-300">{{ line.text }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  content: string
}>()

defineEmits<{
  copy: []
}>()

const parsedLines = computed(() => {
  if (!props.content) return []
  
  const lines = props.content.split('\n').filter(line => line.trim())
  return lines.map(line => {
    const timestampMatch = line.match(/^\[(\d{2}:\d{2})\]/)
    if (timestampMatch) {
      return {
        timestamp: timestampMatch[1],
        text: line.replace(/^\[\d{2}:\d{2}\]\s*/, '')
      }
    }
    return {
      timestamp: null,
      text: line
    }
  })
})
</script>
