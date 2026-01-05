<template>
  <main class="min-h-screen pb-20 page-shell">
    <div class="container mx-auto max-w-6xl px-4">
      <section class="page-hero space-y-4" data-reveal>
        <div class="page-hero__cloud" aria-hidden="true"></div>
        <p class="page-hero__kicker">Dashboard</p>
        <h1 class="page-hero__title">仪表盘</h1>
        <p class="page-hero__subtitle">总览您的积分使用情况、历史记录与订阅状态。</p>
      </section>

      <div v-if="!user" class="mt-8 page-card text-center" data-reveal>
         <p class="text-gray-600 dark:text-gray-300 mb-4">登录后可查看详细数据</p>
         <button class="btn-primary px-6 py-2" @click="openLogin">去登录</button>
      </div>

      <div v-else class="mt-8 space-y-8" data-reveal>
        <!-- Badges -->
        <section class="page-card">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100">我的成就</h3>
            <span class="text-xs text-gray-400">本地记录</span>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div
              v-for="badge in badges"
              :key="badge.id"
              class="flex flex-col items-center gap-2 rounded-xl border border-gray-100 dark:border-slate-800 px-3 py-4"
              :class="unlockedIds.includes(badge.id) ? 'bg-white dark:bg-slate-900' : 'bg-gray-50 dark:bg-slate-800/40 opacity-50'"
            >
              <div class="text-2xl">{{ badge.icon }}</div>
              <div class="text-sm font-semibold text-gray-800 dark:text-gray-100">{{ badge.title }}</div>
              <div class="text-xs text-gray-500 text-center">{{ badge.description }}</div>
            </div>
          </div>
        </section>

        <!-- Top Stats Cards -->
        <section class="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div class="page-card relative overflow-hidden group">
            <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
               <ChartBarIcon class="w-16 h-16 text-primary" />
            </div>
            <div class="text-sm text-gray-500">当前积分</div>
            <div class="mt-2 text-3xl font-bold text-gray-900 dark:text-gray-100">
              <template v-if="loading">...</template>
              <template v-else-if="isProActive">∞</template>
              <template v-else>{{ dashboardData?.credits ?? '--' }}</template>
            </div>
            <div class="mt-2 text-xs text-gray-400">
              <template v-if="isProActive">Pro 无限次使用</template>
              <template v-else>每次消耗 {{ dashboardData?.cost_per_summary ?? 10 }} 积分</template>
            </div>
          </div>

          <div class="page-card relative overflow-hidden group page-card--accent">
             <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
               <ClockIcon class="w-16 h-16 text-purple-600" />
            </div>
            <div class="text-sm text-gray-500">总计使用</div>
            <div class="mt-2 text-3xl font-bold text-gray-900 dark:text-gray-100">
              {{ loading ? '...' : (dashboardData?.total_used ?? '--') }} <span class="text-base font-normal text-gray-500">次</span>
            </div>
            <div class="mt-2 text-xs text-gray-400">
               累计节省时间约 {{ ((dashboardData?.total_used || 0) * 15 / 60).toFixed(1) }} 小时
            </div>
          </div>

          <div class="page-card relative overflow-hidden group">
             <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
               <ReceiptPercentIcon class="w-16 h-16 text-green-600" />
            </div>
            <div class="text-sm text-gray-500">订阅计划</div>
            <div class="mt-2 text-lg font-semibold text-gray-900 dark:text-gray-100 truncate">
              {{ loading ? '...' : planLabel }}
            </div>
            <button class="mt-2 text-xs text-primary hover:underline font-medium" @click="openPricing">
              {{ isProActive ? '管理订阅 →' : '升级 Pro →' }}
            </button>
          </div>
        </section>

        <!-- Main Content Area: Chart and History -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
           <!-- Left Column: Usage Chart & Account Info -->
           <div class="lg:col-span-2 space-y-6">
              <!-- Usage Chart -->
              <div class="page-card">
                 <div class="flex items-center justify-between mb-6">
                    <div>
                       <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100">使用趋势</h3>
                       <p class="text-xs text-gray-500 mt-1">近 14 天每日总结次数</p>
                    </div>
                    <select v-model="chartRange" class="text-xs border-gray-200 rounded-md bg-gray-50 dark:bg-slate-800 dark:border-slate-700">
                       <option value="14">近 14 天</option>
                       <option value="7">近 7 天</option>
                    </select>
                 </div>
                 
                 <div v-if="loading" class="h-40 flex items-center justify-center text-gray-400 text-sm">加载中...</div>
                 <div v-else-if="!chartPoints" class="h-40 flex items-center justify-center text-gray-400 text-sm">暂无数据</div>
                 <div v-else class="relative h-48 w-full">
                    <svg class="w-full h-full overflow-visible" viewBox="0 0 320 120" preserveAspectRatio="none">
                        <!-- Grid Lines -->
                        <line x1="0" y1="20" x2="320" y2="20" stroke="currentColor" class="text-gray-100 dark:text-slate-800" stroke-width="1" />
                        <line x1="0" y1="50" x2="320" y2="50" stroke="currentColor" class="text-gray-100 dark:text-slate-800" stroke-width="1" />
                        <line x1="0" y1="80" x2="320" y2="80" stroke="currentColor" class="text-gray-100 dark:text-slate-800" stroke-width="1" />
                        
                        <!-- Area Fill -->
                        <path :d="`M0,120 ${chartPoints} L320,120 Z`" class="fill-primary/5 dark:fill-primary/10" />
                        
                        <!-- Line -->
                        <polyline
                          :points="chartPoints"
                          fill="none"
                          stroke="url(#usageGradient)"
                          stroke-width="3"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          class="drop-shadow-sm"
                        />
                        <defs>
                          <linearGradient id="usageGradient" x1="0" y1="0" x2="1" y2="0">
                            <stop offset="0%" stop-color="#4f46e5" />
                            <stop offset="100%" stop-color="#06b6d4" />
                          </linearGradient>
                        </defs>
                    </svg>
                 </div>
                 
                 <div class="mt-4 flex justify-between text-[10px] text-gray-400 uppercase font-mono">
                    <span v-for="label in chartLabels" :key="label">{{ label }}</span>
                 </div>
              </div>

              <!-- History Text List -->
              <div class="page-card">
                 <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100">积分记录</h3>
                    <button class="text-xs text-primary hover:underline" @click="fetchDashboard">刷新</button>
                 </div>
                 
                 <div v-if="!dashboardData?.credit_history?.length" class="text-center py-8 text-gray-500 text-sm">
                   暂无记录
                 </div>
                 <div v-else class="space-y-0 divide-y divide-gray-100 dark:divide-slate-800">
                    <div v-for="(item, index) in dashboardData.credit_history" :key="index" class="py-3 flex items-start justify-between group hover:bg-gray-50 dark:hover:bg-slate-800/50 -mx-6 px-6 transition-colors">
                       <div>
                          <div class="flex items-center gap-2">
                             <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
                               {{ item.type === 'consume' ? '总结消耗' : (item.type === 'grant' ? '系统赠送' : '充值获得') }}
                             </span>
                             <span class="text-[10px] text-gray-400">{{ new Date(item.created_at).toLocaleString() }}</span>
                          </div>
                          <div v-if="parseMetadata(item.metadata)?.url" class="mt-1 text-xs text-gray-500 font-mono truncate max-w-[200px] sm:max-w-xs" :title="parseMetadata(item.metadata)?.url">
                             {{ parseMetadata(item.metadata)?.url }}
                          </div>
                       </div>
                       <div :class="item.type === 'consume' ? 'text-red-500' : 'text-green-500'" class="font-mono font-semibold text-sm">
                          {{ item.type === 'consume' ? '-' : '+' }}{{ item.cost }}
                       </div>
                    </div>
                 </div>
              </div>
           </div>

           <!-- Right Column: Account Quick Actions -->
           <div class="lg:col-span-1 space-y-6">
              <div class="page-card bg-gradient-to-br from-gray-900 to-gray-800 text-white dark:border-gray-700">
                 <h3 class="text-lg font-bold mb-1">账号信息</h3>
                 <div class="text-sm opacity-80 mb-6 font-mono">{{ dashboardData?.email || user.email || '未绑定' }}</div>
                 
                 <div class="space-y-4 text-sm">
                    <div class="flex justify-between items-center py-2 border-t border-white/10">
                       <span class="opacity-70">UID</span>
                       <span class="font-mono">{{ user.id.slice(0, 8) }}...</span>
                    </div>
                    <div class="flex justify-between items-center py-2 border-t border-white/10">
                       <span class="opacity-70">注册时间</span>
                       <span>{{ new Date(user.created_at || Date.now()).toLocaleDateString() }}</span>
                    </div>
                 </div>
              </div>

              <div class="page-card">
                 <h3 class="text-sm font-bold text-gray-900 dark:text-gray-100 uppercase tracking-wider mb-4">快捷操作</h3>
                 <nav class="flex flex-col gap-2">
                    <RouterLink to="/billing" class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors text-sm text-gray-600 dark:text-gray-300">
                       <ReceiptPercentIcon class="w-4 h-4" />
                       账单与发票
                    </RouterLink>
                    <button @click="$router.push('/subscriptions')" class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors text-sm text-gray-600 dark:text-gray-300">
                       <BellIcon class="w-4 h-4" />
                       管理订阅
                    </button>
                    <button @click="$router.push('/teams')" class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors text-sm text-gray-600 dark:text-gray-300">
                       <UsersIcon class="w-4 h-4" />
                       我的团队
                    </button>
                    <button @click="$router.push('/invite')" class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors text-sm text-gray-600 dark:text-gray-300">
                       <GiftIcon class="w-4 h-4" />
                       邀请奖励
                    </button>
                 </nav>
              </div>
           </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { inject, ref, onMounted, watch, computed } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useBadges } from '../composables/useBadges'
