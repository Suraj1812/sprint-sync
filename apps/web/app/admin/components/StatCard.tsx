interface StatCardProps {
  label: string
  value: string | number
  trend?: string
  trendUp?: boolean
}

export function StatCard({ label, value, trend, trendUp }: StatCardProps) {
  return (
    <div className="rounded-xl border border-border bg-surface p-4 shadow-sm">
      <p className="text-sm text-muted-foreground">{label}</p>
      <div className="mt-2 flex items-end justify-between">
        <p className="text-3xl font-semibold tracking-tight">{value}</p>
        {trend && (
          <span
            className={`text-sm font-medium ${
              trendUp ? "text-green-600" : "text-red-600"
            }`}
          >
            {trend}
          </span>
        )}
      </div>
    </div>
  )
}
