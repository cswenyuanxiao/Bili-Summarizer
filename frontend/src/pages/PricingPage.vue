<template>
  <main class="min-h-screen pb-20 page-shell">
    <div class="container mx-auto max-w-6xl px-4">
      <!-- Hero Section -->
      <section class="page-hero space-y-4" data-reveal>
        <div class="page-hero__cloud" aria-hidden="true"></div>
        <p class="page-hero__kicker">Pricing</p>
        <h1 class="page-hero__title">方案</h1>
        <p class="page-hero__subtitle">灵活购买额度包或升级 Pro。</p>
        <div class="flex flex-wrap gap-3">
          <button class="btn-primary px-5 py-2 text-sm wiggle-soft" @click="openPricing">立即购买</button>
          <span class="badge-pill badge-soft">支持支付宝 / 微信支付</span>
        </div>
      </section>

      <!-- 套餐卡片 -->
      <section class="grid grid-cols-1 lg:grid-cols-3 gap-5 text-sm text-gray-600 dark:text-gray-300 mt-8" data-reveal>
        <button class="page-card card-hover-elevate card-action" type="button" @click="openPricing">
          <div class="text-base font-semibold text-gray-900 dark:text-gray-100">Starter Pack</div>
          <div class="mt-2 text-2xl font-semibold text-gray-900 dark:text-gray-100">¥1</div>
          <div class="mt-1 text-xs text-gray-500">30 积分 / 适合轻度使用</div>
          <div class="mt-4 text-xs text-primary font-semibold">立即购买 →</div>
        </button>
        <button class="page-card card-hover-elevate page-card--accent card-action" type="button" @click="openPricing">
          <div class="text-base font-semibold text-gray-900 dark:text-gray-100">Pro Pack</div>
          <div class="mt-2 text-2xl font-semibold text-gray-900 dark:text-gray-100">¥3</div>
          <div class="mt-1 text-xs text-gray-500">120 积分 / 高频总结</div>
          <div class="mt-4 text-xs text-primary font-semibold">升级加速 →</div>
        </button>
        <button class="page-card card-hover-elevate card-action" type="button" @click="openPricing">
          <div class="text-base font-semibold text-gray-900 dark:text-gray-100">Pro 专业版</div>
          <div class="mt-2 text-2xl font-semibold text-gray-900 dark:text-gray-100">¥29.9</div>
          <div class="mt-1 text-xs text-gray-500">月付 / 无限次总结</div>
          <div class="mt-4 text-xs text-primary font-semibold">订阅 Pro →</div>
        </button>
      </section>

      <!-- 功能对比表 -->
      <section class="mt-12" data-reveal>
        <FeatureCompareTable />
      </section>

      <!-- FAQ 区域 -->
      <section class="mt-12" data-reveal>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">常见问题</h2>
        <FaqSection :items="pricingFaq" />
      </section>

      <!-- 信任保障 -->
      <section class="mt-12 text-center" data-reveal>
        <div class="page-card max-w-2xl mx-auto">
          <div class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2">💳 安全支付保障</div>
          <div class="text-xs text-gray-500 leading-relaxed">
            支持支付宝、微信支付等主流支付方式。所有交易经过加密处理，保障您的资金安全。
          </div>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { inject } from 'vue'
import { useReveal } from '../composables/useReveal'
import FeatureCompareTable from '../components/FeatureCompareTable.vue'
import FaqSection from '../components/FaqSection.vue'

useReveal()
const appActions = inject<{ openPricing: () => void }>('appActions')
const openPricing = () => appActions?.openPricing()

const pricingFaq = [
  {
    question: '积分怎么计算？',
    answer: '每次总结消耗 10 积分。新用户注册即赠送 50 积分，首次成功总结额外奖励 10 积分。'
  },
  {
    question: '积分会过期吗？',
    answer: '一次性购买的积分包（Starter Pack、Pro Pack）永久有效，不会过期。Pro 专业版订阅期间享受无限次总结。'
  },
  {
    question: '如何升级或降级订阅？',
    answer: '在个人中心的账单页面可以随时升级或取消订阅。取消订阅后，当前周期内仍可继续使用，到期后自动恢复为免费版。'
  },
  {
    question: '支持哪些支付方式？',
    answer: '目前支持支付宝和微信支付。所有支付均经过加密处理，确保您的资金安全。'
  },
  {
    question: '可以退款吗？',
    answer: '积分包一经购买不支持退款。Pro 订阅可随时取消，取消后当前周期仍可使用，不扣除剩余天数费用。'
  },
  {
    question: '企业版如何购买？',
    answer: '如需批量购买或定制化服务，请通过开发者页面联系我们，获取企业级解决方案。'
  }
]
</script>
