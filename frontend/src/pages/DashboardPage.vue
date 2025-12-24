<template>
  <main class="min-h-screen pb-20 page-shell">
    <div class="container mx-auto max-w-6xl px-4">
      <section class="page-hero space-y-4" data-reveal>
        <div class="page-hero__cloud" aria-hidden="true"></div>
        <p class="page-hero__kicker">Dashboard</p>
        <h1 class="page-hero__title">仪表盘</h1>
        <p class="page-hero__subtitle">查看积分余额、使用趋势与订阅状态。</p>
        <div class="flex flex-wrap gap-3">
          <button class="btn-primary px-5 py-2 text-sm wiggle-soft" @click="openDashboard">打开仪表盘</button>
          <span class="badge-pill badge-soft">实时更新</span>
        </div>
      </section>

      <section v-if="user" class="grid grid-cols-1 md:grid-cols-3 gap-5 text-sm text-gray-600 dark:text-gray-300 mt-8" data-reveal>
        <div class="page-card">
          <div class="text-sm text-gray-500">当前积分</div>
          <div class="mt-2 text-3xl font-bold text-gray-900 dark:text-gray-100">
            <template v-if="loading">...</template>
            <template v-else-if="dashboardData?.is_pro_active">∞</template>
            <template v-else>{{ dashboardData?.credits ?? '--' }}</template>
          </div>
          <div class="mt-2 text-xs text-gray-400">
            <template v-if="dashboardData?.is_pro_active">Pro 无限使用</template>
            <template v-else>已使用 {{ dashboardData?.total_used ?? 0 }} 次</template>
          </div>
        </div>

        <div class="page-card page-card--accent">
          <div class="text-sm text-gray-500">每次消耗</div>
          <div class="mt-2 text-3xl font-bold text-gray-900 dark:text-gray-100">
            {{ dashboardData?.cost_per_summary ?? 10 }} <span class="text-base">积分</span>
          </div>
          <div class="mt-2 text-xs text-gray-400">按次计费</div>
        </div>

        <div class="page-card">
          <div class="text-sm text-gray-500">订阅状态</div>
          <div class="mt-2 text-lg font-semibold text-gray-900 dark:text-gray-100">
            {{ loading ? '...' : getSubscriptionLabel(subscriptionData?.plan) }}
          </div>
          <button class="mt-2 text-xs text-primary hover:underline" @click="openPricing">
            升级 Pro →
          </button>
        </div>
      </section>

      <section class="mt-8 text-sm text-gray-600 dark:text-gray-300" data-reveal>
        <div v-if="!user" class="page-card">
          登录后可查看仪表盘数据。
          <button class="ml-2 text-xs font-semibold text-primary hover:underline" @click="openLogin">去登录</button>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { inject, ref, onMounted, watch } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useReveal } from '../composables/useReveal'
import { isSupabaseConfigured, supabase } from '../supabase'

const { user } = useAuth()
useReveal()
const appActions = inject<{ openLogin: () => void; openDashboard: () => void; openPricing: () => void }>('appActions')
const openLogin = () => appActions?.openLogin()
const openDashboard = () => appActions?.openDashboard()
const openPricing = () => appActions?.openPricing()

const loading = ref(false)
const dashboardData = ref<{
  credits: number
  total_used: number
  cost_per_summary: number
  is_pro_active?: boolean  // Pro 是否激活
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

const getSubscriptionLabel = (plan?: string) => {
  if (!plan || plan === 'free') return '免费版'
  if (plan === 'pro') return 'Pro 专业版'
  return plan
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
    
    // Fetch dashboard data
    const dashboardResponse = await fetch('/api/dashboard', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (dashboardResponse.ok) {
      dashboardData.value = await dashboardResponse.json()
    }
    
    // Fetch subscription data
    const subscriptionResponse = await fetch('/api/subscription', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (subscriptionResponse.ok) {
      subscriptionData.value = await subscriptionResponse.json()
    }
  } catch (error) {
    console.error('Failed to fetch dashboard:', error)
  } finally {
    loading.value = false
  }
}

onMounted(fetchDashboard)
watch(user, fetchDashboard)
</script>
