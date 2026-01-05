<template>
  <div v-if="keywords && keywords.length > 0" class="wordcloud-panel">
    <div class="wordcloud-header">
      <div>
        <p class="wordcloud-eyebrow">Word Cloud</p>
        <h3>关键词云</h3>
      </div>
      <span class="wordcloud-pill">Keywords</span>
    </div>

    <div class="wordcloud-canvas">
      <canvas :ref="setCanvasRef"></canvas>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { Chart, registerables } from 'chart.js'
import { WordCloudController, WordElement } from 'chartjs-chart-wordcloud'

Chart.register(...registerables, WordCloudController, WordElement)

interface KeywordItem {
  text: string
  value: number
}

const props = defineProps<{
  keywords: KeywordItem[]
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
let chartInstance: Chart | null = null

const setCanvasRef = (el: HTMLCanvasElement | null) => {
  if (el) canvasRef.value = el
}

const renderWordCloud = () => {
  if (!canvasRef.value) return
  if (!props.keywords || props.keywords.length === 0) return

  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  const ctx = canvasRef.value.getContext('2d')
  if (!ctx) return

  const labels = props.keywords.map(item => item.text)
  const data = props.keywords.map(item => item.value)
  const colors = [
    '#2e83fb',
    '#0ea5e9',
    '#22c55e',
    '#f97316',
    '#a855f7',
    '#ec4899',
  ]

  chartInstance = new Chart(ctx, {
    type: 'wordCloud',
    data: {
      labels,
      datasets: [{
        label: 'keywords',
        data,
        color: colors,
        family: 'inherit'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      }
    }
  })
}

watch(() => props.keywords, () => {
  renderWordCloud()
}, { deep: true })

onMounted(() => {
  renderWordCloud()
})
</script>

<style scoped>
.wordcloud-panel {
  background: #ffffff;
  border-radius: 16px;
  padding: 20px 22px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
}

.wordcloud-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.wordcloud-eyebrow {
  font-size: 12px;
  font-weight: 500;
  color: rgba(33, 36, 39, 0.6);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.wordcloud-header h3 {
  margin-top: 6px;
  font-size: 20px;
  font-weight: 700;
  color: #212427;
}

.wordcloud-pill {
  border-radius: 6px;
  border: 1px solid #2e83fb;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #2e83fb;
  background: #ffffff;
}

.wordcloud-canvas {
  position: relative;
  height: 260px;
}

.wordcloud-canvas canvas {
  width: 100% !important;
  height: 100% !important;
}

.dark .wordcloud-panel {
  background: #1f2937;
  border-color: #374151;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35);
}

.dark .wordcloud-header h3 {
  color: #e5e7eb;
}

.dark .wordcloud-eyebrow {
  color: #9ca3af;
}

.dark .wordcloud-pill {
  background: #1f2937;
  border-color: rgba(46, 131, 251, 0.6);
  color: #93c5fd;
}
</style>
