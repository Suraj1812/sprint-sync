"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"

import { Button, Input, Textarea } from "@sprint-sync/ui"

import { adminApi } from "../../../lib/admin-api"

export default function NewTemplatePage() {
  const router = useRouter()
  const [name, setName] = useState("")
  const [subject, setSubject] = useState("")
  const [html, setHtml] = useState("")
  const [text, setText] = useState("")
  const [variables, setVariables] = useState("")
  const [preview, setPreview] = useState<{ subject: string; html: string | null } | null>(null)

  async function previewTemplate() {
    const result = await adminApi.previewEmailTemplate({
      name,
      variables: Object.fromEntries(
        variables.split(",").map((v) => [v.trim(), `{{ ${v.trim()} }}`]).filter(([k]) => k)
      ),
      locale: "en",
    })
    setPreview(result)
  }

  async function save() {
    await adminApi.createEmailTemplate({
      name,
      subject,
      html_body: html,
      text_body: text,
      variables: variables.split(",").map((v) => v.trim()).filter(Boolean),
    })
    router.push("/admin/communications/templates")
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <h1 className="text-2xl font-semibold">New Email Template</h1>
      <div className="space-y-4">
        <Input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
        <Input placeholder="Subject" value={subject} onChange={(e) => setSubject(e.target.value)} />
        <Textarea placeholder="HTML body" value={html} onChange={(e) => setHtml(e.target.value)} />
        <Textarea placeholder="Text body" value={text} onChange={(e) => setText(e.target.value)} />
        <Input
          placeholder="Variables (comma-separated)"
          value={variables}
          onChange={(e) => setVariables(e.target.value)}
        />
        <div className="flex gap-2">
          <Button onClick={previewTemplate} variant="secondary">Preview</Button>
          <Button onClick={save}>Save</Button>
        </div>
        {preview && (
          <div className="rounded border p-4 space-y-2">
            <p><strong>Subject:</strong> {preview.subject}</p>
            {preview.html && <div dangerouslySetInnerHTML={{ __html: preview.html }} />}
          </div>
        )}
      </div>
    </div>
  )
}
