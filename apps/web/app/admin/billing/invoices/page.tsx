"use client"

import { useEffect, useState } from "react"

import { Badge } from "@sprint-sync/ui"

import { adminApi } from "../../lib/admin-api"
import { Invoice } from "../../lib/admin-types"
import { DataTable } from "../../components/DataTable"

export default function AdminInvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([])

  useEffect(() => {
    adminApi.listInvoices().then((res) => setInvoices(res || []))
  }, [])

  const columns = [
    { header: "Number", cell: (i: Invoice) => i.number || "—" },
    { header: "Status", cell: (i: Invoice) => (
      <Badge variant={i.status === "paid" ? "default" : "secondary"}>
        {i.status}
      </Badge>
    )},
    { header: "Total", cell: (i: Invoice) => `$${i.total.toFixed(2)}` },
    { header: "Paid", cell: (i: Invoice) => `$${i.paid.toFixed(2)}` },
    { header: "Created", cell: (i: Invoice) => i.created_at.slice(0, 10) },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Invoices</h1>
      <DataTable
        columns={columns}
        rows={invoices}
        keyExtractor={(i) => i.id}
        caption="Invoices"
      />
    </div>
  )
}
