"use client"

import { Button, Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger, Separator } from "@sprint-sync/ui"
import { Menu } from "lucide-react"

import { ModeToggle } from "./mode-toggle"
import { AuthDialog } from "./auth-dialog"

const links = [
  { label: "Features", href: "#features" },
  { label: "Product", href: "#product" },
  { label: "Benefits", href: "#benefits" },
  { label: "FAQ", href: "#faq" },
  { label: "Pricing", href: "#cta" },
]

export function MobileNav() {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="Open navigation menu">
          <Menu className="h-5 w-5" />
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-80">
        <SheetHeader>
          <SheetTitle className="text-left">SprintSync</SheetTitle>
        </SheetHeader>
        <nav aria-label="Mobile navigation" className="mt-8 flex flex-col gap-1">
          {links.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
            >
              {link.label}
            </a>
          ))}
          <Separator className="my-4" />
          <AuthDialog mobile />
          <div className="mt-4 flex items-center justify-between px-3">
            <span className="text-sm text-muted-foreground">Theme</span>
            <ModeToggle />
          </div>
        </nav>
      </SheetContent>
    </Sheet>
  )
}
