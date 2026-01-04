// API Request Types
export interface SummarizeRequest {
    url: string;
    mode: 'smart' | 'video';
    focus: 'default' | 'study' | 'gossip' | 'business';
    skip_cache?: boolean;
    template_id?: string | null;
    output_language?: string;
    enable_cot?: boolean;
}

// SSE Event Types
export interface SSEEvent {
    type: 'status' | 'video_downloaded' | 'transcript_complete' | 'summary_complete' | 'error';
    status?: string;
    video_file?: string;
    transcript?: string;
    summary?: string;
    usage?: UsageInfo;
    code?: string;
    error?: string;
}

export interface UsageInfo {
    input_tokens?: number;
    output_tokens?: number;
    total_tokens?: number;
    cot_steps?: Array<{
        step: number;
        title: string;
        thinking: string;
    }>;
    charts?: Array<{
        type: 'bar' | 'pie' | 'line';
        title: string;
        data: {
            labels: string[];
            values: number[];
        };
    }>;
}

// Response Types
export interface SummaryResult {
    summary: string;
    transcript: string;
    videoFile: string | null;
    usage: UsageInfo | null;
}
