"use client"

import Link from "next/link"

const links = [
  { href: "/admin/ai/prompts", label: "Prompt manager", description: "Versioned prompt templates" },
  { href: "/admin/ai/documents", label: "RAG documents", description: "Ingest and search documents" },
  { href: "/admin/ai/usage", label: "Usage & cost", description: "Token and cost analytics" },
  { href: "/admin/ai/providers", label: "Providers", description: "Multi-provider configuration" },
]

export default function AIPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">AI platform</h1>
      <div className="grid gap-4 sm:grid-cols-2">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="rounded-xl border border-border bg-surface p-6 shadow-sm transition-colors hover:bg-accent"
          >
            <p className="font-medium">{link.label}</p>
            <p className="text-sm text-muted-foreground">{link.description}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
