<template>
  <div class="batch-page min-h-screen pb-20">
    <div class="container mx-auto max-w-4xl px-4 py-8">
      <header class="mb-10 text-center">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2 flex items-center justify-center gap-2">
          <span class="icon-chip text-primary/80">
            <BoltIcon class="h-5 w-5" />
          </span>
          批量总结
        </h1>
        <p class="text-gray-500 dark:text-gray-400">一次性总结多个视频，高效处理</p>
      </header>

      <!-- 输入区域 -->
      <div class="bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-white/40 dark:border-slate-800/50 shadow-xl rounded-2xl p-6 mb-8">
        <h2 class="text-lg font-semibold mb-4 flex items-center gap-2">
          <span class="icon-chip-sm text-primary/80">
            <ListBulletIcon class="h-4 w-4" />
          </span>
          视频URL列表
        </h2>
        <textarea
          v-model="urlsText"
          placeholder="每行一个视频URL，例如:&#10;https://www.bilibili.com/video/BV1xxx&#10;https://www.bilibili.com/video/BV1yyy"
          class="w-full h-40 px-4 py-3 rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 focus:ring-2 focus:ring-primary outline-none transition resize-none"
          :disabled="processing"
        ></textarea>
        
        <div class="flex items-center justify-between mt-4">
          <span class="text-sm text-gray-500">
            已输入 {{ urlList.length }} 个URL
          </span>
          <div class="flex gap-2">
            <button 
              class="px-6 py-2 bg-gray-100 dark:bg-slate-800 text-gray-700 dark:text-gray-300 rounded-lg font-semibold hover:bg-gray-200 dark:hover:bg-slate-700 transition"
              @click="clearUrls"
              :disabled="processing"
            >
              清空
            </button>
            <button 
              class="px-6 py-2 bg-gradient-to-r from-primary to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transition disabled:opacity-50"
              @click="startBatch"
              :disabled="processing || urlList.length === 0"
            >
              {{ processing ? '处理中...' : '开始批量总结' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 进度显示 -->
      <div v-if="tasks.length > 0" class="space-y-4">
        <div 
          v-for="task in tasks" 
          :key="task.url"
          class="bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-white/40 dark:border-slate-800/50 shadow-xl rounded-2xl p-5"
        >
          <div class="flex items-center justify-between mb-3">
            <div class="flex-1 mr-4">
              <div class="text-sm font-semibold text-gray-900 dark:text-gray-100 truncate">
                {{ task.url }}
              </div>
              <div class="text-xs text-gray-500 mt-1">
                {{ task.status }}
              </div>
            </div>
            <div class="flex-shrink-0">
              <span v-if="task.state === 'pending'" class="icon-chip-inline text-gray-400">
                <ClockIcon class="h-3.5 w-3.5" />
              </span>
              <span v-else-if="task.state === 'processing'" class="icon-chip-inline text-primary/80">
                <ArrowPathIcon class="h-3.5 w-3.5 animate-spin" />
              </span>
              <span v-else-if="task.state === 'done'" class="icon-chip-inline text-green-500/80">
                <CheckCircleIcon class="h-3.5 w-3.5" />
              </span>
              <span v-else-if="task.state === 'error'" class="icon-chip-inline text-red-500/80">
                <ExclamationCircleIcon class="h-3.5 w-3.5" />
              </span>
            </div>
          </div>

          <!-- 进度条 -->
          <div v-if="task.state === 'processing'" class="w-full bg-gray-200 dark:bg-slate-700 rounded-full h-2">
            <div 
              class="bg-gradient-to-r from-primary to-purple-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${task.progress}%` }"
            ></div>
          </div>

          <!-- 结果预览 -->
          <div v-if="task.summary" class="mt-3 pt-3 border-t border-gray-100 dark:border-slate-800">
            <p class="text-sm text-gray-600 dark:text-gray-300 line-clamp-2">
              {{ task.summary }}
            </p>
            <button 
              class="mt-2 text-xs text-primary hover:underline"
              @click="viewSummary(task)"
            >
              查看完整总结 →
            </button>
          </div>
          
          <!-- 错误信息 -->
          <div v-if="task.error" class="mt-3 pt-3 border-t border-gray-100 dark:border-slate-800">
            <p class="text-sm text-red-500">
              ❌ {{ task.error }}
            </p>
          </div>
        </div>
      </div>

      <!-- 统计信息 -->
      <div v-if="tasks.length > 0" class="mt-8 bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-white/40 dark:border-slate-800/50 shadow-xl rounded-2xl p-5">
        <div class="grid grid-cols-4 gap-4 text-center">
          <div>
            <div class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ tasks.length }}</div>
            <div class="text-xs text-gray-500">总数</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-blue-600">{{ taskStats.processing }}</div>
            <div class="text-xs text-gray-500">处理中</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-green-600">{{ taskStats.done }}</div>
            <div class="text-xs text-gray-500">已完成</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-red-600">{{ taskStats.error }}</div>
            <div class="text-xs text-gray-500">失败</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowPathIcon,
  BoltIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationCircleIcon,
  ListBulletIcon,
} from '@heroicons/vue/24/outline'
import { supabase } from '../supabase'
import { useHistorySync } from '../composables/useHistorySync'

