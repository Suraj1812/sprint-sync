"use client"

import { useEffect, useState } from "react"

import { Badge } from "@sprint-sync/ui"

import { adminApi } from "../../lib/admin-api"
import { Provider } from "../../lib/admin-types"
import { DataTable } from "../../components/DataTable"

export default function AdminAIProvidersPage() {
  const [providers, setProviders] = useState<Provider[]>([])

  useEffect(() => {
    adminApi.listAIProviders().then((res) => setProviders(res || []))
  }, [])

  const columns = [
    { header: "Provider", cell: (p: Provider) => p.name },
    {
      header: "Status",
      cell: (p: Provider) => (
        <Badge variant={p.ok ? "default" : "secondary"}>
          {p.ok ? "Healthy" : "Unavailable"}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">AI providers</h1>
      <DataTable
        columns={columns}
        rows={providers}
        keyExtractor={(p) => p.name}
        caption="AI providers"
      />
    </div>
  )
}
