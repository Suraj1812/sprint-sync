"use client"

import { useEffect, useState } from "react"

import { Button, Input, Label, Switch } from "@sprint-sync/ui"

import { adminApi } from "../lib/admin-api"
import { FeatureFlag } from "../lib/admin-types"
import { DataTable } from "../components/DataTable"

export default function AdminFeatureFlagsPage() {
  const [flags, setFlags] = useState<FeatureFlag[]>([])
  const [newKey, setNewKey] = useState("")
  const [newName, setNewName] = useState("")

  async function load() {
    const res = await adminApi.featureFlags()
    setFlags(res || [])
  }

  useEffect(() => {
    load()
  }, [])

  async function create(e: React.FormEvent) {
    e.preventDefault()
    await adminApi.createFeatureFlag({
      key: newKey,
      name: newName,
      enabled: false,
      environment: "production",
      rollout_percentage: 0,
    })
    setNewKey("")
    setNewName("")
    await load()
  }

  async function toggle(flag: FeatureFlag) {
    await adminApi.updateFeatureFlag(flag.id, { enabled: !flag.enabled })
    await load()
  }

  const columns = [
    { header: "Key", cell: (f: FeatureFlag) => f.key },
    { header: "Name", cell: (f: FeatureFlag) => f.name },
    { header: "Environment", cell: (f: FeatureFlag) => f.environment },
    {
      header: "Enabled",
      cell: (f: FeatureFlag) => (
        <Switch checked={f.enabled} onCheckedChange={() => toggle(f)} />
      ),
    },
    {
      header: "Rollout",
      cell: (f: FeatureFlag) => `${f.rollout_percentage}%`,
    },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Feature flags</h1>
      <form
        onSubmit={create}
        className="flex max-w-xl flex-col gap-4 rounded-xl border border-border bg-surface p-4"
      >
        <div className="space-y-2">
          <Label htmlFor="flag-key">Key</Label>
          <Input
            id="flag-key"
            value={newKey}
            onChange={(e) => setNewKey(e.target.value)}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="flag-name">Name</Label>
          <Input
            id="flag-name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            required
          />
        </div>
        <Button type="submit">Create feature flag</Button>
      </form>
      <DataTable
        columns={columns}
        rows={flags}
        keyExtractor={(f) => f.id}
        caption="Feature flags"
      />
    </div>
  )
}
