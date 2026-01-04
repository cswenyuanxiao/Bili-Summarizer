<template>
  <div v-if="steps && steps.length > 0" class="cot-panel">
    <div class="cot-header">
      <h3>🧠 AI 分析思路</h3>
      <button @click="$emit('close')" class="close-btn">×</button>
    </div>
    
    <div class="cot-steps">
      <div 
        v-for="step in steps" 
        :key="step.step" 
        class="cot-step"
        :class="{ 'active': currentStep >= step.step }"
      >
        <div class="step-header">
          <span class="step-number">{{ step.step }}</span>
          <h4>{{ step.title }}</h4>
        </div>
        <p class="step-thinking">{{ step.thinking }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface CoTStep {
  step: number
  title: string
  thinking: string
}

const props = defineProps<{
  steps: CoTStep[]
}>()

defineEmits<{
  close: []
}>()

const currentStep = ref(0)

// 渐进式显示步骤
watch(() => props.steps, (newSteps) => {
  if (newSteps && newSteps.length > 0) {
    currentStep.value = 0
    const interval = setInterval(() => {
      if (currentStep.value < newSteps.length) {
        currentStep.value++
      } else {
        clearInterval(interval)
      }
    }, 800)
  }
}, { immediate: true })
</script>

<style scoped>
.cot-panel {
  background: linear-gradient(135deg, #f8f9ff 0%, #fff5f5 100%);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid rgba(79, 70, 229, 0.1);
}

.cot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.cot-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #4f46e5;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  color: #9ca3af;
  cursor: pointer;
  line-height: 1;
  padding: 0 8px;
}

.close-btn:hover {
  color: #4f46e5;
}

.cot-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cot-step {
  background: white;
  border-radius: 12px;
  padding: 16px;
  border-left: 4px solid #e5e7eb;
  opacity: 0.4;
  transform: translateX(-10px);
  transition: all 0.5s ease;
}

.cot-step.active {
  opacity: 1;
  transform: translateX(0);
  border-left-color: #4f46e5;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: white;
  border-radius: 50%;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.step-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.step-thinking {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
  line-height: 1.6;
  padding-left: 40px;
}

@media (max-width: 768px) {
  .cot-panel {
    padding: 16px;
  }
  
  .step-thinking {
    padding-left: 0;
  }
}
</style>
