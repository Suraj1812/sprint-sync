"use client"

import { Bell, Command, Menu, Search } from "lucide-react"

import { Button, Input } from "@sprint-sync/ui"

interface AdminTopNavProps {
  onMenuClick: () => void
}

export function AdminTopNav({ onMenuClick }: AdminTopNavProps) {
  return (
    <header className="fixed top-0 z-30 w-full border-b border-border bg-background/95 backdrop-blur">
      <div className="container flex h-16 items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={onMenuClick}
          aria-label="Open navigation"
        >
          <Menu className="h-5 w-5" />
        </Button>

        <div className="flex items-center gap-2">
          <Command className="h-5 w-5 text-primary" aria-hidden="true" />
          <span className="text-lg font-semibold">SprintSync Admin</span>
        </div>

        <div className="hidden flex-1 md:mx-8 md:block">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search users, orgs, flags..."
              className="pl-9"
              aria-label="Global admin search"
            />
          </div>
        </div>

        <div className="ml-auto flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            aria-label="Notifications"
          >
            <Bell className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  )
}
