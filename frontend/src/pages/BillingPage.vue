<template>
  <main class="min-h-screen pb-20 page-shell">
    <div class="container mx-auto max-w-6xl px-4">
      <!-- Hero Section -->
      <section class="page-hero space-y-4" data-reveal>
        <div class="page-hero__cloud" aria-hidden="true"></div>
        <p class="page-hero__kicker">Billing</p>
        <h1 class="page-hero__title">账单与发票</h1>
        <p class="page-hero__subtitle">查看订阅记录、额度包订单及下载发票。</p>
      </section>

      <!-- Main Content -->
      <section class="mt-8" data-reveal>
        <div class="page-card min-h-[400px]">
          <div class="flex items-center justify-between mb-6 border-b border-gray-100 dark:border-gray-800 pb-4">
            <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100">交易记录</h2>
            <button 
              @click="fetchBilling" 
              class="text-sm text-primary hover:text-primary-dark transition-colors flex items-center gap-1"
              :disabled="loading"
            >
              <ArrowPathIcon 
                class="h-4 w-4" 
                :class="{ 'animate-spin': loading }" 
              />
              刷新
            </button>
          </div>

          <div v-if="!user" class="text-center py-12">
            <p class="text-gray-500 mb-4">登录后查看账单信息</p>
            <button class="btn-primary px-6 py-2" @click="openLogin">去登录</button>
          </div>

          <div v-else-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {{ error }}
          </div>

          <div v-else-if="loading && !items.length" class="text-center py-12 text-gray-500">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-200 border-t-primary mb-2"></div>
            <p>加载中...</p>
          </div>

          <div v-else-if="!items.length" class="text-center py-16 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-dashed border-gray-200 dark:border-gray-700">
            <p class="text-gray-500 dark:text-gray-400">暂无账单记录</p>
          </div>

          <div v-else class="space-y-4">
            <!-- Desktop Header -->
            <div class="hidden md:grid grid-cols-5 gap-4 text-xs font-semibold text-gray-500 uppercase tracking-wider px-4">
              <div class="col-span-1">金额</div>
              <div class="col-span-1">状态</div>
              <div class="col-span-2">周期/时间</div>
              <div class="col-span-1 text-right">操作</div>
            </div>

            <!-- List Items -->
            <div
              v-for="item in items"
              :key="item.id"
              class="rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-slate-800/50 hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors p-4 md:grid md:grid-cols-5 md:gap-4 md:items-center"
            >
              <!-- Amount -->
              <div class="flex justify-between md:block col-span-1 mb-2 md:mb-0">
                <span class="md:hidden text-xs text-gray-500">金额</span>
                <span class="font-semibold text-gray-900 dark:text-gray-100 text-lg md:text-base">
                  {{ formatAmount(item.amount_cents, item.currency) }}
                </span>
              </div>

              <!-- Status -->
              <div class="flex justify-between md:block col-span-1 mb-2 md:mb-0">
                <span class="md:hidden text-xs text-gray-500">状态</span>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="statusClass(item.status)">
                  {{ formatStatus(item.status) }}
                </span>
              </div>

              <!-- Period/Date -->
              <div class="col-span-2 mb-3 md:mb-0 space-y-1">
                <div v-if="item.period_start && item.period_end" class="text-xs text-gray-600 dark:text-gray-300">
                  <span class="md:hidden text-gray-500 mr-2">周期:</span>
                  {{ formatDate(item.period_start) }} - {{ formatDate(item.period_end) }}
                </div>
                <div class="text-xs text-gray-500">
                  <span class="md:hidden mr-2">创建于:</span>
                  {{ formatDate(item.created_at) }}
                </div>
              </div>

              <!-- Actions -->
              <div class="col-span-1 text-right pt-3 md:pt-0 border-t border-gray-100 dark:border-gray-800 md:border-0">
                <button
                  v-if="item.invoice_url"
                  @click="openInvoice(item.invoice_url)"
                  class="inline-flex items-center text-xs font-semibold text-primary hover:text-primary-dark transition-colors bg-primary/5 hover:bg-primary/10 px-3 py-1.5 rounded-lg border border-primary/20"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  下载发票
                </button>
                <span v-else class="text-xs text-gray-400 italic">暂无发票</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Help Section -->
      <section class="mt-8 text-center text-xs text-gray-400" data-reveal>
        <p>如需开具公司发票或有其他支付问题，请联系客服支持。</p>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted, inject, watch } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useReveal } from '../composables/useReveal'
import { isSupabaseConfigured, supabase } from '../supabase'
import { ArrowPathIcon } from '@heroicons/vue/24/outline'

useReveal()
const { user } = useAuth()
const appActions = inject<{ openLogin: () => void }>('appActions')
const openLogin = () => appActions?.openLogin()

type BillingItem = {
  id: string
  amount_cents: number
  currency: string
  status: string
  period_start?: string | null
  period_end?: string | null
  invoice_url?: string | null
  created_at?: string | null
}

const loading = ref(false)
const error = ref('')
const items = ref<BillingItem[]>([])

const getSupabaseToken = async () => {
  if (!isSupabaseConfigured || !supabase) return null
  const { data } = await supabase.auth.getSession()
  return data.session?.access_token ?? null
}

const fetchBilling = async () => {
  if (!user.value) {
    items.value = []
    loading.value = false
    return
  }
  if (!isSupabaseConfigured) {
    error.value = '登录服务未配置'
    items.value = []
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const token = await getSupabaseToken()
    if (!token) throw new Error('未获取到登录凭证')
    
    const response = await fetch('/api/billing', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (!response.ok) {
      const text = await response.text()
      try {
        const errObj = JSON.parse(text)
        throw new Error(errObj.detail || '获取账单失败')
      } catch {
        throw new Error(`请求失败 (${response.status})`)
      }
    }
    
    items.value = await response.json()
  } catch (err: any) {
    error.value = err?.message || '获取账单失败'
    console.error(err)
  } finally {
    loading.value = false
  }
}

// Helpers
const formatAmount = (amount: number, currency: string) => {
  if (amount === undefined || amount === null) return '—'
  const value = (amount / 100).toFixed(2)
  return currency === 'CNY' ? `¥${value}` : `${value} ${currency}`
}

const formatDate = (value?: string | null) => {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleDateString()
}

const formatStatus = (status: string) => {
  switch (status) {
    case 'paid': return '已支付'
    case 'pending': return '待支付'
    case 'failed': return '失败'
    default: return status
  }
}

const statusClass = (status: string) => {
  switch (status) {
    case 'paid': return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
    case 'pending': return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300'
    case 'failed': return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300'
    default: return 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'
  }
}

const openInvoice = (url: string) => {
  window.open(url, '_blank', 'noopener')
}

onMounted(() => {
  fetchBilling()
})

watch(user, (newUser) => {
  if (newUser) {
    fetchBilling()
  } else {
    items.value = []
  }
})
</script>
