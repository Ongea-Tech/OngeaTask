import { test, expect } from '@playwright/test';

test('user can log in successfully', async ({ page }) => {
  await page.goto('/auth/login');

  await page.fill('input[name="username"]', 'mercytum@gmail.com');
  await page.fill('input[name="password"]', 'Pass123456');
  await page.getByRole('button', {name:'log in'}).click();

  await expect(page).toHaveURL('/');
  await expect(page.getByText('Ongoing Tasks')).toBeVisible();
});

test('user can create task successfully', async ({ page }) => {
  await page.goto('/');

  await page.fill('input[name="username"]', 'mercytum@gmail.com');
  await page.fill('input[name="password"]', 'Pass123456');
  await page.getByRole('button', {name:'log in'}).click();

  await page.click('button:has-text("Add New Task")');
  await page.fill('input[name="name"]', 'Task 1');
  await page.getByLabel('description').fill('Task 1 description');
  await page.click('button[type="submit"]');
  
  await expect(page.getByRole('heading', {name:'Task 1'})).toBeVisible();
});