<template>
  <div class="compare-page min-h-screen pb-20">
    <div class="container mx-auto max-w-5xl px-4 py-8">
      <header class="mb-10 text-center">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">视频对比分析</h1>
        <p class="text-gray-500 dark:text-gray-400">选择 2-4 个视频，由 AI 进行深度多维对比</p>
      </header>
      
      <!-- 选择区域 -->
      <section v-if="!comparing && !result" class="space-y-8 fade-up">
        <div class="bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-white/40 dark:border-slate-800/50 rounded-3xl p-8 shadow-sm">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-semibold flex items-center gap-2">
              <span class="icon-chip-sm text-primary/80">
                <VideoCameraIcon class="h-4 w-4" />
              </span>
              选择对比视频
            </h2>
            <span class="text-xs text-gray-400">最多可选 4 个</span>
          </div>
          
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <!-- 已选视频 -->
            <div 
              v-for="(video, index) in selectedVideos" 
              :key="video.id"
              class="relative group rounded-2xl overflow-hidden border border-gray-100 dark:border-slate-800 bg-gray-50 dark:bg-slate-900"
            >
              <img :src="video.thumbnail" class="w-full h-32 object-cover" />
              <div class="p-3">
                <div class="text-xs font-bold text-gray-900 dark:text-gray-100 line-clamp-2 h-8">
                  {{ video.title }}
                </div>
              </div>
              <button 
                class="absolute top-2 right-2 w-6 h-6 rounded-full bg-red-500 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                @click="removeVideo(index)"
              >
                ✕
              </button>
            </div>
            
            <!-- 添加按钮 -->
            <button 
              v-if="selectedVideos.length < 4"
              class="h-full min-h-[160px] rounded-2xl border-2 border-dashed border-gray-200 dark:border-slate-800 flex flex-col items-center justify-center gap-2 text-gray-400 hover:border-primary hover:text-primary transition-all bg-gray-50/50 dark:bg-slate-900/30"
              @click="showHistoryModal = true"
            >
              <span class="text-3xl">＋</span>
              <span class="text-sm">添加视频</span>
            </button>
          </div>
        </div>

        <!-- 对比维度 -->
        <div class="bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-white/40 dark:border-slate-800/50 rounded-3xl p-8 shadow-sm">
          <h2 class="text-lg font-semibold mb-6 flex items-center gap-2">
            <span class="icon-chip-sm text-primary/80">
              <AdjustmentsHorizontalIcon class="h-4 w-4" />
            </span>
            对比维度
          </h2>
          <div class="flex flex-wrap gap-3">
            <button 
              v-for="aspect in availableAspects" 
              :key="aspect"
              class="px-4 py-2 rounded-xl text-sm font-medium transition-all"
              :class="selectedAspects.includes(aspect) 
                ? 'bg-primary text-white shadow-md' 
                : 'bg-gray-100 dark:bg-slate-800 text-gray-500 hover:bg-gray-200 dark:hover:bg-slate-700'"
              @click="toggleAspect(aspect)"
            >
              {{ aspect }}
            </button>
          </div>
        </div>
        
        <!-- 开始对比 -->
        <div class="text-center">
          <button 
            class="px-12 py-4 bg-primary text-white rounded-2xl font-bold text-lg shadow-xl shadow-primary/20 hover:scale-105 transition-all disabled:opacity-50 disabled:grayscale disabled:hover:scale-100"
            :disabled="selectedVideos.length < 2"
            @click="startCompare"
          >
            开始 AI 对比分析
          </button>
          <p class="mt-4 text-xs text-gray-400">
            {{ selectedVideos.length < 2 ? '请至少选择 2 个视频' : 'AI 将分析视频的核心差异与共识' }}
          </p>
        </div>
      </section>
      
      <!-- 加载状态 -->
      <div v-if="comparing" class="py-20 flex flex-col items-center justify-center fade-up">
        <div class="relative w-24 h-24 mb-6">
          <div class="absolute inset-0 border-4 border-gray-100 dark:border-slate-800 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="icon-chip text-primary/80">
              <CpuChipIcon class="h-5 w-5" />
            </span>
          </div>
        </div>
        <h3 class="text-xl font-bold mb-2">AI 正在深度分析中</h3>
        <p class="text-gray-500 text-sm">正在提炼多个视频的观点差异，请稍候...</p>
        <div class="mt-8 w-64 h-1.5 bg-gray-100 dark:bg-slate-800 rounded-full overflow-hidden">
           <div class="h-full bg-primary animate-[shimmer_2s_infinite]"></div>
        </div>
      </div>
      
      <!-- 对比结果 -->
      <section v-if="result" class="space-y-8 fade-up">
        <div class="flex items-center justify-between">
          <h2 class="text-2xl font-bold italic">分析结果</h2>
          <button class="px-4 py-2 text-sm text-gray-500 hover:text-primary transition-colors" @click="resetCompare">
            ← 重新开始
          </button>
        </div>

        <!-- 分析总结 -->
        <div class="bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-white/40 dark:border-slate-800/50 rounded-3xl p-8 bg-gradient-to-br from-primary/5 to-purple-500/5 border-primary/20">
          <div class="text-sm font-semibold text-primary uppercase tracking-widest mb-3">Overall Analysis</div>
          <p class="text-lg sm:text-xl text-gray-800 dark:text-gray-200 leading-relaxed font-medium">
            {{ result.analysis_summary }}
          </p>
        </div>

        <!-- 对比表格 -->
        <div class="bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-white/40 dark:border-slate-800/50 rounded-3xl overflow-hidden shadow-lg">
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-gray-50/50 dark:bg-slate-900/50">
                  <th v-for="(header, i) in result.comparison_table.headers" :key="i" 
                      class="px-6 py-4 text-sm font-bold border-b border-gray-100 dark:border-slate-800"
                      :class="{ 'min-w-[150px]': i === 0 }">
                    {{ header }}
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100 dark:divide-slate-800">
                <tr v-for="(row, index) in result.comparison_table.rows" :key="index" class="hover:bg-gray-50/30 dark:hover:bg-slate-900/30 transition-colors">
                  <td v-for="(cell, i) in row" :key="i" class="px-6 py-5 text-sm" :class="{ 'font-bold bg-gray-50/30 dark:bg-slate-900/10': i === 0 }">
                    {{ cell }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- 关键差异 -->
          <div class="bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-white/40 dark:border-slate-800/50 rounded-3xl p-8">
            <h3 class="text-lg font-bold mb-6 flex items-center gap-2 text-orange-500">
              <span class="icon-chip-sm text-orange-500/80">
                <MagnifyingGlassIcon class="h-4 w-4" />
              </span>
              关键差异点
            </h3>
            <div class="space-y-6">
              <div 
                v-for="(diff, index) in result.key_differences" 
                :key="index"
                class="relative pl-6 border-l-2 border-orange-200 dark:border-orange-900/30"
              >
                <div class="font-bold text-gray-900 dark:text-gray-100 mb-2">{{ diff.topic }}</div>
                <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">{{ diff.description }}</p>
                <div class="flex flex-wrap gap-2">
                  <div 
                    v-for="(opinion, i) in diff.videos" 
                    :key="i"
                    class="px-2 py-1 bg-gray-100 dark:bg-slate-800 rounded text-[10px] text-gray-500"
                  >
                    V{{ i + 1 }}: {{ opinion }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 共识点 -->
          <div class="bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-white/40 dark:border-slate-800/50 rounded-3xl p-8">
            <h3 class="text-lg font-bold mb-6 flex items-center gap-2 text-green-500">
              <span class="icon-chip-sm text-green-500/80">
                <CheckCircleIcon class="h-4 w-4" />
              </span>
              核心共识
            </h3>
            <div class="space-y-6">
              <div 
                v-for="(point, index) in result.consensus_points" 
                :key="index"
                class="flex gap-4"
              >
                <div class="icon-chip-inline bg-green-100 dark:bg-green-900/30 text-green-600 flex items-center justify-center">
                  <CheckIcon class="h-3 w-3" />
                </div>
                <div>
                  <div class="font-bold text-gray-900 dark:text-gray-100 text-sm mb-1">{{ point.topic }}</div>
                  <p class="text-xs text-gray-500">{{ point.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 专家建议 -->
        <div v-if="result.recommendations?.length" class="bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-white/40 dark:border-slate-800/50 rounded-3xl p-8 border-l-8 border-primary">
          <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
            <span class="icon-chip-sm text-primary/80">
              <LightBulbIcon class="h-4 w-4" />
            </span>
            推荐建议
          </h3>
          <ul class="space-y-3">
            <li v-for="(rec, i) in result.recommendations" :key="i" class="flex items-start gap-3 text-gray-700 dark:text-gray-300">
              <span class="text-primary mt-1">•</span>
              <span class="text-sm leading-relaxed">{{ rec }}</span>
            </li>
          </ul>
        </div>
      </section>
      
      <!-- 历史记录选择弹窗 -->
      <HistorySelectModal
        v-if="showHistoryModal"
        :exclude-ids="selectedVideos.map(v => v.id)"
        @close="showHistoryModal = false"
        @select="addVideo"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  AdjustmentsHorizontalIcon,
  CheckCircleIcon,
  CheckIcon,
  CpuChipIcon,
  LightBulbIcon,
  MagnifyingGlassIcon,
  VideoCameraIcon,
} from '@heroicons/vue/24/outline'
import HistorySelectModal from '../components/HistorySelectModal.vue'

interface VideoItem {
  id: string
  title: string
  thumbnail: string
  summary: string
  created_at: string
}

interface CompareResult {
  comparison_table: {
    headers: string[]
    rows: string[][]
  }
  key_differences: Array<{
    topic: string
    description: string
    videos: string[]
  }>
  consensus_points: Array<{
    topic: string
    description: string
  }>
  analysis_summary: string
  recommendations: string[]
  video_titles: string[]
}

const selectedVideos = ref<VideoItem[]>([])
const selectedAspects = ref<string[]>(['核心观点', '方法论', '优势与不足', '结论'])
const showHistoryModal = ref(false)
const comparing = ref(false)
const result = ref<CompareResult | null>(null)

const availableAspects = [
  '核心观点', '方法论', '优势与不足', '结论', '适用场景', '数据支撑', '表达风格'
]

function addVideo(video: any) {
  if (selectedVideos.value.length < 4) {
    selectedVideos.value.push(video)
  }
  showHistoryModal.value = false
}

function removeVideo(index: number) {
  selectedVideos.value.splice(index, 1)
}

function toggleAspect(aspect: string) {
  const index = selectedAspects.value.indexOf(aspect)
  if (index > -1) {
    selectedAspects.value.splice(index, 1)
  } else {
    selectedAspects.value.push(aspect)
  }
}

async function startCompare() {
  if (selectedVideos.value.length < 2) return
  
  comparing.value = true
  
  try {
    const token = localStorage.getItem('supabase_token')
    const response = await fetch('/api/compare/direct', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token || ''}`
      },
      body: JSON.stringify({
        summaries: selectedVideos.value.map(v => ({
          id: v.id,
          title: v.title,
          summary: v.summary
        })),
        aspects: selectedAspects.value.length > 0 ? selectedAspects.value : undefined
      })
    })
    
    if (!response.ok) {
      throw new Error('对比失败')
    }
    
    result.value = await response.json()
    
  } catch (error) {
    console.error('Compare failed:', error)
    alert('对比分析失败，请稍后刷新重试')
  } finally {
    comparing.value = false
  }
}

function resetCompare() {
  result.value = null
  selectedVideos.value = []
}

</script>

<style scoped>
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}



.fade-up {
  animation: fadeUp 0.6s ease-out forwards;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
