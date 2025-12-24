<template>
  <div class="api-endpoint border border-gray-200 dark:border-gray-700 rounded-2xl p-6 space-y-6">
    <!-- 标题栏 -->
    <div class="flex items-center gap-3 flex-wrap">
      <span 
        :class="methodClass"
        class="px-3 py-1 rounded-lg text-xs font-bold"
      >
        {{ endpoint.method }}
      </span>
      <code class="text-lg font-mono text-gray-900 dark:text-gray-100">{{ endpoint.path }}</code>
      <span v-if="endpoint.auth !== 'none'" class="badge-pill badge-soft text-xs">
        {{ authLabel }}
      </span>
    </div>
    
    <!-- 描述 -->
    <p class="text-gray-600 dark:text-gray-300">{{ endpoint.description }}</p>
    
    <!-- 请求参数 -->
    <div v-if="endpoint.params.length > 0">
      <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-3">请求参数</h4>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="px-4 py-2 text-left">参数名</th>
              <th class="px-4 py-2 text-left">类型</th>
              <th class="px-4 py-2 text-left">必填</th>
              <th class="px-4 py-2 text-left">说明</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="param in endpoint.params" :key="param.name">
              <td class="px-4 py-2">
                <code class="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">{{ param.name }}</code>
              </td>
              <td class="px-4 py-2 text-gray-600 dark:text-gray-400">{{ param.type }}</td>
              <td class="px-4 py-2">
                <span v-if="param.required" class="text-red-500">✓</span>
                <span v-else class="text-gray-400">○</span>
              </td>
              <td class="px-4 py-2 text-gray-600 dark:text-gray-300">
                {{ param.description }}
                <span v-if="param.example" class="text-xs text-gray-400 block mt-1">
                  示例：<code class="bg-gray-100 dark:bg-gray-800 px-1 rounded">{{ param.example }}</code>
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 请求示例 -->
    <div>
      <div class="flex items-center justify-between mb-3">
        <h4 class="font-semibold text-gray-900 dark:text-gray-100">请求示例</h4>
        <button 
          @click="copyCode(endpoint.requestExample)"
          class="text-xs text-primary hover:underline flex items-center gap-1"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
          </svg>
          复制
        </button>
      </div>
      <pre class="bg-gray-900 text-gray-100 p-4 rounded-xl overflow-x-auto text-sm"><code>{{ endpoint.requestExample }}</code></pre>
    </div>
    
    <!-- 响应示例 -->
    <div>
      <div class="flex items-center justify-between mb-3">
        <h4 class="font-semibold text-gray-900 dark:text-gray-100">响应示例</h4>
        <button 
          @click="copyCode(endpoint.responseExample)"
          class="text-xs text-primary hover:underline flex items-center gap-1"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
          </svg>
          复制
        </button>
      </div>
      <pre class="bg-gray-900 text-gray-100 p-4 rounded-xl overflow-x-auto text-sm"><code>{{ endpoint.responseExample }}</code></pre>
    </div>
    
    <!-- 错误码 -->
    <div v-if="endpoint.errors.length > 0">
      <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-3">错误码</h4>
      <div class="space-y-2">
        <div 
          v-for="error in endpoint.errors" 
          :key="error.code"
          class="flex items-start gap-3 text-sm p-3 bg-red-50 dark:bg-red-900/20 rounded-lg"
        >
          <span class="px-2 py-0.5 bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 rounded font-mono text-xs">
            {{ error.httpStatus }}
          </span>
          <div class="flex-1">
            <code class="text-red-700 dark:text-red-300 font-semibold">{{ error.code }}</code>
            <p class="text-gray-600 dark:text-gray-400 mt-1">{{ error.message }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 注意事项 -->
    <div v-if="endpoint.notes" class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-l-4 border-blue-500">
      <p class="text-sm text-gray-700 dark:text-gray-300">{{ endpoint.notes }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ApiEndpoint } from '../data/apiDocs'

const props = defineProps<{
  endpoint: ApiEndpoint
}>()

const methodClass = computed(() => {
  const classes = {
    GET: 'bg-green-500 text-white',
    POST: 'bg-blue-500 text-white',
    DELETE: 'bg-red-500 text-white',
    PUT: 'bg-yellow-500 text-white'
  }
  return classes[props.endpoint.method]
})

const authLabel = computed(() => {
  const labels = {
    none: '无需认证',
    jwt: '需要登录',
    'api-key': '需要 API Key'
  }
  return labels[props.endpoint.auth]
})

const copyCode = async (code: string) => {
  try {
    await navigator.clipboard.writeText(code)
    // TODO: 显示复制成功提示
  } catch (err) {
    console.error('复制失败:', err)
  }
}
</script>

<style scoped>
.api-endpoint table {
  border-collapse: separate;
  border-spacing: 0;
}

.api-endpoint tbody tr:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.dark .api-endpoint tbody tr:hover {
  background-color: rgba(255, 255, 255, 0.02);
}
</style>
