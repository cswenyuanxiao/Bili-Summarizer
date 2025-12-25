/**
 * LazyImage - 图片懒加载组件
 * 使用 IntersectionObserver 实现懒加载，减少初始加载时间
 */
<template>
  <div 
    ref="containerRef"
    class="lazy-image-container"
    :class="containerClass"
  >
    <!-- 占位骨架屏 -->
    <div 
      v-if="!isLoaded && !isError" 
      class="lazy-image-skeleton absolute inset-0 bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-shimmer"
    />
    
    <!-- 实际图片 -->
    <img
      v-if="shouldLoad"
      :src="src"
      :alt="alt"
      :class="[imageClass, { 'opacity-0': !isLoaded, 'opacity-100 transition-opacity duration-300': isLoaded }]"
      @load="handleLoad"
      @error="handleError"
    />
    
    <!-- 错误状态 -->
    <div 
      v-if="isError" 
      class="lazy-image-error absolute inset-0 flex items-center justify-center bg-gray-100 dark:bg-gray-800 text-gray-400"
    >
      <span class="icon-chip text-gray-400">
        <PhotoIcon class="h-4 w-4" />
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { PhotoIcon } from '@heroicons/vue/24/outline'

const props = withDefaults(defineProps<{
  src: string
  alt?: string
  containerClass?: string
  imageClass?: string
  rootMargin?: string
  threshold?: number
}>(), {
  alt: '',
  containerClass: '',
  imageClass: '',
  rootMargin: '200px',
  threshold: 0.01
})

const containerRef = ref<HTMLElement | null>(null)
const shouldLoad = ref(false)
const isLoaded = ref(false)
const isError = ref(false)

let observer: IntersectionObserver | null = null

const handleLoad = () => {
  isLoaded.value = true
}

const handleError = () => {
  isError.value = true
}

onMounted(() => {
  if (!containerRef.value) return
  
  // 使用 IntersectionObserver 检测可见性
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          shouldLoad.value = true
          observer?.disconnect()
        }
      })
    },
    {
      rootMargin: props.rootMargin,
      threshold: props.threshold
    }
  )
  
  observer.observe(containerRef.value)
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<style scoped>
.lazy-image-container {
  position: relative;
  overflow: hidden;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.animate-shimmer {
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
</style>
