import { describe, it, expect } from 'vitest'

describe('Test Framework Setup', () => {
    it('should run basic test', () => {
        expect(1 + 1).toBe(2)
    })

    it('should handle string comparison', () => {
        const str = 'Bili-Summarizer'
        expect(str).toContain('Bili')
    })

    it('should handle array operations', () => {
        const arr = [1, 2, 3]
        expect(arr).toHaveLength(3)
        expect(arr).toContain(2)
    })
})
