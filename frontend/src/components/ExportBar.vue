<template>
  <div class="export-bar flex flex-col sm:flex-row gap-3 px-4 sm:px-6 py-4 border-t border-gray-200/70 dark:border-gray-700/70 bg-white/60 dark:bg-slate-900/50">
    <button
      @click="$emit('export', 'md')"
      class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl btn-ghost hover:bg-white/60 dark:hover:bg-gray-700/60 transition-all text-sm group"
    >
      <span class="text-lg group-hover:scale-110 transition-transform">📄</span>
      <span>Markdown</span>
    </button>
    <button
      @click="$emit('export', 'txt')"
      class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl btn-ghost hover:bg-white/60 dark:hover:bg-gray-700/60 transition-all text-sm group"
    >
      <span class="text-lg group-hover:scale-110 transition-transform">📝</span>
      <span>TXT</span>
    </button>
    <button
      @click="$emit('export', 'pdf')"
      class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl btn-ghost hover:bg-white/60 dark:hover:bg-gray-700/60 transition-all text-sm group"
    >
      <span class="text-lg group-hover:scale-110 transition-transform">📕</span>
      <span>PDF</span>
    </button>
    <button
      @click="$emit('share')"
      class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl btn-primary shadow-sm hover:shadow-md transition-all text-sm group"
    >
      <span class="text-lg group-hover:scale-110 transition-transform">🎨</span>
      <span>分享卡片</span>
    </button>
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  export: [format: 'md' | 'txt' | 'pdf']
  share: []
}>()
</script>
