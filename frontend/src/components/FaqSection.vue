<template>
  <div class="space-y-3">
    <div 
      v-for="(item, index) in items" 
      :key="index" 
      class="page-card overflow-hidden"
    >
      <button
        :aria-expanded="openIndex === index"
        :aria-controls="`faq-answer-${index}`"
        class="w-full p-4 text-left flex items-center justify-between gap-4 card-action"
        type="button"
        @click="toggle(index)"
        @keydown.enter.prevent="toggle(index)"
        @keydown.space.prevent="toggle(index)"
      >
        <span class="font-medium text-gray-900 dark:text-gray-100 text-sm">{{ item.question }}</span>
        <span 
          class="text-gray-400 text-xl font-light transition-transform duration-200 flex-shrink-0"
          :class="{ 'rotate-45': openIndex === index }"
        >+</span>
      </button>
      <div
        :id="`faq-answer-${index}`"
        class="overflow-hidden transition-all duration-300 ease-in-out"
        :style="{ maxHeight: openIndex === index ? '500px' : '0' }"
      >
        <div class="px-4 pb-4 text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
          {{ item.answer }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface FaqItem {
  question: string
  answer: string
}

defineProps<{
  items: FaqItem[]
}>()

const openIndex = ref<number | null>(null)

const toggle = (index: number) => {
  openIndex.value = openIndex.value === index ? null : index
}
</script>
