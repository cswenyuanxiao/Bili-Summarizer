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
        <p class="mt-2 text-xs text-gray-400">
          登录后会启用积分校验，积分不足将引导升级。
        </p>
      </div>

      <!-- Pricing Plans -->
      <div class="grid md:grid-cols-2 gap-0">
        <!-- Free Plan -->
        <div class="p-8 border-r border-gray-100 dark:border-gray-700 card-hover-elevate">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold dark:text-gray-200">免费版</h3>
            <span class="badge-pill badge-soft">基础</span>
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
        <div class="p-8 bg-gray-50/50 dark:bg-gray-700/20 relative card-hover-elevate">
          <div class="absolute top-4 right-4">
            <span class="badge-pill badge-accent">推荐</span>
          </div>
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-primary">Pro 专业版</h3>
            <span class="badge-pill">高价值</span>
          </div>
          <div class="mb-6 space-y-1">
            <div class="flex items-baseline gap-2">
              <span class="text-4xl font-bold dark:text-white">¥9.9</span>
              <span class="text-gray-400">/月</span>
            </div>
            <div class="text-xs text-gray-400">年付 ¥99 / 年（约省 2 个月）</div>
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
          <div class="space-y-3">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <button 
                @click="handlePayment('pro_monthly', 'alipay')"
                :disabled="loading || subscriptionUnavailable || !isSupabaseConfigured"
                class="w-full py-2.5 rounded-xl bg-gradient-to-r from-primary to-purple-600 text-white font-medium hover:shadow-lg hover:scale-105 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {{ subscriptionUnavailable ? '暂未开放' : (loading ? '处理中...' : '支付宝月付') }}
              </button>
              <button 
                @click="handlePayment('pro_monthly', 'wechat')"
                :disabled="loading || subscriptionUnavailable || !isSupabaseConfigured"
                class="w-full py-2.5 rounded-xl border border-primary/50 text-primary font-medium hover:bg-primary/10 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {{ subscriptionUnavailable ? '暂未开放' : (loading ? '处理中...' : '微信月付') }}
              </button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <button 
                @click="handlePayment('pro_yearly', 'alipay')"
                :disabled="loading || subscriptionUnavailable || !isSupabaseConfigured"
                class="w-full py-2.5 rounded-xl bg-gray-900 text-white font-medium hover:shadow-lg hover:scale-105 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {{ subscriptionUnavailable ? '暂未开放' : (loading ? '处理中...' : '支付宝年付') }}
              </button>
              <button 
                @click="handlePayment('pro_yearly', 'wechat')"
                :disabled="loading || subscriptionUnavailable || !isSupabaseConfigured"
                class="w-full py-2.5 rounded-xl border border-gray-800 text-gray-800 dark:text-gray-100 font-medium hover:bg-gray-100 dark:hover:bg-gray-700 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {{ subscriptionUnavailable ? '暂未开放' : (loading ? '处理中...' : '微信年付') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="border-t border-gray-100 dark:border-gray-700 px-8 py-6 space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold dark:text-gray-200">一次性额度包</h3>
          <span class="badge-pill badge-soft">按需补充</span>
        </div>
        <div class="grid md:grid-cols-2 gap-4">
          <div class="rounded-2xl border border-gray-100 dark:border-gray-700 p-5 card-hover-elevate">
            <div class="flex items-center justify-between">
              <div class="text-base font-semibold">Starter Pack</div>
              <span class="badge-pill">30 积分</span>
            </div>
            <div class="mt-2 text-3xl font-bold">¥19</div>
            <div class="mt-4 grid grid-cols-2 gap-2">
              <button
                @click="handlePayment('starter_pack', 'alipay')"
                :disabled="loading || subscriptionUnavailable || !isSupabaseConfigured"
                class="py-2 rounded-lg bg-primary text-white text-sm font-medium hover:shadow-md transition disabled:opacity-70 disabled:cursor-not-allowed"
              >
                支付宝购买
              </button>
              <button
                @click="handlePayment('starter_pack', 'wechat')"
                :disabled="loading || subscriptionUnavailable || !isSupabaseConfigured"
                class="py-2 rounded-lg border border-primary/40 text-primary text-sm font-medium hover:bg-primary/10 transition disabled:opacity-70 disabled:cursor-not-allowed"
              >
                微信购买
              </button>
            </div>
          </div>
          <div class="rounded-2xl border border-gray-100 dark:border-gray-700 p-5 card-hover-elevate">
            <div class="flex items-center justify-between">
              <div class="text-base font-semibold">Creator Pack</div>
              <span class="badge-pill badge-accent">120 积分</span>
            </div>
            <div class="mt-2 text-3xl font-bold">¥49</div>
            <div class="mt-4 grid grid-cols-2 gap-2">
              <button
                @click="handlePayment('creator_pack', 'alipay')"
                :disabled="loading || subscriptionUnavailable || !isSupabaseConfigured"
                class="py-2 rounded-lg bg-primary text-white text-sm font-medium hover:shadow-md transition disabled:opacity-70 disabled:cursor-not-allowed"
              >
                支付宝购买
              </button>
              <button
                @click="handlePayment('creator_pack', 'wechat')"
                :disabled="loading || subscriptionUnavailable || !isSupabaseConfigured"
                class="py-2 rounded-lg border border-primary/40 text-primary text-sm font-medium hover:bg-primary/10 transition disabled:opacity-70 disabled:cursor-not-allowed"
              >
                微信购买
              </button>
            </div>
          </div>
        </div>
        <div class="text-xs text-gray-400">
          额度包用于补充积分，不影响订阅状态。
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

const handlePayment = async (planId: string, provider: 'alipay' | 'wechat') => {
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
            body: JSON.stringify({ plan_id: planId, provider })
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
