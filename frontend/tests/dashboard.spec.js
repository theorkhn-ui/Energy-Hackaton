import { test, expect } from '@playwright/test';
import fs from 'node:fs/promises';

test('historical results render without runtime errors, and inverter drill-down changes the chart', async ({
  page,
}) => {
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto('/');
  await expect(
    page.getByRole('heading', { name: 'Solar intelligence, at a glance.' }),
  ).toBeVisible();
  await expect(page.locator('.stat-value').first()).toHaveText('91.3%');
  await expect(page.locator('.inverter-tile')).toHaveCount(65);
  await expect(page.locator('.recharts-area-curve')).toBeVisible();
  await page
    .getByRole('button', { name: 'Inverter 01.03.018, 80% of peer output' })
    .click();
  await expect(
    page.getByRole('combobox', { name: 'Inverter', exact: true }),
  ).toHaveValue('01.03.018');
  await expect(
    page.getByRole('heading', { name: 'Every inverter tells a story.' }),
  ).toBeVisible();
  await page.getByRole('button', { name: 'Full history', exact: true }).click();
  await expect(
    page.getByRole('button', { name: 'Full history', exact: true }),
  ).toHaveAttribute('aria-pressed', 'true');
  expect(errors).toEqual([]);
});

test('early detection separates missed tickets, and every analytical view renders', async ({
  page,
}) => {
  await page.goto('/');
  await page
    .getByRole('button', { name: 'Early detection', exact: true })
    .click();
  await expect(page.locator('tbody tr')).toHaveCount(46);
  await page.getByLabel('Show unflagged tickets').check();
  await expect(page.locator('tbody tr')).toHaveCount(4);
  await page
    .getByRole('button', { name: 'Alarm intelligence', exact: true })
    .click();
  await expect(
    page.getByRole('heading', {
      name: 'What is actually stopping production?',
    }),
  ).toBeVisible();
  await expect(page.locator('.recharts-bar-rectangle').first()).toBeVisible();
  await page
    .getByRole('button', { name: 'Energy & impact', exact: true })
    .click();
  await expect(page.locator('.stat-value').first()).toHaveText('997€');
  await expect(page.locator('tbody tr')).toHaveCount(12);
  await page
    .getByRole('button', { name: 'Soiling & shading', exact: true })
    .click();
  await expect(page.locator('.scope-bar')).toContainText('107 inverters');
  await page.getByRole('combobox', { name: 'Orientation' }).selectOption('W');
  await expect(page.getByRole('combobox', { name: 'Orientation' })).toHaveValue(
    'W',
  );
  await expect(
    page.getByRole('heading', {
      name: 'Repeated patterns, ranked by inverter',
    }),
  ).toBeVisible();
  await page
    .getByRole('button', { name: 'Model validation', exact: true })
    .click();
  await expect(
    page.getByRole('heading', { name: 'A uniform 10% loss' }),
  ).toBeVisible();
  await page.getByLabel('Repair in').fill('0');
  await expect(page.locator('.delay-value')).toContainText('€0');
  await page.getByLabel('Repair in').fill('91');
  await expect(page.locator('.delay-value')).toContainText('€385');
});

test('sources identify the committed evidence and JSON export includes actual measurements', async ({
  page,
}) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Data & methodology' }).click();
  await expect(page.locator('dialog')).toBeVisible();
  await expect(page.locator('.source-list a')).toHaveCount(12);
  await expect(page.locator('.source-list a').first()).toHaveAttribute(
    'href',
    /\/blob\/[a-f0-9]{40}\/runs\//,
  );
  await page.keyboard.press('Escape');
  await expect(page.locator('dialog')).toHaveCount(0);
  const downloadEvent = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export results' }).click();
  const download = await downloadEvent;
  const exported = JSON.parse(await fs.readFile(await download.path(), 'utf8'));
  expect(exported.metrics.earlyTickets).toBe(42);
  expect(exported.metrics.unticketedLossEur).toBe(64247);
  expect(exported.metrics.alarmCounts).toEqual({
    NUISANCE: 582,
    TRIP: 204,
    DERATE: 37,
  });
});

test('mobile views fit the viewport and navigation remains usable', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  for (const view of [
    'Overview',
    'Inverter health',
    'Early detection',
    'Alarm intelligence',
    'Energy & impact',
    'Soiling & shading',
    'Model validation',
  ]) {
    await page.getByRole('button', { name: 'Toggle navigation' }).click();
    await page.getByRole('button', { name: view, exact: true }).click();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth,
      ),
    ).toBe(true);
    await expect(page.locator('h1')).toBeVisible();
  }
});
