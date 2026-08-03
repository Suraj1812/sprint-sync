"use client"

import { useEffect, useState } from "react"

import { Button, Input, Label, Textarea } from "@sprint-sync/ui"

import { adminApi } from "../../lib/admin-api"
import { Prompt } from "../../lib/admin-types"
import { DataTable } from "../../components/DataTable"

export default function AdminPromptsPage() {
  const [prompts, setPrompts] = useState<Prompt[]>([])
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [system, setSystem] = useState("")
  const [userTemplate, setUserTemplate] = useState("")
  const [variables, setVariables] = useState("")

  async function load() {
    const res = await adminApi.listPrompts()
    setPrompts(res || [])
  }

  useEffect(() => {
    load()
  }, [])

  async function create(e: React.FormEvent) {
    e.preventDefault()
    await adminApi.createPrompt({
      name,
      description,
      system,
      user_template: userTemplate,
      variables: variables.split(",").map((v) => v.trim()).filter(Boolean),
    })
    setName("")
    setDescription("")
    setSystem("")
    setUserTemplate("")
    setVariables("")
    await load()
  }

  const columns = [
    { header: "Name", cell: (p: Prompt) => p.name },
    { header: "Description", cell: (p: Prompt) => p.description || "—" },
    { header: "Active", cell: (p: Prompt) => (p.is_active ? "Yes" : "No") },
    { header: "Variables", cell: (p: Prompt) => p.variables.join(", ") },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Prompts</h1>
      <form
        onSubmit={create}
        className="flex max-w-xl flex-col gap-4 rounded-xl border border-border bg-surface p-4"
      >
        <div className="space-y-2">
          <Label htmlFor="prompt-name">Name</Label>
          <Input
            id="prompt-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="prompt-description">Description</Label>
          <Input
            id="prompt-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="prompt-system">System message</Label>
          <Textarea
            id="prompt-system"
            value={system}
            onChange={(e) => setSystem(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="prompt-template">User template</Label>
          <Textarea
            id="prompt-template"
            value={userTemplate}
            onChange={(e) => setUserTemplate(e.target.value)}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="prompt-variables">Variables (comma separated)</Label>
          <Input
            id="prompt-variables"
            value={variables}
            onChange={(e) => setVariables(e.target.value)}
          />
        </div>
        <Button type="submit">Create prompt</Button>
      </form>
      <DataTable
        columns={columns}
        rows={prompts}
        keyExtractor={(p) => p.id}
        caption="Prompts"
      />
    </div>
  )
}
