import { test, expect } from "@playwright/test"

test.describe("Landing page", () => {
  test("loads with the correct title", async ({ page }) => {
    await page.goto("/")
    await expect(page).toHaveTitle(/SprintSync/)
  })

  test("has a primary call-to-action", async ({ page }) => {
    await page.goto("/")
    await expect(
      page.getByRole("link", { name: /Get started/i })
    ).toBeVisible()
  })
})
