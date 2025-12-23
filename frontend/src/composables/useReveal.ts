import { onMounted, onBeforeUnmount } from 'vue'

export function useReveal() {
    let observer: IntersectionObserver | null = null

    const observe = () => {
        // Check if user prefers reduced motion
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
        if (prefersReducedMotion) return

        const options = {
            root: null, // viewport
            rootMargin: '0px',
            threshold: 0.1 // Trigger when 10% of element is visible
        }

        observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const el = entry.target as HTMLElement

                    // Get delay from data attribute or default to 0
                    const delay = el.dataset.delay ? parseInt(el.dataset.delay) : 0

                    setTimeout(() => {
                        el.classList.add('reveal--in')
                    }, delay)

                    // Stop observing once revealed
                    observer?.unobserve(el)
                }
            })
        }, options)

        // Select all elements with class .reveal or specific data attribute
        const elements = document.querySelectorAll('[data-reveal], .reveal')
        elements.forEach((el) => {
            // Ensure initial class is present for elements selected via data attribute
            el.classList.add('reveal')
            observer?.observe(el)
        })
    }

    onMounted(() => {
        // Small delay to ensure DOM is ready and initial render is complete
        // Also helps with initial load animations
        setTimeout(observe, 100)
    })

    onBeforeUnmount(() => {
        if (observer) {
            observer.disconnect()
        }
    })

    // Return a refresh function in case DOM changes (e.g. dynamic content loading)
    return {
        refresh: () => {
            if (observer) observer.disconnect()
            setTimeout(observe, 100)
        }
    }
}
