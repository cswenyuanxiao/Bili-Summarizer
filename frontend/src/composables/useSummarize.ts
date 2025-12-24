import { ref } from 'vue'
import type { SummarizeRequest, SSEEvent, SummaryResult } from '../types/api'
import { isSupabaseConfigured, supabase } from '../supabase'

export function useSummarize() {
    const isLoading = ref(false)
    const status = ref('')
    const hint = ref('')
    const detail = ref('')
    const progress = ref(0)
    const phase = ref<'idle' | 'connecting' | 'downloading' | 'transcript' | 'summarizing' | 'finalizing' | 'complete' | 'error'>('idle')
    const elapsedSeconds = ref(0)
    const errorCode = ref<string | null>(null)
    const result = ref<SummaryResult>({
        summary: '',
        transcript: '',
        videoFile: null,
        usage: null,
    })
    let timer: number | null = null
    let eventSource: EventSource | null = null

    const phaseCaps: Record<typeof phase.value, number> = {
        idle: 0,
        connecting: 12,
        downloading: 45,
        transcript: 60,
        summarizing: 85,
        finalizing: 95,
        complete: 100,
        error: 100,
    }

    const startTimer = () => {
        if (timer !== null) return
        elapsedSeconds.value = 0
        timer = window.setInterval(() => {
            elapsedSeconds.value += 1
            const cap = phaseCaps[phase.value]
            if (progress.value < cap - 1) {
                progress.value = Math.min(cap - 1, progress.value + 0.5)
            }
        }, 1000)
    }

    const stopTimer = () => {
        if (timer === null) return
        window.clearInterval(timer)
        timer = null
    }

    const setPhase = (next: typeof phase.value, nextStatus?: string, nextHint?: string, nextProgress?: number) => {
        phase.value = next
        if (nextStatus !== undefined) status.value = nextStatus
        if (nextHint !== undefined) hint.value = nextHint
        if (nextProgress !== undefined) progress.value = nextProgress
    }

    const summarize = (request: SummarizeRequest): Promise<SummaryResult> => {
        return new Promise(async (resolve, reject) => {
            isLoading.value = true
            errorCode.value = null
            setPhase('connecting', '正在连接服务器...', '准备请求并建立连接...', 3)
            detail.value = ''
            startTimer()

            const handleError = (code: string | undefined, message: string) => {
                const map: Record<string, { status: string; hint: string }> = {
                    AUTH_REQUIRED: { status: '需要登录', hint: '登录后即可生成总结' },
                    AUTH_INVALID: { status: '登录已过期', hint: '请重新登录后再试' },
                    CREDITS_EXCEEDED: { status: '积分不足', hint: '请升级或等待获取积分' },
                    DOWNLOAD_FAILED: { status: '下载失败', hint: '请检查链接或稍后再试' },
                    SUMMARY_FAILED: { status: '总结失败', hint: '请稍后再试或更换模式' },
                    INTERNAL_ERROR: { status: '系统错误', hint: '服务暂时不可用，请稍后再试' },
                }
                const fallback = { status: '请求失败', hint: '请稍后再试' }
                const selected = (code && map[code]) ? map[code] : fallback
                errorCode.value = code || null
                detail.value = message
                setPhase('error', selected.status, selected.hint)
                isLoading.value = false
                eventSource?.close()
                eventSource = null
                stopTimer()
                reject(new Error(message))
            }

            try {
                if (eventSource) {
                    eventSource.close()
                    eventSource = null
                }
                // Get current session token
                const token = (isSupabaseConfigured && supabase)
                    ? (await supabase.auth.getSession()).data.session?.access_token
                    : undefined

                const url = `/api/summarize`
                const params = new URLSearchParams({
                    url: request.url,
                    mode: request.mode,
                    focus: request.focus,
                })

                if (token) {
                    params.append('token', token)
                }
                if (request.skip_cache) {
                    params.append('skip_cache', 'true')
                }
                if (request.template_id) {
                    params.append('template_id', request.template_id)
                }

                eventSource = new EventSource(`${url}?${params}`)

                eventSource.onmessage = (event) => {
                    try {
                        const data: SSEEvent = JSON.parse(event.data)

                        if (data.type === 'status') {
                            const statusText = data.status || ''
                            detail.value = statusText

                            if (statusText.trim().toLowerCase() === 'complete') {
                                if (result.value.summary) {
                                    setPhase('complete', '完成！', '结果已准备好', 100)
                                    eventSource?.close()
                                    eventSource = null
                                    isLoading.value = false
                                    stopTimer()
                                    resolve(result.value)
                                }
                                return
                            }

                            if (statusText.includes('Found in cache')) {
                                setPhase('finalizing', '命中缓存，快速加载', '正在整理结果...', 92)
                            } else if (statusText.includes('Checking for subtitles')) {
                                setPhase('downloading', '解析字幕', '尝试获取字幕/转录...', 15)
                            } else if (statusText.includes('Downloading')) {
                                const match = statusText.match(/(\d+(\.\d+)?)/)
                                if (match) {
                                    const percent = parseFloat(match[0])
                                    setPhase('downloading', '下载媒体', '拉取视频/音频素材...', Math.min(45, 10 + percent * 0.35))
                                } else {
                                    setPhase('downloading', '下载媒体', '拉取视频/音频素材...')
                                }
                            } else if (statusText.includes('Download complete')) {
                                setPhase('downloading', '下载完成', '准备分析内容...', 45)
                            } else if (statusText.includes('Uploading file')) {
                                setPhase('summarizing', '上传至 AI', '上传分析素材...', 55)
                            } else if (statusText.includes('Cloud processing')) {
                                setPhase('summarizing', 'AI 预处理', '模型正在预处理素材...', 60)
                            } else if (statusText.includes('AI is analyzing')) {
                                setPhase('summarizing', '生成总结', 'AI 深度分析中...', 70)
                            } else if (statusText.includes('Analysis complete')) {
                                setPhase('finalizing', '整理结果', '生成结构化输出...', 90)
                            } else if (statusText.includes('AI analysis is taking longer')) {
                                setPhase('summarizing', '生成总结', '已在努力处理，可能需要更久...')
                            } else {
                                setPhase(phase.value, statusText || status.value, hint.value)
                            }
                        } else if (data.type === 'video_downloaded') {
                            result.value.videoFile = data.video_file || null
                            setPhase('downloading', '素材就绪', '准备生成字幕与总结...', 40)
                        } else if (data.type === 'transcript_complete') {
                            result.value.transcript = data.transcript || ''
                            if (phase.value !== 'complete') {
                                setPhase('transcript', '字幕完成', '正在生成总结...', 60)
                            }
                        } else if (data.type === 'summary_complete') {
                            result.value.summary = data.summary || ''
                            result.value.usage = data.usage || null
                            setPhase('complete', '完成！', '结果已准备好', 100)
                            isLoading.value = false
                            eventSource?.close()
                            eventSource = null
                            stopTimer()
                            resolve(result.value)
                        } else if (data.type === 'error' || data.error) {
                            handleError(data.code, data.error || '未知错误')
                        }
                    } catch (err) {
                        console.error('SSE parsing error:', err)
                    }
                }

                eventSource.onerror = (err) => {
                    console.error('SSE error:', err)
                    if (phase.value === 'complete' || result.value.summary) {
                        eventSource?.close()
                        eventSource = null
                        resolve(result.value)
                        return
                    }
                    eventSource?.close()
                    eventSource = null
                    isLoading.value = false
                    setPhase('error', '连接失败', '请检查网络或稍后重试')
                    stopTimer()
                    reject(new Error('SSE connection failed'))
                }
            } catch (error) {
                console.error('Summarize error:', error)
                handleError('INTERNAL_ERROR', '请求失败')
            }
        })
    }

    return {
        isLoading,
        status,
        hint,
        detail,
        progress,
        phase,
        elapsedSeconds,
        errorCode,
        result,
        summarize,
    }
}
