<template>
  <div class="subscriptions-page min-h-screen pb-20">
    <div class="container mx-auto max-w-4xl px-4 py-8">
      <header class="mb-10 text-center">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">每日总结推送</h1>
        <p class="text-gray-500 dark:text-gray-400">关注你喜爱的 UP 主，第一时间获取 AI 视频总结</p>
      </header>

      <!-- 搜索栏 -->
      <section class="mb-12">
        <div class="bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-white/40 dark:border-slate-800/50 shadow-xl rounded-2xl p-6 shadow-sm">
          <h2 class="text-lg font-semibold mb-4 flex items-center gap-2">
            <span class="icon-chip-sm text-primary/80">
              <MagnifyingGlassIcon class="h-4 w-4" />
            </span>
            发现 UP 主
          </h2>
          <div class="flex gap-3">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="输入 UP 主昵称或关键词..."
              class="flex-1 px-4 py-3 rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 focus:ring-2 focus:ring-primary outline-none transition"
              @keyup.enter="handleSearch"
            />
            <button 
              class="px-6 py-3 bg-primary text-white rounded-xl font-semibold hover:opacity-90 transition disabled:opacity-50"
              :disabled="searching || searchQuery.length < 2"
              @click="handleSearch"
            >
              {{ searching ? '搜索中...' : '搜索' }}
            </button>
          </div>

          <!-- 搜索结果 -->
          <div v-if="searchResults.length > 0" class="mt-6 space-y-3">
            <div 
              v-for="up in searchResults" 
              :key="up.mid"
              class="flex items-center justify-between p-4 rounded-xl bg-gray-50 dark:bg-slate-900/50 border border-gray-100 dark:border-slate-800"
            >
              <a 
                :href="`https://space.bilibili.com/${up.mid}`" 
                target="_blank"
                class="flex items-center gap-4 hover:opacity-80 transition-opacity"
              >
                <img :src="getProxyUrl(up.avatar)" class="w-12 h-12 rounded-full border-2 border-white dark:border-slate-700" />
                <div>
                  <div class="font-bold text-gray-900 dark:text-gray-100">{{ up.name }}</div>
                  <div class="text-xs text-gray-500">{{ up.fans }} 粉丝 · {{ up.videos }} 视频</div>
                </div>
              </a>
              <button 
                class="px-4 py-2 rounded-lg text-sm font-semibold transition"
                :class="isSubscribed(up.mid) ? 'bg-gray-200 text-gray-500 cursor-not-allowed' : 'bg-primary/10 text-primary hover:bg-primary/20'"
                :disabled="isSubscribed(up.mid)"
                @click="handleSubscribe(up)"
              >
                {{ isSubscribed(up.mid) ? '已订阅' : '订阅' }}
              </button>
            </div>
          </div>
          <div v-else-if="searched && !searching" class="mt-6 text-center text-gray-500 text-sm">
            未找到相关 UP 主
          </div>
        </div>
      </section>

      <!-- 订阅列表 -->
      <section>
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <span class="icon-chip-sm text-primary/80">
              <FolderIcon class="h-4 w-4" />
            </span>
            我的关注 ({{ subscriptions.length }})
          </h2>
          <button 
            class="text-sm text-primary hover:underline font-medium"
            @click="enablePushNotifications"
          >
            <span class="inline-flex items-center gap-1">
              <span class="icon-chip-inline text-primary/80">
                <BellAlertIcon class="h-3.5 w-3.5" />
              </span>
              开启推送权限
            </span>
          </button>
        </div>

        <div v-if="loading" class="flex flex-col items-center justify-center py-20 grayscale opacity-50">
          <span class="icon-chip text-gray-400 mb-4">
            <ArrowPathIcon class="h-5 w-5 animate-spin" />
          </span>
           <p>正在拉取列表...</p>
        </div>

        <div v-else-if="subscriptions.length === 0" class="text-center py-20 bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-white/40 dark:border-slate-800/50 shadow-xl rounded-2xl">
          <div class="mx-auto mb-4 icon-chip text-primary/80">
            <CloudIcon class="h-5 w-5" />
          </div>
          <p class="text-gray-500">你还没有订阅任何 UP 主</p>
          <p class="text-xs text-gray-400 mt-2">快在上方搜索并开启你的每日总结之旅吧</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            v-for="sub in subscriptions" 
            :key="sub.id"
            class="bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-white/40 dark:border-slate-800/50 shadow-xl rounded-2xl p-5 border border-gray-100 dark:border-slate-800 hover:shadow-md transition group"
          >
            <div class="flex items-start justify-between mb-4">
              <a 
                :href="`https://space.bilibili.com/${sub.up_mid}`" 
                target="_blank"
                class="flex items-center gap-3 hover:opacity-80 transition-opacity"
              >
                <img :src="getProxyUrl(sub.up_avatar)" class="w-12 h-12 rounded-xl" />
                <div>
                  <div class="font-bold text-gray-900 dark:text-gray-100 line-clamp-1">{{ sub.up_name }}</div>
                  <div class="text-[10px] text-gray-400 mt-1">
                    订阅于 {{ formatDate(sub.created_at) }}
                  </div>
                </div>
              </a>
              <button 
                class="opacity-0 group-hover:opacity-100 p-2 text-gray-400 hover:text-red-500 transition-all"
                title="取消订阅"
                @click="confirmUnsubscribe(sub)"
              >
                <span class="icon-chip-inline text-red-500/80">
                  <TrashIcon class="h-3.5 w-3.5" />
                </span>
              </button>
            </div>

            <div class="flex items-center justify-between pt-4 border-t border-gray-50 dark:border-slate-800 mb-3">
               <div class="flex gap-2">
                 <span 
                   v-for="method in sub.notify_methods" 
                   :key="method"
                   class="px-2 py-0.5 bg-gray-100 dark:bg-slate-800 rounded text-[10px] text-gray-500 font-medium"
                 >
                   {{ method === 'browser' ? '浏览器' : '邮件' }}
                 </span>
               </div>
               <div class="text-xs text-gray-500">
                 {{ sub.last_video_bvid ? '已更' : '等待更新' }}
               </div>
            </div>

            <!-- 视频展示区域 (默认展开) -->
            <div class="mt-4 pt-4 border-t border-gray-100 dark:border-slate-800">
              <div v-if="sub.videosLoading" class="flex items-center justify-center py-8">
                <span class="icon-chip-inline text-gray-400">
                  <ArrowPathIcon class="h-3.5 w-3.5 animate-spin" />
                </span>
              </div>
              <div v-else-if="sub.videos && sub.videos.length > 0" class="space-y-3">
                <a 
                  v-for="video in sub.videos" 
                  :key="video.bvid"
                  :href="video.url"
                  target="_blank"
                  class="flex gap-3 p-3 rounded-lg bg-gray-50/50 dark:bg-slate-800/50 hover:bg-gray-100 dark:hover:bg-slate-800 transition group/video"
                >
                  <img 
                    :src="getProxyUrl(video.cover)" 
                    class="w-24 h-16 rounded-lg object-cover flex-shrink-0"
                    alt="视频封面"
                  />
                  <div class="flex-1 min-w-0">
                    <div class="text-sm font-medium text-gray-900 dark:text-gray-100 line-clamp-2 group-hover/video:text-primary transition">
                      {{ video.title }}
                    </div>
                    <div class="text-xs text-gray-400 mt-1 flex items-center gap-2">
                      <span>{{ video.duration }}</span>
                      <span>·</span>
                      <span>{{ formatTimestamp(video.created) }}</span>
                    </div>
                  </div>
                </a>
              </div>
              <div v-else-if="!sub.videosLoading" class="text-center py-4 text-sm text-gray-400">
                该UP主暂无视频
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  ArrowPathIcon,
  BellAlertIcon,
  CloudIcon,
  FolderIcon,
  MagnifyingGlassIcon,
  TrashIcon,
} from '@heroicons/vue/24/outline'
import { supabase } from '../supabase'
import { subscribeToPush } from '../utils/push'

