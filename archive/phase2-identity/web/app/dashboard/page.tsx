import { redirect } from "next/navigation"

import { api } from "@/lib/api"

type MeResponse = {
  id: string
  email: string
  full_name: string | null
  role: string
}

export default async function DashboardPage() {
  let user: MeResponse
  try {
    user = await api<MeResponse>("/api/v1/auth/me")
  } catch {
    redirect("/login")
  }

  return (
    <main className="p-8">
      <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
      <p className="mt-2 text-slate-600">
        Welcome, {user.email}. Role: {user.role}
      </p>
    </main>
  )
}
