"use client"

import { useActionState } from "react"

import { registerAction } from "@/actions/auth"
import { Button } from "@/components/ui/button"

export default function RegisterPage() {
  const [state, formAction, isPending] = useActionState(registerAction, {
    error: "",
  })

  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <form
        action={formAction}
        className="w-full max-w-sm space-y-6 rounded-2xl border border-slate-200 p-8 shadow-sm"
      >
        <h1 className="text-2xl font-semibold tracking-tight">
          Create account
        </h1>
        {state.error && (
          <div
            className="rounded-md bg-red-50 p-3 text-sm text-red-700"
            role="alert"
          >
            {state.error}
          </div>
        )}
        <div className="space-y-2">
          <label htmlFor="fullName" className="block text-sm font-medium">
            Full name
          </label>
          <input
            id="fullName"
            name="fullName"
            type="text"
            autoComplete="name"
            maxLength={255}
            className="w-full rounded-md border border-slate-300 p-2.5 text-sm focus:border-slate-900 focus:outline-none"
          />
        </div>
        <div className="space-y-2">
          <label htmlFor="email" className="block text-sm font-medium">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            className="w-full rounded-md border border-slate-300 p-2.5 text-sm focus:border-slate-900 focus:outline-none"
          />
        </div>
        <div className="space-y-2">
          <label htmlFor="password" className="block text-sm font-medium">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="new-password"
            minLength={12}
            required
            className="w-full rounded-md border border-slate-300 p-2.5 text-sm focus:border-slate-900 focus:outline-none"
          />
        </div>
        <Button
          type="submit"
          className="w-full"
          disabled={isPending}
          aria-disabled={isPending}
        >
          {isPending ? "Creating account..." : "Create account"}
        </Button>
      </form>
    </main>
  )
}
