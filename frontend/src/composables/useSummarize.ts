import { ref } from 'vue'
import type { SummarizeRequest, SSEEvent, SummaryResult } from '../types/api'

export function useSummarize() {
    const isLoading = ref(false)
    const status = ref('')
    const progress = ref(0)
    const result = ref<SummaryResult>({
        summary: '',
        transcript: '',
        videoFile: null,
        usage: null,
    })

    const summarize = async (request: SummarizeRequest) => {
        isLoading.value = true
        status.value = '正在连接服务器...'
        progress.value = 0

        try {
            // Get current session token
            const { data: { session } } = await import('../supabase').then(m => m.supabase.auth.getSession())
            const token = session?.access_token

            const url = `/api/summarize`
            const params = new URLSearchParams({
                url: request.url,
                mode: request.mode,
                focus: request.focus,
            })

            if (token) {
                params.append('token', token)
            }

            const eventSource = new EventSource(`${url}?${params}`)

            eventSource.onmessage = (event) => {
                try {
                    const data: SSEEvent = JSON.parse(event.data)

                    if (data.type === 'status') {
                        status.value = data.status || ''
                        // Simulate progress
                        if (progress.value < 90) {
                            progress.value += 10
                        }
                    } else if (data.type === 'video_downloaded') {
                        result.value.videoFile = data.video_file || null
                        progress.value = 30
                    } else if (data.type === 'transcript_complete') {
                        result.value.transcript = data.transcript || ''
                        progress.value = 60
                    } else if (data.type === 'summary_complete') {
                        result.value.summary = data.summary || ''
                        result.value.usage = data.usage || null
                        progress.value = 100
                        status.value = '完成！'
                        eventSource.close()
                        isLoading.value = false
                    } else if (data.type === 'error' || data.error) {
                        throw new Error(data.error || '未知错误')
                    }
                } catch (err) {
                    console.error('SSE parsing error:', err)
                }
            }

            eventSource.onerror = (err) => {
                console.error('SSE error:', err)
                eventSource.close()
                isLoading.value = false
                status.value = '连接失败'
            }
        } catch (error) {
            console.error('Summarize error:', error)
            isLoading.value = false
            status.value = '请求失败'
        }
    }

    return {
        isLoading,
        status,
        progress,
        result,
        summarize,
    }
}
