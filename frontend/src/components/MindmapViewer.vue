<template>
  <div class="mindmap-viewer glass-card card-hover-elevate rounded-3xl overflow-hidden">
    <div class="card-header flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 px-4 sm:px-6 py-4 border-b border-gray-200/70 dark:border-gray-700/70 bg-white/60 dark:bg-slate-900/50">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
        🧠 思维导图
      </h3>
      <div class="flex flex-wrap gap-2">
        <button
          @click="$emit('export-svg')"
          class="px-3 py-1.5 text-xs sm:text-sm bg-white/70 dark:bg-slate-800/70 hover:bg-white rounded-lg transition-colors"
        >
          导出 SVG
        </button>
        <button
          @click="$emit('export-png')"
          class="px-3 py-1.5 text-xs sm:text-sm bg-white/70 dark:bg-slate-800/70 hover:bg-white rounded-lg transition-colors"
        >
          导出 PNG
        </button>
      </div>
    </div>
    <div class="mindmap-container flex items-center justify-center min-h-[260px] sm:min-h-[300px] p-4 sm:p-6">
      <p v-if="!diagram && !isRendering" class="text-gray-500 dark:text-gray-400">
        暂无思维导图。
      </p>
      <p v-if="isRendering" class="text-gray-500 dark:text-gray-400">
        正在渲染思维导图...
      </p>
      <div v-if="error" class="text-red-500">{{ error }}</div>
      <div v-if="svgMarkup" ref="svgContainer" class="w-full flex justify-center" v-html="svgMarkup"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import mermaid from 'mermaid'

const props = defineProps<{
  diagram: string
}>()

defineEmits<{
  'export-svg': []
  'export-png': []
}>()

const isRendering = ref(false)
const error = ref('')
const svgMarkup = ref('')
const svgContainer = ref<HTMLElement | null>(null)

const getSvgElement = () => {
  return svgContainer.value?.querySelector('svg') as SVGSVGElement | null
}

defineExpose({
  getSvgElement,
  getSvgMarkup: () => svgMarkup.value,
  isRendering
})

onMounted(() => {
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'loose',
    theme: 'base',
    themeVariables: {
      fontFamily: '"Inter", "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif',
      primaryColor: '#4f46e5',
      primaryTextColor: '#fff',
      primaryBorderColor: '#4338ca',
      lineColor: '#94a3b8',
      secondaryColor: '#e0e7ff',
      tertiaryColor: '#f8fafc'
    }
  })
})

const renderDiagram = async () => {
  if (!props.diagram) {
    svgMarkup.value = ''
    return
  }
  
  isRendering.value = true
  error.value = ''
  svgMarkup.value = ''
  
  try {
    const { svg } = await mermaid.render(`mermaid-${Date.now()}`, props.diagram)
    svgMarkup.value = svg
  } catch (err) {
    console.error('Mermaid rendering error:', err)
    error.value = '思维导图渲染失败'
  } finally {
    isRendering.value = false
  }
}

watch(() => props.diagram, () => {
  renderDiagram()
}, { immediate: true })
</script>
