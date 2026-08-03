"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

import { Button, Input, Textarea } from "@sprint-sync/ui"

import { adminApi } from "../../lib/admin-api"
import { Workflow } from "../../lib/admin-types"
import { DataTable } from "../../components/DataTable"

export default function AdminWorkflowsPage() {
  const router = useRouter()
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [name, setName] = useState("")
  const [trigger, setTrigger] = useState('{"event": "user.registered"}')
  const [steps, setSteps] = useState('[{"action": "emit_domain_event", "config": {"event_type": "welcome.user"}}]')

  useEffect(() => {
    adminApi.listWorkflows().then((res) => setWorkflows(res || []))
  }, [])

  async function save() {
    await adminApi.createWorkflow({
      name,
      trigger: JSON.parse(trigger),
      steps: JSON.parse(steps),
    })
    const res = await adminApi.listWorkflows()
    setWorkflows(res || [])
  }

  const columns = [
    { header: "Name", cell: (w: Workflow) => w.name },
    { header: "Trigger", cell: (w: Workflow) => JSON.stringify(w.trigger) },
    { header: "Active", cell: (w: Workflow) => (w.is_active ? "Yes" : "No") },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Workflows</h1>
      <div className="grid gap-4 max-w-2xl">
        <Input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
        <Textarea label="Trigger" value={trigger} onChange={(e) => setTrigger(e.target.value)} />
        <Textarea label="Steps" value={steps} onChange={(e) => setSteps(e.target.value)} />
        <Button onClick={save}>Create workflow</Button>
      </div>
      <DataTable
        columns={columns}
        rows={workflows}
        keyExtractor={(w) => w.id}
        caption="Workflows"
      />
    </div>
  )
}
