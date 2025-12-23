<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @mousedown.self="$emit('close')">
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-2xl overflow-hidden transform transition-all h-[600px] flex flex-col">
      
      <!-- Header -->
      <div class="p-6 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center">
        <div>
           <h2 class="text-2xl font-bold text-gray-900 dark:text-white">API 密钥管理</h2>
           <p class="text-sm text-gray-500 dark:text-gray-400">创建 API Key 以便在您的应用中集成 Bili-Summarizer 能力。</p>
        </div>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
           <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-6 space-y-8">
        
        <!-- Create New Key -->
        <div class="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-5 border border-gray-100 dark:border-gray-700">
           <h3 class="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">创建新密钥</h3>
           <div v-if="featureUnavailable || !isSupabaseConfigured" class="mb-4 rounded-lg border border-yellow-200 bg-yellow-50 px-3 py-2 text-sm text-yellow-800">
             该功能暂未开放或未配置登录服务。
           </div>
           <div class="flex gap-3">
             <input 
               v-model="newKeyName" 
               type="text" 
               placeholder="密钥名称 (例如: Chrome Extension)" 
                class="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
             />
             <button 
               @click="createKey" 
               :disabled="!newKeyName || creating || featureUnavailable || !isSupabaseConfigured"
               class="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 font-medium"
             >
               {{ creating ? '生成中...' : '生成密钥' }}
             </button>
           </div>

           <!-- Success Alert (Copy Only Once) -->
           <div v-if="createdKey" class="mt-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
              <div class="flex items-start gap-3">
                <svg class="w-5 h-5 text-green-600 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                <div class="flex-1">
                   <p class="text-sm font-medium text-green-800 dark:text-green-300 mb-2">生成成功！请立即复制保存，它将不会再次显示。</p>
                   <div class="flex items-center gap-2 bg-white dark:bg-black/20 p-2 rounded border border-green-200 dark:border-green-800/50">
                     <code class="text-sm font-mono text-green-700 dark:text-green-400 break-all select-all">{{ createdKey }}</code>
                     <button @click="copyKey" class="text-green-600 hover:text-green-800 p-1">
                        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>
                     </button>
                   </div>
                </div>
              </div>
           </div>
        </div>

        <!-- Key List -->
        <div>
          <h3 class="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">现有密钥</h3>
          <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>
          <div v-else-if="featureUnavailable || !isSupabaseConfigured" class="text-center py-8 text-gray-500 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
             功能暂未开放
          </div>
          <div v-else-if="keys.length === 0" class="text-center py-8 text-gray-500 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
             暂无 API 密钥
          </div>
          <div v-else class="space-y-3">
             <div v-for="key in keys" :key="key.id" class="flex items-center justify-between p-4 bg-white dark:bg-gray-700/30 border border-gray-100 dark:border-gray-700 rounded-xl hover:border-gray-300 transition-colors">
                <div class="space-y-1">
                  <div class="font-medium text-gray-900 dark:text-white flex items-center gap-2">
                    {{ key.name }}
                    <span class="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-600" v-if="key.is_active">Active</span>
                  </div>
                  <div class="text-sm font-mono text-gray-500">{{ key.prefix }}****************</div>
                  <div class="text-xs text-gray-400">创建于 {{ new Date(key.created_at).toLocaleDateString() }}</div>
                  <div class="text-xs text-gray-500">
                    近 7 天 {{ usageMap[key.id]?.uses_7d ?? 0 }} 次 · 累计 {{ usageMap[key.id]?.total_uses ?? 0 }} 次 · 上次使用 {{ formatDate(usageMap[key.id]?.last_used_at) }}
                  </div>
                </div>
                <button 
                  @click="revokeKey(key.id)" 
                  class="text-sm text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 px-3 py-1.5 rounded-lg transition-colors"
                >
                  撤销
                </button>
             </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { isSupabaseConfigured, supabase } from '../supabase'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close'])

interface ApiKey {
  id: string
  name: string
  prefix: string
  is_active: boolean
  created_at: string
}

const keys = ref<ApiKey[]>([])
const loading = ref(false)
const creating = ref(false)
const newKeyName = ref('')
const createdKey = ref('') // Raw key shown only once
const featureUnavailable = ref(false)
const usageMap = ref<Record<string, { total_uses: number; uses_7d: number; last_used_at?: string | null }>>({})

// Load keys when modal opens
watch(() => props.show, (newVal) => {
  if (newVal) {
    fetchKeys()
    fetchUsage()
    createdKey.value = ''
    newKeyName.value = ''
  }
})

const getAuthHeaders = async (): Promise<Record<string, string>> => {
    if (!isSupabaseConfigured || !supabase) return {}
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.access_token) return {}
    return {
        Authorization: `Bearer ${session.access_token}`
    }
}

const fetchKeys = async () => {
  if (!isSupabaseConfigured) {
    featureUnavailable.value = true
    return
  }
  loading.value = true
  try {
    const headers = await getAuthHeaders()
    const res = await fetch('/api/keys', { headers })
    if (res.status === 404 || res.status === 501) {
       featureUnavailable.value = true
       return
    }
    if (res.ok) {
       keys.value = await res.json()
       featureUnavailable.value = false
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const fetchUsage = async () => {
  if (!isSupabaseConfigured) return
  try {
    const headers = await getAuthHeaders()
    const res = await fetch('/api/keys/usage', { headers })
    if (!res.ok) return
    const data = await res.json()
    usageMap.value = data.reduce((acc: Record<string, any>, item: any) => {
      acc[item.id] = item
      return acc
    }, {})
  } catch (e) {
    console.error('Usage fetch failed', e)
  }
}

const createKey = async () => {
  if (!newKeyName.value) return
  if (featureUnavailable.value || !isSupabaseConfigured) return
  creating.value = true
  try {
    const headers = await getAuthHeaders()
    const res = await fetch('/api/keys', {
        method: 'POST',
        headers: {
            ...headers,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: newKeyName.value })
    })
    
    if (res.status === 404 || res.status === 501) {
        featureUnavailable.value = true
        throw new Error('API 密钥功能暂未开放')
    }
    if (res.ok) {
        const data = await res.json()
        createdKey.value = data.key // This is the RAW key
        fetchKeys() // Refresh list
        fetchUsage()
        newKeyName.value = ''
    }
  } catch (e) {
      alert('创建失败: ' + e)
  } finally {
      creating.value = false
  }
}

const revokeKey = async (id: string) => {
    if (!confirm('确定要撤销此密钥吗？撤销后无法恢复，使用此密钥的应用将失效。')) return
    
    try {
        const headers = await getAuthHeaders()
        const res = await fetch(`/api/keys/${id}`, { method: 'DELETE', headers })
        if (res.status === 404 || res.status === 501) {
            featureUnavailable.value = true
            throw new Error('API 密钥功能暂未开放')
        }
        fetchKeys()
        fetchUsage()
    } catch (e) {
        alert('撤销失败')
    }
}

const copyKey = () => {
    if (createdKey.value) {
        navigator.clipboard.writeText(createdKey.value)
        alert('已复制到剪贴板')
    }
}

const formatDate = (value?: string | null) => {
  if (!value) return '未使用'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleDateString()
}
</script>
