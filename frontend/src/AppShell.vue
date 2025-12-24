<template>
  <div id="app" class="relative">
    <div class="aurora" aria-hidden="true">
      <div class="aurora-blob top-[-120px] left-1/2 -translate-x-1/2 bg-[#f59e0b]/70"></div>
      <div class="aurora-blob is-secondary top-24 right-[-120px] bg-[#60a5fa]/70"></div>
      <div class="aurora-blob is-tertiary top-[360px] left-[-80px] bg-[#22d3ee]/70"></div>
    </div>

    <header class="relative z-40">
      <div class="hero-glow" aria-hidden="true"></div>
      <div class="hero-fade" aria-hidden="true"></div>
      <div class="sticky top-0 z-40 backdrop-blur-xl bg-white/70 dark:bg-slate-900/70 border-b border-gray-200/70 dark:border-slate-800/70">
        <div class="container mx-auto max-w-6xl px-4 sm:px-6">
          <div class="flex items-center justify-between h-14 sm:h-16">
            <RouterLink to="/" class="flex items-center gap-3">
              <div class="flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-cyan-400 text-white font-semibold">✨</div>
              <div class="text-base sm:text-lg font-semibold tracking-tight text-gray-900 dark:text-gray-100">Bili-Summarizer</div>
            </RouterLink>

            <nav class="hidden lg:flex items-center gap-6 text-sm text-gray-600 dark:text-gray-300">
              <RouterLink to="/product" class="hover:text-gray-900 dark:hover:text-white transition-colors">产品</RouterLink>
              <RouterLink to="/pricing" class="hover:text-gray-900 dark:hover:text-white transition-colors">方案</RouterLink>
              <RouterLink to="/docs" class="hover:text-gray-900 dark:hover:text-white transition-colors">使用文档</RouterLink>
              <RouterLink v-if="user" to="/dashboard" class="hover:text-gray-900 dark:hover:text-white transition-colors">仪表盘</RouterLink>
              <RouterLink v-if="user" to="/billing" class="hover:text-gray-900 dark:hover:text-white transition-colors">账单</RouterLink>
              <RouterLink v-if="user" to="/invite" class="hover:text-gray-900 dark:hover:text-white transition-colors">邀请好友</RouterLink>
              <RouterLink v-if="user" to="/developer" class="hover:text-gray-900 dark:hover:text-white transition-colors">开发者 API</RouterLink>
            </nav>

            <div class="flex items-center gap-3">
              <button
                @click="toggleTheme"
                class="w-9 h-9 flex items-center justify-center rounded-full bg-gray-100 dark:bg-slate-800 text-lg hover:scale-105 transition-transform"
                title="切换主题"
              >
                {{ isDark ? '☀️' : '🌙' }}
              </button>

              <div v-if="user" ref="userMenuRef" class="relative">
                <button
                  class="flex items-center gap-2 focus:outline-none"
                  :aria-expanded="showUserMenu"
                  aria-haspopup="menu"
                  @click="toggleUserMenu"
                >
                  <img 
                    :src="user.user_metadata?.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.email?.charAt(0) || 'U')}&background=4f46e5&color=fff`" 
                    :alt="user.email"
                    class="w-9 h-9 rounded-full border-2 border-white/30 hover:border-primary transition-colors shadow-md"
                    @error="(e: Event) => { (e.target as HTMLImageElement).src = 'https://ui-avatars.com/api/?name=U&background=4f46e5&color=fff' }"
                  />
                </button>
                
                <div
                  v-show="showUserMenu"
                  class="absolute top-full -right-4 mt-2 w-56 glass-card rounded-xl overflow-hidden border border-white/40 z-[70] flex flex-col shadow-2xl py-1"
                  role="menu"
                >
                  <div class="px-5 py-3 border-b border-gray-100 dark:border-gray-700/50 bg-gray-50/50 dark:bg-slate-800/50">
                    <p class="text-sm font-semibold text-gray-900 dark:text-gray-100 truncate">{{ user.email }}</p>
                    <div class="flex items-center gap-2 mt-1">
                      <span class="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded-sm bg-primary/10 text-primary border border-primary/20 font-bold">{{ planLabel }}</span>
                      <button @click="openPricing" class="text-xs text-gray-500 hover:text-primary font-medium transition-colors">升级</button>
                    </div>
                  </div>
                  
                  <div class="p-1 flex flex-col gap-0.5">
                    <RouterLink to="/pricing" class="flex items-center justify-between px-4 py-2.5 rounded-md hover:bg-gray-100 dark:hover:bg-slate-700/70 transition-all duration-200 group" @click="showUserMenu = false">
                      <span class="text-sm font-medium text-gray-700 dark:text-gray-200 group-hover:text-gray-900 dark:group-hover:text-white group-hover:translate-x-1 transition-transform">升级 Pro</span>
                      <span class="text-[10px] font-bold bg-gradient-to-r from-primary to-purple-600 text-white px-1.5 py-0.5 rounded shadow-sm">HOT</span>
                    </RouterLink>
                    
                    <RouterLink to="/dashboard" class="flex items-center px-4 py-2.5 rounded-md hover:bg-gray-100 dark:hover:bg-slate-700/70 transition-all duration-200 group" @click="showUserMenu = false">
                      <span class="text-sm font-medium text-gray-700 dark:text-gray-200 group-hover:text-gray-900 dark:group-hover:text-white group-hover:translate-x-1 transition-transform">仪表盘</span>
                    </RouterLink>
                    
                    <RouterLink to="/billing" class="flex items-center px-4 py-2.5 rounded-md hover:bg-gray-100 dark:hover:bg-slate-700/70 transition-all duration-200 group" @click="showUserMenu = false">
                      <span class="text-sm font-medium text-gray-700 dark:text-gray-200 group-hover:text-gray-900 dark:group-hover:text-white group-hover:translate-x-1 transition-transform">账单与发票</span>
                    </RouterLink>
                    
                    <RouterLink to="/invite" class="flex items-center px-4 py-2.5 rounded-md hover:bg-gray-100 dark:hover:bg-slate-700/70 transition-all duration-200 group" @click="showUserMenu = false">
                      <span class="text-sm font-medium text-gray-700 dark:text-gray-200 group-hover:text-gray-900 dark:group-hover:text-white group-hover:translate-x-1 transition-transform">邀请好友</span>
                    </RouterLink>
                    
                    <RouterLink to="/developer" class="flex items-center px-4 py-2.5 rounded-md hover:bg-gray-100 dark:hover:bg-slate-700/70 transition-all duration-200 group" @click="showUserMenu = false">
                      <span class="text-sm font-medium text-gray-700 dark:text-gray-200 group-hover:text-gray-900 dark:group-hover:text-white group-hover:translate-x-1 transition-transform">开发者 API</span>
                    </RouterLink>
                    
                    <RouterLink to="/docs" class="flex items-center px-4 py-2.5 rounded-md hover:bg-gray-100 dark:hover:bg-slate-700/70 transition-all duration-200 group" @click="showUserMenu = false">
                      <span class="text-sm font-medium text-gray-700 dark:text-gray-200 group-hover:text-gray-900 dark:group-hover:text-white group-hover:translate-x-1 transition-transform">使用文档</span>
                    </RouterLink>
                  </div>
                  
                  <div class="px-1 pb-1 pt-1 border-t border-gray-100 dark:border-gray-700/50 mt-1">
                    <button 
                      @click="handleLogout"
                      class="w-full flex items-center px-4 py-2.5 rounded-md text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all duration-200 group"
                    >
                      <span class="text-sm font-semibold group-hover:translate-x-1 transition-transform">退出登录</span>
                    </button>
                  </div>
                </div>
              </div>

              <button 
                v-else
                @click="openLogin"
                class="px-4 py-2 rounded-full bg-gray-900 text-white text-sm font-medium hover:shadow-lg transition-all"
              >
                登录 / 注册
              </button>

              <button
                ref="mobileMenuButtonRef"
                class="lg:hidden w-9 h-9 flex items-center justify-center rounded-full bg-gray-100 dark:bg-slate-800"
                @click="showMobileMenu = !showMobileMenu"
              >
                ☰
              </button>
            </div>
          </div>
          <div v-if="showMobileMenu" ref="mobileMenuRef" class="lg:hidden pb-4">
            <div class="rounded-2xl glass-card p-4 space-y-2 text-sm text-gray-700 dark:text-gray-200">
              <RouterLink class="w-full text-left" to="/product" @click="showMobileMenu = false">产品</RouterLink>
              <RouterLink class="w-full text-left" to="/pricing" @click="showMobileMenu = false">方案</RouterLink>
              <RouterLink class="w-full text-left" to="/docs" @click="showMobileMenu = false">使用文档</RouterLink>
              <RouterLink v-if="user" class="w-full text-left" to="/dashboard" @click="showMobileMenu = false">仪表盘</RouterLink>
              <RouterLink v-if="user" class="w-full text-left" to="/billing" @click="showMobileMenu = false">账单与发票</RouterLink>
              <RouterLink v-if="user" class="w-full text-left" to="/invite" @click="showMobileMenu = false">邀请好友</RouterLink>
              <RouterLink v-if="user" class="w-full text-left" to="/developer" @click="showMobileMenu = false">开发者 API</RouterLink>
            </div>
          </div>
        </div>
      </div>
    </header>

    <RouterView />

    <LoginModal :show="showLoginModal" @close="showLoginModal = false" />
    <PricingModal :show="showPricingModal" @close="showPricingModal = false" />
    <ApiKeyModal :show="showApiKeyModal" @close="showApiKeyModal = false" />
    <DashboardModal
      :show="showDashboard"
      :loading="dashboardLoading"
      :error="dashboardError"
      :data="dashboardData"
      :subscription="subscriptionData"
      @close="showDashboard = false"
      @refresh="fetchDashboard"
      @upgrade="openPricing"
    />
    <InviteModal
      :show="showInviteModal"
      @close="showInviteModal = false"
      @refreshed="fetchDashboard"
    />
    <BillingModal
      :show="showBillingModal"
      :loading="billingLoading"
      :error="billingError"
      :items="billingItems"
      @close="showBillingModal = false"
    />
    <UsageGuideModal :show="showUsageGuide" @close="showUsageGuide = false" />

    <footer class="bg-gray-100 dark:bg-gray-800 py-6 text-center text-sm text-gray-600 dark:text-gray-400">
      <div class="container mx-auto">
        <p>
          Powered by <a href="https://ai.google.dev/" target="_blank" class="text-primary hover:underline">Google Gemini</a> · Built with ❤️
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, provide } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import LoginModal from './components/LoginModal.vue'
import PricingModal from './components/PricingModal.vue'
import ApiKeyModal from './components/ApiKeyModal.vue'
import DashboardModal from './components/DashboardModal.vue'
import BillingModal from './components/BillingModal.vue'
import InviteModal from './components/InviteModal.vue'
import UsageGuideModal from './components/UsageGuideModal.vue'
import { useTheme } from './composables/useTheme'
import { useAuth } from './composables/useAuth'
import { isSupabaseConfigured, supabase } from './supabase'