// 引入历史记录同步功能
const { syncToCloud, getLocalHistory, saveLocalHistory } = useHistorySync()
const router = useRouter()

interface Task {
  url: string
  state: 'pending' | 'processing' | 'done' | 'error'
  status: string
  progress: number
  summary?: string
  error?: string
}

const urlsText = ref('')
const processing = ref(false)
const tasks = ref<Task[]>([])
const batchMode: 'smart' | 'video' = 'smart'
const batchFocus = 'default'

const urlList = computed(() => {
  return urlsText.value
    .split('\n')
    .map(line => line.trim())
    .filter(line => line && line.includes('bilibili.com'))
})

const taskStats = computed(() => {
  return {
    processing: tasks.value.filter(t => t.state === 'processing').length,
    done: tasks.value.filter(t => t.state === 'done').length,
    error: tasks.value.filter(t => t.state === 'error').length
  }
})

function clearUrls() {
  urlsText.value = ''
  tasks.value = []
}

async function startBatch() {
  processing.value = true
  
  // 初始化任务列表
  tasks.value = urlList.value.map(url => ({
    url,
    state: 'pending',
    status: '等待处理...',
    progress: 0
  }))

  try {
    // 检查supabase是否可用
    if (!supabase) {
      throw new Error('认证服务未配置')
    }
    
    // 获取认证token
    const { data: { session } } = await supabase.auth.getSession()
    
    if (!session) {
      throw new Error('请先登录')
    }

    // 调用批量总结API
    const response = await fetch('/api/batch/summarize', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${session.access_token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        urls: urlList.value,
        mode: batchMode,
        focus: batchFocus
      })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }

    const { job_id } = await response.json()

    // 轮询任务状态
    await pollBatchStatus(job_id, session.access_token)

  } catch (err: any) {
    // 所有任务标记为失败
    tasks.value.forEach(task => {
      task.state = 'error'
      task.status = '批量提交失败'
      task.error = err.message || String(err)
    })
  } finally {
    processing.value = false
  }
}

