/**
 * useVirtualList - 虚拟滚动 composable
 * 用于高效渲染长列表，只渲染可见区域的元素
 */
import { ref, computed, onMounted, onUnmounted, watch, type Ref } from 'vue'

export interface VirtualListOptions {
    itemHeight: number
    overscan?: number // 额外渲染的元素数量（上下各多渲染几个）
}

export function useVirtualList<T>(
    items: Ref<T[]>,
    options: VirtualListOptions
) {
    const { itemHeight, overscan = 5 } = options

    const containerRef = ref<HTMLElement | null>(null)
    const scrollTop = ref(0)
    const containerHeight = ref(0)

    // 计算可见区域
    const visibleRange = computed(() => {
        const start = Math.max(0, Math.floor(scrollTop.value / itemHeight) - overscan)
        const visibleCount = Math.ceil(containerHeight.value / itemHeight)
        const end = Math.min(items.value.length, start + visibleCount + overscan * 2)

        return { start, end }
    })

    // 只返回可见的元素
    const visibleItems = computed(() => {
        return items.value.slice(visibleRange.value.start, visibleRange.value.end).map((item, index) => ({
            item,
            index: visibleRange.value.start + index
        }))
    })

    // 列表总高度
    const totalHeight = computed(() => items.value.length * itemHeight)

    // 顶部偏移（用于定位可见元素）
    const offsetTop = computed(() => visibleRange.value.start * itemHeight)

    // 滚动处理
    const handleScroll = (event: Event) => {
        const target = event.target as HTMLElement
        scrollTop.value = target.scrollTop
    }

    // 初始化容器高度
    const updateContainerHeight = () => {
        if (containerRef.value) {
            containerHeight.value = containerRef.value.clientHeight
        }
    }

    // 滚动到指定索引
    const scrollToIndex = (index: number, behavior: ScrollBehavior = 'smooth') => {
        if (containerRef.value) {
            containerRef.value.scrollTo({
                top: index * itemHeight,
                behavior
            })
        }
    }

    onMounted(() => {
        updateContainerHeight()
        window.addEventListener('resize', updateContainerHeight)

        if (containerRef.value) {
            containerRef.value.addEventListener('scroll', handleScroll, { passive: true })
        }
    })

    onUnmounted(() => {
        window.removeEventListener('resize', updateContainerHeight)

        if (containerRef.value) {
            containerRef.value.removeEventListener('scroll', handleScroll)
        }
    })

    // 当 items 变化时重新计算
    watch(items, () => {
        updateContainerHeight()
    })

    return {
        containerRef,
        visibleItems,
        totalHeight,
        offsetTop,
        scrollToIndex,
        containerStyle: computed(() => ({
            height: '100%',
            overflow: 'auto'
        })),
        wrapperStyle: computed(() => ({
            height: `${totalHeight.value}px`,
            position: 'relative' as const
        })),
        itemsStyle: computed(() => ({
            position: 'absolute' as const,
            top: `${offsetTop.value}px`,
            left: 0,
            right: 0
        }))
    }
}
