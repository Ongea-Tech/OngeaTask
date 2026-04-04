import {test, expect} from 'playwright/test';

test('login test', async ({ page }) => {
  await page.goto('http://127.0.0.1:5001/auth/login');

  await page.fill('input[name="username"]', 'mercytum@gmail.com');
  await page.fill('input[name="password"]', 'Pass123456');
  await page.click('button[type="submit"]');

  await expect(page).toHaveURL('http://127.0.0.1:5001/');
  await expect(page.getByText('Ongoing Tasks')).toBeVisible();
});

