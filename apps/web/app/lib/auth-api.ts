"use client"

const AUTH_API = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth`

function getToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem("access_token")
}

async function authFetch(path: string, options: RequestInit = {}) {
  const token = getToken()
  const res = await fetch(`${AUTH_API}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...options,
  })

  if (!res.ok) {
    const data = await res.json().catch(() => ({ message: `Error ${res.status}` }))
    throw new Error(data.detail?.[0]?.msg || data.message || `Auth error: ${res.status}`)
  }

  return res.json()
}

export const authApi = {
  getToken,
  setToken: (token: string) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("access_token", token)
    }
  },
  removeToken: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token")
    }
  },
  login: (body: { email: string; password: string }) =>
    authFetch("/login", { method: "POST", body: JSON.stringify(body) }),
  register: (body: {
    email: string
    password: string
    first_name: string
    last_name: string
  }) => authFetch("/register", { method: "POST", body: JSON.stringify(body) }),
  logout: () => authFetch("/logout", { method: "POST", body: JSON.stringify({}) }),
  me: () => authFetch("/me"),
}