async function pollBatchStatus(jobId: string, token: string) {
  const maxAttempts = 120 // 最多轮询2分钟
  let attempts = 0
  let latestResults: Record<string, { summary?: string; transcript?: string }> | null = null
  let completed = false

  while (attempts < maxAttempts) {
    try {
      const response = await fetch(`/api/batch/${jobId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error(`轮询失败: HTTP ${response.status}`)
      }

      const data = await response.json()
      if (data?.results && Object.keys(data.results).length > 0) {
        latestResults = data.results
      }
      
      // 更新任务进度
      updateTasksFromBatchStatus(data)

      // 检查是否完成
      if (data.status === 'completed' || data.status === 'partial' || data.status === 'failed') {
        completed = true
        break
      }

      // 等待1秒后继续轮询
      await new Promise(resolve => setTimeout(resolve, 1000))
      attempts++

    } catch (err) {
      console.error('轮询错误:', err)
      break
    }
  }

  if (attempts >= maxAttempts) {
    tasks.value.forEach(task => {
      if (task.state === 'processing' || task.state === 'pending') {
        task.state = 'error'
        task.status = '处理超时'
        task.error = '任务处理时间过长，请稍后查看结果'
      }
    })
  }

  if (latestResults) {
    const infoMap = await fetchVideoInfoForUrls(Object.keys(latestResults))
    appendBatchResultsToHistory(latestResults, infoMap, batchMode, batchFocus)
  }

  // 批量总结完成后,刷新历史记录
  try {
    await syncToCloud()
    console.log('批量总结完成,历史记录已刷新')
  } catch (err) {
    console.error('历史记录刷新失败:', err)
  }

  if (completed) {
    try {
      await router.push({ name: 'home', query: { from: 'batch', t: Date.now().toString() } })
    } catch (err) {
      console.error('跳转主页失败:', err)
    }
  }
}

function updateTasksFromBatchStatus(batchData: any) {
  const { results, errors, progress } = batchData

  tasks.value.forEach(task => {
    // 检查是否有结果
    if (results && results[task.url]) {
      task.state = 'done'
      task.status = '总结完成'
      task.progress = 100
      task.summary = results[task.url].summary || '总结成功'
    } 
    // 检查是否有错误
    else if (errors && errors[task.url]) {
      task.state = 'error'
      task.status = '总结失败'
      task.error = errors[task.url]
      task.progress = 0
    }
    // 否则标记为处理中
    else if (task.state === 'pending') {
      task.state = 'processing'
      task.status = 'AI分析中...'
      task.progress = Math.min(progress || 0, 90)
    }
  })
}

async function fetchVideoInfoForUrls(urls: string[]) {
  const infoMap: Record<string, { title?: string; thumbnail?: string }> = {}
  await Promise.all(urls.map(async (url) => {
    try {
      const response = await fetch('/api/video-info', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      })
      if (!response.ok) {
        return
      }
      const data = await response.json()
      infoMap[url] = {
        title: data?.title || '',
        thumbnail: data?.thumbnail || ''
      }
    } catch (err) {
      console.error('批量获取视频信息失败:', err)
    }
  }))
  return infoMap
}

function appendBatchResultsToHistory(
  results: Record<string, { summary?: string; transcript?: string }>,
  infoMap: Record<string, { title?: string; thumbnail?: string }>,
  mode: 'smart' | 'video',
  focus: string
) {
  const history = getLocalHistory()
  const updatedMap = new Map<string, typeof history[number]>()

  history.forEach(item => {
    const key = `${item.video_url}|${item.mode}|${item.focus}`
    updatedMap.set(key, item)
  })

  Object.entries(results).forEach(([url, result]) => {
    const key = `${url}|${mode}|${focus}`
    const existing = updatedMap.get(key)
    const info = infoMap[url] || {}
    const now = new Date().toISOString()
    updatedMap.set(key, {
      id: existing?.id,
      video_url: url,
      video_title: existing?.video_title || info.title || '',
      video_thumbnail: existing?.video_thumbnail || info.thumbnail || '',
      mode,
      focus,
      summary: result.summary || existing?.summary || '',
      transcript: result.transcript || existing?.transcript || '',
      mindmap: existing?.mindmap || '',
      created_at: existing?.created_at || now,
      updated_at: now
    })
  })

  const merged = Array.from(updatedMap.values()).sort((a, b) => {
    const timeA = new Date(a.created_at || 0).getTime()
    const timeB = new Date(b.created_at || 0).getTime()
    return timeB - timeA
  })

  saveLocalHistory(merged.slice(0, 50))
}

function viewSummary(task: Task) {
  if (!task.summary) return
  
  // TODO: 显示详情弹窗或跳转到总结页面
  const message = `【${task.url}】\n\n${task.summary.substring(0, 500)}${task.summary.length > 500 ? '...' : ''}`
  alert(message)
}
</script>