const { isDark, toggleTheme, initTheme } = useTheme()
onMounted(() => {
  initTheme()
})

const { user, logout } = useAuth()
const showLoginModal = ref(false)
const showPricingModal = ref(false)
const showApiKeyModal = ref(false)
const showDashboard = ref(false)
const showBillingModal = ref(false)
const showInviteModal = ref(false)
const showUsageGuide = ref(false)
const showUserMenu = ref(false)
const showMobileMenu = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)
const mobileMenuRef = ref<HTMLElement | null>(null)
const mobileMenuButtonRef = ref<HTMLElement | null>(null)

const dashboardLoading = ref(false)
const dashboardError = ref('')
const dashboardData = ref<{
  credits: number
  total_used: number
  cost_per_summary: number
  daily_usage?: { day: string; count: number }[]
  email?: string | null
} | null>(null)
const subscriptionData = ref<{
  plan: string
  status: string
  current_period_end?: string | null
} | null>(null)
const billingLoading = ref(false)
const billingError = ref('')
const billingItems = ref<Array<{
  id: string
  amount_cents: number
  currency: string
  status: string
  period_start?: string | null
  period_end?: string | null
  invoice_url?: string | null
  created_at?: string | null
}>>([])

const getSupabaseToken = async () => {
  if (!isSupabaseConfigured || !supabase) return null
  const { data } = await supabase.auth.getSession()
  return data.session?.access_token ?? null
}

