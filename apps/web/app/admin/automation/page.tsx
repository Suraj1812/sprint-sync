"use client"

import { useEffect, useState } from "react"

import { adminApi } from "../lib/admin-api"
import { DomainEvent } from "../lib/admin-types"
import { DataTable } from "../components/DataTable"

export default function AdminAutomationPage() {
  const [events, setEvents] = useState<DomainEvent[]>([])

  useEffect(() => {
    adminApi.listEvents().then((res) => setEvents(res || []))
  }, [])

  const columns = [
    { header: "Event", cell: (e: DomainEvent) => e.event_type },
    { header: "Status", cell: (e: DomainEvent) => e.status },
    { header: "Created", cell: (e: DomainEvent) => e.created_at.slice(0, 19) },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Automation</h1>
      <DataTable
        columns={columns}
        rows={events.slice(0, 20)}
        keyExtractor={(e) => e.id}
        caption="Recent domain events"
      />
    </div>
  )
}