import { useReveal } from '../composables/useReveal'
import { useChartData } from '../composables/useChartData'
import { isSupabaseConfigured, supabase } from '../supabase'
import { 
  ChartBarIcon, 
  ClockIcon, 
  ReceiptPercentIcon, 
  UsersIcon, 
  BellIcon, 
  GiftIcon 
} from '@heroicons/vue/24/outline'

const { user } = useAuth()
const { badges, unlockedIds } = useBadges()
useReveal()
const appActions = inject<{ openLogin: () => void; openPricing: () => void }>('appActions')
const openLogin = () => appActions?.openLogin()
const openPricing = () => appActions?.openPricing()

const loading = ref(false)
const chartRange = ref('14')
const dashboardData = ref<{
  credits: number
  total_used: number
  cost_per_summary: number
  is_pro_active?: boolean
  daily_usage?: { day: string; count: number }[]
  credit_history?: {
    type: string
    cost: number
    metadata: string | null
    created_at: string
  }[]
  email?: string | null
} | null>(null)

const subscriptionData = ref<{
  plan: string
  status: string
} | null>(null)

const getSupabaseToken = async () => {
  if (!isSupabaseConfigured || !supabase) return null
  const { data } = await supabase.auth.getSession()
  return data.session?.access_token ?? null
}

