/**
 * Vue I18n 配置
 */
import { createI18n } from 'vue-i18n'
import zhCN from './zh-CN'
import enUS from './en-US'

// 从 localStorage 获取用户语言偏好，默认为中文
function getDefaultLocale(): string {
    const saved = localStorage.getItem('locale')
    if (saved && ['zh-CN', 'en-US'].includes(saved)) {
        return saved
    }

    // 检测浏览器语言
    const browserLang = navigator.language
    if (browserLang.startsWith('zh')) {
        return 'zh-CN'
    }
    if (browserLang.startsWith('en')) {
        return 'en-US'
    }

    return 'zh-CN' // 默认中文
}

const i18n = createI18n({
    legacy: false, // 使用 Composition API 模式
    locale: getDefaultLocale(),
    fallbackLocale: 'zh-CN',
    messages: {
        'zh-CN': zhCN,
        'en-US': enUS,
    },
})

export default i18n

// 导出可用语言列表
export const availableLocales = [
    { code: 'zh-CN', name: '简体中文', flag: '🇨🇳' },
    { code: 'en-US', name: 'English', flag: '🇺🇸' },
]
