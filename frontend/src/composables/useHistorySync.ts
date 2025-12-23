import { ref } from 'vue'
import { isSupabaseConfigured } from '../supabase'

interface HistoryItem {
    id?: string
    video_url: string
    video_title?: string
    video_thumbnail?: string
    mode: string
    focus: string
    summary: string
    transcript?: string
    mindmap?: string
    created_at?: string
    updated_at?: string
}

const LOCAL_KEY = 'bili_summarizer_history'
const syncing = ref(false)
const lastSyncTime = ref<Date | null>(null)

export function useHistorySync() {
    const getAuthHeaders = async () => {
        if (!isSupabaseConfigured) return {}
        const { data: { session } } = await import('../supabase').then(m => m.supabase!.auth.getSession())
        const token = session?.access_token
        const headers: Record<string, string> = {}
        if (token) {
            headers['Authorization'] = `Bearer ${token}`
        }
        return headers
    }

    // 获取本地历史
    const getLocalHistory = (): HistoryItem[] => {
        const data = localStorage.getItem(LOCAL_KEY)
        return data ? JSON.parse(data) : []
    }

    // 保存到本地
    const saveLocalHistory = (items: HistoryItem[]) => {
        localStorage.setItem(LOCAL_KEY, JSON.stringify(items))
    }

    // 同步到云端
    const syncToCloud = async () => {
        syncing.value = true
        try {
            const local = getLocalHistory()
            if (!isSupabaseConfigured) {
                return local
            }

            // 1. 获取云端数据
            const cloudResponse = await fetch('/api/history', {
                headers: await getAuthHeaders()
            })

            if (!cloudResponse.ok) {
                if (cloudResponse.status === 401) {
                    // 未登录，跳过同步
                    console.log('Not logged in, skipping cloud sync')
                    return local
                }
                throw new Error('Failed to fetch cloud history')
            }

            const cloud: HistoryItem[] = await cloudResponse.json()

            // 2. 合并策略：以 (video_url + mode + focus) 为唯一键
            const merged = new Map<string, HistoryItem>()

            // 先添加云端数据
            for (const item of cloud) {
                const key = `${item.video_url}|${item.mode}|${item.focus}`
                merged.set(key, item)
            }

            // 再合并本地数据
            const toUpload: HistoryItem[] = []
            for (const item of local) {
                const key = `${item.video_url}|${item.mode}|${item.focus}`

                if (!merged.has(key)) {
                    // 本地有但云端没有，需要上传
                    toUpload.push(item)
                    merged.set(key, item)
                } else {
                    // 都有，取时间更新的
                    const cloudItem = merged.get(key)!
                    const localTime = new Date(item.created_at || 0)
                    const cloudTime = new Date(cloudItem.created_at || 0)

                    if (localTime > cloudTime) {
                        toUpload.push(item)
                        merged.set(key, item)
                    }
                }
            }

            // 3. 上传本地新增/更新的项
            if (toUpload.length > 0) {
                const uploadResponse = await fetch('/api/history', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(await getAuthHeaders())
                    },
                    body: JSON.stringify(toUpload)
                })

                if (!uploadResponse.ok) {
                    console.error('Failed to upload history')
                }
            }

            // 4. 更新本地存储为合并后的结果
            const finalHistory = Array.from(merged.values())
                .sort((a, b) => {
                    const timeA = new Date(a.created_at || 0).getTime()
                    const timeB = new Date(b.created_at || 0).getTime()
                    return timeB - timeA
                })

            saveLocalHistory(finalHistory)
            lastSyncTime.value = new Date()

            console.log(`Synced ${toUpload.length} items to cloud, merged ${finalHistory.length} total`)

            return finalHistory

        } catch (error) {
            console.error('History sync error:', error)
            // 同步失败时返回本地数据
            return getLocalHistory()
        } finally {
            syncing.value = false
        }
    }

    // 添加新历史记录
    const addHistoryItem = (item: Omit<HistoryItem, 'created_at'>) => {
        const history = getLocalHistory()
        const newItem: HistoryItem = {
            ...item,
            created_at: new Date().toISOString()
        }

        history.unshift(newItem)

        // 最多保留 50 条
        if (history.length > 50) {
            history.length = 50
        }

        saveLocalHistory(history)
        return newItem
    }

    // 删除历史记录
    const deleteHistoryItem = async (id: string) => {
        try {
            // 删除云端
            const response = await fetch(`/api/history/${id}`, {
                method: 'DELETE',
                headers: await getAuthHeaders()
            })

            if (!response.ok && response.status !== 404) {
                console.error('Failed to delete from cloud')
            }

            // 删除本地
            const history = getLocalHistory()
            const filtered = history.filter(item => item.id !== id)
            saveLocalHistory(filtered)

            return filtered

        } catch (error) {
            console.error('Delete history error:', error)
            throw error
        }
    }

    // 清空所有历史
    const clearHistory = () => {
        saveLocalHistory([])
    }

    return {
        syncing,
        lastSyncTime,
        getLocalHistory,
        saveLocalHistory,
        syncToCloud,
        addHistoryItem,
        deleteHistoryItem,
        clearHistory
    }
}
