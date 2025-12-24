<template>
  <div class="fixed inset-0 z-[60] flex items-center justify-center p-4 sm:p-6">
    <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" @click="$emit('close')"></div>
    
    <div class="relative w-full max-w-2xl glass-card rounded-3xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
      <div class="p-6 border-b border-gray-100 dark:border-slate-800 flex items-center justify-between">
        <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100 italic">选择视频进行对比</h3>
        <button @click="$emit('close')" class="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-full transition-colors text-xl">✕</button>
      </div>

      <div class="flex-1 overflow-y-auto p-6">
        <div v-if="loading" class="flex flex-col items-center justify-center py-20 grayscale opacity-50">
           <div class="animate-spin text-4xl mb-4">🌀</div>
           <p>正在拉取历史记录...</p>
        </div>

        <div v-else-if="items.length === 0" class="text-center py-20">
          <p class="text-gray-500">暂无历史记录</p>
        </div>

        <div v-else class="grid grid-cols-1 gap-3">
          <div 
            v-for="item in availableItems" 
            :key="item.id"
            class="flex items-center gap-4 p-3 rounded-2xl bg-gray-50 dark:bg-slate-900/50 border border-gray-100 dark:border-slate-800 hover:border-primary transition cursor-pointer group"
            @click="$emit('select', item)"
          >
            <img :src="item.thumbnail" class="w-24 h-14 rounded-xl object-cover shadow-sm" />
            <div class="flex-1 min-w-0">
              <div class="font-bold text-gray-900 dark:text-gray-100 line-clamp-1 group-hover:text-primary transition-colors text-sm">
                {{ item.title }}
              </div>
              <div class="text-[10px] text-gray-500 mt-1">
                {{ formatDate(item.created_at) }} · {{ item.mode }}
              </div>
            </div>
            <div class="text-primary text-xl opacity-0 group-hover:opacity-100">＋</div>
          </div>
        </div>
      </div>

      <div class="p-4 bg-gray-50 dark:bg-slate-900/80 border-t border-gray-100 dark:border-slate-800 text-center text-xs text-gray-400">
        只能选择已生成的总结内容进行对比
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const props = defineProps<{
  excludeIds: string[]
}>()

const emit = defineEmits(['close', 'select'])

const items = ref<any[]>([])
const loading = ref(true)

const availableItems = computed(() => {
  return items.value.filter(i => !props.excludeIds.includes(i.id))
})

async function fetchHistory() {
  loading.value = true
  try {
    const token = localStorage.getItem('supabase_token')
    const res = await fetch('/api/history', {
      headers: { 'Authorization': `Bearer ${token || ''}` }
    })
    const data = await res.json()
    items.value = (data.history || []).map((i: any) => ({
      id: i.id,
      title: i.video_title || '未命名',
      thumbnail: i.video_thumbnail || 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?auto=format&fit=crop&q=80&w=200',
      summary: i.summary,
      mode: i.mode,
      created_at: i.created_at
    }))
  } catch (err) {
    console.error('Fetch history failed:', err)
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string) {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

onMounted(() => {
  fetchHistory()
})
</script>
