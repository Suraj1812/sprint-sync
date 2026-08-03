const BILLING_API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function apiFetch(path: string, options: RequestInit = {}) {
  const res = await fetch(`${BILLING_API}/api/v1${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(body || res.statusText)
  }
  if (res.status === 204) return null
  return res.json()
}

export const billingApi = {
  listPlans: () => apiFetch("/billing/plans"),
  getCustomer: () => apiFetch("/billing/customer"),
  createCheckout: (body: object) =>
    apiFetch("/billing/checkout", { method: "POST", body: JSON.stringify(body) }),
  createPortal: (body: object) =>
    apiFetch("/billing/portal", { method: "POST", body: JSON.stringify(body) }),
  listSubscriptions: () => apiFetch("/billing/subscriptions"),
  listInvoices: () => apiFetch("/billing/invoices"),
  getEntitlements: () => apiFetch("/billing/entitlements"),
}
