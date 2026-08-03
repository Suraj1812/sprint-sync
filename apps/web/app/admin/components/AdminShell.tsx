"use client"

import { useState } from "react"

import { AdminSidebar } from "./AdminSidebar"
import { AdminTopNav } from "./AdminTopNav"

export function AdminShell({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-background text-foreground">
      <AdminTopNav onMenuClick={() => setSidebarOpen(true)} />
      <div className="flex">
        <AdminSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main
          id="admin-main"
          className="flex-1 p-4 pt-20 md:p-8 md:pt-24"
          tabIndex={-1}
        >
          {children}
        </main>
      </div>
    </div>
  )
}
