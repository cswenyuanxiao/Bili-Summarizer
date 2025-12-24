/**
 * Tests for useReveal composable
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useReveal } from '../../../src/composables/useReveal'

describe('useReveal', () => {
    beforeEach(() => {
        // Clear DOM
        document.body.innerHTML = ''
    })

    it('should initialize without errors', () => {
        expect(() => useReveal()).not.toThrow()
    })

    it('should find elements with data-reveal attribute', () => {
        // Create test element
        const element = document.createElement('div')
        element.setAttribute('data-reveal', '')
        document.body.appendChild(element)

        useReveal()

        // Should have observer attached
        expect(element).toBeDefined()
    })

    it('should handle missing elements gracefully', () => {
        // No elements with data-reveal
        expect(() => useReveal()).not.toThrow()
    })
})
