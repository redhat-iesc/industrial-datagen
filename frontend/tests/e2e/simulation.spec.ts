import { test, expect } from '@playwright/test';

test.describe('Feature: Simulation Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('Simulation Dashboard')).toBeVisible();
  });

  test('Scenario: User selects a simulator and starts a simulation', async ({ page }) => {
    // When I select the "Chemical Reactor" simulator
    await page.getByText('Chemical Reactor').click();

    // And I click the "Start" button
    await page.getByRole('button', { name: 'Start' }).click();

    // Then the simulation should be running (Stop button visible)
    await expect(page.getByRole('button', { name: 'Stop' })).toBeVisible();

    // And live chart data should appear
    await page.waitForTimeout(2000);
    await expect(page.locator('.pf-v6-c-card').filter({ hasText: 'Process Trend Analysis' })).toBeVisible();

    // When I click the "Stop" button
    await page.getByRole('button', { name: 'Stop' }).click();

    // Then the simulation should be stopped (Start button visible again)
    await expect(page.getByRole('button', { name: 'Start' })).toBeVisible();
  });

  test('Scenario: User selects each simulator type', async ({ page }) => {
    // Then I should see all 5 simulator cards
    await expect(page.getByText('Refinery Distillation')).toBeVisible();
    await expect(page.getByText('Chemical Reactor')).toBeVisible();
    await expect(page.getByText('Pulp Digester')).toBeVisible();
    await expect(page.getByText('Pharma Reactor')).toBeVisible();
    await expect(page.getByText('Rotating Equipment')).toBeVisible();

    // When I select the "Refinery Distillation" simulator
    await page.getByText('Refinery Distillation').click();
    // Then the parameter panel should show refinery parameters
    await expect(page.getByText('Crude Temperature')).toBeVisible();
    await expect(page.getByText('Feed Rate')).toBeVisible();

    // When I select the "Pulp Digester" simulator
    await page.getByText('Pulp Digester').click();
    // Then the parameter panel should show pulp parameters
    await expect(page.getByText('Wood Input')).toBeVisible();
    await expect(page.getByText('Alkali Concentration')).toBeVisible();
    await expect(page.getByText('Cooking Time')).toBeVisible();

    // When I select the "Rotating Equipment" simulator
    await page.getByText('Rotating Equipment').click();
    // Then the anomaly panel should be visible
    await expect(page.getByText('Fault Injection')).toBeVisible();
    await expect(page.getByText('Bearing Fault')).toBeVisible();
    await expect(page.getByText('Rotor Imbalance')).toBeVisible();
    await expect(page.getByText('Misalignment')).toBeVisible();
  });

  test('Scenario: Real-time chart updates with simulation data', async ({ page }) => {
    // When I click the "Start" button
    await page.getByRole('button', { name: 'Start' }).click();

    // And I wait for simulation data
    await page.waitForTimeout(2500);

    // Then the statistics panel should show computed values
    await expect(page.getByText(/min:.*max:.*avg:/).first()).toBeVisible();

    // When I click the "Stop" button
    await page.getByRole('button', { name: 'Stop' }).click();

    // Then the chart data should be preserved (stats still visible)
    await expect(page.getByText(/min:.*max:.*avg:/).first()).toBeVisible();
  });

  test('Scenario: User resets the simulation', async ({ page }) => {
    // When I click the "Start" button
    await page.getByRole('button', { name: 'Start' }).click();

    // And I wait for simulation data
    await page.waitForTimeout(2000);

    // And I click the "Stop" button
    await page.getByRole('button', { name: 'Stop' }).click();

    // And I click the "Reset" button
    await page.getByRole('button', { name: 'Reset' }).click();

    // Then the chart should show no data
    await expect(page.getByText('No data yet. Start a simulation to see live charts.')).toBeVisible();

    // And the statistics should show no data
    await expect(page.getByText('No data available.')).toBeVisible();
  });
});
