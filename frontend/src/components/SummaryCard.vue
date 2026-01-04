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
      <div v-if="content" class="summary-layout">
        <section class="summary-block summary-block--summary">
          <div class="summary-block__header">
            <div>
              <p class="summary-block__eyebrow">Summary</p>
              <h4 class="summary-block__title">总结</h4>
            </div>
            <span class="summary-block__pill">Summary</span>
          </div>
          <p v-if="abstractText" class="summary-block__body">{{ abstractText }}</p>
          <p v-else class="summary-empty">暂无摘要内容。</p>
        </section>

        <section class="summary-block summary-block--takeaways">
          <div class="summary-block__header">
            <div>
              <p class="summary-block__eyebrow">Takeaways</p>
              <h4 class="summary-block__title">核心要点</h4>
            </div>
            <span class="summary-block__pill is-outline">Takeaways</span>
          </div>
          <ul v-if="keyPoints.length" class="summary-takeaway-list">
            <li v-for="(point, index) in keyPoints" :key="`${point}-${index}`">
              <span class="summary-takeaway-dot"></span>
              <span>{{ point }}</span>
            </li>
          </ul>
          <p v-else class="summary-empty">暂无要点。</p>
        </section>

        <section v-if="quoteText" class="summary-block summary-block--insight">
          <div class="summary-block__header">
            <div>
              <p class="summary-block__eyebrow">Insight</p>
              <h4 class="summary-block__title">关键洞察</h4>
            </div>
            <span class="summary-block__pill is-highlight">Insight</span>
          </div>
          <p class="summary-block__quote">{{ quoteText }}</p>
        </section>

        <section class="summary-block summary-block--details">
          <div class="summary-block__header">
            <div>
              <p class="summary-block__eyebrow">Details</p>
              <h4 class="summary-block__title">详细内容</h4>
            </div>
            <span class="summary-block__pill is-outline">Full</span>
          </div>
          <div
            class="summary-content prose dark:prose-invert max-w-none"
            v-html="renderedContent"
          ></div>
        </section>
      </div>
      <p v-else class="summary-empty">暂无总结内容。</p>
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

const sanitizeSummary = (content: string) => {
  const trimmed = content.trim()
  if (!trimmed) return ''
  const lines = trimmed.split('\n')
  const firstLine = lines[0]?.trim() || ''
  const hasMarkdownLead = firstLine.startsWith('#') || firstLine.startsWith('-') || firstLine.startsWith('【')
  const prefixPattern = /^(好的|当然|以下是|下面是|这是|为你|给你|好的，没问题|没问题).{0,12}(总结|概述|提要)?[：:，,。.\s]*/
  if (!hasMarkdownLead && prefixPattern.test(firstLine)) {
    lines[0] = firstLine.replace(prefixPattern, '').trim()
    if (!lines[0]) {
      lines.shift()
    }
  }
  return lines.join('\n').trim()
}

const tokens = computed<any[]>(() => {
  if (!props.content) return []
  return marked.lexer(sanitizeSummary(props.content)) as any[]
})

const getTokenIndex = (type: string) => tokens.value.findIndex(item => item.type === type)

const abstractTokenIndex = computed(() => getTokenIndex('paragraph'))
const listTokenIndex = computed(() => getTokenIndex('list'))
const quoteTokenIndex = computed(() => getTokenIndex('blockquote'))

const abstractText = computed(() => {
  const token = tokens.value[abstractTokenIndex.value] as any
  return token?.text?.trim() || ''
})

const keyPoints = computed(() => {
  const listToken = tokens.value[listTokenIndex.value] as any
  if (!listToken || !listToken.items?.length) return []
  return listToken.items.slice(0, 5).map((item: any) => item.text.trim()).filter(Boolean)
})

const quoteText = computed(() => {
  const quoteToken = tokens.value[quoteTokenIndex.value] as any
  if (!quoteToken) return ''
  const parts = quoteToken.tokens?.map((item: any) => item.text).filter(Boolean) || []
  return parts.join(' ').trim()
})

