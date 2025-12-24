/**
 * useLazyLoad - 通用懒加载 composable
 * 可用于任何需要懒加载的场景
 */
import { ref, onMounted, onUnmounted, type Ref } from 'vue'

export interface LazyLoadOptions {
    rootMargin?: string
    threshold?: number
    once?: boolean // 是否只触发一次
}

export function useLazyLoad(
    elementRef: Ref<HTMLElement | null>,
    options: LazyLoadOptions = {}
) {
    const { rootMargin = '200px', threshold = 0.01, once = true } = options

    const isVisible = ref(false)
    const hasBeenVisible = ref(false)

    let observer: IntersectionObserver | null = null

    const startObserving = () => {
        if (!elementRef.value) return

        observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    isVisible.value = entry.isIntersecting

                    if (entry.isIntersecting) {
                        hasBeenVisible.value = true

                        if (once) {
                            observer?.disconnect()
                        }
                    }
                })
            },
            { rootMargin, threshold }
        )

        observer.observe(elementRef.value)
    }

    onMounted(() => {
        startObserving()
    })

    onUnmounted(() => {
        observer?.disconnect()
    })

    return {
        isVisible,
        hasBeenVisible
    }
}
