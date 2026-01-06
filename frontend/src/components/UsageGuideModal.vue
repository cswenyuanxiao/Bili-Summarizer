<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @mousedown.self="$emit('close')">
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto transform transition-all">
      <div class="p-6 text-center border-b border-gray-100 dark:border-gray-700">
        <h2 class="text-2xl font-bold bg-gradient-to-r from-primary to-cyan-500 bg-clip-text text-transparent">
          使用文档
        </h2>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
          快速上手与访问入口
        </p>
      </div>

      <div class="p-6 space-y-6 text-sm text-gray-700 dark:text-gray-200">
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2">快速上手</h3>
          <ol class="list-decimal ml-5 space-y-1">
            <li>粘贴 Bilibili 视频链接，选择模式与视角。</li>
            <li>等待生成结果，查看总结、转录与思维导图。</li>
            <li>需要导出时使用 Markdown/TXT/PDF 或 SVG/PNG。</li>
          </ol>
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2">推荐访问入口</h3>
          <ul class="list-disc ml-5 space-y-1">
            <li>开发调试：`http://localhost:5173`</li>
            <li>本地准上线：`http://localhost:8000`</li>
            <li>Docker：`http://localhost`</li>
            <li>Render：服务 URL（例如 `https://xxx.onrender.com`）</li>
          </ul>
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2">历史记录说明</h3>
          <p>
            历史记录保存在浏览器 localStorage 中，按“域名 + 端口”隔离。切换地址后历史会显示为空。
          </p>
        </div>
      </div>

      <div class="px-6 py-4 bg-gray-50 dark:bg-gray-700/50 flex items-center justify-end">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-sm bg-white dark:bg-slate-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors"
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  show: boolean
}>()

defineEmits<{
  close: []
}>()
</script>
