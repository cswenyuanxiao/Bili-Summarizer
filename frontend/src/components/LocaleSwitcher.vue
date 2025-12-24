<template>
  <div class="locale-switcher relative">
    <button
      @click="isOpen = !isOpen"
      class="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      :title="$t('common.language')"
    >
      <span class="text-base">{{ localeFlag }}</span>
      <span class="hidden sm:inline">{{ localeName }}</span>
      <svg 
        class="w-3 h-3 transition-transform" 
        :class="{ 'rotate-180': isOpen }"
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>
    
    <!-- Dropdown -->
    <Transition name="dropdown">
      <div 
        v-if="isOpen"
        class="absolute right-0 top-full mt-1 w-36 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden z-50"
      >
        <button
          v-for="loc in availableLocales"
          :key="loc.code"
          @click="selectLocale(loc.code)"
          class="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          :class="{ 'bg-primary-light/20 dark:bg-primary/20': locale === loc.code }"
        >
          <span class="text-base">{{ loc.flag }}</span>
          <span>{{ loc.name }}</span>
          <svg 
            v-if="locale === loc.code"
            class="w-4 h-4 ml-auto text-primary" 
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useLocale } from '../composables/useLocale'

const { locale, localeName, localeFlag, availableLocales, setLocale } = useLocale()

const isOpen = ref(false)

function selectLocale(code: string) {
  setLocale(code)
  isOpen.value = false
}

// 点击外部关闭
function handleClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.locale-switcher')) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
