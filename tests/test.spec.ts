import { test, expect } from '@playwright/test';

test("login test", async ({ page }) => {
  await page.goto("/auth/login");

  await page.fill("input[name='username']", "admin");
  await page.fill("input[name='password']", "admin");
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page.getByRole("heading", { name: "Ongoing Tasks" })).toBeVisible();
});

test("add task test", async ({ page }) => {
  await page.goto("/auth/login");

  await page.fill("input[name='username']", "admin");
  await page.fill("input[name='password']", "admin");
  await page.getByRole("button", { name: "Log in" }).click();

  await page.getByRole("button", { name: "Add New Task" }).click();
  await page.getByLabel("Task Name").fill("New Test Task");
  await page.getByLabel("Description").fill("This is a test task.");
  await page.getByRole("button", { name: "Create Task" }).click();
  await expect(page.getByText("Test Task")).toBeVisible();
});

test("open task and go back to task list test", async ({ page }) => {
  await page.goto("/auth/login");

  await page.fill("input[name='username']", "admin");
  await page.fill("input[name='password']", "admin");
  await page.getByRole("button", { name: "Log in" }).click();

  await page.getByTestId("task-card").first().click();
  await page.locator(".fa-arrow-left").click();

  await expect(page.getByRole("heading", { name: "Ongoing Tasks" })).toBeVisible();
});

test("delete and restore task test", async ({ page }) => {
  await page.goto("/auth/login");

  await page.fill("input[name='username']", "admin");
  await page.fill("input[name='password']", "admin");
  await page.getByRole("button", { name: "Log in" }).click();

  await page.getByTestId("task-checkbox").first().check();
  await page.getByRole("button", { name: "🗑️ Move to Trash" }).click();
  await page.getByRole("link", { name: "Trash" }).click();
  await page.locator('input[name="task_ids"]').first().check();
  await page.getByRole("button", { name: "Restore" }).click();
  await page.getByRole("link", { name: "Tasks" }).click();
  await expect(page.getByText("New Test Task")).toBeVisible();
});

test("move to history and restore task test", async ({ page }) => {
  await page.goto("/auth/login");

  await page.fill("input[name='username']", "admin");
  await page.fill("input[name='password']", "admin");
  await page.getByRole("button", { name: "Log in" }).click();

  await page.getByTestId("task-checkbox").first().check();
  await page.getByRole("button", { name: "Mark as Completed" }).click();
  await page.getByRole("link", { name: "History" }).click();
  await page.locator('input[name="task_ids"]').first().check();
  await page.getByRole("button", { name: "Reopen task" }).click();
  await page.getByRole("link", { name: "Tasks" }).click();
  await expect(page.getByText("New Test Task")).toBeVisible();
});

test("logout test", async ({ page }) => {
  await page.goto("/auth/login");

  await page.fill("input[name='username']", "admin");
  await page.fill("input[name='password']", "admin");
  await page.getByRole("button", { name: "Log in" }).click();
  await page.waitForURL("/");

  await page.getByRole("link", { name: "Logout" }).click();
  await page.getByRole("link", { name: "Yes" }).click();
  await expect(page.getByRole("button", { name: "Log in" })).toBeVisible();
});