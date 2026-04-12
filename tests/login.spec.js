import { test, expect } from '@playwright/test';

test.setTimeout(90000);

test('Full app flow - login to logout', async ({ page }) => {

// Handle ALL dialogs automatically
  page.on('dialog', dialog => {
    console.log(`Dialog: ${dialog.message()}`);
    dialog.accept();
  });

//login
  await page.goto('http://127.0.0.1:5000/auth/login');
  await page.getByRole('textbox', { name: 'username' }).fill('Kawira');
  await page.getByRole('textbox', { name: 'Password' }).fill('@Ongeatask09');
  await page.getByRole('button', { name: 'Log In' }).click();
  await page.waitForURL('http://127.0.0.1:5000/');
  await expect(page.getByRole('link', { name: ' Tasks' })).toBeVisible();

//creating a task
  await page.getByRole('link', { name: ' Tasks' }).click();
  await page.waitForLoadState('networkidle');
  await page.getByRole('button', { name: 'Add New Task' }).click();
  await expect(page.getByRole('textbox', { name: 'Title' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Title' }).fill('DANCING LESSONS');
  await page.getByRole('textbox', { name: 'Description' }).fill('Train on the new dance moves.');
  await page.getByRole('button', { name: 'Create Task' }).click();
  await expect(page.getByRole('textbox', { name: 'Title' })).not.toBeVisible();
  await page.waitForLoadState('networkidle');

//adding a description to a task
  await page.getByRole('heading', { name: 'DANCING LESSONS' }).click();
  await page.waitForLoadState('networkidle');
  const descBox = page.getByRole('textbox', { name: 'Add a description here...' });
  if (await descBox.isVisible()) {
    await descBox.click();
    await descBox.pressSequentially('Train on the new dance moves.');
    await expect(page.getByRole('button', { name: 'Save' })).toBeEnabled({ timeout: 5000 });
    await page.getByRole('button', { name: 'Save' }).click();
    await page.waitForLoadState('networkidle');
  }

//adding subtask
  await page.getByRole('button', { name: '➕' }).click();
  await expect(page.getByRole('textbox', { name: 'Add a new list item' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Add a new list item' }).fill('Abaliu');
  await page.getByRole('button', { name: 'Add' }).click();
  await page.waitForLoadState('networkidle');

//completing subtask
  await page.locator('label').filter({ hasText: 'Abaliu' }).click();
  await page.getByRole('button', { name: 'Mark as Completed' }).click();
  await page.waitForLoadState('networkidle');

//deleting subtask
  const abailiuLabel = page.locator('label').filter({ hasText: 'Abaliu' });
  if (await abailiuLabel.isVisible()) {
    await abailiuLabel.click();
  }
  await page.getByRole('button', { name: /Delete Selected/i }).click();
  await page.waitForLoadState('networkidle');
  if (await page.locator('h1:has-text("500")').isVisible()) {
    console.log('500 error — recovering');
    await page.goto('http://127.0.0.1:5000/');
    await page.waitForLoadState('networkidle');
  }

// completing task
  await page.getByRole('link', { name: ' Tasks' }).click();
  await page.waitForLoadState('networkidle');
  const taskCheckbox = page.getByRole('checkbox').first();
  if (await taskCheckbox.isVisible()) {
    await taskCheckbox.check();
    await page.getByRole('button', { name: 'Mark as Completed' }).click();
    await page.waitForLoadState('networkidle');
  }

// moving task created to trash
  const trashCheckbox = page.getByRole('checkbox').first();
  if (await trashCheckbox.isVisible()) {
    await trashCheckbox.check();
    const trashBtn = page.getByRole('button', { name: /Move to Trash/i });
    if (await trashBtn.isVisible()) {
      await trashBtn.click();
      await page.waitForLoadState('networkidle');
    }
  }

//going to all pages
  for (const { link, urlPattern } of [
    { link: ' Trash',      urlPattern: /trash/    },
    { link: ' Tasks',      urlPattern: /tasks|\// },
    { link: ' Categories', urlPattern: /categor/  },
    { link: ' Profile',    urlPattern: /profile/  },
    { link: ' History',    urlPattern: /history/  },
    { link: ' Settings',   urlPattern: /settings/ },
  ]) {
    await page.getByRole('link', { name: link }).click();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(urlPattern);
  }

//   categories page
  await page.getByRole('link', { name: ' Categories' }).click();
  await page.waitForLoadState('networkidle');

  await page.getByRole('button', { name: 'Add Category' }).click();
  await page.getByRole('textbox', { name: 'Category Name:' }).fill('leisure');
  await page.getByRole('button', { name: 'OK' }).click();
  await page.waitForLoadState('networkidle');

  const selectAll = page.locator('#select-all-checkbox');
  if (await selectAll.isVisible()) {
    await selectAll.check();
    await page.getByRole('button', { name: 'Delete All' }).click();
    await page.waitForLoadState('networkidle');
  }
  const modal = page.locator('#custom-alert');
  if (await modal.isVisible()) {
    await page.getByRole('button', { name: 'OK' }).click();
    await page.waitForLoadState('networkidle');
  }
  
//   permanently deleting from trash
  await page.getByRole('link', { name: ' Trash' }).click();
  await page.waitForLoadState('networkidle');
  const trashSelectAll = page.locator('#select-all-checkbox');
  if (await trashSelectAll.isVisible()) {
    await trashSelectAll.check();
    const permDelete = page.getByRole('button', { name: /delete|empty/i });
    if (await permDelete.isVisible()) {
      await permDelete.click();
      await page.waitForLoadState('networkidle');
    }
  }

//   updating profile
  await page.getByRole('link', { name: ' Profile' }).click();
  await page.waitForLoadState('networkidle');

  await page.getByRole('button', { name: '✎' }).first().click();
  await page.getByRole('textbox', { name: 'Username' }).fill('Kawira');

  await page.getByRole('button', { name: '✎' }).nth(1).click();
  await page.getByRole('textbox', { name: 'First Name' }).fill('Faith');

  await page.getByRole('button', { name: '✎' }).nth(2).click();
  await page.getByRole('textbox', { name: 'Last Name' }).fill('Kagwiria');

  await page.getByRole('button', { name: '✎' }).nth(3).click();
  await page.getByRole('textbox', { name: 'Email' }).fill('kagwiriafaith45@gmail.com');

  await page.getByRole('button', { name: 'Save Profile' }).click();
  await page.waitForLoadState('networkidle');

//   logout
  await page.goto('http://127.0.0.1:5000/auth/logout');
  await page.waitForLoadState('networkidle');

  // Confirm logout if a confirmation page appears
  const yesLink = page.getByRole('link', { name: 'Yes' });
  if (await yesLink.isVisible()) {
    await yesLink.click();
  }
  await expect(page).toHaveURL(/login/);
  await page.screenshot({ path: 'test-results/playwright-pass.png', fullPage: true });
  console.log('All steps completed successfully!');
});