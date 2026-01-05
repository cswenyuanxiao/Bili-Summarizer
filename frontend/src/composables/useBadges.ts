import { ref } from 'vue'

type BadgeId = 'night_owl' | 'early_bird' | 'learner' | 'first_summary'

interface BadgeDef {
  id: BadgeId
  title: string
  description: string
  icon: string
}

const BADGE_STORAGE_KEY = 'bs_badges'
const SUMMARY_COUNT_KEY = 'bs_summary_count'

const BADGES: BadgeDef[] = [
  { id: 'night_owl', title: '夜猫子', description: '凌晨 0-5 点使用', icon: '🌙' },
  { id: 'early_bird', title: '早起鸟', description: '早晨 5-9 点使用', icon: '🐦' },
  { id: 'learner', title: '好学者', description: '累计总结 > 5 次', icon: '🎓' },
  { id: 'first_summary', title: '首尝鲜', description: '第一次使用 AI 总结', icon: '⚡' },
]

const readUnlocked = (): BadgeId[] => {
  try {
    const raw = localStorage.getItem(BADGE_STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

const writeUnlocked = (ids: BadgeId[]) => {
  localStorage.setItem(BADGE_STORAGE_KEY, JSON.stringify(ids))
}

const readSummaryCount = (): number => {
  try {
    const raw = localStorage.getItem(SUMMARY_COUNT_KEY)
    return raw ? Number(raw) || 0 : 0
  } catch {
    return 0
  }
}

const writeSummaryCount = (count: number) => {
  localStorage.setItem(SUMMARY_COUNT_KEY, String(count))
}

export function useBadges() {
  const unlockedIds = ref<BadgeId[]>(readUnlocked())
  const summaryCount = ref(readSummaryCount())

  const checkAndUnlockBadges = () => {
    const now = new Date()
    const hour = now.getHours()
    const newUnlocked: BadgeId[] = []

    const currentUnlocked = new Set(unlockedIds.value)

    const nextCount = summaryCount.value + 1
    summaryCount.value = nextCount
    writeSummaryCount(nextCount)

    if (!currentUnlocked.has('first_summary')) {
      currentUnlocked.add('first_summary')
      newUnlocked.push('first_summary')
    }

    if (nextCount >= 5 && !currentUnlocked.has('learner')) {
      currentUnlocked.add('learner')
      newUnlocked.push('learner')
    }

    if (hour >= 0 && hour < 5 && !currentUnlocked.has('night_owl')) {
      currentUnlocked.add('night_owl')
      newUnlocked.push('night_owl')
    }

    if (hour >= 5 && hour < 9 && !currentUnlocked.has('early_bird')) {
      currentUnlocked.add('early_bird')
      newUnlocked.push('early_bird')
    }

    const updated = Array.from(currentUnlocked)
    unlockedIds.value = updated
    writeUnlocked(updated)

    const resolved = newUnlocked
      .map(id => BADGES.find(badge => badge.id === id))
      .filter((badge): badge is BadgeDef => Boolean(badge))
    return resolved
  }

  return {
    badges: BADGES,
    unlockedIds,
    summaryCount,
    checkAndUnlockBadges,
  }
}