interface UPInfo {
  mid: string
  name: string
  avatar: string
  fans?: number
  videos?: number
  sign?: string
}

interface Video {
  bvid: string
  title: string
  cover: string
  duration: string
  created: number
  url: string
}

interface Subscription {
  id: string
  up_mid: string
  up_name: string
  up_avatar: string
  notify_methods: string[]
  last_video_bvid: string
  created_at: string
  // 新增字段用于视频展示
  videos?: Video[]
  videosLoading?: boolean
}

const searchQuery = ref('')
const searching = ref(false)
const searched = ref(false)
const searchResults = ref<UPInfo[]>([])
const subscriptions = ref<Subscription[]>([])
const loading = ref(true)

async function handleSearch() {
  if (searchQuery.value.length < 2) return
  searching.value = true
  searched.value = true
  try {
    const res = await fetch(`/api/subscriptions/search?keyword=${encodeURIComponent(searchQuery.value)}`)
    const data = await res.json()
    searchResults.value = data.users || []
  } catch (err) {
    console.error('Search failed:', err)
  } finally {
    searching.value = false
  }
}

async function fetchSubscriptions() {
  loading.value = true
  try {
    if (!supabase) throw new Error('Supabase not initialized')
    const { data: sessionData } = await supabase.auth.getSession()
    const token = sessionData.session?.access_token
    const res = await fetch('/api/subscriptions', {
      headers: { 'Authorization': `Bearer ${token || ''}` }
    })
    const data = await res.json()
    subscriptions.value = data.subscriptions || []
    
    // 自动加载所有UP主的视频
    if (subscriptions.value.length > 0) {
      await loadAllUpVideos(token || '')
    }
  } catch (err) {
    console.error('Fetch subscriptions failed:', err)
  } finally {
    loading.value = false
  }
}

