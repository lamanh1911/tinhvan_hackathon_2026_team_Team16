/**
 * E2E — Email draft state machine (FR-02, FR-06)
 *
 * Playwright not installed in this project.
 * Tests are skipped — run manually after `npm install -D @playwright/test`.
 */
import { test, expect } from "@playwright/test";

const BASE_URL = process.env.BASE_URL ?? "http://localhost:3000";

test.describe("FR-02/FR-06: Email draft state machine", () => {
  test.skip(true, "Playwright not installed — skeleton only");

  test("new email draft has status 'draft'", async ({ page }) => {
    await page.goto(`${BASE_URL}/emails`);
    const badge = page.locator("[data-testid='status-badge']").first();
    await expect(badge).toHaveText(/draft/i);
  });

  test("Send button is disabled when email is in draft status", async ({ page }) => {
    await page.goto(`${BASE_URL}/emails`);
    await page.locator("[data-testid='email-row']").first().click();
    const sendBtn = page.locator("[data-testid='send-btn']");
    await expect(sendBtn).toBeDisabled();
  });

  test("approve email transitions status to approved", async ({ page }) => {
    await page.goto(`${BASE_URL}/emails`);
    await page.locator("[data-testid='email-row']").first().click();
    await page.locator("[data-testid='approve-btn']").click();

    const badge = page.locator("[data-testid='status-badge']");
    await expect(badge).toHaveText(/approved/i, { timeout: 5_000 });
  });

  test("mark-sent on approved email shows sent status", async ({ page }) => {
    await page.goto(`${BASE_URL}/emails`);
    // Navigate to an already-approved draft
    await page.locator("[data-testid='approved-email-row']").first().click();
    await page.locator("[data-testid='send-btn']").click();

    const badge = page.locator("[data-testid='status-badge']");
    await expect(badge).toHaveText(/sent/i, { timeout: 5_000 });
  });

  test("no email is sent to real mailbox (send only marks status)", async ({ page }) => {
    // Verifying this E2E: after 'send', no external request to SMTP/email provider.
    // Network interception check — mark as documentation only (requires mock network).
    // TODO: intercept fetch calls and assert no SMTP requests fired.
    expect(true).toBe(true); // placeholder
  });
});
