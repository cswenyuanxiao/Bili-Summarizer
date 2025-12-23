<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @mousedown.self="$emit('close')">
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-lg overflow-hidden transform transition-all">
      <div class="p-6 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">邀请好友</h2>
          <p class="text-sm text-gray-500 dark:text-gray-400">邀请成功双方各得 10 积分</p>
        </div>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="p-6 space-y-5">
        <div v-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {{ error }}
        </div>
        <div class="rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-slate-900/40 p-4">
          <div class="text-xs uppercase tracking-wide text-gray-400">我的邀请码</div>
          <div class="mt-3 flex items-center justify-between gap-3">
            <div class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {{ inviteCode || '未生成' }}
            </div>
            <button
              @click="handleCreateCode"
              class="px-3 py-1.5 text-sm bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
            >
              生成邀请码
            </button>
            <button
              v-if="inviteCode"
              @click="copyCode"
              class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-white dark:hover:bg-slate-800 transition-colors"
            >
              复制
            </button>
          </div>
          <div class="mt-2 text-xs text-gray-500">已邀请 {{ totalRedeemed }} 人</div>
        </div>

        <div class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-slate-800 p-4 space-y-3">
          <div class="text-sm font-medium text-gray-900 dark:text-gray-100">兑换邀请码</div>
          <div class="flex gap-2">
            <input
              v-model="redeemCode"
              type="text"
              placeholder="输入好友邀请码"
              class="flex-1 px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-900"
            />
            <button
              @click="handleRedeem"
              class="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors"
            >
              兑换
            </button>
          </div>
        </div>
      </div>

      <div class="px-6 py-4 bg-gray-50 dark:bg-gray-700/50 flex items-center justify-between text-xs text-gray-500">
        <span>每位用户仅可兑换一次</span>
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
import { ref, watch } from 'vue'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  close: []
  refreshed: []
}>()

const inviteCode = ref('')
const totalRedeemed = ref(0)
const redeemCode = ref('')
const error = ref('')

const fetchInvite = async () => {
  error.value = ''
  try {
    const token = (await import('../supabase').then(m => m.supabase.auth.getSession())).data.session?.access_token
    if (!token) return
    const response = await fetch('/api/invites', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.ok) throw new Error('获取邀请码失败')
    const data = await response.json()
    inviteCode.value = data.code || ''
    totalRedeemed.value = data.total_redeemed || 0
  } catch (err: any) {
    error.value = err?.message || '获取邀请码失败'
  }
}

const handleCreateCode = async () => {
  error.value = ''
  try {
    const token = (await import('../supabase').then(m => m.supabase.auth.getSession())).data.session?.access_token
    if (!token) return
    const response = await fetch('/api/invites', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.ok) throw new Error('创建邀请码失败')
    const data = await response.json()
    inviteCode.value = data.code
  } catch (err: any) {
    error.value = err?.message || '创建邀请码失败'
  }
}

const handleRedeem = async () => {
  if (!redeemCode.value) return
  error.value = ''
  try {
    const token = (await import('../supabase').then(m => m.supabase.auth.getSession())).data.session?.access_token
    if (!token) return
    const response = await fetch('/api/invites/redeem', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ code: redeemCode.value })
    })
    if (!response.ok) {
      const data = await response.json()
      throw new Error(data?.detail || '兑换失败')
    }
    redeemCode.value = ''
    await fetchInvite()
    emit('refreshed')
    alert('兑换成功，积分已到账')
  } catch (err: any) {
    error.value = err?.message || '兑换失败'
  }
}

const copyCode = () => {
  if (!inviteCode.value) return
  navigator.clipboard.writeText(inviteCode.value)
  alert('邀请码已复制')
}

watch(() => props.show, (value) => {
  if (value) {
    fetchInvite()
  }
})
</script>
