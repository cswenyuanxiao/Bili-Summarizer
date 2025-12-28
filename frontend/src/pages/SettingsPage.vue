<template>
  <main class="min-h-screen pb-20 page-shell">
    <div class="container mx-auto max-w-6xl px-4">
      <section class="page-hero space-y-4" data-reveal>
        <div class="page-hero__cloud" aria-hidden="true"></div>
        <p class="page-hero__kicker">Settings</p>
        <h1 class="page-hero__title">设置</h1>
        <p class="page-hero__subtitle">管理您的个人资料、偏好设置和开发者选项。</p>
      </section>

      <div v-if="!user" class="mt-8 page-card text-center" data-reveal>
        <p class="text-gray-600 dark:text-gray-300 mb-4">登录后可管理设置</p>
        <button class="btn-primary px-6 py-2" @click="openLogin">去登录</button>
      </div>

      <div v-else class="mt-8 grid grid-cols-1 lg:grid-cols-4 gap-6" data-reveal>
        <!-- Sidebar -->
        <nav class="lg:col-span-1">
          <div class="page-card p-2 space-y-1">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                'w-full text-left px-4 py-2.5 rounded-lg transition-colors flex items-center gap-3',
                activeTab === tab.id
                  ? 'bg-primary/10 text-primary font-semibold'
                  : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-slate-800'
              ]"
            >
              <component :is="tab.icon" class="h-4 w-4" />
              {{ tab.label }}
            </button>
          </div>
        </nav>

        <!-- Content -->
        <div class="lg:col-span-3">
          <!-- General Tab -->
          <div v-if="activeTab === 'general'" class="page-card space-y-6">
            <div>
              <h2 class="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">通用设置</h2>
              
              <div class="space-y-6">
                <!-- Theme -->
                <div class="flex items-center justify-between pb-4 border-b border-gray-200 dark:border-gray-700">
                  <div>
                    <div class="font-semibold text-gray-900 dark:text-gray-100">主题外观</div>
                    <div class="text-sm text-gray-500 mt-1">选择您偏好的界面主题</div>
                  </div>
                  <button
                    @click="toggleTheme"
                    class="w-14 h-14 flex items-center justify-center rounded-full bg-gray-100 dark:bg-slate-800 hover:scale-105 transition-transform"
                    :title="isDark ? '切换为亮色' : '切换为暗色'"
                  >
                    <SunIcon v-if="isDark" class="h-5 w-5 text-amber-500" />
                    <MoonIcon v-else class="h-5 w-5 text-slate-600 dark:text-slate-300" />
                  </button>
                </div>

                <!-- Language -->
                <div class="flex items-center justify-between pb-4 border-b border-gray-200 dark:border-gray-700">
                  <div>
                    <div class="font-semibold text-gray-900 dark:text-gray-100">语言</div>
                    <div class="text-sm text-gray-500 mt-1">更改界面显示语言</div>
                  </div>
                  <LocaleSwitcher />
                </div>

                <!-- Default Summary Mode -->
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-semibold text-gray-900 dark:text-gray-100">默认总结模式</div>
                    <div class="text-sm text-gray-500 mt-1">选择智能模式或视频模式</div>
                  </div>
                  <select class="px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-slate-800 text-sm">
                    <option value="smart">智能模式</option>
                    <option value="video">视频模式</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- Account Tab -->
          <div v-if="activeTab === 'account'" class="page-card space-y-6">
            <div>
              <h2 class="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">账户信息</h2>
              
              <div class="space-y-6">
                <!-- Profile -->
                <div class="flex items-center gap-4 pb-6 border-b border-gray-200 dark:border-gray-700">
                  <img 
                    :src="user.user_metadata?.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.email?.charAt(0) || 'U')}&background=4f46e5&color=fff`" 
                    :alt="user.email"
                    class="w-16 h-16 rounded-full border-2 border-primary/30"
                  />
                  <div class="flex-1">
                    <div class="font-semibold text-gray-900 dark:text-gray-100">{{ user.email }}</div>
                    <div class="text-xs text-gray-500 mt-1">UID: {{ user.id.slice(0, 8) }}...</div>
                  </div>
                </div>

                <!-- Subscription -->
                <div class="pb-6 border-b border-gray-200 dark:border-gray-700">
                  <div class="flex items-center justify-between mb-3">
                    <div class="font-semibold text-gray-900 dark:text-gray-100">订阅计划</div>
                    <span class="text-xs uppercase tracking-wider px-2 py-1 rounded-sm bg-primary/10 text-primary border border-primary/20 font-bold">
                      {{ planLabel }}
                    </span>
                  </div>
                  <RouterLink to="/pricing" class="inline-block text-sm text-primary hover:underline">
                    {{ planLabel === 'Pro' ? '管理订阅' : '升级至 Pro' }} →
                  </RouterLink>
                </div>

                <!-- Danger Zone -->
                <div>
                  <div class="font-semibold text-red-600 mb-3">危险操作</div>
                  <button 
                    @click="handleLogout"
                    class="px-4 py-2 text-sm border border-red-200 text-red-600 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                  >
                    退出登录
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Developer Tab -->
          <div v-if="activeTab === 'developer'" class="page-card space-y-6">
            <div>
              <h2 class="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">开发者设置</h2>
              
              <div class="space-y-6">
                <div>
                  <div class="flex items-center justify-between mb-4">
                    <div>
                      <div class="font-semibold text-gray-900 dark:text-gray-100">API Keys</div>
                      <div class="text-sm text-gray-500 mt-1">管理您的 API 访问密钥</div>
                    </div>
                    <button @click="openApiKey" class="btn-primary px-4 py-2 text-sm">
                      创建新密钥
                    </button>
                  </div>
                  <div class="text-sm text-gray-500 p-4 bg-gray-50 dark:bg-slate-800 rounded-lg">
                    点击"创建新密钥"按钮打开管理面板
                  </div>
                </div>

                <div class="pb-6 border-t border-gray-200 dark:border-gray-700 pt-6">
                  <RouterLink to="/api-docs" class="text-sm text-primary hover:underline">
                    查看 API 文档 →
                  </RouterLink>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, inject, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { 
  Cog6ToothIcon,
  UserCircleIcon,
  CodeBracketIcon,
  SunIcon,
  MoonIcon
} from '@heroicons/vue/24/outline'
import { useAuth } from '../composables/useAuth'
import { useReveal } from '../composables/useReveal'
import { useTheme } from '../composables/useTheme'
import LocaleSwitcher from '../components/LocaleSwitcher.vue'
import { isSupabaseConfigured, supabase } from '../supabase'

