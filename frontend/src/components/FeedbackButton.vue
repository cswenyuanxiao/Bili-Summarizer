<template>
  <button
    class="fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full bg-primary text-white shadow-2xl hover:scale-110 hover:shadow-primary/30 transition-all duration-300 flex items-center justify-center group"
    @click="emit('click')"
    aria-label="反馈建议"
    title="反馈建议"
  >
    <svg 
      class="w-7 h-7 transition-transform group-hover:rotate-12" 
      fill="none" 
      viewBox="0 0 24 24" 
      stroke="currentColor"
    >
      <path 
        stroke-linecap="round" 
        stroke-linejoin="round" 
        stroke-width="2" 
        d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
      />
    </svg>
    
    <!-- 小动画气泡 -->
    <span class="absolute top-0 right-0 flex h-3 w-3">
      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
      <span class="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
    </span>
  </button>
</template>

<script setup lang="ts">
const emit = defineEmits<{
  click: []
}>()
</script>
