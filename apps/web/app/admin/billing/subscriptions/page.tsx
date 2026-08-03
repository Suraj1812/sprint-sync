"use client"

import { useEffect, useState } from "react"

import { adminApi } from "../../lib/admin-api"
import { Subscription } from "../../lib/admin-types"
import { DataTable } from "../../components/DataTable"

export default function AdminSubscriptionsPage() {
  const [subs, setSubs] = useState<Subscription[]>([])

  useEffect(() => {
    adminApi.listSubscriptions().then((res) => setSubs(res || []))
  }, [])

  const columns = [
    { header: "ID", cell: (s: Subscription) => s.id.slice(0, 8) },
    { header: "Status", cell: (s: Subscription) => s.status },
    { header: "Plan", cell: (s: Subscription) => s.plan_id.slice(0, 8) },
    { header: "Price", cell: (s: Subscription) => s.price_id.slice(0, 8) },
    { header: "Seats", cell: (s: Subscription) => s.seats },
    { header: "Period ends", cell: (s: Subscription) => s.current_period_end?.slice(0, 10) || "—" },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Subscriptions</h1>
      <DataTable
        columns={columns}
        rows={subs}
        keyExtractor={(s) => s.id}
        caption="Subscriptions"
      />
    </div>
  )
}
