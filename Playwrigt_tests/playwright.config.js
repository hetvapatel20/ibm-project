import { defineConfig } from '@playwright/test';

export default defineConfig({
  // 1. Tamara folder nu sachu naam ahi lakho
  testDir: './Playwrigt_tests', 
  
  // 2. Aa pattern thi .test.js ane .spec.js banne run thase
  testMatch: '**/*.{test,spec}.js', 
  
  timeout: 30000,
  
  // Workers: Ek sathe ketla tests run karva (10 tests mate 2-3 workers sara rehse)
  workers: 3,

  use: {
    baseURL: 'http://127.0.0.1:8080',
    headless: false, // Tame browser khultu joi saksho
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'on-first-retry', // Debugging mate khub kaam lagse
  },
  
  reporter: [['html', { open: 'always' }]], // Test khatam thaya pachi automatic report khulshe
});