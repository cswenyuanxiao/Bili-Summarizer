<template>
  <div class="teams-page min-h-screen pb-20">
    <div class="container mx-auto max-w-6xl px-4 py-8">
      <header class="mb-10 flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">团队协作</h1>
          <p class="text-gray-500 dark:text-gray-400">与伙伴共享深度见解</p>
        </div>
        <button 
          class="px-6 py-3 bg-primary text-white rounded-2xl font-bold shadow-lg shadow-primary/20 hover:scale-105 transition"
          @click="showCreateModal = true"
        >
          ＋ 创建团队
        </button>
      </header>
      
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <!-- 团队列表侧边栏 -->
        <aside class="lg:col-span-3 space-y-4">
          <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest px-2">我的团队</h2>
          <div v-if="teams.length === 0 && !loading" class="p-8 text-center glass-card rounded-2xl">
             <p class="text-xs text-gray-500">尚无团队</p>
          </div>
          <div v-else class="space-y-2">
            <div 
              v-for="team in teams" 
              :key="team.id"
              class="p-4 rounded-2xl cursor-pointer transition-all border"
              :class="activeTeamId === team.id 
                ? 'bg-primary text-white border-primary shadow-md' 
                : 'bg-white dark:bg-slate-900 border-gray-100 dark:border-slate-800 hover:border-primary/50'"
              @click="selectTeam(team.id)"
            >
              <div class="font-bold truncate">{{ team.name }}</div>
              <div class="text-[10px] mt-1 opacity-70">{{ team.role === 'admin' ? '管理员' : '成员' }}</div>
            </div>
          </div>
        </aside>
        
        <!-- 团队主内容 -->
        <main class="lg:col-span-9">
          <div v-if="!activeTeamId" class="flex flex-col items-center justify-center py-40 glass-card rounded-3xl opacity-50">
            <div class="text-6xl mb-6">🤝</div>
            <p class="text-gray-500">请在左侧选择一个团队以查看详情</p>
          </div>
          
          <div v-else-if="activeTeam" class="space-y-8 fade-up">
            <!-- 团队详情头部 -->
            <div class="glass-card rounded-3xl p-8 relative overflow-hidden">
              <div class="relative z-10">
                <h2 class="text-2xl font-bold mb-2">{{ activeTeam.name }}</h2>
                <p class="text-gray-500 dark:text-gray-400 text-sm mb-6">{{ activeTeam.description || '暂无描述' }}</p>
                <div class="flex items-center gap-6">
                  <div class="flex -space-x-3">
                    <div 
                      v-for="(member, i) in activeTeam.members.slice(0, 5)" 
                      :key="i"
                      class="w-10 h-10 rounded-full border-2 border-white dark:border-slate-800 bg-gray-200 flex items-center justify-center text-xs font-bold"
                    >
                      {{ member.user_id.slice(0, 2).toUpperCase() }}
                    </div>
                    <div v-if="activeTeam.members.length > 5" class="w-10 h-10 rounded-full border-2 border-white dark:border-slate-800 bg-gray-100 flex items-center justify-center text-[10px] font-bold">
                      +{{ activeTeam.members.length - 5 }}
                    </div>
                  </div>
                  <button class="text-xs text-primary font-bold hover:underline">邀请成员</button>
                </div>
              </div>
              <div class="absolute top-0 right-0 p-8 text-6xl opacity-10 select-none">✨</div>
            </div>
            
            <!-- 共享列表 -->
            <section>
              <h3 class="text-xl font-bold mb-6 flex items-center gap-2">
                <span>📂</span> 共享总结
              </h3>
              
              <div v-if="activeTeam.summaries.length === 0" class="py-20 text-center glass-card rounded-3xl bg-gray-50/50 dark:bg-slate-900/30">
                <p class="text-gray-500">该团队成员尚未分享任何内容</p>
                <button class="mt-4 text-sm text-primary hover:underline">去分享第一篇</button>
              </div>
              
              <div v-else class="grid grid-cols-1 gap-6">
                <!-- 总结条目 -->
                <div 
                  v-for="item in activeTeam.summaries" 
                  :key="item.share_id"
                  class="glass-card rounded-3xl overflow-hidden hover:shadow-xl transition-all group"
                >
                  <div class="flex flex-col md:flex-row">
                    <div class="md:w-64 h-40 md:h-auto relative overflow-hidden">
                      <img :src="item.video_thumbnail" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                    </div>
                    <div class="flex-1 p-6 flex flex-col justify-between">
                      <div>
                        <div class="flex items-center justify-between mb-2">
                          <span class="text-[10px] bg-gray-100 dark:bg-slate-800 px-2 py-0.5 rounded-full font-bold text-gray-500 uppercase tracking-widest">
                            {{ item.mode }}
                          </span>
                          <span class="text-[10px] text-gray-400">分享于 {{ formatDate(item.shared_at) }}</span>
                        </div>
                        <h4 class="text-lg font-bold mb-3 hover:text-primary transition-colors cursor-pointer">
                          {{ item.title }}
                        </h4>
                        <p class="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mb-4 italic">
                          {{ item.summary.slice(0, 150) }}...
                        </p>
                      </div>
                      
                      <div class="flex items-center justify-between pt-4 border-t border-gray-50 dark:border-slate-800">
                        <div class="flex gap-2 text-xs">
                          <button class="text-gray-400 hover:text-primary flex items-center gap-1" @click="showComments(item)">
                            <span>💬</span> {{ getCommentCount(item.id) }} 评论
                          </button>
                          <button class="text-gray-400 hover:text-red-500 flex items-center gap-1">
                            <span>❤️</span> 赞
                          </button>
                        </div>
                        <button class="px-4 py-1.5 bg-gray-900 text-white rounded-lg text-xs font-bold hover:bg-black transition">
                          查看详情
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </main>
      </div>
    </div>
    
    <!-- 创建团队弹窗 -->
    <div v-if="showCreateModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" @click="showCreateModal = false"></div>
      <div class="relative w-full max-w-md glass-card rounded-3xl p-8 shadow-2xl">
        <h3 class="text-xl font-bold mb-6 italic">创建新团队</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-400 mb-2">团队名称</label>
            <input 
              v-model="newTeam.name" 
              type="text" 
              placeholder="例如：技术学习小组"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-900 outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-400 mb-2">描述 (可选)</label>
            <textarea 
              v-model="newTeam.description" 
              placeholder="简短介绍团队目标..."
              class="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-900 outline-none focus:ring-2 focus:ring-primary h-24 resize-none"
            ></textarea>
          </div>
          <button 
            class="w-full py-4 bg-primary text-white rounded-xl font-bold shadow-lg shadow-primary/20 hover:opacity-90 transition disabled:opacity-50"
            :disabled="!newTeam.name"
            @click="handleCreateTeam"
          >
            确认创建
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Team {
  id: string
  name: string
  description: string
  role: string
  owner_id: string
  created_at: string
}

