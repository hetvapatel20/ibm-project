const { test, expect } = require('@playwright/test');

test('Login Page Load', async ({ page }) => {
  await page.goto('http://127.0.0.1:8080/login');
  await expect(page.locator('input[name="username"]')).toBeVisible();
  await expect(page.locator('input[name="password"]')).toBeVisible();
});

test('Valid Login', async ({ page }) => {
  await page.goto('http://127.0.0.1:8080/login');
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await expect(page.locator('text=SmartCity NOC Central')).toBeVisible();
});

test('Invalid Login', async ({ page }) => {
  await page.goto('http://127.0.0.1:8080/login');
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'wrongpass');
  await page.click('button[type="submit"]');
  await expect(page.locator('text=Invalid')).toBeVisible();
});