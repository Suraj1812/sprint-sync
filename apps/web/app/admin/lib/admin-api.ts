"use client"

const ADMIN_API = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/admin`

function getToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem("admin_token")
}

async function adminFetch(path: string, options: RequestInit = {}) {
  const token = getToken()
  const res = await fetch(`${ADMIN_API}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...options,
  })

  if (res.status === 401) {
    window.location.href = "/admin/login"
    return null
  }

  if (!res.ok) {
    throw new Error(`Admin API error: ${res.status}`)
  }

  return res.json()
}

export const adminApi = {
  dashboard: () => adminFetch("/dashboard"),
  users: (params: Record<string, string> = {}) =>
    adminFetch(`/users?${new URLSearchParams(params)}`),
  updateUser: (userId: string, body: object) =>
    adminFetch(`/users/${userId}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  resetPassword: (userId: string) =>
    adminFetch(`/users/${userId}/reset-password`, { method: "POST" }),
  featureFlags: () => adminFetch("/feature-flags"),
  createFeatureFlag: (body: object) =>
    adminFetch("/feature-flags", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  updateFeatureFlag: (id: string, body: object) =>
    adminFetch(`/feature-flags/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  audit: (params: Record<string, string> = {}) =>
    adminFetch(`/audit-logs?${new URLSearchParams(params)}`),
  organizations: () => adminFetch("/organizations"),
  createOrganization: (body: object) =>
    adminFetch("/organizations", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  login: async (body: object) => {
    const res = await adminFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
    })
    if (res?.access_token && typeof window !== "undefined") {
      localStorage.setItem("admin_token", res.access_token)
    }
    return res
  },
  logout: async () => {
    const res = await adminFetch("/auth/logout", { method: "POST" })
    if (typeof window !== "undefined") {
      localStorage.removeItem("admin_token")
    }
    return res
  },
  aiChat: (body: object) =>
    adminFetch("/ai/chat", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  createPrompt: (body: object) =>
    adminFetch("/ai/prompts", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  listPrompts: (skip = 0, limit = 50) =>
    adminFetch(`/ai/prompts?skip=${skip}&limit=${limit}`),
  ingestDocument: (body: object) =>
    adminFetch("/ai/documents", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  searchDocuments: (body: object) =>
    adminFetch("/ai/documents/search", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  aiUsage: () => adminFetch("/ai/usage"),
  listAIProviders: () => adminFetch("/ai/providers"),
  listPlans: (skip = 0, limit = 50) =>
    adminFetch(`/billing/plans?skip=${skip}&limit=${limit}`),
  getPlan: (id: string) => adminFetch(`/billing/plans/${id}`),
  listSubscriptions: () => adminFetch("/billing/admin/subscriptions"),
  listInvoices: () => adminFetch("/billing/admin/invoices"),
  listBillingEvents: () => adminFetch("/billing/admin/events"),
  billingMetrics: () => adminFetch("/billing/admin/metrics"),
  createCheckout: (body: object) =>
    adminFetch("/billing/checkout", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  createPortal: (body: object) =>
    adminFetch("/billing/portal", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  listOrganizations: () => adminFetch("/tenancy/admin/organizations"),
  listWorkspaces: () => adminFetch("/tenancy/admin/workspaces"),
  listInvitations: () => adminFetch("/tenancy/admin/invitations"),
  suspendOrganization: (id: string) =>
    adminFetch(`/tenancy/admin/organizations/${id}/suspend`, { method: "POST" }),
  listEmailTemplates: () => adminFetch("/communications/admin/templates"),
  createEmailTemplate: (body: object) =>
    adminFetch("/communications/admin/templates", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  previewEmailTemplate: (body: object) =>
    adminFetch("/communications/admin/templates/preview", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  communicationStats: () => adminFetch("/communications/admin/stats"),
  listWorkflows: () => adminFetch("/automation/workflows"),
  createWorkflow: (body: object) =>
    adminFetch("/automation/workflows", { method: "POST", body: JSON.stringify(body) }),
  listApiKeys: () => adminFetch("/automation/api-keys"),
  createApiKey: (body: object) =>
    adminFetch("/automation/api-keys", { method: "POST", body: JSON.stringify(body) }),
  revokeApiKey: (id: string) =>
    adminFetch(`/automation/api-keys/${id}/revoke`, { method: "POST" }),
  listOAuthClients: () => adminFetch("/automation/oauth/clients"),
  createOAuthClient: (body: object) =>
    adminFetch("/automation/oauth/clients", { method: "POST", body: JSON.stringify(body) }),
  listEvents: () => adminFetch("/automation/events"),
}
