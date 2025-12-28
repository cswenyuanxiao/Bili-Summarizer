import { computed, type Ref } from 'vue'

interface DailyUsage {
    day: string
    count: number
}

export function useChartData(
    dailyUsage: Ref<DailyUsage[] | undefined>,
    rangeInDays: Ref<string>
) {
    // 获取排序后的数据切片
    const getSortedSlice = () => {
        const entries = dailyUsage.value ?? []
        if (!entries.length) return []

        // 确保数据按时间排序（从旧到新）
        const sorted = [...entries].sort((a, b) =>
            new Date(a.day).getTime() - new Date(b.day).getTime()
        )

        const days = parseInt(rangeInDays.value)
        return sorted.slice(-days)
    }

    // 生成 SVG 路径点
    const chartPoints = computed(() => {
        const sliced = getSortedSlice()
        if (!sliced.length) return ''

        const values = sliced.map(item => item.count)
        const max = Math.max(1, ...values)
        const stepX = 320 / Math.max(1, values.length - 1)

        return values
            .map((value, index) => {
                const x = stepX * index
                const y = 110 - (value / max) * 90
                return `${x},${y}`
            })
            .join(' ')
    })

    // 生成图表标签
    const chartLabels = computed(() => {
        const sliced = getSortedSlice()
        if (!sliced.length) return []

        const labels = sliced.map(item => item.day.slice(5)) // 'MM-DD'
        if (labels.length <= 7) return labels

        // 下采样标签（避免拥挤）
        const step = Math.ceil(labels.length / 7)
        return labels.filter((_, index) => index % step === 0)
    })

    return {
        chartPoints,
        chartLabels
    }
}
