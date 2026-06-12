/**
 * E2E — Schedule proposal flow (FR-03 online, FR-04 offline)
 *
 * Playwright not installed in this project.
 * Tests are skipped — run manually after `npm install -D @playwright/test`.
 */
import { test, expect } from "@playwright/test";

const BASE_URL = process.env.BASE_URL ?? "http://localhost:3000";

test.describe("FR-03: Online schedule proposal", () => {
  test.skip(true, "Playwright not installed — skeleton only");

  test("online tab creates proposal with 4 slots", async ({ page }) => {
    await page.goto(`${BASE_URL}/schedule`);
    await page.locator("[data-testid='tab-online']").click();
    await page.locator("[data-testid='create-proposal-btn']").click();

    const slots = page.locator("[data-testid='slot-row']");
    await expect(slots).toHaveCount(4, { timeout: 10_000 });
  });

  test("proposal mode badge shows 'Online'", async ({ page }) => {
    await page.goto(`${BASE_URL}/schedule`);
    await page.locator("[data-testid='tab-online']").click();
    await page.locator("[data-testid='create-proposal-btn']").click();

    await expect(page.locator("[data-testid='mode-badge']").first()).toHaveText(
      /online/i,
      { timeout: 10_000 }
    );
  });
});

test.describe("FR-04: Offline schedule proposal", () => {
  test.skip(true, "Playwright not installed — skeleton only");

  test("offline tab requires location before creating proposal", async ({ page }) => {
    await page.goto(`${BASE_URL}/schedule`);
    await page.locator("[data-testid='tab-offline']").click();
    await page.locator("[data-testid='create-proposal-btn']").click();

    await expect(
      page.locator("[data-testid='location-error']")
    ).toBeVisible({ timeout: 3_000 });
  });

  test("offline proposal shows travel buffer badge on each slot", async ({ page }) => {
    await page.goto(`${BASE_URL}/schedule`);
    await page.locator("[data-testid='tab-offline']").click();
    await page.locator("[data-testid='location-input']").fill("123 Main Street, Hanoi");
    await page.locator("[data-testid='create-proposal-btn']").click();

    const badge = page.locator("[data-testid='travel-buffer-badge']").first();
    await expect(badge).toBeVisible({ timeout: 10_000 });
    await expect(badge).toContainText(/min travel/i);
  });

  test("offline proposal mode badge shows 'Offline'", async ({ page }) => {
    await page.goto(`${BASE_URL}/schedule`);
    await page.locator("[data-testid='tab-offline']").click();
    await page.locator("[data-testid='location-input']").fill("123 Main Street, Hanoi");
    await page.locator("[data-testid='create-proposal-btn']").click();

    await expect(page.locator("[data-testid='mode-badge']").first()).toHaveText(
      /offline/i,
      { timeout: 10_000 }
    );
  });
});
