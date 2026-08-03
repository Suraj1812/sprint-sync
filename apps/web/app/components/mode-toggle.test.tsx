import { describe, it, expect, vi } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"

import { ModeToggle } from "@/app/components/mode-toggle"

vi.mock("next-themes", () => ({
  useTheme: () => ({ theme: "light", setTheme: vi.fn() }),
}))

describe("ModeToggle", () => {
  it("renders a theme toggle button with an accessible label", async () => {
    render(<ModeToggle />)
    await waitFor(() => {
      const button = screen.getByLabelText("Switch to dark theme")
      expect(button).toBeInTheDocument()
    })
  })
})