const { user, logout } = useAuth()
const { isDark, toggleTheme } = useTheme()
useReveal()

const appActions = inject<{ openLogin: () => void; openApiKey: () => void }>('appActions')
const openLogin = () => appActions?.openLogin()
const openApiKey = () => appActions?.openApiKey()

const activeTab = ref('general')

const tabs = [
  { id: 'general', label: '通用', icon: Cog6ToothIcon },
  { id: 'account', label: '账户', icon: UserCircleIcon },
  { id: 'developer', label: '开发者', icon: CodeBracketIcon }
]

const subscriptionData = ref<{
  plan: string
  status: string
} | null>(null)

const planLabel = computed(() => {
  if (subscriptionData.value?.plan === 'pro' && subscriptionData.value?.status === 'active') {
    return 'Pro'
  }
  return '免费版'
})

const getSupabaseToken = async () => {
  if (!isSupabaseConfigured || !supabase) return null
  const { data } = await supabase.auth.getSession()
  return data.session?.access_token ?? null
}

const fetchSubscription = async () => {
  if (!user.value || !isSupabaseConfigured) {
    subscriptionData.value = null
    return
  }
  try {
    const token = await getSupabaseToken()
    if (!token) return
    const response = await fetch('/api/subscription', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (response.ok) {
      subscriptionData.value = await response.json()
    }
  } catch {
    subscriptionData.value = null
  }
}

const handleLogout = async () => {
  if (!confirm('确定要退出登录吗？')) return
  try {
    await logout()
  } catch (error: any) {
    alert(`退出登录失败: ${error?.message || '未知错误'}`)
  }
}

onMounted(() => {
  fetchSubscription()
})
</script>
