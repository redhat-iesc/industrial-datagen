import { test, expect } from '@playwright/test';

test.describe('Feature: Dataset Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('Simulation Dashboard')).toBeVisible();
  });

  test('Scenario: User navigates to datasets page', async ({ page }) => {
    // When I click the "Datasets" navigation link
    await page.getByRole('link', { name: 'Datasets' }).click();

    // Then I should see the datasets page title
    await expect(page.locator('h1').filter({ hasText: 'Datasets' })).toBeVisible();

    // And I should see the generate dataset form
    await expect(page.getByText('Generate Dataset').first()).toBeVisible();
    await expect(page.getByText('Process Type')).toBeVisible();
    await expect(page.getByText('Samples')).toBeVisible();
    await expect(page.getByText('Format')).toBeVisible();
    await expect(page.getByText('Include Anomalies')).toBeVisible();
  });

  test('Scenario: Navigation between pages', async ({ page }) => {
    // When I click the "Datasets" navigation link
    await page.getByRole('link', { name: 'Datasets' }).click();

    // Then I should see the datasets page title
    await expect(page.locator('h1').filter({ hasText: 'Datasets' })).toBeVisible();

    // When I click the "Dashboard" navigation link
    await page.getByRole('link', { name: 'Dashboard' }).click();

    // Then I should see the simulation dashboard
    await expect(page.getByText('Simulation Dashboard')).toBeVisible();
    await expect(page.getByText('Refinery Distillation')).toBeVisible();
  });
});
