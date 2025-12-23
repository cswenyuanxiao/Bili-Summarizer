<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @mousedown.self="$emit('close')">
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-md overflow-hidden transform transition-all">
      
      <!-- Header -->
      <div class="p-6 text-center border-b border-gray-100 dark:border-gray-700">
        <h2 class="text-2xl font-bold bg-gradient-to-r from-primary to-cyan-500 bg-clip-text text-transparent">
          登录 Bili-Summarizer
        </h2>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
          解锁更多功能与每日额度
        </p>
      </div>

      <!-- Content -->
      <div class="p-8 space-y-4">
        <div v-if="!isSupabaseConfigured" class="rounded-xl border border-yellow-200 bg-yellow-50 px-4 py-3 text-sm text-yellow-800">
          当前环境未配置登录服务，暂时无法使用账号功能。
        </div>
        <div v-else class="rounded-xl border border-blue-100/80 bg-blue-50/80 px-4 py-3 text-xs text-blue-700 dark:border-blue-500/40 dark:bg-blue-950/40 dark:text-blue-200">
          登录后会启用积分校验与云端同步；积分不足时会提示升级。
        </div>
        
        <!-- Email Form -->
        <div class="space-y-3">
            <input 
                v-model="email" 
                type="email" 
                placeholder="邮箱地址"
                class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all dark:text-white"
            />
            <input 
                v-model="password" 
                type="password" 
                placeholder="密码"
                class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all dark:text-white"
            />
            <button 
                @click="handleEmailAuth"
                :disabled="isLoading || !isSupabaseConfigured"
                class="w-full py-3 bg-primary hover:bg-primary-dark text-white rounded-xl font-medium transition-colors disabled:opacity-50"
            >
                {{ isLoading ? '处理中...' : (isSignUp ? '注册账号' : '登录') }}
            </button>
            
            <div class="text-center text-sm text-gray-500">
                <span v-if="isSignUp">已有账号？ <button @click="isSignUp = false" class="text-primary hover:underline">去登录</button></span>
                <span v-else>没有账号？ <button @click="isSignUp = true" class="text-primary hover:underline">去注册</button></span>
            </div>
        </div>

        <div class="relative flex py-2 items-center">
            <div class="flex-grow border-t border-gray-200 dark:border-gray-600"></div>
            <span class="flex-shrink-0 mx-4 text-gray-400 text-sm">或者社交登录</span>
            <div class="flex-grow border-t border-gray-200 dark:border-gray-600"></div>
        </div>

        <button
          @click="handleGitHubLogin"
          :disabled="!isSupabaseConfigured"
          class="w-full flex items-center justify-center gap-3 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors dark:text-gray-200"
        >
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.604-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.597 1.028 2.688 0 3.848-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
          </svg>
          <span class="font-medium">GitHub 登录</span>
        </button>

        <!-- Google Login -->
        <button
          @click="handleGoogleLogin"
          :disabled="!isSupabaseConfigured"
          class="w-full flex items-center justify-center gap-3 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors dark:text-gray-200"
        >
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
             <path d="M12.24 10.285V14.4h6.806c-.275 1.765-2.056 5.174-6.806 5.174-4.095 0-7.439-3.389-7.439-7.574s3.345-7.574 7.439-7.574c2.33 0 3.891.989 4.785 1.849l3.254-3.138C18.189 1.186 15.479 0 12.24 0c-6.635 0-12 5.365-12 12s5.365 12 12 12c6.926 0 11.52-4.869 11.52-11.726 0-.788-.085-1.39-.189-1.989H12.24z"/>
          </svg>
          <span class="font-medium">Google 登录</span>
        </button>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 bg-gray-50 dark:bg-gray-700/50 text-center text-xs text-gray-400">
        登录即代表您同意我们的 <a href="#" class="underline hover:text-primary">服务条款</a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuth } from '../composables/useAuth'
import { ref } from 'vue'
import { isSupabaseConfigured } from '../supabase'

defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close'])
const { loginWithGitHub, loginWithEmail, signUpWithEmail, loginWithGoogle } = useAuth()
const email = ref('')
const password = ref('')
const isSignUp = ref(false)
const isLoading = ref(false)

const handleEmailAuth = async () => {
  if (!email.value || !password.value) return
  isLoading.value = true
  try {
    if (isSignUp.value) {
      await signUpWithEmail(email.value, password.value)
      alert('注册成功！请检查邮箱完成验证（如果是测试环境可能无需验证）')
    } else {
      await loginWithEmail(email.value, password.value)
      emit('close')
    }
  } catch (e: any) {
    alert('操作失败: ' + e.message)
  } finally {
    isLoading.value = false
  }
}

const handleGitHubLogin = async () => {
  try {
    await loginWithGitHub()
  } catch (e: any) {
    alert('GitHub 登录失败: ' + e.message)
  }
}

const handleGoogleLogin = async () => {
  try {
    await loginWithGoogle()
  } catch (e: any) {
    alert('Google 登录失败: ' + e.message)
  }
}
</script>
