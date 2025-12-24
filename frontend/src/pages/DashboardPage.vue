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

      <section class="grid grid-cols-1 md:grid-cols-3 gap-5 text-sm text-gray-600 dark:text-gray-300 mt-8" data-reveal>
        <button class="page-card card-hover-elevate card-action" type="button" @click="openDashboard">
          <div class="text-sm font-semibold text-gray-900 dark:text-gray-100">积分概览</div>
          <div class="mt-2 text-xs text-gray-500">查看剩余积分与本月使用次数。</div>
          <div class="mt-4 text-xs text-primary font-semibold">查看详情 →</div>
        </button>
        <button class="page-card card-hover-elevate page-card--accent card-action" type="button" @click="openDashboard">
          <div class="text-sm font-semibold text-gray-900 dark:text-gray-100">消费趋势</div>
          <div class="mt-2 text-xs text-gray-500">每日使用曲线与高峰提醒。</div>
          <div class="mt-4 text-xs text-primary font-semibold">打开面板 →</div>
        </button>
        <button class="page-card card-hover-elevate card-action" type="button" @click="openDashboard">
          <div class="text-sm font-semibold text-gray-900 dark:text-gray-100">订阅状态</div>
          <div class="mt-2 text-xs text-gray-500">套餐剩余天数与自动续费提示。</div>
          <div class="mt-4 text-xs text-primary font-semibold">查看订阅 →</div>
        </button>
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
import { inject } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useReveal } from '../composables/useReveal'

const { user } = useAuth()
useReveal()
const appActions = inject<{ openLogin: () => void; openDashboard: () => void }>('appActions')
const openLogin = () => appActions?.openLogin()
const openDashboard = () => appActions?.openDashboard()
</script>
