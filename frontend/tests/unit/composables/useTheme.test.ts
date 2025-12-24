/**
 * Tests for useTheme composable
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { ref } from 'vue'
import { useTheme } from '../../../src/composables/useTheme'

describe('useTheme', () => {
    beforeEach(() => {
        // Clear localStorage before each test
        localStorage.clear()
        // Reset document class
        document.documentElement.className = ''
    })

    it('should initialize with system preference', () => {
        const { isDark } = useTheme()
        expect(isDark).toBeDefined()
        expect(typeof isDark.value).toBe('boolean')
    })

    it('should toggle theme correctly', () => {
        const { isDark, toggleTheme } = useTheme()
        const initialValue = isDark.value

        toggleTheme()

        expect(isDark.value).toBe(!initialValue)
    })

    it('should persist theme in localStorage', () => {
        const { toggleTheme } = useTheme()

        toggleTheme()

        const stored = localStorage.getItem('theme')
        expect(stored).toBeTruthy()
    })

    it('should apply dark class to document', () => {
        const { isDark, toggleTheme } = useTheme()

        if (!isDark.value) {
            toggleTheme() // Make it dark
        }

        expect(document.documentElement.classList.contains('dark')).toBe(true)
    })
})
