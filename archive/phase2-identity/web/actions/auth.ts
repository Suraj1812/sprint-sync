"use server"

import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { z } from "zod"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

const loginSchema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(12, "Password must be at least 12 characters"),
})

const registerSchema = loginSchema.extend({
  fullName: z.string().max(255).optional(),
})

type TokenResponse = {
  access_token: string
  refresh_token: string
  token_type: string
}

async function setAuthCookies(tokens: TokenResponse) {
  const cookieStore = await cookies()
  const isProduction = process.env.NODE_ENV === "production"

  cookieStore.set("access_token", tokens.access_token, {
    httpOnly: true,
    secure: isProduction,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 15,
  })
  cookieStore.set("refresh_token", tokens.refresh_token, {
    httpOnly: true,
    secure: isProduction,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  })
}

export async function loginAction(
  _prevState: unknown,
  formData: FormData,
): Promise<{ error?: string }> {
  const data = Object.fromEntries(formData)
  const parsed = loginSchema.safeParse(data)
  if (!parsed.success) {
    return { error: parsed.error.errors[0].message }
  }

  const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(parsed.data),
  })
  if (!res.ok) {
    return { error: "Invalid credentials" }
  }
  const tokens: TokenResponse = await res.json()
  await setAuthCookies(tokens)
  redirect("/dashboard")
}

export async function registerAction(
  _prevState: unknown,
  formData: FormData,
): Promise<{ error?: string }> {
  const data = Object.fromEntries(formData)
  const parsed = registerSchema.safeParse(data)
  if (!parsed.success) {
    return { error: parsed.error.errors[0].message }
  }

  const res = await fetch(`${API_BASE}/api/v1/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: parsed.data.email,
      password: parsed.data.password,
      full_name: parsed.data.fullName || undefined,
    }),
  })
  if (!res.ok) {
    return { error: "Registration failed" }
  }
  const tokens: TokenResponse = await res.json()
  await setAuthCookies(tokens)
  redirect("/dashboard")
}
