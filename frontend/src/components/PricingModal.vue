<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @mousedown.self="$emit('close')">
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-2xl overflow-hidden transform transition-all">
      
      <!-- Header -->
      <div class="p-8 text-center border-b border-gray-100 dark:border-gray-700 bg-gradient-to-b from-primary/5 to-transparent">
        <h2 class="text-3xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
          升级到 Pro 专业版
        </h2>
        <p class="mt-3 text-gray-500 dark:text-gray-400">
          解锁无限能，释放 AI 全部潜力
        </p>
      </div>

      <!-- Pricing Plans -->
      <div class="grid md:grid-cols-2 gap-0">
        <!-- Free Plan -->
        <div class="p-8 border-r border-gray-100 dark:border-gray-700">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold dark:text-gray-200">免费版</h3>
          </div>
          <div class="mb-6">
             <span class="text-4xl font-bold dark:text-white">¥0</span>
             <span class="text-gray-400">/永久</span>
          </div>
          <ul class="space-y-3 mb-8">
            <li class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <svg class="w-5 h-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              每日 3 次总结
            </li>
            <li class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <svg class="w-5 h-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              标准响应速度
            </li>
            <li class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <svg class="w-5 h-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              基础思维导图
            </li>
          </ul>
          <button class="w-full py-2.5 rounded-xl border border-gray-200 dark:border-gray-600 text-gray-500 cursor-default" disabled>
            当前套餐
          </button>
        </div>

        <!-- Pro Plan -->
        <div class="p-8 bg-gray-50/50 dark:bg-gray-700/20 relative">
          <div class="absolute top-0 right-0 bg-gradient-to-l from-purple-500 to-indigo-500 text-white text-xs font-bold px-3 py-1 rounded-bl-xl">
            推荐
          </div>
           <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-primary">Pro 专业版</h3>
          </div>
          <div class="mb-6">
             <span class="text-4xl font-bold dark:text-white">¥9.9</span>
             <span class="text-gray-400">/月</span>
          </div>
          <ul class="space-y-3 mb-8">
            <li class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-200 font-medium">
              <svg class="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              无限次总结
            </li>
            <li class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-200 font-medium">
              <svg class="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              优先队列处理 (极速)
            </li>
            <li class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-200 font-medium">
              <svg class="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              高级导出功能 (PPT/PDF)
            </li>
             <li class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-200 font-medium">
              <svg class="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              7x24 专属客服
            </li>
          </ul>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <button 
              @click="handleSubscribe('alipay')"
              :disabled="loading || subscriptionUnavailable || !isSupabaseConfigured"
              class="w-full py-2.5 rounded-xl bg-gradient-to-r from-primary to-purple-600 text-white font-medium hover:shadow-lg hover:scale-105 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {{ subscriptionUnavailable ? '暂未开放' : (loading ? '处理中...' : '支付宝升级') }}
            </button>
            <button 
              @click="handleSubscribe('wechat')"
              :disabled="loading || subscriptionUnavailable || !isSupabaseConfigured"
              class="w-full py-2.5 rounded-xl border border-primary/50 text-primary font-medium hover:bg-primary/10 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {{ subscriptionUnavailable ? '暂未开放' : (loading ? '处理中...' : '微信升级') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '../composables/useAuth'
import { isSupabaseConfigured } from '../supabase'

defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close', 'success'])
const { user } = useAuth()
const loading = ref(false)
const subscriptionUnavailable = ref(false)

const handleSubscribe = async (provider: 'alipay' | 'wechat') => {
    if (!isSupabaseConfigured) {
        alert('当前环境未配置登录服务，无法订阅。')
        return
    }
    if (!user.value) {
        alert('请先登录')
        return
    }

    loading.value = true
    try {
        // Get token
        const { data: { session } } = await import('../supabase').then(m => m.supabase.auth.getSession())
        const token = session?.access_token

        const res = await fetch('/api/payments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ plan_id: 'pro_monthly', provider })
        })

        if (res.status === 404 || res.status === 501) {
            subscriptionUnavailable.value = true
            throw new Error('订阅功能暂未开放')
        }
        if (!res.ok) throw new Error('订阅失败')
        
        const data = await res.json()
        if (data.payment_url) {
          window.open(data.payment_url, '_blank', 'noopener')
          alert('已打开支付页面，请完成支付。')
          emit('success')
        } else {
          alert('支付已创建，请等待支付回调完成升级。')
        }
    } catch (e: any) {
        alert(e.message)
    } finally {
        loading.value = false
    }
}
</script>
