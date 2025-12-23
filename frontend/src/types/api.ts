// API Request Types
export interface SummarizeRequest {
    url: string;
    mode: 'smart' | 'video';
    focus: 'default' | 'study' | 'gossip' | 'business';
}

// SSE Event Types
export interface SSEEvent {
    type: 'status' | 'video_downloaded' | 'transcript_complete' | 'summary_complete' | 'error';
    status?: string;
    video_file?: string;
    transcript?: string;
    summary?: string;
    usage?: UsageInfo;
    error?: string;
}

export interface UsageInfo {
    input_tokens?: number;
    output_tokens?: number;
    total_tokens?: number;
}

// Response Types
export interface SummaryResult {
    summary: string;
    transcript: string;
    videoFile: string | null;
    usage: UsageInfo | null;
}
