<template>
  <main class="min-h-screen pb-20 page-shell">
    <div class="container mx-auto max-w-6xl px-4">
      <!-- Hero Section -->
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

      <!-- 产品演示区 -->
      <section class="mt-12" data-reveal>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 text-center">产品演示</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="page-card">
            <img 
              src="/assets/demo/summary.png" 
              alt="AI 总结过程演示" 
              class="w-full h-48 object-cover rounded-lg mb-3"
            />
            <div class="text-base font-semibold text-gray-900 dark:text-gray-100">实时总结</div>
            <div class="mt-2 text-xs text-gray-500">SSE 推送，在线观看 AI 思考过程</div>
          </div>
          <div class="page-card">
            <img 
              src="/assets/demo/mindmap.png" 
              alt="思维导图生成演示" 
              class="w-full h-48 object-cover rounded-lg mb-3"
            />
            <div class="text-base font-semibold text-gray-900 dark:text-gray-100">智能导图</div>
            <div class="mt-2 text-xs text-gray-500">自动生成知识结构，支持 SVG/PNG 导出</div>
          </div>
        </div>
      </section>

      <!-- 三大核心能力 -->
      <section class="grid grid-cols-1 md:grid-cols-3 gap-5 text-sm text-gray-600 dark:text-gray-300 mt-12" data-reveal>
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

      <!-- 使用场景区 -->
      <section class="mt-12" data-reveal>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 text-center">适用场景</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div class="page-card text-center">
            <div class="mx-auto mb-3 icon-chip bg-blue-100/70 dark:bg-blue-900/30 text-blue-600 dark:text-blue-300">
              <AcademicCapIcon class="h-5 w-5" />
            </div>
            <div class="text-base font-semibold text-gray-900 dark:text-gray-100">学生学习</div>
            <div class="mt-2 text-xs text-gray-500">快速提取课程重点，生成复习笔记</div>
          </div>
          <div class="page-card text-center page-card--accent">
            <div class="mx-auto mb-3 icon-chip bg-purple-100/70 dark:bg-purple-900/30 text-purple-600 dark:text-purple-300">
              <PencilSquareIcon class="h-5 w-5" />
            </div>
            <div class="text-base font-semibold text-gray-900 dark:text-gray-100">创作者研究</div>
            <div class="mt-2 text-xs text-gray-500">分析爆款视频，挖掘内容灵感</div>
          </div>
          <div class="page-card text-center">
            <div class="mx-auto mb-3 icon-chip bg-emerald-100/70 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-300">
              <CodeBracketIcon class="h-5 w-5" />
            </div>
            <div class="text-base font-semibold text-gray-900 dark:text-gray-100">开发者学习</div>
            <div class="mt-2 text-xs text-gray-500">快速学习技术教程，整理知识点</div>
          </div>
        </div>
      </section>

      <!-- 技术优势区 -->
      <section class="mt-12 mb-8" data-reveal>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6 text-center">技术优势</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div class="page-card">
            <div class="flex items-center gap-2 text-base font-semibold text-gray-900 dark:text-gray-100">
              <span class="icon-chip-sm text-primary/80">
                <BoltIcon class="h-4 w-4" />
              </span>
              SSE 实时推送
            </div>
            <div class="mt-2 text-xs text-gray-500 leading-relaxed">
              Server-Sent Events 技术，实时展示 AI 思考过程，告别漫长等待
            </div>
          </div>
          <div class="page-card">
            <div class="flex items-center gap-2 text-base font-semibold text-gray-900 dark:text-gray-100">
              <span class="icon-chip-sm text-primary/80">
                <MapIcon class="h-4 w-4" />
              </span>
              智能思维导图
            </div>
            <div class="mt-2 text-xs text-gray-500 leading-relaxed">
              基于 Mermaid.js 自动生成知识结构，支持 SVG/PNG 多格式导出
            </div>
          </div>
          <div class="page-card">
            <div class="flex items-center gap-2 text-base font-semibold text-gray-900 dark:text-gray-100">
              <span class="icon-chip-sm text-primary/80">
                <ChatBubbleLeftRightIcon class="h-4 w-4" />
              </span>
              AI 追问功能
            </div>
            <div class="mt-2 text-xs text-gray-500 leading-relaxed">
              基于视频内容深度对话，挖掘细节与延伸知识
            </div>
          </div>
        </div>
      </section>

      <!-- CTA -->
      <section class="mt-12 text-center" data-reveal>
        <button class="btn-primary px-8 py-3 text-base wiggle-soft" @click="goHome">
          开始使用 Bili-Summarizer
        </button>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import {
  AcademicCapIcon,
  BoltIcon,
  ChatBubbleLeftRightIcon,
  CodeBracketIcon,
  MapIcon,
  PencilSquareIcon,
} from '@heroicons/vue/24/outline'
import { useRouter } from 'vue-router'
import { useReveal } from '../composables/useReveal'

const router = useRouter()
useReveal()
const goHome = () => {
  router.push('/')
}
</script>
