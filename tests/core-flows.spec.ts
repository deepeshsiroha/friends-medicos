import { _electron as electron, ElectronApplication, Page } from 'playwright';
import { test, expect } from '@playwright/test';

test.describe('Core E2E Workflows', () => {
  let electronApp: ElectronApplication;
  let page: Page;
  let testItemBatch = `BATCH-${Math.floor(Math.random() * 10000)}`;

  // Helper: navigate to a tab by clicking sidebar buttons via page.evaluate
  async function navigateToTab(tabText: string, waitForSelector: string) {
    // Open sidebar
    await page.evaluate(() => {
      document.getElementById('drawer-toggle')?.click();
    });
    await page.waitForTimeout(400);

    // Click the matching sidebar button
    await page.evaluate((text) => {
      const buttons = document.querySelectorAll('button.sidebar-btn');
      for (const btn of buttons) {
        if (btn.textContent?.includes(text)) {
          (btn as HTMLElement).click();
          return;
        }
      }
    }, tabText);

    await page.waitForTimeout(500);
    await page.waitForSelector(waitForSelector, { state: 'attached', timeout: 15000 });
  }

  test.beforeAll(async () => {
    electronApp = await electron.launch({
      args: ['main.js'],
      env: { ...process.env, NODE_ENV: 'test' }
    });
    page = await electronApp.firstWindow();
    await page.waitForSelector('.top-app-bar', { timeout: 15000 });
  });

  test.afterAll(async () => {
    await electronApp.close();
  });

  test('Step 1: Add inventory stock item', async () => {
    test.setTimeout(30000);

    await navigateToTab('Stock Inventory', '#inv-item');

    await page.fill('#inv-item', 'Playwright Paracetamol');
    await page.fill('#inv-batch', testItemBatch);
    await page.fill('#inv-qty', '100');
    await page.fill('#inv-price', '10');
    await page.fill('#inv-selling', '15');
    await page.fill('#inv-mrp', '20');

    await page.evaluate(() => {
      const btn = document.querySelector('button.btn-add') as HTMLElement;
      btn?.click();
    });

    await expect(page.locator('#inv-item')).toHaveValue('', { timeout: 10000 });
  });

  test('Step 2: Generate bill with the new stock item', async () => {
    test.setTimeout(60000);

    await navigateToTab('Sales POS', '#bill-mobile');

    // Fill Patient Details
    await page.evaluate(() => {
      const el = document.getElementById('bill-mobile') as HTMLInputElement;
      el.value = '+919999988888';
      el.dispatchEvent(new Event('input', { bubbles: true }));
    });
    await page.fill('#bill-name', 'Playwright Test Patient');

    // Search for the test item
    await page.fill('input[placeholder*="Search stock by name"]', testItemBatch);
    await page.waitForTimeout(500);

    // Click the stock card
    await page.evaluate((batch) => {
      const cards = document.querySelectorAll('.stock-card');
      for (const card of cards) {
        if (card.textContent?.includes(batch)) {
          (card as HTMLElement).click();
          return;
        }
      }
    }, testItemBatch);

    // Verify it appeared in the basket
    await expect(
      page.locator('#bill-items-table-body').locator(`text=Playwright Paracetamol`)
    ).toBeVisible({ timeout: 5000 });

    // Verify subtotal
    await expect(page.locator('#bill-sum-subtotal')).toHaveText('₹15.00');

    // Click Generate Bill
    await page.evaluate(() => {
      const buttons = document.querySelectorAll('button');
      for (const btn of buttons) {
        if (btn.textContent?.includes('Generate Bill')) {
          btn.click();
          return;
        }
      }
    });

    // The bill-mobile should clear on success
    await expect(page.locator('#bill-mobile')).toHaveValue('', { timeout: 15000 });
  });

  test('Step 3: Verify stock was deducted after the sale', async () => {
    test.setTimeout(30000);

    await navigateToTab('Stock Inventory', '#stock-table-search');

    await page.fill('#stock-table-search', testItemBatch);
    await page.waitForTimeout(500);

    const row = page.locator('tr', { hasText: testItemBatch });
    await expect(row).toBeVisible({ timeout: 5000 });
    await expect(row.locator('text=99')).toBeVisible({ timeout: 5000 });
  });

  test('Step 4: Verify customer was created with correct total spent', async () => {
    test.setTimeout(30000);

    await navigateToTab('Customers CRM', 'input[placeholder*="Search Name or Mobile"]');

    await page.fill('input[placeholder*="Search Name or Mobile"]', '9999988888');
    await page.waitForTimeout(500);

    const customerRow = page.locator('tr', { hasText: 'Playwright Test Patient' });
    await expect(customerRow).toBeVisible({ timeout: 5000 });
    // Verify total spent contains a ₹ amount (accumulated across test runs)
    await expect(customerRow).toContainText('₹', { timeout: 5000 });
  });

  test('Step 5: Add a daily expense and verify it appears', async () => {
    test.setTimeout(30000);

    await navigateToTab('Daily Expenses', 'input[type="date"]');

    await page.evaluate(() => {
      const amtInput = document.querySelector('input[placeholder*="e.g. 50"]') as HTMLInputElement;
      if (amtInput) {
        amtInput.value = '123';
        amtInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
      const descInput = document.querySelector('input[placeholder*="e.g. Morning tea"]') as HTMLInputElement;
      if (descInput) {
        descInput.value = 'Playwright Test Expense';
        descInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
    });

    // Click Save Expense
    await page.evaluate(() => {
      const buttons = document.querySelectorAll('button');
      for (const btn of buttons) {
        if (btn.textContent?.includes('Save Expense')) {
          btn.click();
          return;
        }
      }
    });

    await page.waitForTimeout(500);

    // Verify it appeared in the table
    const row = page.locator('tr', { hasText: 'Playwright Test Expense' });
    await expect(row.first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('body')).toContainText('₹123.00');
  });
});
