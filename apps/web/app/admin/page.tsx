"use client"

import { useEffect, useState } from "react"

import { adminApi } from "./lib/admin-api"
import { DashboardStats } from "./lib/admin-types"
import { StatCard } from "./components/StatCard"

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    adminApi
      .dashboard()
      .then((res) => setStats(res as DashboardStats))
      .catch((err) => setError(err.message))
  }, [])

  if (error) return <p className="text-destructive">{error}</p>
  if (!stats) return <p className="text-muted-foreground">Loading dashboard...</p>

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total users" value={stats.total_users} />
        <StatCard label="Active users" value={stats.active_users} />
        <StatCard
          label="New registrations (24h)"
          value={stats.new_registrations_24h}
        />
        <StatCard
          label="Failed logins (24h)"
          value={stats.failed_logins_24h}
          trend={stats.failed_logins_24h > 10 ? "Investigate" : "Normal"}
          trendUp={stats.failed_logins_24h > 10}
        />
        <StatCard label="Admin sessions" value={stats.admin_sessions} />
        <StatCard
          label="Pending feature flags"
          value={stats.pending_feature_flags}
        />
        <StatCard label="Uptime" value={stats.uptime} />
        <StatCard label="Version" value={stats.version} />
      </div>
    </div>
  )
}
