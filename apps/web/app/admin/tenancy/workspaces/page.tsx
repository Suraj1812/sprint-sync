"use client"

import { useEffect, useState } from "react"

import { adminApi } from "../../lib/admin-api"
import { WorkspaceAdmin } from "../../lib/admin-types"
import { DataTable } from "../../components/DataTable"

export default function AdminWorkspacesPage() {
  const [workspaces, setWorkspaces] = useState<WorkspaceAdmin[]>([])

  useEffect(() => {
    adminApi.listWorkspaces().then((res) => setWorkspaces(res || []))
  }, [])

  const columns = [
    { header: "Name", cell: (w: WorkspaceAdmin) => w.name },
    { header: "Slug", cell: (w: WorkspaceAdmin) => w.slug },
    { header: "Organization", cell: (w: WorkspaceAdmin) => w.organization_id.slice(0, 8) },
    { header: "Archived", cell: (w: WorkspaceAdmin) => (w.is_archived ? "Yes" : "No") },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Workspaces</h1>
      <DataTable
        columns={columns}
        rows={workspaces}
        keyExtractor={(w) => w.id}
        caption="Workspaces"
      />
    </div>
  )
}