const openLogin = () => {
  showLoginModal.value = true
}

const openPricing = () => {
  showPricingModal.value = true
}

const openDashboard = async () => {
  showUserMenu.value = false
  showMobileMenu.value = false
  showDashboard.value = true
  await fetchDashboard()
}

const openBilling = async () => {
  showUserMenu.value = false
  showMobileMenu.value = false
  showBillingModal.value = true
  await fetchBilling()
}

const openInvite = () => {
  showUserMenu.value = false
  showMobileMenu.value = false
  showInviteModal.value = true
}

const openApiKey = () => {
  showUserMenu.value = false
  showMobileMenu.value = false
  showApiKeyModal.value = true
}

const openUsageGuide = () => {
  showUsageGuide.value = true
}

const handleLogout = async () => {
  try {
    await logout()
    showUserMenu.value = false
    showPricingModal.value = false
    showApiKeyModal.value = false
    showDashboard.value = false
    showBillingModal.value = false
    showInviteModal.value = false
    showUsageGuide.value = false
    showLoginModal.value = false
  } catch (error: any) {
    alert(`退出登录失败: ${error?.message || '未知错误'}`)
  }
}

const fetchDashboard = async () => {
  if (!user.value) {
    dashboardData.value = null
    return
  }
  if (!isSupabaseConfigured) {
    dashboardError.value = '登录服务未配置'
    dashboardData.value = null
    return
  }
  dashboardLoading.value = true
  dashboardError.value = ''
  try {
    const token = await getSupabaseToken()
    if (!token) throw new Error('未获取到登录凭证')
    const response = await fetch('/api/dashboard', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.ok) {
      const text = await response.text()
      try {
        const error = JSON.parse(text)
        throw new Error(error.detail || '获取仪表盘失败')
      } catch {
        throw new Error(`请求失败 (${response.status})`)
      }
    }
    dashboardData.value = await response.json()
  } catch (error: any) {
    dashboardError.value = error?.message || '获取仪表盘失败'
  } finally {
    dashboardLoading.value = false
  }
}

