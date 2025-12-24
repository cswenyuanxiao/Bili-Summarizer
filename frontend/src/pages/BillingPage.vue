<template>
  <main class="min-h-screen pb-20 page-shell">
    <div class="container mx-auto max-w-6xl px-4">
      <section class="page-hero space-y-4" data-reveal>
        <div class="page-hero__cloud" aria-hidden="true"></div>
        <p class="page-hero__kicker">Billing</p>
        <h1 class="page-hero__title">账单</h1>
        <p class="page-hero__subtitle">查看订阅与额度包订单。</p>
        <div class="flex flex-wrap gap-3">
          <button class="btn-primary px-5 py-2 text-sm wiggle-soft" @click="openBilling">查看账单</button>
          <span class="badge-pill badge-soft">发票支持</span>
        </div>
      </section>

      <section class="grid grid-cols-1 md:grid-cols-3 gap-5 text-sm text-gray-600 dark:text-gray-300 mt-8" data-reveal>
        <div class="page-card card-hover-elevate">
          <div class="text-sm font-semibold text-gray-900 dark:text-gray-100">订阅记录</div>
          <div class="mt-2 text-xs text-gray-500">展示每次续费的周期与金额。</div>
        </div>
        <div class="page-card card-hover-elevate page-card--accent">
          <div class="text-sm font-semibold text-gray-900 dark:text-gray-100">额度包订单</div>
          <div class="mt-2 text-xs text-gray-500">查看一次性积分包的购买记录。</div>
        </div>
        <div class="page-card card-hover-elevate">
          <div class="text-sm font-semibold text-gray-900 dark:text-gray-100">发票状态</div>
          <div class="mt-2 text-xs text-gray-500">下载电子发票或申请补开。</div>
        </div>
      </section>

      <section class="mt-8 text-sm text-gray-600 dark:text-gray-300" data-reveal>
        <div v-if="!user" class="page-card">
          登录后可查看账单与发票。
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
const appActions = inject<{ openLogin: () => void; openBilling: () => void }>('appActions')
const openLogin = () => appActions?.openLogin()
const openBilling = () => appActions?.openBilling()
</script>
