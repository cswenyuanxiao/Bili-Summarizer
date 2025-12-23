<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @mousedown.self="$emit('close')">
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-2xl overflow-hidden transform transition-all">
      <div class="p-6 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">账单与发票</h2>
          <p class="text-sm text-gray-500 dark:text-gray-400">查看订阅记录与发票</p>
        </div>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="p-6 space-y-4 max-h-[520px] overflow-y-auto">
        <div v-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {{ error }}
        </div>
        <div v-else-if="loading" class="text-center py-8 text-gray-500">加载中...</div>
        <div v-else-if="!items.length" class="text-center py-10 text-gray-500 bg-gray-50 dark:bg-gray-700/40 rounded-xl">
          暂无账单记录
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="item in items"
            :key="item.id"
            class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-slate-800 p-4 flex flex-col gap-3"
          >
            <div class="flex items-center justify-between">
              <div class="font-medium text-gray-900 dark:text-gray-100">
                {{ formatAmount(item.amount_cents, item.currency) }}
              </div>
              <span class="text-xs px-2 py-0.5 rounded-full" :class="statusClass(item.status)">
                {{ formatStatus(item.status) }}
              </span>
            </div>
            <div class="text-xs text-gray-500">
              账单周期 {{ formatDate(item.period_start) }} - {{ formatDate(item.period_end) }}
            </div>
            <div class="flex items-center justify-between text-xs text-gray-400">
              <span>账单创建 {{ formatDate(item.created_at) }}</span>
              <button
                v-if="item.invoice_url"
                @click="openInvoice(item.invoice_url)"
                class="text-primary hover:underline"
              >
                下载发票
              </button>
              <span v-else class="text-gray-300">暂无发票</span>
            </div>
          </div>
        </div>
      </div>

      <div class="px-6 py-4 bg-gray-50 dark:bg-gray-700/50 flex items-center justify-between text-xs text-gray-500">
        <span>需要发票请联系客服</span>
        <button
          @click="$emit('close')"
          class="px-3 py-1.5 text-sm text-gray-600 dark:text-gray-200 hover:text-primary"
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
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

defineProps<{
  show: boolean
  loading: boolean
  error: string
  items: BillingItem[]
}>()

defineEmits<{
  close: []
}>()

const formatAmount = (amount: number, currency: string) => {
  if (!amount) return `¥0`
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
    case 'paid':
      return '已支付'
    case 'pending':
      return '待支付'
    case 'failed':
      return '失败'
    default:
      return status
  }
}

const statusClass = (status: string) => {
  switch (status) {
    case 'paid':
      return 'bg-green-100 text-green-700'
    case 'pending':
      return 'bg-yellow-100 text-yellow-700'
    case 'failed':
      return 'bg-red-100 text-red-700'
    default:
      return 'bg-gray-100 text-gray-600'
  }
}

const openInvoice = (url: string) => {
  window.open(url, '_blank', 'noopener')
}
</script>
