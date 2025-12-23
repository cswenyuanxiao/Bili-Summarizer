<template>
  <div class="mindmap-viewer bg-white dark:bg-slate-800 rounded-3xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700 mb-8">
    <div class="card-header flex justify-between items-center px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-slate-900/50">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
        🧠 思维导图
      </h3>
      <div class="flex gap-2">
        <button
          @click="$emit('export-svg')"
          class="px-3 py-1.5 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
        >
          导出 SVG
        </button>
        <button
          @click="$emit('export-png')"
          class="px-3 py-1.5 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
        >
          导出 PNG
        </button>
      </div>
    </div>
    <div class="mindmap-container flex items-center justify-center min-h-[300px] p-6">
      <p v-if="!diagram && !isRendering" class="text-gray-500 dark:text-gray-400">
        暂无思维导图。
      </p>
      <p v-if="isRendering" class="text-gray-500 dark:text-gray-400">
        正在渲染思维导图...
      </p>
      <div v-if="error" class="text-red-500">{{ error }}</div>
      <div v-if="svgMarkup" class="w-full flex justify-center" v-html="svgMarkup"></div>
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
