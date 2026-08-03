"use client"

import { useEffect, useState } from "react"

import { Badge, Button, Input } from "@sprint-sync/ui"

import { adminApi } from "../lib/admin-api"
import { AdminUser } from "../lib/admin-types"
import { DataTable } from "../components/DataTable"

export default function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [q, setQ] = useState("")
  const [loading, setLoading] = useState(false)

  async function load() {
    setLoading(true)
    const res = await adminApi.users(q ? { q } : {})
    setUsers(res?.data || [])
    setLoading(false)
  }

  useEffect(() => {
    load()
  }, [])

  async function toggleActive(user: AdminUser) {
    await adminApi.updateUser(user.id, { is_active: !user.is_active })
    await load()
  }

  async function handleReset(user: AdminUser) {
    const res = await adminApi.resetPassword(user.id)
    if (res?.data?.temp_password) {
      // eslint-disable-next-line no-alert
      alert(`Temporary password: ${res.data.temp_password}`)
    }
  }

  const columns = [
    { header: "Email", cell: (u: AdminUser) => u.email },
    {
      header: "Name",
      cell: (u: AdminUser) => `${u.first_name || ""} ${u.last_name || ""}`.trim() || "—",
    },
    { header: "Role", cell: (u: AdminUser) => u.role },
    {
      header: "Status",
      cell: (u: AdminUser) => (
        <Badge variant={u.is_active ? "default" : "secondary"}>
          {u.is_active ? "Active" : "Suspended"}
        </Badge>
      ),
    },
    {
      header: "Verified",
      cell: (u: AdminUser) => (u.email_verified ? "Yes" : "No"),
    },
    {
      header: "Actions",
      cell: (u: AdminUser) => (
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => toggleActive(u)}>
            {u.is_active ? "Suspend" : "Activate"}
          </Button>
          <Button size="sm" variant="outline" onClick={() => handleReset(u)}>
            Reset password
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Users</h1>
      <div className="flex max-w-md gap-2">
        <Input
          type="search"
          placeholder="Search users..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && load()}
          aria-label="Search users"
        />
        <Button onClick={load} disabled={loading}>
          Search
        </Button>
      </div>
      <DataTable
        columns={columns}
        rows={users}
        keyExtractor={(u) => u.id}
        caption="Admin user list"
      />
    </div>
  )
}