const renderedContent = computed(() => {
  if (!props.content) return ''
  const filtered = tokens.value.filter((_, index) => {
    if (abstractText.value && index === abstractTokenIndex.value) return false
    if (keyPoints.value.length && index === listTokenIndex.value) return false
    if (quoteText.value && index === quoteTokenIndex.value) return false
    return true
  })
  return marked.parser(filtered as any)
})
</script>

<style scoped>
.summary-layout {
  display: grid;
  gap: 20px;
}

.summary-block {
  border-radius: 10px;
  border: 1px solid #e1e1e1;
  background: #ffffff;
  padding: 18px 20px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

.dark .summary-block {
  border-color: #374151;
  background: #1f2937;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.35);
}

.summary-block__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.summary-block__eyebrow {
  font-size: 12px;
  font-weight: 500;
  color: rgba(33, 36, 39, 0.6);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.dark .summary-block__eyebrow {
  color: #9ca3af;
}

.summary-block__title {
  margin-top: 6px;
  font-size: 22px;
  font-weight: 700;
  color: #212427;
}

.dark .summary-block__title {
  color: #e5e7eb;
}

.summary-block__pill {
  border-radius: 6px;
  border: 1px solid #2e83fb;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #2e83fb;
  background: #ffffff;
}

.dark .summary-block__pill {
  background: #1f2937;
}

.summary-block__pill.is-outline {
  border-color: #d8d8d8;
  color: #6b7280;
}

.dark .summary-block__pill.is-outline {
  border-color: #4b5563;
  color: #d1d5db;
}

.summary-block__pill.is-highlight {
  border-color: rgba(46, 131, 251, 0.3);
  color: #2e83fb;
  background: rgba(46, 131, 251, 0.06);
}

.summary-block__body {
  font-size: 14px;
  line-height: 1.8;
  color: #212427;
}

.dark .summary-block__body {
  color: #e5e7eb;
}

.summary-takeaway-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  font-size: 14px;
  color: #212427;
}

.dark .summary-takeaway-list {
  color: #e5e7eb;
}

.summary-takeaway-list li {
  display: grid;
  grid-template-columns: 10px 1fr;
  gap: 12px;
  align-items: flex-start;
}

.summary-takeaway-dot {
  width: 10px;
  height: 10px;
  margin-top: 6px;
  border-radius: 9999px;
  background: #2e83fb;
}

.summary-block__quote {
  padding: 12px 14px;
  border-radius: 8px;
  border: 1px solid rgba(46, 131, 251, 0.3);
  border-left-width: 3px;
  background: rgba(46, 131, 251, 0.06);
  font-size: 14px;
  line-height: 1.8;
  color: #212427;
}

.dark .summary-block__quote {
  border-color: rgba(46, 131, 251, 0.35);
  background: rgba(46, 131, 251, 0.12);
  color: #e5e7eb;
}

.summary-empty {
  color: #9ca3af;
  font-size: 13px;
}

.dark .summary-empty {
  color: #6b7280;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 14px;
  font-size: 14px;
  line-height: 1.8;
  color: #212427;
}

.summary-content :deep(> *) {
  margin: 0;
}

.summary-content :deep(h1) {
  font-size: 22px;
  font-weight: 700;
  color: #212427;
}

.summary-content :deep(h2) {
  font-size: 20px;
  font-weight: 700;
  color: #212427;
}

.summary-content :deep(h3) {
  font-size: 18px;
  font-weight: 700;
  color: #212427;
}

.summary-content :deep(h4) {
  font-size: 16px;
  font-weight: 700;
  color: #212427;
}

.summary-content :deep(p),
.summary-content :deep(li) {
  font-size: 14px;
  color: #212427;
}

.summary-content :deep(ul),
.summary-content :deep(ol) {
  padding-inline-start: 25px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-content :deep(a) {
  color: #212427;
  text-decoration: none;
}

.summary-content :deep(img) {
  max-width: 100%;
}

.dark .summary-content,
.dark .summary-content :deep(h1),
.dark .summary-content :deep(h2),
.dark .summary-content :deep(h3),
.dark .summary-content :deep(h4),
.dark .summary-content :deep(p),
.dark .summary-content :deep(li),
.dark .summary-content :deep(a) {
  color: #e5e7eb;
}
</style>
