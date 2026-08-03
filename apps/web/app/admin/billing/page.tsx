"use client"

import { useEffect, useState } from "react"

import { adminApi } from "../lib/admin-api"
import { BillingMetrics } from "../lib/admin-types"
import { StatCard } from "../components/StatCard"

export default function AdminBillingPage() {
  const [metrics, setMetrics] = useState<BillingMetrics | null>(null)

  useEffect(() => {
    adminApi.billingMetrics().then((res) => setMetrics(res as BillingMetrics))
  }, [])

  if (!metrics) return <p className="text-muted-foreground">Loading billing...</p>

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Billing overview</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="MRR" value={`$${metrics.mrr.toFixed(2)}`} />
        <StatCard label="ARR" value={`$${metrics.arr.toFixed(2)}`} />
        <StatCard label="Active subs" value={metrics.active_subscriptions} />
        <StatCard
          label="Failed payments (30d)"
          value={metrics.failed_payments_30d}
        />
      </div>
    </div>
  )
}
