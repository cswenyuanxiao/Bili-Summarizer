<template>
  <main class="min-h-screen pb-20 page-shell">
    <div class="container mx-auto max-w-6xl px-4">
      <!-- Hero Section -->
      <section class="page-hero space-y-4" data-reveal>
        <div class="page-hero__cloud" aria-hidden="true"></div>
        <p class="page-hero__kicker">Docs</p>
        <h1 class="page-hero__title">使用文档</h1>
        <p class="page-hero__subtitle">快速上手与常见问题。</p>
        <div class="flex flex-wrap gap-3">
          <button class="btn-primary px-5 py-2 text-sm wiggle-soft" @click="openUsageGuide">查看详细指南</button>
          <span class="badge-pill badge-soft">最新版本</span>
        </div>
      </section>

      <!-- 快速上手 -->
      <section class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600 dark:text-gray-300 mt-8" data-reveal>
        <button class="page-card card-hover-elevate card-action" type="button" @click="openUsageGuide">
          <div class="text-base font-semibold text-gray-900 dark:text-gray-100">快速上手</div>
          <ol class="mt-2 space-y-1 text-xs text-gray-500 list-decimal list-inside">
            <li>登录后获取积分</li>
            <li>粘贴 B 站链接生成总结</li>
            <li>导出或分享结果</li>
          </ol>
          <div class="mt-4 text-xs text-primary font-semibold">打开指南 →</div>
        </button>
        <button class="page-card card-hover-elevate page-card--accent card-action" type="button" @click="openUsageGuide">
          <div class="text-base font-semibold text-gray-900 dark:text-gray-100">常见问题</div>
          <div class="mt-2 text-xs text-gray-500">积分不足时可购买额度包或升级订阅。</div>
          <div class="mt-4 text-xs text-primary font-semibold">查看 FAQ →</div>
        </button>
      </section>

      <!-- 功能详解 -->
      <section class="mt-12" data-reveal>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">功能详解</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div class="page-card">
            <div class="flex items-center gap-2 text-base font-semibold text-gray-900 dark:text-gray-100">
              <span class="icon-chip-sm text-primary/80">
                <DocumentTextIcon class="h-4 w-4" />
              </span>
              视频总结
            </div>
            <div class="mt-2 text-xs text-gray-500 leading-relaxed">
              支持智能模式（优先字幕）和视频模式（AI 分析画面），提供结构化总结和关键观点提取
            </div>
          </div>
          <div class="page-card">
            <div class="flex items-center gap-2 text-base font-semibold text-gray-900 dark:text-gray-100">
              <span class="icon-chip-sm text-primary/80">
                <MapIcon class="h-4 w-4" />
              </span>
              思维导图
            </div>
            <div class="mt-2 text-xs text-gray-500 leading-relaxed">
              自动生成 Mermaid 格式思维导图，支持导出 SVG/PNG，可在其他工具中继续编辑
            </div>
          </div>
          <div class="page-card">
            <div class="flex items-center gap-2 text-base font-semibold text-gray-900 dark:text-gray-100">
              <span class="icon-chip-sm text-primary/80">
                <ChatBubbleLeftRightIcon class="h-4 w-4" />
              </span>
              AI 追问
            </div>
            <div class="mt-2 text-xs text-gray-500 leading-relaxed">
              基于视频内容进行深度对话，挖掘细节、解答疑问、探索延伸知识
            </div>
          </div>
        </div>
      </section>

      <!-- 开发者文档 -->
      <section class="mt-12" data-reveal>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">开发者文档</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <button class="page-card card-hover-elevate card-action" type="button" @click="goToDeveloper">
            <div class="flex items-center gap-2 text-base font-semibold text-gray-900 dark:text-gray-100">
              <span class="icon-chip-sm text-primary/80">
                <KeyIcon class="h-4 w-4" />
              </span>
              API 接入
            </div>
            <div class="mt-2 text-xs text-gray-500 leading-relaxed">
              获取 API Key，通过 RESTful API 调用总结功能，集成到您的应用中
            </div>
            <div class="mt-4 text-xs text-primary font-semibold">查看 API 文档 →</div>
          </button>
          <div class="page-card">
            <div class="flex items-center gap-2 text-base font-semibold text-gray-900 dark:text-gray-100">
              <span class="icon-chip-sm text-amber-500/80">
                <ExclamationTriangleIcon class="h-4 w-4" />
              </span>
              错误码说明
            </div>
            <div class="mt-2 text-xs text-gray-500 space-y-1">
              <div>• 403: 积分不足</div>
              <div>• 429: 请求频率过高</div>
              <div>• 500: 视频下载失败</div>
            </div>
          </div>
        </div>
      </section>

      <!-- FAQ -->
      <section class="mt-12" data-reveal>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">常见问题</h2>
        <FaqSection :items="docsFaq" />
      </section>

      <!-- 贡献指南 -->
      <section class="mt-12 text-center" data-reveal>
        <div class="page-card max-w-2xl mx-auto">
          <div class="flex items-center justify-center gap-2 text-base font-semibold text-gray-900 dark:text-gray-100 mb-2">
            <span class="icon-chip-sm text-primary/80">
              <CodeBracketSquareIcon class="h-4 w-4" />
            </span>
            开源贡献
          </div>
          <div class="text-xs text-gray-500 leading-relaxed mb-4">
            Bili-Summarizer 是开源项目，欢迎提交 Issue 和 Pull Request
          </div>
          <a 
            href="https://github.com/cswenyuanxiao/Bili-Summarizer" 
            target="_blank"
            rel="noopener noreferrer"
            class="inline-block btn-primary px-5 py-2 text-sm"
          >
            访问 GitHub →
          </a>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { inject } from 'vue'
import {
  ChatBubbleLeftRightIcon,
  CodeBracketSquareIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  KeyIcon,
  MapIcon,
} from '@heroicons/vue/24/outline'
import { useRouter } from 'vue-router'
import { useReveal } from '../composables/useReveal'
import FaqSection from '../components/FaqSection.vue'

useReveal()
const router = useRouter()
const appActions = inject<{ openUsageGuide: () => void }>('appActions')
const openUsageGuide = () => appActions?.openUsageGuide()
const goToDeveloper = () => router.push('/developer')

const docsFaq = [
  {
    question: '支持哪些视频平台？',
    answer: '目前仅支持 Bilibili（B 站）视频。支持 BV 号、AV 号、短链接等多种格式。'
  },
  {
    question: '思维导图支持哪些格式？',
    answer: '思维导图基于 Mermaid.js 生成，支持导出 SVG 和 PNG 格式。SVG 格式可在 Figma、Sketch 等设计工具中编辑。'
  },
  {
    question: '如何保存历史记录？',
    answer: '登录后的总结会自动保存到云端。在仪表盘页面可以查看所有历史记录，支持搜索和筛选。'
  },
  {
    question: 'API 如何获取 Key？',
    answer: '访问开发者页面，点击"生成 API Key"即可创建。Pro 专业版用户可创建多个 Key，并设置单独的权限。'
  }
]
</script>
