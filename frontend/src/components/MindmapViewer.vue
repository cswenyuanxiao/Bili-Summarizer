<template>
  <div class="mindmap-viewer glass-card card-hover-elevate rounded-3xl overflow-hidden border border-gray-100 dark:border-gray-800 shadow-xl shadow-indigo-50/50 dark:shadow-none">
    <div class="card-header flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 px-6 py-5 border-b border-gray-100 dark:border-gray-700/50 bg-white/80 dark:bg-slate-900/60 backdrop-blur-md">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-indigo-50 dark:bg-indigo-900/30 rounded-xl text-primary">
          <MapIcon class="h-5 w-5" />
        </div>
        <div>
          <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100">思维导图</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">✨ AI 生成的核心知识结构</p>
        </div>
      </div>
      <div class="flex flex-wrap gap-2">
        <button
          @click="$emit('export-svg')"
          class="inline-flex items-center px-3 py-1.5 text-xs font-semibold text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-slate-800 hover:bg-gray-100 dark:hover:bg-slate-700 border border-gray-200 dark:border-gray-700 rounded-lg transition-all active:scale-95"
        >
          SVG
        </button>
        <button
          @click="$emit('export-png')"
          class="inline-flex items-center px-3 py-1.5 text-xs font-semibold text-white bg-primary hover:bg-primary-hover shadow-lg shadow-primary/20 rounded-lg transition-all active:scale-95"
        >
          PNG
        </button>
      </div>
    </div>
    
    <!-- 绘图区域：添加点阵背景 -->
    <div class="mindmap-container relative flex items-center justify-center min-h-[360px] p-8 bg-slate-50/50 dark:bg-slate-900/30">
      <!-- 装饰背景 -->
      <div class="absolute inset-0 pattern-dots pointer-events-none opacity-40"></div>
      
      <div class="relative z-10 w-full overflow-x-auto custom-scrollbar flex justify-center">
        <p v-if="!diagram && !isRendering" class="text-gray-400 dark:text-gray-500 flex flex-col items-center gap-2">
          <span class="text-4xl">🗺️</span>
          <span>暂无思维导图数据</span>
        </p>
        
        <div v-if="isRendering" class="flex flex-col items-center gap-3 animate-pulse">
          <div class="h-8 w-32 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
          <div class="flex gap-4">
            <div class="h-24 w-24 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            <div class="h-24 w-24 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
          </div>
          <span class="text-sm text-gray-500">正在构建知识图谱...</span>
        </div>

        <div v-if="error" class="text-red-500 bg-red-50 dark:bg-red-900/20 px-4 py-2 rounded-lg text-sm border border-red-100 dark:border-red-800/50">
          {{ error }}
        </div>
        
        <div 
          v-if="svgMarkup" 
          ref="svgContainer" 
          class="mermaid-wrapper w-full flex justify-center transform transition-transform" 
          v-html="svgMarkup"
        ></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 点阵背景 */
.pattern-dots {
  background-image: radial-gradient(#cbd5e1 1px, transparent 1px);
  background-size: 20px 20px;
}
.dark .pattern-dots {
  background-image: radial-gradient(#334155 1px, transparent 1px);
}

/* 强制 Mermaid 样式优化 */
:deep(.mermaid svg) {
  font-family: 'Inter', system-ui, sans-serif !important;
  max-width: 100% !important;
  height: auto !important;
}

/* 节点阴影与质感 */
:deep(.node rect), :deep(.node circle), :deep(.node polygon), :deep(.node path) {
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.05));
  transition: all 0.3s ease;
}

:deep(.node:hover rect), :deep(.node:hover circle), :deep(.node:hover polygon) {
  filter: drop-shadow(0 8px 12px rgba(99, 102, 241, 0.15));
  stroke-width: 2px;
}

/* 连线优化 */
:deep(.edgePath path) {
  stroke-width: 2px !important;
  stroke-linecap: round !important; 
  opacity: 0.8;
}
</style>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { MapIcon } from '@heroicons/vue/24/outline'
import { renderMermaid } from '../utils/mermaidRenderer'

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

const renderDiagram = async () => {
  if (!props.diagram) {
    svgMarkup.value = ''
    return
  }
  
  isRendering.value = true
  error.value = ''
  
  const result = await renderMermaid(props.diagram, 'mindmap')
  
  if (result.success && result.svg) {
    svgMarkup.value = result.svg
  } else {
    error.value = result.error || '思维导图渲染失败'
    console.error('Mindmap error:', result.error)
  }
  
  isRendering.value = false
}

watch(() => props.diagram, () => {
  renderDiagram()
}, { immediate: true })
</script>
