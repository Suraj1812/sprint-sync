"use client"

import { useState } from "react"

import { Button, Input, Label, Textarea } from "@sprint-sync/ui"

import { adminApi } from "../../lib/admin-api"
import { SearchResult } from "../../lib/admin-types"
import { DataTable } from "../../components/DataTable"

export default function AdminAIDocumentsPage() {
  const [title, setTitle] = useState("")
  const [source, setSource] = useState("")
  const [text, setText] = useState("")
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<SearchResult[]>([])

  async function ingest(e: React.FormEvent) {
    e.preventDefault()
    await adminApi.ingestDocument({ title, source, text })
    setTitle("")
    setSource("")
    setText("")
  }

  async function search(e: React.FormEvent) {
    e.preventDefault()
    const res = await adminApi.searchDocuments({ query, top_k: 5 })
    setResults(res || [])
  }

  const columns = [
    { header: "ID", cell: (r: SearchResult) => r.id.slice(0, 8) },
    { header: "Content", cell: (r: SearchResult) => r.content.slice(0, 120) },
    { header: "Score", cell: (r: SearchResult) => r.score.toFixed(3) },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">RAG documents</h1>
      <form
        onSubmit={ingest}
        className="flex max-w-xl flex-col gap-4 rounded-xl border border-border bg-surface p-4"
      >
        <div className="space-y-2">
          <Label htmlFor="doc-title">Title</Label>
          <Input
            id="doc-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="doc-source">Source</Label>
          <Input
            id="doc-source"
            value={source}
            onChange={(e) => setSource(e.target.value)}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="doc-text">Text</Label>
          <Textarea
            id="doc-text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={6}
            required
          />
        </div>
        <Button type="submit">Ingest document</Button>
      </form>

      <form
        onSubmit={search}
        className="flex max-w-xl flex-col gap-4 rounded-xl border border-border bg-surface p-4"
      >
        <div className="space-y-2">
          <Label htmlFor="search-query">Semantic search</Label>
          <Input
            id="search-query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            required
          />
        </div>
        <Button type="submit">Search</Button>
      </form>

      <DataTable
        columns={columns}
        rows={results}
        keyExtractor={(r) => r.id}
        caption="Search results"
      />
    </div>
  )
}
