import { test, expect } from '@playwright/test';

test.describe('API Key Management', () => {
    test('should load Bili-Summarizer homepage', async ({ page }) => {
        await page.goto('/');

        // Check that the page loads
        await expect(page).toHaveTitle(/Bili-Summarizer|frontend/i);
    });

    test('should show login modal when trying to access developer features', async ({ page }) => {
        await page.goto('/');

        // Try to access developer page
        await page.click('text=开发者');

        // Should redirect or show some indication
        await expect(page).toHaveURL(/developer/);
    });

    test.skip('should be able to generate API key', async ({ page }) => {
        // This test requires authentication to be set up
        // TODO: Implement when auth is properly configured
    });

    test.skip('should display API key usage statistics', async ({ page }) => {
        // This is the test that would have caught today's bug!
        // It tests the /api/keys/usage endpoint
        // TODO: Implement when auth is properly configured
    });
});
