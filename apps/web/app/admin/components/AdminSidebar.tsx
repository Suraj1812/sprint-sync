"use client"

import { usePathname } from "next/navigation"
import Link from "next/link"
import {
  BarChart3,
  Bell,
  BookOpen,
  Briefcase,
  Building2,
  CreditCard,
  FileText,
  Flag,
  Globe,
  LayoutDashboard,
  Layers,
  Mail,
  Puzzle,
  Receipt,
  Server,
  Settings,
  Shield,
  Sparkles,
  Users,
  X,
  Zap,
} from "lucide-react"

import { Button } from "@sprint-sync/ui"

const links = [
  { href: "/admin", label: "Dashboard", icon: LayoutDashboard },
  { href: "/admin/users", label: "Users", icon: Users },
  { href: "/admin/organizations", label: "Organizations", icon: Building2 },
  { href: "/admin/feature-flags", label: "Feature flags", icon: Flag },
  { href: "/admin/audit", label: "Audit logs", icon: Shield },
  { href: "/admin/ai", label: "AI platform", icon: Sparkles },
  { href: "/admin/ai/prompts", label: "Prompts", icon: BookOpen },
  { href: "/admin/ai/documents", label: "RAG documents", icon: FileText },
  { href: "/admin/ai/usage", label: "AI usage", icon: BarChart3 },
  { href: "/admin/ai/providers", label: "AI providers", icon: Server },
  { href: "/admin/billing", label: "Billing", icon: CreditCard },
  { href: "/admin/billing/subscriptions", label: "Subscriptions", icon: Zap },
  { href: "/admin/billing/invoices", label: "Invoices", icon: Receipt },
  { href: "/admin/billing/events", label: "Billing events", icon: BarChart3 },
  { href: "/admin/tenancy", label: "Tenancy", icon: Globe },
  { href: "/admin/tenancy/workspaces", label: "Workspaces", icon: Layers },
  { href: "/admin/tenancy/invitations", label: "Invitations", icon: Briefcase },
  { href: "/admin/communications", label: "Communications", icon: Mail },
  { href: "/admin/communications/templates", label: "Email templates", icon: Bell },
  { href: "/admin/automation", label: "Automation", icon: Puzzle },
  { href: "/admin/automation/workflows", label: "Workflows", icon: Zap },
  { href: "/admin/automation/api-keys", label: "API keys", icon: Shield },
  { href: "/admin/automation/oauth", label: "OAuth", icon: Users },
  { href: "/admin/system", label: "System", icon: Settings },
]

interface AdminSidebarProps {
  open: boolean
  onClose: () => void
}

export function AdminSidebar({ open, onClose }: AdminSidebarProps) {
  const pathname = usePathname()

  const nav = (
    <nav aria-label="Admin navigation" className="flex flex-col gap-1 p-4">
      {links.map((link) => {
        const Icon = link.icon
        const isActive = pathname === link.href
        return (
          <Link
            key={link.href}
            href={link.href}
            onClick={onClose}
            aria-current={isActive ? "page" : undefined}
            className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent aria-[current=page]:bg-accent aria-[current=page]:text-accent-foreground"
          >
            <Icon className="h-4 w-4" aria-hidden="true" />
            {link.label}
          </Link>
        )
      })}
    </nav>
  )

  return (
    <>
      <aside className="sticky top-16 hidden h-[calc(100vh-4rem)] w-64 border-r border-border bg-background md:block">
        {nav}
      </aside>

      {open && (
        <div
          className="fixed inset-0 z-40 flex md:hidden"
          role="dialog"
          aria-modal="true"
        >
          <div
            className="flex-1 bg-black/50"
            onClick={onClose}
            aria-hidden="true"
          />
          <div className="h-full w-64 bg-background shadow-lg">
            <div className="flex h-16 items-center justify-between border-b border-border px-4">
              <span className="font-semibold">SprintSync</span>
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                aria-label="Close navigation"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            {nav}
          </div>
        </div>
      )}
    </>
  )
}
