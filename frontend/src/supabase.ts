import { createClient } from '@supabase/supabase-js'

type RuntimeConfig = {
    VITE_SUPABASE_URL?: string
    VITE_SUPABASE_ANON_KEY?: string
}

const runtimeConfig = (globalThis as typeof globalThis & { __APP_CONFIG__?: RuntimeConfig }).__APP_CONFIG__ || {}

const supabaseUrl = runtimeConfig.VITE_SUPABASE_URL || import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = runtimeConfig.VITE_SUPABASE_ANON_KEY || import.meta.env.VITE_SUPABASE_ANON_KEY

export const isSupabaseConfigured = Boolean(supabaseUrl && supabaseAnonKey)

if (!isSupabaseConfigured) {
    console.warn('Supabase URL or Key is missing. Auth features will be disabled.')
}

// 只有配置完整时才创建客户端，否则导出 null
export const supabase = isSupabaseConfigured
    ? createClient(supabaseUrl, supabaseAnonKey)
    : null
