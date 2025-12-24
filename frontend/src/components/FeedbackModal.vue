<template>
  <Teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      @click.self="emit('close')"
    >
      <div
        class="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-md shadow-2xl transform transition-all"
        role="dialog"
        aria-labelledby="feedback-title"
        aria-modal="true"
      >
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 id="feedback-title" class="text-xl font-bold text-gray-900 dark:text-gray-100">
            反馈与建议
          </h2>
          <button
            @click="emit('close')"
            class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            aria-label="关闭"
          >
            <span class="text-xl text-gray-500">×</span>
          </button>
        </div>

        <!-- Body -->
        <div class="p-6 space-y-5">
          <!-- 反馈类型 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              反馈类型
            </label>
            <div class="flex flex-wrap gap-3">
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  v-model="feedbackType"
                  value="bug"
                  class="w-4 h-4 text-primary focus:ring-primary"
                />
                <span class="text-sm text-gray-700 dark:text-gray-300">🐛 问题反馈</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  v-model="feedbackType"
                  value="feature"
                  class="w-4 h-4 text-primary focus:ring-primary"
                />
                <span class="text-sm text-gray-700 dark:text-gray-300">💡 功能建议</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  v-model="feedbackType"
                  value="other"
                  class="w-4 h-4 text-primary focus:ring-primary"
                />
                <span class="text-sm text-gray-700 dark:text-gray-300">💬 其他</span>
              </label>
            </div>
          </div>

          <!-- 反馈内容 -->
          <div>
            <label for="feedback-content" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              详细描述
            </label>
            <textarea
              id="feedback-content"
              v-model="content"
              class="w-full h-32 p-3 border border-gray-300 dark:border-gray-600 rounded-xl resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="请描述您遇到的问题或您的建议..."
              :disabled="submitting"
            ></textarea>
            <p class="mt-1 text-xs text-gray-500">{{ content.length }} / 500</p>
          </div>

          <!-- 联系方式 -->
          <div>
            <label for="feedback-contact" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              联系方式 <span class="text-gray-400">(可选)</span>
            </label>
            <input
              id="feedback-contact"
              type="email"
              v-model="contact"
              class="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="your@email.com"
              :disabled="submitting"
            />
          </div>

          <!-- 错误/成功提示 -->
          <div v-if="error" class="p-3 rounded-xl bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm">
            {{ error }}
          </div>
          <div v-if="success" class="p-3 rounded-xl bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 text-sm">
            感谢您的反馈！我们会尽快处理。
          </div>
        </div>

        <!-- Footer -->
        <div class="flex gap-3 justify-end p-6 border-t border-gray-200 dark:border-gray-700">
          <button
            @click="emit('close')"
            class="px-5 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-colors"
            :disabled="submitting"
          >
            取消
          </button>
          <button
            @click="submitFeedback"
            class="btn-primary px-5 py-2 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="!canSubmit || submitting"
          >
            {{ submitting ? '提交中...' : '提交反馈' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { isSupabaseConfigured, supabase } from '../supabase'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const feedbackType = ref<'bug' | 'feature' | 'other'>('bug')
const content = ref('')
const contact = ref('')
const submitting = ref(false)
const error = ref('')
const success = ref(false)

const canSubmit = computed(() => {
  return content.value.trim().length > 0 && content.value.length <= 500
})

const resetForm = () => {
  feedbackType.value = 'bug'
  content.value = ''
  contact.value = ''
  error.value = ''
  success.value = false
  submitting.value = false
}

const submitFeedback = async () => {
  if (!canSubmit.value) return

  submitting.value = true
  error.value = ''
  success.value = false

  try {
    const payload: any = {
      feedback_type: feedbackType.value,
      content: content.value.trim(),
      contact: contact.value.trim() || null
    }

    // 如果用户已登录，添加 token
    let headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }
    if (isSupabaseConfigured && supabase) {
      const { data } = await supabase.auth.getSession()
      if (data.session?.access_token) {
        headers['Authorization'] = `Bearer ${data.session.access_token}`
      }
    }

    const response = await fetch('/api/feedback', {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: '提交失败' }))
      throw new Error(errorData.detail || `请求失败 (${response.status})`)
    }

    success.value = true
    setTimeout(() => {
      emit('close')
      resetForm()
    }, 2000)
  } catch (err: any) {
    error.value = err.message || '提交失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    resetForm()
  }
})
</script>
