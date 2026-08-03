"use client"

import { useEffect, useState } from "react"

import { Badge } from "@sprint-sync/ui"

import { adminApi } from "../../lib/admin-api"
import { BillingEvent } from "../../lib/admin-types"
import { DataTable } from "../../components/DataTable"

export default function AdminBillingEventsPage() {
  const [events, setEvents] = useState<BillingEvent[]>([])

  useEffect(() => {
    adminApi.listBillingEvents().then((res) => setEvents(res || []))
  }, [])

  const columns = [
    { header: "Provider", cell: (e: BillingEvent) => e.provider },
    { header: "Type", cell: (e: BillingEvent) => e.event_type },
    { header: "Processed", cell: (e: BillingEvent) => (
      <Badge variant={e.processed ? "default" : "secondary"}>
        {e.processed ? "Yes" : "No"}
      </Badge>
    )},
    { header: "Attempts", cell: (e: BillingEvent) => e.attempts },
    { header: "Created", cell: (e: BillingEvent) => e.created_at.slice(0, 10) },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Billing events</h1>
      <DataTable
        columns={columns}
        rows={events}
        keyExtractor={(e) => e.id}
        caption="Billing events"
      />
    </div>
  )
}
