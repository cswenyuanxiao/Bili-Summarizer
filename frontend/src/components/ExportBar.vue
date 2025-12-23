<template>
  <div class="export-bar flex flex-col sm:flex-row gap-3 px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-slate-900/50">
    <button
      @click="$emit('export', 'md')"
      class="export-btn flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors w-full sm:w-auto min-h-[44px]"
    >
      📄 Markdown
    </button>
    <button
      @click="$emit('export', 'txt')"
      class="export-btn flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors w-full sm:w-auto min-h-[44px]"
    >
      📝 TXT
    </button>
    <button
      @click="$emit('export', 'pdf')"
      class="export-btn flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors w-full sm:w-auto min-h-[44px]"
    >
      📕 PDF
    </button>
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  export: [format: 'md' | 'txt' | 'pdf']
}>()
</script>
