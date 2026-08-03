"use client"

import { useEffect, useState } from "react"
import Link from "next/link"

import { Button } from "@sprint-sync/ui"

import { adminApi } from "../../lib/admin-api"
import { EmailTemplate } from "../../lib/admin-types"
import { DataTable } from "../../components/DataTable"

export default function AdminTemplatesPage() {
  const [templates, setTemplates] = useState<EmailTemplate[]>([])

  useEffect(() => {
    adminApi.listEmailTemplates().then((res) => setTemplates(res || []))
  }, [])

  const columns = [
    { header: "Name", cell: (t: EmailTemplate) => t.name },
    { header: "Locale", cell: (t: EmailTemplate) => t.locale },
    { header: "Version", cell: (t: EmailTemplate) => t.version },
    { header: "Subject", cell: (t: EmailTemplate) => t.subject },
    { header: "Active", cell: (t: EmailTemplate) => (t.is_active ? "Yes" : "No") },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Email Templates</h1>
        <Button asChild>
          <Link href="/admin/communications/templates/new">New template</Link>
        </Button>
      </div>
      <DataTable
        columns={columns}
        rows={templates}
        keyExtractor={(t) => t.id}
        caption="Email templates"
      />
    </div>
  )
}
