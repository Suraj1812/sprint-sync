"use client"

import { useEffect, useState } from "react"

import { Button } from "@sprint-sync/ui"

import { billingApi } from "./lib/billing-api"

interface Plan {
  id: string
  name: string
  description: string | null
  is_enterprise: boolean
}

interface Entitlement {
  feature: string
  limit: number | null
}

export default function BillingPage() {
  const [plans, setPlans] = useState<Plan[]>([])
  const [entitlements, setEntitlements] = useState<Entitlement[]>([])
  const [subscriptions, setSubscriptions] = useState<[]>([])
  const [invoices, setInvoices] = useState<[]>([])

  useEffect(() => {
    billingApi.listPlans().then(setPlans)
    billingApi.getEntitlements().then(setEntitlements)
    billingApi.listSubscriptions().then(setSubscriptions)
    billingApi.listInvoices().then(setInvoices)
  }, [])

  async function upgrade(plan: Plan) {
    const res = await billingApi.createCheckout({
      price_id: plan.id,
      success_url: `${window.location.origin}/billing/success`,
      cancel_url: `${window.location.origin}/billing/cancel`,
    })
    window.location.href = res.url
  }

  async function openPortal() {
    const res = await billingApi.createPortal({
      return_url: window.location.href,
    })
    window.location.href = res.url
  }

  return (
    <div className="container mx-auto max-w-4xl space-y-8 py-8">
      <h1 className="text-2xl font-semibold">Billing</h1>
      <div className="space-y-4">
        <h2 className="text-lg font-medium">Your entitlements</h2>
        <ul className="rounded-xl border border-border bg-surface p-4">
          {entitlements.map((e) => (
            <li key={e.feature} className="flex justify-between py-1">
              <span className="capitalize">{e.feature}</span>
              <span className="text-muted-foreground">
                {e.limit ?? "Unlimited"}
              </span>
            </li>
          ))}
        </ul>
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-medium">Plans</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className="rounded-xl border border-border bg-surface p-4"
            >
              <p className="font-medium">{plan.name}</p>
              <p className="text-sm text-muted-foreground">
                {plan.description}
              </p>
              <Button
                size="sm"
                className="mt-3"
                onClick={() => upgrade(plan)}
                disabled={plan.is_enterprise}
              >
                {plan.is_enterprise ? "Contact sales" : "Subscribe"}
              </Button>
            </div>
          ))}
        </div>
      </div>

      <Button variant="outline" onClick={openPortal}>
        Manage payment methods
      </Button>
    </div>
  )
}
