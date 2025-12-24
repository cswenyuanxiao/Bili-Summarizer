<template>
  <main class="min-h-screen pb-20 page-shell">
    <div class="container mx-auto max-w-6xl px-4">
      <div class="flex flex-col gap-[var(--section-gap)]">
        <section class="page-hero space-y-4" data-reveal>
          <div class="page-hero__cloud" aria-hidden="true"></div>
          <p class="page-hero__kicker">Referral</p>
          <h1 class="page-hero__title">邀请好友一起升级 AI 复盘效率</h1>
          <p class="page-hero__subtitle">分享你的专属邀请码，好友成功注册并使用后，双方各得 10 积分。</p>
          <div class="flex flex-wrap gap-3">
            <button class="btn-primary px-5 py-2 text-sm wiggle-soft" @click="openInvite">生成邀请码</button>
            <button class="px-5 py-2 text-sm rounded-full border border-gray-300 dark:border-slate-700 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-slate-800 transition" @click="openLogin">
              登录查看记录
            </button>
          </div>
        </section>

        <section class="grid grid-cols-1 md:grid-cols-2 gap-6" data-reveal>
          <div class="page-card space-y-4">
            <div class="flex items-center justify-between">
              <div class="text-sm font-semibold text-gray-900 dark:text-gray-100">专属邀请码</div>
              <span class="badge-pill badge-soft">实时更新</span>
            </div>
            <p class="text-sm text-gray-500">登录后生成你的邀请码链接，一键复制发送到群聊或社交平台。</p>
            <div class="rounded-2xl border border-dashed border-gray-200 dark:border-slate-700 px-4 py-3 text-xs text-gray-400">
              登录后展示邀请码与链接
            </div>
            <button class="text-sm text-primary hover:underline" @click="openInvite">打开邀请面板</button>
          </div>

          <div class="page-card page-card--accent space-y-4">
            <div class="text-sm font-semibold text-gray-900 dark:text-gray-100">奖励到账节奏</div>
            <ul class="text-sm text-gray-600 dark:text-gray-300 space-y-2">
              <li>好友注册并登录，系统记录邀请关系。</li>
              <li>好友完成首次总结后，双方立即获得 10 积分。</li>
              <li>奖励记录会显示在账单与仪表盘中。</li>
            </ul>
            <div v-if="!user" class="rounded-2xl border border-blue-100/80 bg-blue-50/80 px-4 py-3 text-sm text-blue-700">
              登录后可生成邀请码与兑换奖励。
              <button class="ml-2 text-xs font-semibold text-primary hover:underline" @click="openLogin">去登录</button>
            </div>
          </div>
        </section>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { inject } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useReveal } from '../composables/useReveal'

const { user } = useAuth()
useReveal()
const appActions = inject<{ openLogin: () => void; openInvite: () => void }>('appActions')
const openLogin = () => appActions?.openLogin()
const openInvite = () => appActions?.openInvite()
</script>
