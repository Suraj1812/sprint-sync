"use client"

import { useEffect, useState } from "react"

import { Button, Input, Textarea } from "@sprint-sync/ui"

import { adminApi } from "../../lib/admin-api"
import { OAuthClient } from "../../lib/admin-types"
import { DataTable } from "../../components/DataTable"

export default function AdminOAuthPage() {
  const [clients, setClients] = useState<OAuthClient[]>([])
  const [name, setName] = useState("")
  const [uris, setUris] = useState("http://localhost:3000/callback")
  const [scopes, setScopes] = useState("read")
  const [newSecret, setNewSecret] = useState<string | null>(null)

  useEffect(() => {
    adminApi.listOAuthClients().then((res) => setClients(res || []))
  }, [])

  async function create() {
    const res = await adminApi.createOAuthClient({
      name,
      redirect_uris: uris.split(",").map((u) => u.trim()),
      allowed_scopes: scopes.split(",").map((s) => s.trim()),
    })
    setNewSecret(res.client_secret)
    const list = await adminApi.listOAuthClients()
    setClients(list || [])
  }

  const columns = [
    { header: "Name", cell: (c: OAuthClient) => c.name },
    { header: "Client ID", cell: (c: OAuthClient) => c.client_id },
    { header: "Active", cell: (c: OAuthClient) => (c.is_active ? "Yes" : "No") },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">OAuth Clients</h1>
      {newSecret && (
        <div className="rounded border p-4">
          <p className="font-medium">Copy the client secret now — it will not be shown again.</p>
          <code className="block mt-2 break-all">{newSecret}</code>
        </div>
      )}
      <div className="grid gap-4 max-w-md">
        <Input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
        <Textarea label="Redirect URIs" value={uris} onChange={(e) => setUris(e.target.value)} />
        <Input placeholder="Allowed scopes" value={scopes} onChange={(e) => setScopes(e.target.value)} />
        <Button onClick={create}>Register client</Button>
      </div>
      <DataTable columns={columns} rows={clients} keyExtractor={(c) => c.id} caption="OAuth clients" />
    </div>
  )
}
