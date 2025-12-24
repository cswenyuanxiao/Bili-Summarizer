/**
 * useLocale - 语言切换 composable
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { availableLocales } from '../locales'

export function useLocale() {
    const { locale, t } = useI18n()

    const currentLocale = computed(() => locale.value)

    const currentLocaleName = computed(() => {
        const found = availableLocales.find(l => l.code === locale.value)
        return found?.name || locale.value
    })

    const currentLocaleFlag = computed(() => {
        const found = availableLocales.find(l => l.code === locale.value)
        return found?.flag || '🌐'
    })

    function setLocale(newLocale: string) {
        if (availableLocales.some(l => l.code === newLocale)) {
            locale.value = newLocale
            localStorage.setItem('locale', newLocale)
            document.documentElement.lang = newLocale
        }
    }

    function toggleLocale() {
        const currentIndex = availableLocales.findIndex(l => l.code === locale.value)
        const nextIndex = (currentIndex + 1) % availableLocales.length
        const nextLocale = availableLocales[nextIndex]
        if (nextLocale) {
            setLocale(nextLocale.code)
        }
    }

    return {
        t,
        locale: currentLocale,
        localeName: currentLocaleName,
        localeFlag: currentLocaleFlag,
        availableLocales,
        setLocale,
        toggleLocale,
    }
}
