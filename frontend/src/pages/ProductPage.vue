<template>
  <main class="min-h-screen pb-20 page-shell">
    <div class="container mx-auto max-w-6xl px-4">
      <section class="page-hero space-y-4" data-reveal>
        <div class="page-hero__cloud" aria-hidden="true"></div>
        <p class="page-hero__kicker">Product</p>
        <h1 class="page-hero__title">产品</h1>
        <p class="page-hero__subtitle">把 B 站长视频拆成可执行的知识模块。</p>
        <div class="flex flex-wrap gap-3">
          <button class="btn-primary px-5 py-2 text-sm wiggle-soft" @click="goHome">立即体验</button>
          <span class="badge-pill badge-soft">云端同步 · 导出 · 邀请奖励</span>
        </div>
      </section>

      <section class="grid grid-cols-1 md:grid-cols-3 gap-5 text-sm text-gray-600 dark:text-gray-300 mt-8" data-reveal>
        <button class="page-card card-hover-elevate card-action" type="button" @click="goHome">
          <div class="text-base font-semibold text-gray-900 dark:text-gray-100">结构化总结</div>
          <div class="mt-2 text-xs text-gray-500">一键生成关键观点、结论与行动项。</div>
          <div class="mt-4 text-xs text-primary font-semibold">立即体验 →</div>
        </button>
        <button class="page-card card-hover-elevate card-action" type="button" @click="goHome">
          <div class="text-base font-semibold text-gray-900 dark:text-gray-100">自动转录</div>
          <div class="mt-2 text-xs text-gray-500">精准字幕与时间戳，方便回看。</div>
          <div class="mt-4 text-xs text-primary font-semibold">立即体验 →</div>
        </button>
        <button class="page-card card-hover-elevate page-card--accent card-action" type="button" @click="goHome">
          <div class="text-base font-semibold text-gray-900 dark:text-gray-100">思维导图</div>
          <div class="mt-2 text-xs text-gray-500">自动生成知识脉络，支持导出。</div>
          <div class="mt-4 text-xs text-primary font-semibold">立即体验 →</div>
        </button>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useReveal } from '../composables/useReveal'

const router = useRouter()
useReveal()
const goHome = () => {
  router.push('/')
}
</script>
