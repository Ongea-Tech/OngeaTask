import { test, expect } from '@playwright/test';

test('user can log in successfully', async ({ page }) => {
  await page.goto('/auth/login');

  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="password"]', 'password123');
  await page.getByRole('button', {name:'log in'}).click();

  await expect(page).toHaveURL('/');
  await expect(page.getByText('Ongoing Tasks')).toBeVisible();
});

test('user can create task successfully', async ({ page }) => {
  await page.goto('/');

  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="password"]', 'password123');
  await page.getByRole('button', {name:'log in'}).click();

  await page.click('button:has-text("Add New Task")');
  await page.getByLabel('Title').fill('Task 1');
  await page.getByLabel('Description').fill('Task 1 description');
  await page.getByRole('button', {name:'submit'}).click();
  
  await expect(page.getByRole('heading', {name:'Task 1'})).toBeVisible();
});