// 统一的 Pro 状态判断
const isProActive = computed(() => {
  return (subscriptionData.value?.plan === 'pro' && 
          subscriptionData.value?.status === 'active') ||
         dashboardData.value?.is_pro_active === true
})

const planLabel = computed(() => {
  return isProActive.value ? 'Pro 专业版' : '免费版'
})

// 使用 composable 处理图表数据
const dailyUsageRef = computed(() => dashboardData.value?.daily_usage)
const { chartPoints, chartLabels } = useChartData(dailyUsageRef, chartRange)

const parseMetadata = (jsonStr: string | null) => {
  if (!jsonStr) return null
  try {
    return JSON.parse(jsonStr)
  } catch {
    return null
  }
}

const fetchDashboard = async () => {
  if (!user.value) {
    dashboardData.value = null
    subscriptionData.value = null
    return
  }
  loading.value = true
  try {
    const token = await getSupabaseToken()
    if (!token) return
    
    // Parallel fetch
    const [dashRes, subRes] = await Promise.all([
      fetch('/api/dashboard', { headers: { Authorization: `Bearer ${token}` } }),
      fetch('/api/subscription', { headers: { Authorization: `Bearer ${token}` } })
    ])
    
    if (dashRes.ok) dashboardData.value = await dashRes.json()
    if (subRes.ok) subscriptionData.value = await subRes.json()
    
  } catch (error) {
    console.error('Failed to fetch dashboard:', error)
  } finally {
    loading.value = false
  }
}

// 使用防抖避免频繁刷新（1秒内多次调用只执行一次）
import { useDebounceFn } from '@vueuse/core'
const debouncedFetchDashboard = useDebounceFn(fetchDashboard, 1000)

onMounted(fetchDashboard)
watch(user, debouncedFetchDashboard)
</script>
