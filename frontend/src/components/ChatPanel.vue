<template>
  <div class="chat-panel bg-white dark:bg-slate-800 rounded-3xl shadow-xl p-6 border border-gray-200 dark:border-gray-700">
    <h3 class="text-xl font-bold mb-4 flex items-center gap-2 text-gray-900 dark:text-gray-100">
      <span class="text-2xl">💬</span>
      AI 追问
    </h3>
    
    <!-- 对话历史 -->
    <div ref="chatHistory" class="chat-history space-y-4 mb-4 max-h-96 overflow-y-auto">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        :class="[
          'flex',
          msg.role === 'user' ? 'justify-end' : 'justify-start'
        ]"
      >
        <div
          :class="[
            'max-w-[80%] p-4 rounded-2xl shadow-sm',
            msg.role === 'user' 
              ? 'bg-gradient-to-br from-primary to-purple-600 text-white' 
              : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
          ]"
        >
          <div class="text-xs font-semibold mb-1 opacity-70">
            {{ msg.role === 'user' ? '你' : 'AI 助手' }}
          </div>
          <div 
            class="prose prose-sm dark:prose-invert max-w-none"
            :class="msg.role === 'user' ? 'prose-invert' : ''"
            v-html="marked(msg.content)"
          />
        </div>
      </div>
      
      <!-- 加载中动画 -->
      <div v-if="isLoading" class="flex items-start gap-3">
        <div class="max-w-[80%] p-4 rounded-2xl shadow-sm bg-gray-100 dark:bg-gray-700">
          <div class="text-xs font-semibold mb-1 opacity-70 text-gray-900 dark:text-gray-100">AI 助手</div>
          <div class="flex items-center gap-2 text-gray-600 dark:text-gray-400">
            <div class="flex gap-1">
              <div class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 0s"></div>
              <div class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
              <div class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            </div>
            <span class="text-sm">正在思考...</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 输入框 -->
    <div class="flex gap-3">
      <input
        v-model="input"
        @keyup.enter="sendMessage"
        :disabled="isLoading"
        placeholder="追问细节问题..."
        class="flex-1 px-4 py-3 input-base text-base"
      />
      <button
        @click="sendMessage"
        :disabled="!input.trim() || isLoading"
        class="px-6 py-3 btn-primary transition-all flex items-center justify-center min-w-[80px]"
      >
        <span v-if="!isLoading">发送</span>
        <span v-else>...</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { marked } from 'marked'

const props = defineProps<{
  summary: string
  transcript: string
}>()

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const messages = ref<Message[]>([])
const input = ref('')
const isLoading = ref(false)
const chatHistory = ref<HTMLElement | null>(null)

// 自动滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (chatHistory.value) {
    chatHistory.value.scrollTop = chatHistory.value.scrollHeight
  }
}

watch(messages, () => {
  scrollToBottom()
}, { deep: true })

async function sendMessage() {
  if (!input.value.trim() || isLoading.value) return
  
  const question = input.value.trim()
  input.value = ''
  isLoading.value = true
  
  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: question
  })
  
  scrollToBottom()
  
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        summary: props.summary,
        transcript: props.transcript,
        question,
        history: messages.value.slice(0, -1) // 不包含刚添加的用户消息
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('No response body')
    }
    const decoder = new TextDecoder()
    
    let assistantMessage = ''
    
    // 添加空的 assistant 消息
    messages.value.push({
      role: 'assistant',
      content: ''
    })
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      const text = decoder.decode(value)
      const lines = text.split('\n')
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            
            if (data.content) {
              assistantMessage += data.content
              const lastMessage = messages.value[messages.value.length - 1]
              if (lastMessage) {
                lastMessage.content = assistantMessage
              }
              scrollToBottom()
            }
            
            if (data.done) {
              isLoading.value = false
            }
            
            if (data.error) {
              throw new Error(data.error)
            }
          } catch (e) {
            if (!(e instanceof SyntaxError)) {
              console.error('Parse error:', e)
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('Chat error:', error)
    alert('追问失败，请重试')
    // 移除失败的消息
    const lastMessage = messages.value[messages.value.length - 1]
    if (lastMessage?.role === 'assistant' && !lastMessage.content) {
      messages.value.pop()
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.chat-history::-webkit-scrollbar {
  width: 6px;
}

.chat-history::-webkit-scrollbar-track {
  background: transparent;
}

.chat-history::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.dark .chat-history::-webkit-scrollbar-thumb {
  background: #475569;
}

.prose :deep(p) {
  margin: 0.5em 0;
}

.prose :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 0.2em 0.4em;
  border-radius: 0.25em;
  font-size: 0.9em;
}

.prose-invert :deep(code) {
  background: rgba(255, 255, 255, 0.2);
}
</style>
