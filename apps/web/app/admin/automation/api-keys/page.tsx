"use client"

import { useEffect, useState } from "react"

import { Button, Input } from "@sprint-sync/ui"

import { adminApi } from "../../lib/admin-api"
import { ApiKey } from "../../lib/admin-types"
import { DataTable } from "../../components/DataTable"

export default function AdminApiKeysPage() {
  const [keys, setKeys] = useState<ApiKey[]>([])
  const [name, setName] = useState("")
  const [scopes, setScopes] = useState("*")
  const [newKey, setNewKey] = useState<string | null>(null)

  useEffect(() => {
    adminApi.listApiKeys().then((res) => setKeys(res || []))
  }, [])

  async function create() {
    const res = await adminApi.createApiKey({
      name,
      scopes: scopes.split(",").map((s) => s.trim()),
    })
    setNewKey(res.key)
    const list = await adminApi.listApiKeys()
    setKeys(list || [])
  }

  async function revoke(id: string) {
    await adminApi.revokeApiKey(id)
    const list = await adminApi.listApiKeys()
    setKeys(list || [])
  }

  const columns = [
    { header: "Name", cell: (k: ApiKey) => k.name },
    { header: "Preview", cell: (k: ApiKey) => k.key_preview },
    { header: "Scopes", cell: (k: ApiKey) => k.scopes.join(", ") },
    { header: "Usage", cell: (k: ApiKey) => k.usage_count },
    {
      header: "Actions",
      cell: (k: ApiKey) => (
        <Button size="sm" variant="destructive" onClick={() => revoke(k.id)}>
          Revoke
        </Button>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">API Keys</h1>
      {newKey && (
        <div className="rounded border p-4">
          <p className="font-medium">Copy this key now — it will not be shown again.</p>
          <code className="block mt-2 break-all">{newKey}</code>
        </div>
      )}
      <div className="grid gap-4 max-w-md">
        <Input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
        <Input placeholder="Scopes" value={scopes} onChange={(e) => setScopes(e.target.value)} />
        <Button onClick={create}>Create key</Button>
      </div>
      <DataTable columns={columns} rows={keys} keyExtractor={(k) => k.id} caption="API keys" />
    </div>
  )
}