const fetchSubscription = async () => {
  if (!user.value || !isSupabaseConfigured) {
    subscriptionData.value = null
    return
  }
  try {
    const token = await getSupabaseToken()
    if (!token) throw new Error('未获取到登录凭证')
    const response = await fetch('/api/subscription', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.ok) {
      const text = await response.text()
      try {
        const error = JSON.parse(text)
        throw new Error(error.detail || '获取订阅信息失败')
      } catch {
        throw new Error(`请求失败 (${response.status})`)
      }
    }
    subscriptionData.value = await response.json()
  } catch {
    subscriptionData.value = null
  }
}

const fetchBilling = async () => {
  if (!user.value) {
    billingItems.value = []
    return
  }
  if (!isSupabaseConfigured) {
    billingError.value = '登录服务未配置'
    billingItems.value = []
    return
  }
  billingLoading.value = true
  billingError.value = ''
  try {
    const token = await getSupabaseToken()
    if (!token) throw new Error('未获取到登录凭证')
    const response = await fetch('/api/billing', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.ok) {
      const text = await response.text()
      try {
        const error = JSON.parse(text)
        throw new Error(error.detail || '获取账单失败')
      } catch {
        throw new Error(`请求失败 (${response.status})`)
      }
    }
    billingItems.value = await response.json()
  } catch (error: any) {
    billingError.value = error?.message || '获取账单失败'
  } finally {
    billingLoading.value = false
  }
}

const planLabel = computed(() => {
  if (subscriptionData.value?.plan === 'pro' && subscriptionData.value?.status === 'active') {
    return 'Pro'
  }
  return '免费版'
})

watch(user, (nextUser) => {
  if (nextUser) {
    fetchDashboard().catch(() => undefined)
    fetchSubscription().catch(() => undefined)
  } else {
    showUserMenu.value = false
    showPricingModal.value = false
    showApiKeyModal.value = false
    showDashboard.value = false
    showBillingModal.value = false
    showInviteModal.value = false
    showUsageGuide.value = false
  }
})

const handleDocumentClick = (event: MouseEvent) => {
  if (!showUserMenu.value || !userMenuRef.value) return
  const target = event.target as Node | null
  if (target && userMenuRef.value.contains(target)) return
  showUserMenu.value = false
}

const handleMobileMenuClick = (event: MouseEvent) => {
  if (!showMobileMenu.value || !mobileMenuRef.value) return
  const target = event.target as Node | null
  if (target && mobileMenuButtonRef.value?.contains(target)) return
  if (target && mobileMenuRef.value.contains(target)) return
  showMobileMenu.value = false
}

const handleDocumentKeydown = (event: KeyboardEvent) => {
  if (event.key !== 'Escape') return
  showUserMenu.value = false
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  document.addEventListener('click', handleMobileMenuClick)
  document.addEventListener('keydown', handleDocumentKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
  document.removeEventListener('click', handleMobileMenuClick)
  document.removeEventListener('keydown', handleDocumentKeydown)
})

provide('appActions', {
  openLogin,
  openPricing,
  openDashboard,
  openBilling,
  openInvite,
  openApiKey,
  openUsageGuide
})
</script>
