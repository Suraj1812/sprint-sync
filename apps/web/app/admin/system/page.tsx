"use client"

import { Button, Switch } from "@sprint-sync/ui"

export default function AdminSystemPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">System</h1>
      <div className="max-w-2xl space-y-4 rounded-xl border border-border bg-surface p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium">Maintenance mode</p>
            <p className="text-sm text-muted-foreground">
              Show a maintenance page to non-admin users.
            </p>
          </div>
          <Switch aria-label="Toggle maintenance mode" />
        </div>
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium">Public registrations</p>
            <p className="text-sm text-muted-foreground">
              Allow new user signups without admin approval.
            </p>
          </div>
          <Switch defaultChecked aria-label="Toggle public registrations" />
        </div>
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium">Verbose logging</p>
            <p className="text-sm text-muted-foreground">
              Increase backend log level for debugging.
            </p>
          </div>
          <Switch aria-label="Toggle verbose logging" />
        </div>
        <Button variant="outline" className="mt-4">
          Save system settings
        </Button>
      </div>
    </div>
  )
}
