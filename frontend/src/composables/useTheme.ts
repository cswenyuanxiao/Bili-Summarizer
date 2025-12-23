import { ref } from 'vue'

// Singleton state shared across all components
const isDark = ref(false)

// Helper to update DOM
const updateDOM = (dark: boolean) => {
    if (typeof document !== 'undefined') {
        if (dark) {
            document.documentElement.classList.add('dark')
        } else {
            document.documentElement.classList.remove('dark')
        }
    }
}

export function useTheme() {
    const initTheme = () => {
        const saved = localStorage.getItem('theme')
        const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches
        isDark.value = saved === 'dark' || (!saved && prefersDark)
        updateDOM(isDark.value)
    }

    const toggleTheme = () => {
        isDark.value = !isDark.value
        updateDOM(isDark.value)
        localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
    }

    return {
        isDark,
        toggleTheme,
        initTheme,
    }
}