async function loadAllUpVideos(token: string) {
  // 并发加载所有UP主的视频
  const loadPromises = subscriptions.value.map(async (sub) => {
    sub.videosLoading = true
    try {
      const res = await fetch(`/api/subscriptions/videos?up_mid=${sub.up_mid}&count=2`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (res.ok) {
        const data = await res.json()
        sub.videos = data.videos || []
      } else {
        sub.videos = []
      }
    } catch (err) {
      console.error(`Load videos for UP ${sub.up_name} failed:`, err)
      sub.videos = []
    } finally {
      sub.videosLoading = false
    }
  })
  
  await Promise.all(loadPromises)
}

async function handleSubscribe(up: UPInfo) {
  try {
    if (!supabase) throw new Error('Supabase not initialized')
    const { data: sessionData } = await supabase.auth.getSession()
    const token = sessionData.session?.access_token
    const res = await fetch('/api/subscriptions', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token || ''}` 
      },
      body: JSON.stringify({
        up_mid: up.mid,
        up_name: up.name,
        up_avatar: up.avatar,
        notify_methods: ['browser']
      })
    })
    
    if (res.ok) {
      await fetchSubscriptions()
      // 清空搜索结果中的这一项
      searchResults.value = searchResults.value.filter(i => i.mid !== up.mid)
    } else {
      const data = await res.json()
      const errorMsg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
      alert(errorMsg || '订阅失败')
    }
  } catch (err) {
    alert('订阅请求失败')
  }
}

async function confirmUnsubscribe(sub: Subscription) {
  if (!confirm(`确定要取消关注 ${sub.up_name} 吗？`)) return
  
  try {
    if (!supabase) throw new Error('Supabase not initialized')
    const { data: sessionData } = await supabase.auth.getSession()
    const token = sessionData.session?.access_token
    const res = await fetch(`/api/subscriptions/${sub.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token || ''}` }
    })
    
    if (res.ok) {
      subscriptions.value = subscriptions.value.filter(i => i.id !== sub.id)
    }
  } catch (err) {
    alert('操作失败')
  }
}

async function enablePushNotifications() {
  const result = await Notification.requestPermission()
  if (result === 'granted') {
    const sub = await subscribeToPush()
    if (sub) {
      alert('推送权限已开启！')
    }
  } else {
    alert('请在浏览器设置中允许通知权限')
  }
}

function isSubscribed(mid: string) {
  return subscriptions.value.some(s => s.up_mid === mid)
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

function formatTimestamp(timestamp: number) {
  const date = new Date(timestamp * 1000)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return '今天'
  if (diffDays === 1) return '昨天'
  if (diffDays < 7) return `${diffDays}天前`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}周前`
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

function getProxyUrl(url: string) {
  if (!url) return ''
  // Bilibili 图片通常以 http: 开头，weserv 需要清理
  const cleanUrl = url.replace(/^https?:\/\//, '')
  return `https://images.weserv.nl/?url=${cleanUrl}&w=120&h=120&fit=cover`
}

onMounted(() => {
  fetchSubscriptions()
})
</script>
