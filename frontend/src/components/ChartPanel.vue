<template>
  <div v-if="charts && charts.length > 0" class="chart-panel">
    <h3>📊 数据可视化</h3>
    
    <div class="charts-grid">
      <div v-for="(chart, index) in charts" :key="index" class="chart-item">
        <h4>{{ chart.title }}</h4>
        <div class="chart-container">
          <canvas :ref="el => setChartRef(el, index)"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

interface ChartData {
  type: 'bar' | 'pie' | 'line'
  title: string
  data: {
    labels: string[]
    values: number[]
  }
}

const props = defineProps<{
  charts: ChartData[]
}>()

const chartRefs = ref<(HTMLCanvasElement | null)[]>([])
const chartInstances = ref<Chart[]>([])

const setChartRef = (el: any, index: number) => {
  if (el) {
    chartRefs.value[index] = el as HTMLCanvasElement
  }
}

const renderCharts = () => {
  // 清理旧图表
  chartInstances.value.forEach(chart => chart.destroy())
  chartInstances.value = []

  if (!props.charts || props.charts.length === 0) return

  props.charts.forEach((chartData, index) => {
    const canvas = chartRefs.value[index]
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const colors = [
      'rgba(79, 70, 229, 0.8)',
      'rgba(124, 58, 237, 0.8)',
      'rgba(236, 72, 153, 0.8)',
      'rgba(251, 146, 60, 0.8)',
      'rgba(34, 197, 94, 0.8)',
      'rgba(14, 165, 233, 0.8)',
    ]

    const chart = new Chart(ctx, {
      type: chartData.type,
      data: {
        labels: chartData.data.labels,
        datasets: [{
          label: chartData.title,
          data: chartData.data.values,
          backgroundColor: chartData.type === 'pie' 
            ? colors 
            : 'rgba(79, 70, 229, 0.8)',
          borderColor: 'rgba(79, 70, 229, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            display: chartData.type === 'pie',
            position: 'bottom'
          }
        },
        scales: chartData.type !== 'pie' ? {
          y: {
            beginAtZero: true
          }
        } : undefined
      }
    })

    chartInstances.value.push(chart)
  })
}

watch(() => props.charts, () => {
  renderCharts()
}, { deep: true })

onMounted(() => {
  renderCharts()
})
</script>

<style scoped>
.chart-panel {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-top: 24px;
  border: 1px solid #e5e7eb;
}

.chart-panel h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 20px 0;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.chart-item {
  background: #f9fafb;
  border-radius: 12px;
  padding: 16px;
}

.chart-item h4 {
  font-size: 14px;
  font-weight: 600;
  color: #4b5563;
  margin: 0 0 12px 0;
  text-align: center;
}

.chart-container {
  position: relative;
  height: 250px;
}

.chart-container canvas {
  max-height: 250px;
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-panel {
    padding: 16px;
  }
}
</style>
