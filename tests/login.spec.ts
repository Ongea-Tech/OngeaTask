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
  await page.getByRole('button', {name:'create task'}).click();
  
  await expect(page.getByRole('heading', {name:'Task 1'})).toBeVisible();
});

test('user can create a description successfully', async ({ page }) => {
  await page.goto('/'); 

  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="password"]', 'password123');
  await page.getByRole('button', {name:'log in'}).click();

  await page.click('button:has-text("Add New Task")');
  await page.getByLabel('Title').fill('Task 1');

  await page.fill('textarea[name="description"]', 'This is a test description');

  await page.getByRole('button', { name: 'Create Task' }).click(); 

  await expect(page.getByText('This is a test description')).toBeVisible();
});

test('user can log out successfully', async ({ page }) => {
  await page.goto('/auth/login'); 

  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="password"]', 'password123');
  await page.getByRole('button', {name:'log in'}).click();

  await page.goto('/logout'); 

  await page.getByRole('link', { name: 'Yes' }).click();

  await expect(page).toHaveURL('/auth/login');
});

test('user can navigate to all pages', async ({ page }) => {
  await page.goto('/auth/login'); 

  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="password"]', 'password123');
  await page.getByRole('button', {name:'log in'}).click();

  await page.goto('/');
  await expect(page).toHaveURL('/');
  await expect(page.getByText('Ongoing Tasks')).toBeVisible();

  await page.goto('/categories');
  await expect(page).toHaveURL('/categories');
  await expect(page.getByRole('heading', {name:'Categories'})).toBeVisible();

  await page.goto('/profile');
  await expect(page).toHaveURL('/profile');
  await expect(page.getByRole('heading', {name:'Profile'})).toBeVisible();

  await page.goto('/history');
  await expect(page).toHaveURL('/history');
  await expect(page.getByRole('heading', {name:'History'})).toBeVisible();

  await page.goto('/trash');
  await expect(page).toHaveURL('/trash');
  await expect(page.getByRole('heading', {name:'Trash'})).toBeVisible();

  await page.goto('/settings');
  await expect(page).toHaveURL('/settings');
  await expect(page.getByRole('heading', {name:'Settings'})).toBeVisible();

  await page.goto('/logout');
  await expect(page).toHaveURL('/logout');
  await page.getByRole('link', { name: 'Yes' }).click();
  await expect(page).toHaveURL('/auth/login');

});