<template>
  <main class="min-h-screen pb-20 page-shell">
    <div class="container mx-auto max-w-6xl px-4">
      <section class="page-hero space-y-4" data-reveal>
        <div class="page-hero__cloud" aria-hidden="true"></div>
        <div class="page-hero__kicker">Pricing</div>
        <div class="page-hero__title">方案</div>
        <div class="page-hero__subtitle">灵活购买额度包或升级 Pro。</div>
        <div class="flex flex-wrap gap-3">
          <button class="btn-primary px-5 py-2 text-sm wiggle-soft" @click="openPricing">立即购买</button>
          <span class="badge-pill badge-soft">支持支付宝 / 微信支付</span>
        </div>
      </section>

      <section class="grid grid-cols-1 lg:grid-cols-3 gap-5 text-sm text-gray-600 dark:text-gray-300 mt-8" data-reveal>
        <div class="page-card card-hover-elevate">
          <div class="text-base font-semibold text-gray-900 dark:text-gray-100">Starter Pack</div>
          <div class="mt-2 text-2xl font-semibold text-gray-900 dark:text-gray-100">¥1</div>
          <div class="mt-1 text-xs text-gray-500">30 积分 / 适合轻度使用</div>
        </div>
        <div class="page-card card-hover-elevate page-card--accent">
          <div class="text-base font-semibold text-gray-900 dark:text-gray-100">Pro Pack</div>
          <div class="mt-2 text-2xl font-semibold text-gray-900 dark:text-gray-100">¥3</div>
          <div class="mt-1 text-xs text-gray-500">120 积分 / 高频总结</div>
        </div>
        <div class="page-card card-hover-elevate">
          <div class="text-base font-semibold text-gray-900 dark:text-gray-100">Pro 专业版</div>
          <div class="mt-2 text-2xl font-semibold text-gray-900 dark:text-gray-100">¥29.9</div>
          <div class="mt-1 text-xs text-gray-500">月付 / 无限次总结</div>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { inject } from 'vue'

const appActions = inject<{ openPricing: () => void }>('appActions')
const openPricing = () => appActions?.openPricing()
</script>
