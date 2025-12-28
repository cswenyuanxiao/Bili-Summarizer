<template>
  <main class="min-h-screen pb-20 page-shell">
    <div class="container mx-auto max-w-4xl px-4">
      <section class="page-hero space-y-4" data-reveal>
        <div class="page-hero__cloud" aria-hidden="true"></div>
        <p class="page-hero__kicker">Changelog</p>
        <h1 class="page-hero__title">更新日志</h1>
        <p class="page-hero__subtitle">查看 Bili-Summarizer 的最新功能与优化。</p>
      </section>

      <div class="mt-12 space-y-8" data-reveal>
        <div
          v-for="(version, index) in changelog"
          :key="version.version"
          class="relative pl-8 pb-8"
          :class="{ 'border-l-2 border-gray-200 dark:border-gray-700': index < changelog.length - 1 }"
        >
          <!-- Timeline dot -->
          <div class="absolute left-0 top-0 w-4 h-4 rounded-full bg-primary border-4 border-white dark:border-slate-900 -translate-x-[9px]"></div>
          
          <div class="page-card">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-3">
                <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100">{{ version.version }}</h2>
                <span class="badge-pill badge-soft text-xs">{{ version.date }}</span>
              </div>
            </div>

            <!-- Added -->
            <div v-if="version.added.length" class="mb-4">
              <div class="flex items-center gap-2 mb-2">
                <PlusCircleIcon class="h-4 w-4 text-green-600" />
                <h3 class="text-sm font-semibold text-gray-900 dark:text-gray-100">新增功能</h3>
              </div>
              <ul class="space-y-1 text-sm text-gray-600 dark:text-gray-300 pl-6">
                <li v-for="(item, i) in version.added" :key="i" class="list-disc">{{ item }}</li>
              </ul>
            </div>

            <!-- Changed -->
            <div v-if="version.changed.length" class="mb-4">
              <div class="flex items-center gap-2 mb-2">
                <ArrowPathIcon class="h-4 w-4 text-blue-600" />
                <h3 class="text-sm font-semibold text-gray-900 dark:text-gray-100">优化改进</h3>
              </div>
              <ul class="space-y-1 text-sm text-gray-600 dark:text-gray-300 pl-6">
                <li v-for="(item, i) in version.changed" :key="i" class="list-disc">{{ item }}</li>
              </ul>
            </div>

            <!-- Fixed -->
            <div v-if="version.fixed.length">
              <div class="flex items-center gap-2 mb-2">
                <WrenchScrewdriverIcon class="h-4 w-4 text-amber-600" />
                <h3 class="text-sm font-semibold text-gray-900 dark:text-gray-100">问题修复</h3>
              </div>
              <ul class="space-y-1 text-sm text-gray-600 dark:text-gray-300 pl-6">
                <li v-for="(item, i) in version.fixed" :key="i" class="list-disc">{{ item }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  PlusCircleIcon,
  ArrowPathIcon,
  WrenchScrewdriverIcon
} from '@heroicons/vue/24/outline'
import { useReveal } from '../composables/useReveal'

useReveal()

interface ChangelogItem {
  version: string
  date: string
  added: string[]
  changed: string[]
  fixed: string[]
}

const changelog = ref<ChangelogItem[]>([
  {
    version: '2.1.0',
    date: '2025-12-25',
    added: [
      'Pro 无限使用功能:Pro 订阅用户在订阅期内享受无限次总结，积分冻结',
      'Dashboard 返回 is_pro_active 标志，前端显示 ∞ 符号'
    ],
    changed: [
      '架构重构：main.py 模块化 (2895 行 → 模块化)',
      '新增 web_app/routers/ 目录：health, dashboard, templates, share, payments',
      '新增 web_app/startup/ 目录：db_init.py 异步数据库初始化'
    ],
    fixed: [
      'CI/CD 修复：preflight 健康检查失败、requirements.txt guard 触发问题',
      'Render 部署修复：502 Bad Gateway、前端 SPA serving 缺失 index.html 处理',
      'API 500 错误修复：templates.py, payments.py, share.py 添加缺失的导入'
    ]
  },
  {
    version: '2.0.0',
    date: '2025-12-25',
    added: [
      '分享卡片生成：支持 4 种模板、Pillow 渲染、24h 过期清理',
      '收藏夹导入：解析 B 站收藏夹 URL，批量导入视频',
      '总结模板自定义：支持预设模板 + 用户自定义 Prompt',
      '语音播报：集成 Edge TTS，支持多种中文语音',
      '每日推送：UP 主订阅管理、邮件/浏览器推送、APScheduler 定时任务',
      '总结对比：支持 2-4 视频 AI 深度对比',
      '团队协作：团队 CRUD、内容共享、评论系统'
    ],
    changed: [],
    fixed: [
      'teams.py: 修复表结构不匹配（JOIN 错误、字段名错误）',
      'compare.py: 修复 Supabase 数据源兼容性',
      'subscriptions.py: 修复 notify_methods JSON 解析'
    ]
  },
  {
    version: '1.2.0',
    date: '2025-12-25',
    added: [
      '支付全链路：完整的支付订单创建、状态更新和发货流程',
      '支付宝 Wap Pay 集成、微信支付 Native 集成',
      '回调幂等处理：idempotency.py 模块防止重复回调导致重复发货',
      '对账服务：reconciliation.py 检测并修复数据不一致',
      '批量总结：batch_summarize.py 支持一次提交多个视频 URL（最多 20 个）'
    ],
    changed: [
      'payment_orders 表新增 transaction_id 字段',
      '数据库初始化新增 idempotency_keys 表'
    ],
    fixed: [
      '修复任务队列中同步函数阻塞事件循环的问题（使用 run_in_executor）'
    ]
  },
  {
    version: '1.1.0',
    date: '2024-12-24',
    added: [
      'PDF 导出稳定性（中文字体、长文分页）',
      '思维导图渲染稳定性（预处理 + 降级）',
      '任务队列架构（asyncio.Queue + Worker）',
      '请求限流机制（令牌桶算法）',
      '完整 API 文档页面 (/api-docs)',
      '服务条款与隐私政策页面',
      '用户反馈功能'
    ],
    changed: [],
    fixed: []
  },
  {
    version: '1.0.0',
    date: '2024-12-23',
    added: [
      '核心总结功能',
      '思维导图生成',
      '视频播放集成',
      '暗色模式',
      '响应式设计',
      '云端部署支持'
    ],
    changed: [],
    fixed: []
  }
])
</script>
