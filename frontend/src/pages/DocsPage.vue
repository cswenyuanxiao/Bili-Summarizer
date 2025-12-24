<template>
  <main class="min-h-screen pb-20 page-shell">
    <div class="container mx-auto max-w-6xl px-4">
      <section class="page-hero space-y-4" data-reveal>
        <div class="page-hero__cloud" aria-hidden="true"></div>
        <div class="page-hero__kicker">Docs</div>
        <div class="page-hero__title">使用文档</div>
        <div class="page-hero__subtitle">快速上手与常见问题。</div>
        <div class="flex flex-wrap gap-3">
          <button class="btn-primary px-5 py-2 text-sm wiggle-soft" @click="openUsageGuide">查看详细指南</button>
          <span class="badge-pill badge-soft">最新版本</span>
        </div>
      </section>

      <section class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600 dark:text-gray-300 mt-8" data-reveal>
        <div class="page-card card-hover-elevate">
          <div class="text-base font-semibold text-gray-900 dark:text-gray-100">快速上手</div>
          <ol class="mt-2 space-y-1 text-xs text-gray-500 list-decimal list-inside">
            <li>登录后获取积分</li>
            <li>粘贴 B 站链接生成总结</li>
            <li>导出或分享结果</li>
          </ol>
        </div>
        <div class="page-card card-hover-elevate page-card--accent">
          <div class="text-base font-semibold text-gray-900 dark:text-gray-100">常见问题</div>
          <div class="mt-2 text-xs text-gray-500">积分不足时可购买额度包或升级订阅。</div>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { inject } from 'vue'

const appActions = inject<{ openUsageGuide: () => void }>('appActions')
const openUsageGuide = () => appActions?.openUsageGuide()
</script>
