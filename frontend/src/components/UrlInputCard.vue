<template>
  <div class="input-section relative z-20 fade-up delay-2">
    <div class="container mx-auto max-w-4xl px-4">
      <div class="input-card glass-card card-hover-elevate rounded-3xl p-6 sm:p-8 lg:p-10">
        <form @submit.prevent="handleSubmit">
          <!-- URL Input Row -->
          <div class="url-input-row flex flex-col md:flex-row gap-3 md:gap-4 mb-5 sm:mb-6">
            <input
              v-model="formData.url"
              type="text"
              id="video-url"
              class="flex-1 px-4 sm:px-6 py-3.5 sm:py-4 input-base text-base sm:text-lg"
              placeholder="粘贴 Bilibili 视频链接，例如: https://www.bilibili.com/video/BV..."
              required
            />
            <button
              type="submit"
              :disabled="isLoading"
              class="px-6 sm:px-8 py-3.5 sm:py-4 btn-primary transition-all flex items-center justify-center gap-2 w-full md:w-auto min-h-[44px]"
            >
              <span>✨</span> 生成总结
            </button>
          </div>

          <!-- Options Row -->
          <div class="options-row flex flex-col md:flex-row gap-3 md:gap-6">
            <div class="option-group flex flex-col md:flex-row md:items-center gap-2 md:gap-3 w-full md:w-auto">
              <label for="summarize-mode" class="text-sm font-semibold text-gray-600 dark:text-gray-400 whitespace-nowrap">
                模式
              </label>
              <select
                v-model="formData.mode"
                id="summarize-mode"
                class="px-4 py-2 border border-gray-300/80 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 cursor-pointer w-full md:w-auto"
              >
                <option value="smart">智能 (优先字幕)</option>
                <option value="video">视频 (画面分析)</option>
              </select>
            </div>

            <div class="option-group flex flex-col md:flex-row md:items-center gap-2 md:gap-3 w-full md:w-auto">
              <label for="analysis-focus" class="text-sm font-semibold text-gray-600 dark:text-gray-400 whitespace-nowrap">
                视角
              </label>
              <select
                v-model="formData.focus"
                id="analysis-focus"
                class="px-4 py-2 border border-gray-300/80 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 cursor-pointer w-full md:w-auto"
              >
                <option value="default">综合总结</option>
                <option value="study">深度学习</option>
                <option value="gossip">趣味互动</option>
                <option value="business">商业洞察</option>
              </select>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import type { SummarizeRequest } from '../types/api'

defineProps<{
  isLoading?: boolean
}>()

const emit = defineEmits<{
  submit: [request: SummarizeRequest]
}>()

const formData = reactive<SummarizeRequest>({
  url: '',
  mode: 'smart',
  focus: 'default',
})

const handleSubmit = () => {
  emit('submit', { ...formData })
}
</script>
