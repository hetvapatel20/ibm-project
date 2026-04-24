const { test, expect } = require('@playwright/test');

test('Node Status Table Visible', async ({ page }) => {
  await page.goto('http://127.0.0.1:8080/login');
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await expect(page.locator('text=Node Status')).toBeVisible();
  await expect(page.locator('text=LANE')).toBeVisible();
});

test('Crisis Lockdown Button Visible', async ({ page }) => {
  await page.goto('http://127.0.0.1:8080/login');
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await expect(page.locator('text=CRISIS LOCKDOWN')).toBeVisible();
});

test('AI Mode Button Visible', async ({ page }) => {
  await page.goto('http://127.0.0.1:8080/login');
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await expect(page.locator('text=AI Mode').first()).toBeVisible();
});