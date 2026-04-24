import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  testMatch: '**/*.test.js',
  timeout: 30000,
  use: {
    baseURL: 'http://127.0.0.1:8080',
    headless: false,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  reporter: 'html',
});