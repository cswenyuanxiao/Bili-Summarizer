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

        if (!isSupabaseConfigured) {
            user.value = null
            loading.value = false
            return
        }

        // Get initial session
        const { data } = await supabase.auth.getSession()
        user.value = data.session?.user ?? null
        loading.value = false

        // Listen for auth changes
        supabase.auth.onAuthStateChange((_event, session) => {
            user.value = session?.user ?? null
            loading.value = false
        })
    }

    void initAuth()

    const loginWithEmail = async (email: string, password: string) => {
        if (!isSupabaseConfigured) throw new Error('Auth is not configured')
        const { error } = await supabase.auth.signInWithPassword({
            email,
            password
        })
        if (error) throw error
    }

    const signUpWithEmail = async (email: string, password: string) => {
        if (!isSupabaseConfigured) throw new Error('Auth is not configured')
        const { error } = await supabase.auth.signUp({
            email,
            password
        })
        if (error) throw error
    }

    const loginWithGitHub = async () => {
        if (!isSupabaseConfigured) throw new Error('Auth is not configured')
        const { error } = await supabase.auth.signInWithOAuth({
            provider: 'github',
            options: {
                redirectTo: window.location.origin
            }
        })
        if (error) throw error
    }

    const loginWithGoogle = async () => {
        if (!isSupabaseConfigured) throw new Error('Auth is not configured')
        const { error } = await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: window.location.origin
            }
        })
        if (error) throw error
    }

    const logout = async () => {
        if (!isSupabaseConfigured) throw new Error('Auth is not configured')
        const { error } = await supabase.auth.signOut()
        if (error) throw error
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
