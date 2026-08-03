import type { Metadata } from "next"

import { AdminShell } from "./components/AdminShell"

export const metadata: Metadata = {
  title: { default: "Admin", template: "%s | SprintSync Admin" },
  description: "Enterprise admin platform for SprintSync.",
}

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <AdminShell>{children}</AdminShell>
}
