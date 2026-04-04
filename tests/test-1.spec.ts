import { test, expect } from '@playwright/test';


test ('login test', async ({ page }) => {
  await page.goto('/auth/login');

  await page.getByRole('textbox', { name: 'Email' }).click();
  await page.getByRole('textbox', { name: 'Email' }).fill('mercytum@gmail.com');
  await page.getByRole('textbox', { name: 'Enter your password' }).click();
  await page.getByRole('textbox', { name: 'Enter your password' }).fill('Pass123456');
  await page.getByRole('button', { name: 'Log in' }).click();

  await expect(page).toHaveURL('/');
  await expect(page.getByText('Ongoing Tasks')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Add New Task' })).toBeVisible();
});

test ('create_task', async ({ page }) => {
  await page.goto('/auth/login');

  await page.getByRole('textbox', { name: 'Email' }).click();
  await page.getByRole('textbox', { name: 'Email' }).fill('mercytum@gmail.com');
  await page.getByRole('textbox', { name: 'Enter your password' }).click();
  await page.getByRole('textbox', { name: 'Enter your password' }).fill('Pass123456');
  await page.getByRole('button', { name: 'Log in' }).click();

  await page.getByRole('button', { name: 'Add New Task' }).click();
  await page.getByRole('textbox', { name: 'Task Name (required):' }).click();
  await page.getByRole('textbox', { name: 'Task Name (required):' }).fill('Testing with Playwright');
  await page.getByRole('textbox', { name: 'Description:' }).click();
  await page.getByRole('textbox', { name: 'Description:' }).fill('Description from Playwright');
  await page.getByRole('button', { name: 'Create Task' }).click();

  await expect(page.getByText('Testing with Playwright')).toBeVisible();
  await expect(page.getByText('Description from Playwright')).toBeVisible();

});