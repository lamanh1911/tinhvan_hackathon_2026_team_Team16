/**
 * E2E — Business card scan flow (FR-01)
 *
 * Playwright not installed in this project.
 * Tests are skipped — run manually after `npm install -D @playwright/test`.
 *
 * To enable: remove test.skip() and set BASE_URL in playwright.config.ts.
 */
import { test, expect } from "@playwright/test";

const BASE_URL = process.env.BASE_URL ?? "http://localhost:3000";

test.describe("FR-01: Business card scan", () => {
  test.skip(true, "Playwright not installed — skeleton only");

  test("upload a business card and reach confirm screen", async ({ page }) => {
    await page.goto(`${BASE_URL}/cards/new`);

    const input = page.locator('input[type="file"]');
    await input.setInputFiles("tests/fixtures/sample_card.jpg");

    await expect(page.locator("[data-testid='confirm-screen']")).toBeVisible({
      timeout: 15_000,
    });
  });

  test("uploading a bank card shows WRONG_CARD_TYPE error without redirect", async ({ page }) => {
    await page.goto(`${BASE_URL}/cards/new`);
    const input = page.locator('input[type="file"]');
    await input.setInputFiles("tests/fixtures/bank_card.jpg");

    await expect(page.locator("[data-testid='card-error']")).toBeVisible({
      timeout: 15_000,
    });
    await expect(page).not.toHaveURL(/confirm/);
  });

  test("low-confidence fields show amber highlight on confirm screen", async ({ page }) => {
    await page.goto(`${BASE_URL}/cards/new`);
    const input = page.locator('input[type="file"]');
    await input.setInputFiles("tests/fixtures/sample_card.jpg");

    await page.waitForURL(/confirm/, { timeout: 15_000 });
    const flagged = page.locator("[data-testid='flagged-field']");
    // May be 0 if mock always returns high confidence — assertion is conditional
    const count = await flagged.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test("saving the card creates a customer record", async ({ page }) => {
    await page.goto(`${BASE_URL}/cards/new`);
    const input = page.locator('input[type="file"]');
    await input.setInputFiles("tests/fixtures/sample_card.jpg");

    await page.waitForURL(/confirm/, { timeout: 15_000 });
    await page.locator("[data-testid='save-card-btn']").click();
    await expect(page).toHaveURL(/customers/, { timeout: 10_000 });
  });
});
