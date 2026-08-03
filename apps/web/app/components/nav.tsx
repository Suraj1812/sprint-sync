"use client"

import { Button } from "@sprint-sync/ui"
import { Zap } from "lucide-react"

import { ModeToggle } from "./mode-toggle"
import { MobileNav } from "./mobile-nav"

const links = [
  { label: "Features", href: "#features" },
  { label: "Product", href: "#product" },
  { label: "Benefits", href: "#benefits" },
  { label: "FAQ", href: "#faq" },
]

export function Nav() {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/40 bg-background/80 backdrop-blur-md">
      <div className="container flex h-16 items-center justify-between">
        <a href="/" className="flex items-center gap-2 text-foreground">
          <Zap className="h-5 w-5" aria-hidden="true" />
          <span className="text-lg font-semibold tracking-tight">SprintSync</span>
        </a>

        <nav
          aria-label="Main navigation"
          className="hidden items-center gap-6 md:flex"
        >
          {links.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="hidden items-center gap-2 md:flex">
          <ModeToggle />
          <Button asChild size="sm">
            <a href="#cta">Get started</a>
          </Button>
        </div>

        <div className="flex items-center gap-2 md:hidden">
          <ModeToggle />
          <MobileNav />
        </div>
      </div>
    </header>
  )
}
