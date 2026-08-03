"use client"

import { useEffect, useState } from "react"

import { Button } from "@sprint-sync/ui"

import { adminApi } from "../lib/admin-api"
import { Organization } from "../lib/admin-types"
import { DataTable } from "../components/DataTable"

export default function AdminTenancyPage() {
  const [orgs, setOrgs] = useState<Organization[]>([])

  useEffect(() => {
    adminApi.listOrganizations().then((res) => setOrgs(res || []))
  }, [])

  async function suspend(id: string) {
    await adminApi.suspendOrganization(id)
    await adminApi.listOrganizations().then((res) => setOrgs(res || []))
  }

  const columns = [
    { header: "Name", cell: (o: Organization) => o.name },
    { header: "Slug", cell: (o: Organization) => o.slug },
    { header: "Active", cell: (o: Organization) => (o.is_active ? "Yes" : "No") },
    { header: "Billing", cell: (o: Organization) => o.billing_email || "—" },
    { header: "Created", cell: (o: Organization) => o.created_at.slice(0, 10) },
    {
      header: "Actions",
      cell: (o: Organization) => (
        <Button size="sm" variant="destructive" onClick={() => suspend(o.id)}>
          Suspend
        </Button>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Tenancy</h1>
      <DataTable
        columns={columns}
        rows={orgs}
        keyExtractor={(o) => o.id}
        caption="Organizations"
      />
    </div>
  )
}
