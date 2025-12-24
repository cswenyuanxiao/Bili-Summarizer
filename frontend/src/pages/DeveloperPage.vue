<template>
  <main class="min-h-screen pb-20 page-shell">
    <div class="container mx-auto max-w-6xl px-4">
      <div class="flex flex-col gap-[var(--section-gap)]">
        <section class="page-hero space-y-4" data-reveal>
          <div class="page-hero__cloud" aria-hidden="true"></div>
          <p class="page-hero__kicker">Developer API</p>
          <h1 class="page-hero__title">把 Bili-Summarizer 融入你的自动化流程</h1>
          <p class="page-hero__subtitle">使用 API Key 调用总结、转录与结构化导出能力，支持任务队列与批量处理。</p>
          <div class="flex flex-wrap gap-3">
            <button class="btn-primary px-5 py-2 text-sm wiggle-soft" @click="openApiKey">管理 API Key</button>
            <button class="px-5 py-2 text-sm rounded-full border border-gray-300 dark:border-slate-700 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-slate-800 transition" @click="openLogin">
              登录查看配额
            </button>
          </div>
        </section>

        <section class="grid grid-cols-1 md:grid-cols-3 gap-6" data-reveal>
          <div class="page-card space-y-3">
            <div class="text-sm font-semibold text-gray-900 dark:text-gray-100">核心接口</div>
            <p class="text-sm text-gray-500">/api/summarize、/api/transcript、/api/export 三大能力覆盖主流程。</p>
            <span class="badge-pill badge-soft">稳定 SLA</span>
          </div>
          <div class="page-card space-y-3">
            <div class="text-sm font-semibold text-gray-900 dark:text-gray-100">安全策略</div>
            <p class="text-sm text-gray-500">支持 API Key 绑定、额度控制与访问日志审计。</p>
            <span class="badge-pill badge-soft">细粒度控制</span>
          </div>
          <div class="page-card page-card--accent space-y-3">
            <div class="text-sm font-semibold text-gray-900 dark:text-gray-100">集成建议</div>
            <p class="text-sm text-gray-500">适配 Zapier/Make、内部审批系统或内容运营后台。</p>
            <span class="badge-pill badge-accent">快速落地</span>
          </div>
        </section>

        <section class="page-card space-y-4" data-reveal>
          <div class="flex items-center justify-between">
            <div class="text-sm font-semibold text-gray-900 dark:text-gray-100">接入流程</div>
            <span class="badge-pill badge-soft">5 分钟完成</span>
          </div>
          <ol class="list-decimal pl-5 text-sm text-gray-600 dark:text-gray-300 space-y-2">
            <li>登录后生成专属 API Key。</li>
            <li>在请求 Header 中加入 Authorization: Bearer &lt;key&gt;。</li>
            <li>在控制台查看请求记录与扣费统计。</li>
          </ol>
          <div v-if="!user" class="rounded-2xl border border-blue-100/80 bg-blue-50/80 px-4 py-3 text-sm text-blue-700">
            登录后可创建与管理 API Key。
            <button class="ml-2 text-xs font-semibold text-primary hover:underline" @click="openLogin">去登录</button>
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
const appActions = inject<{ openLogin: () => void; openApiKey: () => void }>('appActions')
const openLogin = () => appActions?.openLogin()
const openApiKey = () => appActions?.openApiKey()
</script>