interface TeamMember {
  user_id: string
  role: string
  joined_at: string
}

interface TeamSummary {
  id: string
  share_id: string
  summary: string
  title: string
  video_thumbnail: string
  mode: string
  shared_at: string
}

interface TeamDetail extends Team {
  members: TeamMember[]
  summaries: TeamSummary[]
}

const teams = ref<Team[]>([])
const activeTeamId = ref<string | null>(null)
const activeTeam = ref<TeamDetail | null>(null)
const loading = ref(true)
const showCreateModal = ref(false)
const newTeam = ref({ name: '', description: '' })

async function fetchTeams() {
  loading.value = true
  try {
    const token = localStorage.getItem('supabase_token')
    const res = await fetch('/api/teams', {
      headers: { 'Authorization': `Bearer ${token || ''}` }
    })
    const data = await res.json()
    teams.value = data.teams || []
  } catch (err) {
    console.error('Fetch teams failed:', err)
  } finally {
    loading.value = false
  }
}

async function selectTeam(teamId: string) {
  activeTeamId.value = teamId
  try {
    const token = localStorage.getItem('supabase_token')
    const res = await fetch(`/api/teams/${teamId}`, {
      headers: { 'Authorization': `Bearer ${token || ''}` }
    })
    activeTeam.value = await res.json()
  } catch (err) {
    console.error('Fetch team details failed:', err)
  }
}

async function handleCreateTeam() {
  try {
    const token = localStorage.getItem('supabase_token')
    const res = await fetch('/api/teams', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token || ''}` 
      },
      body: JSON.stringify(newTeam.value)
    })
    
    if (res.ok) {
      const created = await res.json()
      teams.value.unshift(created)
      showCreateModal.value = false
      newTeam.value = { name: '', description: '' }
      selectTeam(created.id)
    }
  } catch (err) {
    alert('创建失败')
  }
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`
}

function getCommentCount(summaryId: string) {
  // 模拟数据，实际应从 API 获取
  return Math.floor(Math.random() * 5)
}

function showComments(item: TeamSummary) {
  alert(`查看 "${item.title}" 的评论列表 (功能开发中)`)
}

onMounted(() => {
  fetchTeams()
})
</script>

<style scoped>
.glass-card {
  @apply bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border border-white/40 dark:border-slate-800/50;
}

.fade-up {
  animation: fadeUp 0.6s ease-out forwards;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
