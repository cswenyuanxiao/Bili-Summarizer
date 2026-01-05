<template>
  <div class="mindmap-viewer glass-card card-hover-elevate rounded-3xl overflow-hidden border border-gray-100 dark:border-gray-800 shadow-xl shadow-sky-50/60 dark:shadow-none">
    <div class="card-header flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 px-6 py-5 border-b border-gray-100 dark:border-gray-700/50 bg-white/80 dark:bg-slate-900/60 backdrop-blur-md">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-sky-50 dark:bg-sky-900/30 rounded-xl text-sky-500">
          <MapIcon class="h-5 w-5" />
        </div>
        <div>
          <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100">思维导图</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">✨ Markmap 交互式脑图</p>
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

    <div class="mindmap-container relative flex items-center justify-center min-h-[360px] p-6 bg-slate-50/60 dark:bg-slate-900/40">
      <div class="absolute inset-0 pattern-grid pointer-events-none opacity-40"></div>

      <div ref="toolbarHost" class="absolute right-6 top-6 z-10"></div>

      <div class="relative z-10 w-full overflow-hidden">
        <p v-if="!diagram && !isRendering" class="text-gray-400 dark:text-gray-500 flex flex-col items-center gap-2">
          <span class="text-4xl">🧠</span>
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

        <svg
          v-show="diagram && !error"
          ref="svgRef"
          class="markmap w-full h-[360px]"
          aria-label="mindmap"
        ></svg>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onBeforeUnmount, nextTick, onMounted } from 'vue'
import { MapIcon } from '@heroicons/vue/24/outline'
import { Transformer } from 'markmap-lib'
import { Markmap } from 'markmap-view'
import { Toolbar } from 'markmap-toolbar'
import 'markmap-toolbar/dist/style.css'

const props = defineProps<{
  diagram: string
}>()

defineEmits<{
  'export-svg': []
  'export-png': []
}>()

const svgRef = ref<SVGSVGElement | null>(null)
const toolbarHost = ref<HTMLDivElement | null>(null)
const isRendering = ref(false)
const error = ref('')
const transformer = new Transformer()
const markmapInstance = ref<Markmap | null>(null)
const toolbarInstance = ref<Toolbar | null>(null)
const resizeObserver = ref<ResizeObserver | null>(null)

const getSvgElement = () => svgRef.value

defineExpose({
  getSvgElement,
  isRendering
})

const ensureToolbar = () => {
  if (!toolbarHost.value || !markmapInstance.value || toolbarInstance.value) return
  toolbarInstance.value = new Toolbar()
  toolbarInstance.value.attach(markmapInstance.value)
  toolbarInstance.value.setBrand(false)
  toolbarHost.value.append(toolbarInstance.value.render())
}

const cleanup = () => {
  resizeObserver.value?.disconnect()
  resizeObserver.value = null
  toolbarHost.value?.replaceChildren()
  toolbarInstance.value = null
  markmapInstance.value = null
}

const updateMarkmap = async () => {
  if (!props.diagram) {
    cleanup()
    error.value = ''
    return
  }
  if (!svgRef.value) return

  isRendering.value = true
  error.value = ''

  try {
    const { root } = transformer.transform(props.diagram)
    if (!markmapInstance.value) {
      markmapInstance.value = Markmap.create(svgRef.value, { autoFit: true } as any, root)
    } else {
      markmapInstance.value.setData(root)
    }
    await nextTick()
    markmapInstance.value.fit()
    ensureToolbar()
    if (!resizeObserver.value && svgRef.value.parentElement) {
      resizeObserver.value = new ResizeObserver(() => markmapInstance.value?.fit())
      resizeObserver.value.observe(svgRef.value.parentElement)
    }
  } catch (err) {
    error.value = '思维导图渲染失败'
    console.error('Markmap render error:', err)
  } finally {
    isRendering.value = false
  }
}

watch(() => props.diagram, () => {
  updateMarkmap()
}, { immediate: true })

watch(svgRef, (value) => {
  if (value && props.diagram) {
    updateMarkmap()
  }
})

onMounted(() => {
  if (props.diagram) {
    updateMarkmap()
  }
})

onBeforeUnmount(() => {
  cleanup()
})
</script>

<style scoped>
.pattern-grid {
  background-image: linear-gradient(90deg, rgba(148, 163, 184, 0.16) 1px, transparent 1px),
    linear-gradient(rgba(148, 163, 184, 0.16) 1px, transparent 1px);
  background-size: 28px 28px;
}
.dark .pattern-grid {
  background-image: linear-gradient(90deg, rgba(51, 65, 85, 0.32) 1px, transparent 1px),
    linear-gradient(rgba(51, 65, 85, 0.32) 1px, transparent 1px);
}

:deep(svg.markmap) {
  background: transparent;
}
:deep(svg.markmap text) {
  fill: #0f172a;
}
.dark :deep(svg.markmap text) {
  fill: #e2e8f0;
}
:deep(svg.markmap path) {
  stroke: #94a3b8;
}
.dark :deep(svg.markmap path) {
  stroke: #64748b;
}
:deep(.markmap-toolbar) {
  border-radius: 12px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
}
.dark :deep(.markmap-toolbar) {
  border-color: rgba(51, 65, 85, 0.8);
  background: rgba(15, 23, 42, 0.9);
}
</style>
