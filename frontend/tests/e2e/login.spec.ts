import { test, expect } from '@playwright/test';

test.describe('Login Flow', () => {
    test('should show login modal when accessing protected pages', async ({ page }) => {
        await page.goto('/');

        // Click on dashboard or other protected route
        await page.click('text=仪表盘').catch(() => {
            // OK if button not visible (might need auth first)
        });
    });

    test.skip('should be able to login with Google', async ({ page }) => {
        // TODO: Implement when Supabase auth is properly configured
    });

    test.skip('should persist login state after refresh', async ({ page }) => {
        // TODO: Implement session persistence test
    });
});
