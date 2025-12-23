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

    const toggleTheme = (event?: MouseEvent) => {
        const updateTheme = () => {
            isDark.value = !isDark.value
            updateDOM(isDark.value)
            localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
        }

        const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
        const startViewTransition = (document as Document & {
            startViewTransition?: (callback: () => void) => { ready: Promise<void> }
        }).startViewTransition?.bind(document)

        if (!startViewTransition || reduceMotion) {
            updateTheme()
            return
        }

        const x = event?.clientX ?? window.innerWidth / 2
        const y = event?.clientY ?? window.innerHeight / 2
        const endRadius = Math.hypot(
            Math.max(x, window.innerWidth - x),
            Math.max(y, window.innerHeight - y)
        )

        const transition = startViewTransition(() => {
            updateTheme()
        })

        transition.ready.then(() => {
            const clipPath = [
                `circle(0px at ${x}px ${y}px)`,
                `circle(${endRadius}px at ${x}px ${y}px)`,
            ]
            document.documentElement.animate(
                { clipPath },
                {
                    duration: 400,
                    easing: 'ease-in',
                    pseudoElement: '::view-transition-new(root)',
                }
            )
        })
    }

    return {
        isDark,
        toggleTheme,
        initTheme,
    }
}
