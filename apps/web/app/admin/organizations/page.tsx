"use client"

import { useEffect, useState } from "react"

import { Badge, Button, Input, Label } from "@sprint-sync/ui"

import { adminApi } from "../lib/admin-api"
import { DataTable } from "../components/DataTable"

interface Organization {
  id: string
  name: string
  slug: string
  owner_id: string
  is_active: boolean
}

export default function AdminOrganizationsPage() {
  const [orgs, setOrgs] = useState<Organization[]>([])
  const [name, setName] = useState("")
  const [slug, setSlug] = useState("")
  const [ownerId, setOwnerId] = useState("")

  async function load() {
    const res = await adminApi.organizations()
    setOrgs(res || [])
  }

  useEffect(() => {
    load()
  }, [])

  async function create(e: React.FormEvent) {
    e.preventDefault()
    await adminApi.createOrganization({
      name,
      slug,
      owner_id: ownerId,
    })
    setName("")
    setSlug("")
    setOwnerId("")
    await load()
  }

  const columns = [
    { header: "Name", cell: (o: Organization) => o.name },
    { header: "Slug", cell: (o: Organization) => o.slug },
    { header: "Owner", cell: (o: Organization) => o.owner_id },
    {
      header: "Status",
      cell: (o: Organization) => (
        <Badge variant={o.is_active ? "default" : "secondary"}>
          {o.is_active ? "Active" : "Disabled"}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Organizations</h1>
      <form
        onSubmit={create}
        className="flex max-w-xl flex-col gap-4 rounded-xl border border-border bg-surface p-4"
      >
        <div className="space-y-2">
          <Label htmlFor="org-name">Name</Label>
          <Input
            id="org-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="org-slug">Slug</Label>
          <Input
            id="org-slug"
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="org-owner">Owner user ID</Label>
          <Input
            id="org-owner"
            value={ownerId}
            onChange={(e) => setOwnerId(e.target.value)}
            required
          />
        </div>
        <Button type="submit">Create organization</Button>
      </form>
      <DataTable
        columns={columns}
        rows={orgs}
        keyExtractor={(o) => o.id}
        caption="Organizations"
      />
    </div>
  )
}
