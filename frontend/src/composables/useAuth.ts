import { ref } from 'vue'
import { supabase, isSupabaseConfigured } from '../supabase'
import type { User } from '@supabase/supabase-js'

const user = ref<User | null>(null)
const loading = ref(true)
let initialized = false

export function useAuth() {
    const initAuth = async () => {
        if (initialized) return
        initialized = true

        if (!isSupabaseConfigured || !supabase) {
            user.value = null
            loading.value = false
            return
        }

        const resetAuthState = async () => {
            try {
                await supabase.auth.signOut({ scope: 'local' })
            } catch {
                // ignore sign out failures
            }
            user.value = null
            loading.value = false
        }

        // Get initial session
        try {
            const { data, error } = await supabase.auth.getSession()
            if (error) {
                await resetAuthState()
                return
            }
            user.value = data.session?.user ?? null
            loading.value = false
        } catch {
            await resetAuthState()
            return
        }

        // Listen for auth changes
        supabase.auth.onAuthStateChange((event, session) => {
            if (event === 'TOKEN_REFRESH_FAILED' || event === 'USER_DELETED') {
                void resetAuthState()
                return
            }
            user.value = session?.user ?? null
            loading.value = false
        })
    }

    void initAuth()

    const loginWithEmail = async (email: string, password: string) => {
        if (!isSupabaseConfigured || !supabase) throw new Error('Auth is not configured')
        const { data, error } = await supabase.auth.signInWithPassword({
            email,
            password
        })
        if (error) throw error
        if (!data.session) {
            const { data: sessionData, error: sessionError } = await supabase.auth.getSession()
            if (sessionError || !sessionData.session) {
                await supabase.auth.signOut({ scope: 'local' })
                throw new Error('登录会话异常，请清理缓存后重试')
            }
        }
    }

    const signUpWithEmail = async (email: string, password: string) => {
        if (!isSupabaseConfigured || !supabase) throw new Error('Auth is not configured')
        const { error } = await supabase.auth.signUp({
            email,
            password
        })
        if (error) throw error
    }

    const loginWithGitHub = async () => {
        if (!isSupabaseConfigured || !supabase) throw new Error('Auth is not configured')
        const { error } = await supabase.auth.signInWithOAuth({
            provider: 'github',
            options: {
                redirectTo: window.location.origin
            }
        })
        if (error) throw error
    }

    const loginWithGoogle = async () => {
        if (!isSupabaseConfigured || !supabase) throw new Error('Auth is not configured')
        const { error } = await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: window.location.origin
            }
        })
        if (error) throw error
    }

    const logout = async () => {
        if (!isSupabaseConfigured || !supabase) {
            user.value = null
            return
        }
        const { error } = await supabase.auth.signOut({ scope: 'local' })
        if (error && error.message !== 'Auth session missing!') throw error
        user.value = null
    }

    return {
        user,
        loading,
        loginWithGitHub,
        loginWithGoogle,
        loginWithEmail,
        signUpWithEmail,
        logout
    }
}
