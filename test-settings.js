const { test, expect } = require('@playwright/test');
test('can type in settings address', async ({ page }) => {
  await page.goto('http://localhost:8080');
  await page.click('text=Settings');
  const addressInput = page.locator('#set-pharmacy-address');
  await addressInput.fill('New Address 123');
  const value = await addressInput.inputValue();
  console.log("INPUT VALUE AFTER TYPE:", value);
});
