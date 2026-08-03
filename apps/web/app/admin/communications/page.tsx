"use client"

import { useEffect, useState } from "react"

import { adminApi } from "../lib/admin-api"
import { DeliveryStats } from "../lib/admin-types"
import { StatCard } from "../components/StatCard"

export default function AdminCommunicationsPage() {
  const [stats, setStats] = useState<DeliveryStats | null>(null)

  useEffect(() => {
    adminApi.communicationStats().then((res) => setStats(res))
  }, [])

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Communications</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total" value={String(stats?.total ?? "—")} />
        <StatCard label="Pending" value={String(stats?.pending ?? "—")} />
        <StatCard label="Completed" value={String(stats?.completed ?? "—")} />
        <StatCard label="Failed" value={String(stats?.failed ?? "—")} />
      </div>
      <div className="rounded-lg border p-4">
        <h2 className="text-lg font-medium mb-2">By channel</h2>
        <pre className="text-sm overflow-auto">
          {JSON.stringify(stats?.by_channel ?? {}, null, 2)}
        </pre>
      </div>
    </div>
  )
}
