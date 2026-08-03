"use client"

import { useEffect, useState } from "react"

import { adminApi } from "../lib/admin-api"
import { AuditLog } from "../lib/admin-types"
import { DataTable } from "../components/DataTable"

export default function AdminAuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([])

  useEffect(() => {
    adminApi.audit().then((res) => setLogs(res?.data || []))
  }, [])

  const columns = [
    { header: "When", cell: (l: AuditLog) => new Date(l.created_at).toLocaleString() },
    { header: "Actor", cell: (l: AuditLog) => l.actor_email || l.actor_id || "System" },
    { header: "Action", cell: (l: AuditLog) => l.action },
    { header: "Resource", cell: (l: AuditLog) => l.resource },
    { header: "Resource ID", cell: (l: AuditLog) => l.resource_id || "—" },
    { header: "IP", cell: (l: AuditLog) => l.ip_address || "—" },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Audit logs</h1>
      <DataTable
        columns={columns}
        rows={logs}
        keyExtractor={(l) => l.id}
        caption="Admin audit log"
      />
    </div>
  )
}
