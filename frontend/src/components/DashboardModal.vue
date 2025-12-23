<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @mousedown.self="$emit('close')">
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-lg overflow-hidden transform transition-all">
      <div class="p-6 text-center border-b border-gray-100 dark:border-gray-700">
        <h2 class="text-2xl font-bold bg-gradient-to-r from-primary to-cyan-500 bg-clip-text text-transparent">
          账户仪表盘
        </h2>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
          额度与使用概览
        </p>
      </div>

      <div class="p-6 space-y-4">
        <div v-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {{ error }}
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-slate-900/40 p-4">
            <div class="text-xs uppercase tracking-wide text-gray-400">当前积分</div>
            <div class="mt-2 text-3xl font-semibold text-gray-900 dark:text-gray-100">
              {{ loading ? '...' : (data?.credits ?? '--') }}
            </div>
            <div class="mt-2 text-xs text-gray-500">
              每次总结消耗 {{ data?.cost_per_summary ?? 10 }} 积分
            </div>
          </div>
          <div class="rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-slate-900/40 p-4">
            <div class="text-xs uppercase tracking-wide text-gray-400">已使用次数</div>
            <div class="mt-2 text-3xl font-semibold text-gray-900 dark:text-gray-100">
              {{ loading ? '...' : (data?.total_used ?? '--') }}
            </div>
            <div class="mt-2 text-xs text-gray-500">
              剩余次数约 {{ remainingUses }}
            </div>
          </div>
        </div>

        <div class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-slate-800 p-4">
          <div class="flex items-center justify-between mb-3">
            <div class="text-sm font-semibold text-gray-900 dark:text-gray-100">近 14 天使用次数</div>
            <div class="text-xs text-gray-400">每日总结次数</div>
          </div>
          <div v-if="!chartPoints.length" class="text-xs text-gray-500">暂无数据</div>
          <svg v-else class="w-full h-28" viewBox="0 0 320 120" preserveAspectRatio="none">
            <polyline
              :points="chartPoints"
              fill="none"
              stroke="url(#usageGradient)"
              stroke-width="3"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <defs>
              <linearGradient id="usageGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stop-color="#4f46e5" />
                <stop offset="100%" stop-color="#06b6d4" />
              </linearGradient>
            </defs>
          </svg>
          <div class="mt-3 grid grid-cols-7 gap-2 text-[10px] text-gray-400">
            <span v-for="label in chartLabels" :key="label" class="text-center">{{ label }}</span>
          </div>
        </div>

        <div class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-slate-800 p-4 text-sm text-gray-600 dark:text-gray-300 space-y-3">
          <div class="flex items-center justify-between">
            <span>账号邮箱</span>
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ data?.email || '未绑定' }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span>当前套餐</span>
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ planLabel }}</span>
          </div>
          <div class="flex items-center justify-between text-xs text-gray-400">
            <span>到期时间</span>
            <span>{{ subscription?.current_period_end ? new Date(subscription.current_period_end).toLocaleDateString() : '无' }}</span>
          </div>
        </div>
      </div>

      <div class="px-6 py-4 bg-gray-50 dark:bg-gray-700/50 flex items-center justify-between text-xs text-gray-500">
        <span>新用户注册即送 30 积分</span>
        <div class="flex gap-2">
          <button
            @click="$emit('refresh')"
            class="px-3 py-1.5 text-sm bg-white dark:bg-slate-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors"
          >
            刷新
          </button>
          <button
            @click="$emit('upgrade')"
            class="px-3 py-1.5 text-sm text-primary border border-primary/40 rounded-lg hover:bg-primary/10 transition-colors"
          >
            升级
          </button>
          <button
            @click="$emit('close')"
            class="px-3 py-1.5 text-sm text-gray-600 dark:text-gray-200 hover:text-primary"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  show: boolean
  loading: boolean
  error: string
  data: {
    credits: number
    total_used: number
    cost_per_summary: number
    daily_usage?: { day: string; count: number }[]
    email?: string | null
  } | null
  subscription?: {
    plan: string
    status: string
    current_period_end?: string | null
  } | null
}>()

defineEmits<{
  close: []
  refresh: []
  upgrade: []
}>()

const remainingUses = computed(() => {
  if (!props.data) return '--'
  const cost = props.data.cost_per_summary || 10
  return Math.floor((props.data.credits || 0) / cost)
})

const planLabel = computed(() => {
  const plan = props.subscription?.plan
  const status = props.subscription?.status
  if (plan === 'pro' && status === 'active') return 'Pro 专业版'
  return '免费版'
})

const chartPoints = computed(() => {
  const entries = props.data?.daily_usage ?? []
  if (!entries.length) return ''
  const values = entries.map(item => item.count)
  const max = Math.max(1, ...values)
  const stepX = 320 / Math.max(1, values.length - 1)
  return values
    .map((value, index) => {
      const x = stepX * index
      const y = 110 - (value / max) * 90
      return `${x},${y}`
    })
    .join(' ')
})

const chartLabels = computed(() => {
  const entries = props.data?.daily_usage ?? []
  if (!entries.length) return []
  const labels = entries.map(item => item.day.slice(5))
  if (labels.length <= 7) return labels
  const step = Math.ceil(labels.length / 7)
  return labels.filter((_, index) => index % step === 0).slice(0, 7)
})
</script>
