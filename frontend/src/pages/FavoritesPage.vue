<template>
  <div class="favorites-page min-h-screen pb-20">
    <div class="container mx-auto max-w-6xl px-4 py-8">
      <header class="mb-10 text-center">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2 flex items-center justify-center gap-2">
          <span class="icon-chip text-amber-500/80">
            <StarIcon class="h-5 w-5" />
          </span>
          我的收藏
        </h1>
        <p class="text-gray-500 dark:text-gray-400">保存你喜欢的总结内容，随时查看</p>
      </header>

      <!-- 加载状态 -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-20">
        <span class="icon-chip text-gray-400 mb-4">
          <ArrowPathIcon class="h-5 w-5 animate-spin" />
        </span>
        <p class="text-gray-500">正在加载收藏...</p>
      </div>

      <!-- 收藏列表 -->
      <div v-else-if="favorites.length > 0" class="space-y-4">
        <div 
          v-for="item in favorites" 
          :key="item.id"
          class="bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-white/40 dark:border-slate-800/50 shadow-xl rounded-2xl p-6 hover:shadow-2xl transition-all group"
        >
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1">
              <h3 class="font-bold text-lg text-gray-900 dark:text-gray-100 mb-2">
                {{ item.title }}
              </h3>
              <div class="text-xs text-gray-500 flex items-center gap-3">
                <span class="inline-flex items-center gap-1">
                  <span class="icon-chip-inline text-gray-400">
                    <CalendarDaysIcon class="h-3.5 w-3.5" />
                  </span>
                  {{ formatDate(item.created_at) }}
                </span>
              </div>
            </div>
            <button 
              class="opacity-0 group-hover:opacity-100 p-2 text-gray-400 hover:text-red-500 transition-all"
              title="删除收藏"
              @click="removeFavorite(item.id)"
            >
              <span class="icon-chip-inline text-red-500/80">
                <TrashIcon class="h-3.5 w-3.5" />
              </span>
            </button>
          </div>

          <p class="text-sm text-gray-600 dark:text-gray-300 line-clamp-3 mb-4">
            {{ item.summary || '(无总结内容)' }}
          </p>

          <div class="flex gap-2">
            <a 
              :href="`https://www.bilibili.com/video/${item.bvid}`" 
              target="_blank"
              class="px-4 py-2 bg-primary/10 text-primary rounded-lg text-sm font-medium hover:bg-primary/20 transition"
            >
              查看原视频
            </a>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="text-center py-20 bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-white/40 dark:border-slate-800/50 shadow-xl rounded-2xl">
        <div class="mx-auto mb-4 icon-chip text-primary/80">
          <InboxIcon class="h-5 w-5" />
        </div>
        <p class="text-gray-500 mb-2">还没有收藏任何总结</p>
        <p class="text-xs text-gray-400">在总结页面点击"收藏"按钮即可保存</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  ArrowPathIcon,
  CalendarDaysIcon,
  InboxIcon,
  StarIcon,
  TrashIcon,
} from '@heroicons/vue/24/outline'
import { supabase } from '../supabase'

interface Favorite {
  id: string
  bvid: string
  title: string
  cover: string
  summary: string
  created_at: string
}

const favorites = ref<Favorite[]>([])
const loading = ref(true)

onMounted(async () => {
  await fetchFavorites()
})

async function fetchFavorites() {
  loading.value = true
  try {
    // 获取认证token
    const { data: { session } } = await supabase.auth.getSession()
    
    if (!session) {
      console.warn('未登录，无法获取收藏列表')
      favorites.value = []
      loading.value = false
      return
    }
    
    // 调用后端API
    const response = await fetch('/api/favorites', {
      headers: {
        'Authorization': `Bearer ${session.access_token}`
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    favorites.value = data.favorites || []
    
  } catch (err) {
    console.error('获取收藏列表失败:', err)
    favorites.value = []
  } finally {
    loading.value = false
  }
}

async function removeFavorite(id: string) {
  if (!confirm('确定要删除这个收藏吗?')) return
  
  try {
    // 获取认证token
    const { data: { session } } = await supabase.auth.getSession()
    
    if (!session) {
      alert('请先登录')
      return
    }
    
    // 调用删除API
    const response = await fetch(`/api/favorites/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${session.access_token}`
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    
    // 更新本地列表
    favorites.value = favorites.value.filter(f => f.id !== id)
    
  } catch (err) {
    console.error('删除收藏失败:', err)
    alert('删除失败，请重试')
  }
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
