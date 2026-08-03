"use client"

import { useEffect, useState } from "react"

import { Badge } from "@sprint-sync/ui"

import { adminApi } from "../../lib/admin-api"
import { InvitationAdmin } from "../../lib/admin-types"
import { DataTable } from "../../components/DataTable"

export default function AdminInvitationsPage() {
  const [invitations, setInvitations] = useState<InvitationAdmin[]>([])

  useEffect(() => {
    adminApi.listInvitations().then((res) => setInvitations(res || []))
  }, [])

  const columns = [
    { header: "Email", cell: (i: InvitationAdmin) => i.email },
    { header: "Role", cell: (i: InvitationAdmin) => i.role },
    { header: "Status", cell: (i: InvitationAdmin) => (
      <Badge variant={i.accepted_at ? "default" : i.rejected_at ? "secondary" : "outline"}>
        {i.accepted_at ? "Accepted" : i.rejected_at ? "Rejected" : "Pending"}
      </Badge>
    )},
    { header: "Organization", cell: (i: InvitationAdmin) => i.organization_id.slice(0, 8) },
    { header: "Expires", cell: (i: InvitationAdmin) => i.expires_at.slice(0, 10) },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Invitations</h1>
      <DataTable
        columns={columns}
        rows={invitations}
        keyExtractor={(i) => i.id}
        caption="Invitations"
      />
    </div>
  )
}
