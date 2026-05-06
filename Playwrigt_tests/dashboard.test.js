const { test, expect } = require('@playwright/test');

// Reusable login function
async function loginAndWait(page) {
  await page.goto('http://127.0.0.1:8080/login');
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'admin123');
  await page.click('button[type="submit"]');
  
  await page.waitForSelector('text=TOTAL PROCESSED', { state: 'visible' }); 
}

test('Dashboard data load', async ({ page }) => {
  await loginAndWait(page);

  await expect(page.locator('text=TOTAL PROCESSED')).toBeVisible();
  await expect(page.locator('text=ACTIVE FLOW')).toBeVisible();
  await expect(page.locator('text=AI EFFICIENCY')).toBeVisible();
  

  await expect(page.locator('text=HEAVY UNITS')).toBeVisible();
});

test('All 4 Nodes Visible', async ({ page }) => {
  await loginAndWait(page);

  await expect(page.locator('text=NODE-01: NORTH')).toBeVisible({ timeout: 10000 });
  await expect(page.locator('text=NODE-02: SOUTH')).toBeVisible({ timeout: 10000 });
  await expect(page.locator('text=NODE-03: EAST')).toBeVisible({ timeout: 10000 });
  await expect(page.locator('text=NODE-04: WEST')).toBeVisible({ timeout: 10000 });
});

