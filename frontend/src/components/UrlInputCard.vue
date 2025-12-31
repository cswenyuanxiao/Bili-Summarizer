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
              <span class="icon-chip-inline text-white/90">
                <SparklesIcon class="h-3.5 w-3.5" />
              </span>
              生成总结
            </button>
            <button
              type="button"
              class="px-5 py-3.5 btn-ghost border border-gray-200 dark:border-gray-700/50 rounded-xl text-sm font-medium hover:bg-gray-50/80 dark:hover:bg-gray-800/80 transition-colors"
              @click="$emit('bulk')"
            >
              <span class="icon-chip-inline text-gray-500 mr-1">
                <Squares2X2Icon class="h-3.5 w-3.5" />
              </span>
              批量导入
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
              <label for="summary-template" class="text-sm font-semibold text-gray-600 dark:text-gray-400 whitespace-nowrap">
                模板
              </label>
              <select
                v-model="formData.template_id"
                id="summary-template"
                class="px-4 py-2 border border-gray-300/80 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 cursor-pointer w-full md:w-auto min-w-[120px]"
              >
                <option :value="null">默认总结</option>
                <option v-for="t in templates" :key="t.id" :value="t.id">
                  {{ t.name }}
                </option>
              </select>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted, ref, watch } from 'vue'
import { SparklesIcon, Squares2X2Icon } from '@heroicons/vue/24/outline'
import type { SummarizeRequest } from '../types/api'

const props = defineProps<{
  isLoading?: boolean
  modelValue?: string
}>()

const emit = defineEmits<{
  submit: [request: SummarizeRequest]
  bulk: []
  'update:modelValue': [value: string]
}>()

const templates = ref<any[]>([])

const formData = reactive<SummarizeRequest & { template_id?: string | null }>({
  url: props.modelValue || '',
  mode: 'smart',
  focus: 'default',
  template_id: null
})

// 同步外部传入的 modelValue
watch(() => props.modelValue, (newVal) => {
  if (newVal !== undefined) {
    formData.url = newVal
  }
})

// 当本地 url 改变时通知外部
watch(() => formData.url, (newVal) => {
  emit('update:modelValue', newVal)
})

onMounted(async () => {
  try {
    const res = await fetch('/api/templates', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('supabase_token') || ''}`
      }
    })
    if (res.ok) {
      templates.value = await res.json()
    }
  } catch (err) {
    console.error('Failed to fetch templates:', err)
  }
})

const handleSubmit = () => {
  emit('submit', { ...formData } as any)
}
</script>
