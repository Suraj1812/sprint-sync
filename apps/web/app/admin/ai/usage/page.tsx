"use client"

import { useEffect, useState } from "react"

import { adminApi } from "../../lib/admin-api"
import { UsageStats } from "../../lib/admin-types"
import { StatCard } from "../../components/StatCard"

export default function AdminAIUsagePage() {
  const [stats, setStats] = useState<UsageStats | null>(null)

  useEffect(() => {
    adminApi.aiUsage().then((res) => setStats(res as UsageStats))
  }, [])

  if (!stats) return <p className="text-muted-foreground">Loading usage...</p>

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">AI usage and cost</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="30-day cost"
          value={`$${stats.total_cost_30d.toFixed(4)}`}
        />
        <StatCard
          label="30-day tokens"
          value={stats.total_tokens_30d}
        />
      </div>
    </div>
  )
}
