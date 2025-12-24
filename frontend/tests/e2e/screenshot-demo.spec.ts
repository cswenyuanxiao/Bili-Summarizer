
import { test, expect } from '@playwright/test';

test('Documentation Screenshots', async ({ page }) => {
    // 1. 设置视口大小 (模拟桌面)
    await page.setViewportSize({ width: 1280, height: 800 });

    // 2. 访问首页
    await page.goto('http://localhost:5173/');
    // Wait for network to be idle (page loaded)
    await page.waitForLoadState('networkidle');

    // 截图1：首页
    await page.screenshot({ path: 'docs/screenshots/01_homepage.png' });

    // 3. 访问订阅页面
    await page.goto('http://localhost:5173/subscriptions');
    // 等待订阅列表加载
    await page.waitForSelector('.subscriptions-page');

    // 截图2：订阅页面（未搜索状态）
    await page.screenshot({ path: 'docs/screenshots/02_subscriptions_empty.png' });

    // 4. 执行搜索交互
    const searchInput = page.getByPlaceholder('输入 UP 主昵称或关键词...');
    await searchInput.fill('Lex');

    // 点击搜索按钮
    const searchButton = page.getByRole('button', { name: '搜索' });
    await searchButton.click();

    // 等待搜索结果出现
    // 注意：这里假设搜索会有结果返回，实际环境可能需要 mock 或者真实的后端支持
    // 为了演示，我们等待一段时间或者等待特定元素
    await page.waitForTimeout(2000); // 简单等待2秒，实际最好用 waitForSelector

    // 截图3：搜索结果
    await page.screenshot({ path: 'docs/screenshots/03_search_results.png' });
});
