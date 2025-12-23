import { ref, onMounted } from 'vue'
import { supabase } from '../supabase'
import type { User } from '@supabase/supabase-js'

const user = ref<User | null>(null)
const loading = ref(true)

export function useAuth() {

    onMounted(async () => {
        // Get initial session
        const { data } = await supabase.auth.getSession()
        user.value = data.session?.user ?? null
        loading.value = false

        // Listen for auth changes
        supabase.auth.onAuthStateChange((_event, session) => {
            user.value = session?.user ?? null
            loading.value = false
        })
    })

    const loginWithEmail = async (email: string, password: string) => {
        const { error } = await supabase.auth.signInWithPassword({
            email,
            password
        })
        if (error) throw error
    }

    const signUpWithEmail = async (email: string, password: string) => {
        const { error } = await supabase.auth.signUp({
            email,
            password
        })
        if (error) throw error
    }

    const loginWithGitHub = async () => {
        const { error } = await supabase.auth.signInWithOAuth({
            provider: 'github',
            options: {
                redirectTo: window.location.origin
            }
        })
        if (error) throw error
    }

    const loginWithGoogle = async () => {
        const { error } = await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: window.location.origin
            }
        })
        if (error) throw error
    }

    const logout = async () => {
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
