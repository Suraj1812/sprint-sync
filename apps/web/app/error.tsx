"use client"

import { useEffect } from "react"

import { Button } from "@sprint-sync/ui"

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // TODO: report to Sentry in production.
    // eslint-disable-next-line no-console
    console.error(error)
  }, [error])

  return (
    <main className="container flex min-h-screen flex-col items-center justify-center text-center">
      <h1 className="text-3xl font-bold">Something went wrong</h1>
      <p className="mt-4 text-muted-foreground">
        We are sorry, but an unexpected error occurred. Please try again.
      </p>
      {error.digest && (
        <p className="mt-2 text-xs text-muted-foreground">
          Error digest: {error.digest}
        </p>
      )}
      <Button className="mt-6" onClick={reset}>
        Try again
      </Button>
    </main>
  )
}
