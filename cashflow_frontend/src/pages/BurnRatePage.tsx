import { useEffect, useMemo, useState } from 'react'
import { AlertTriangle, CalendarDays, PackageSearch, TrendingDown, type LucideIcon } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { type BurnRateData, api, formatNaira, getErrorMessage } from '@/lib/api'

const periodOptions = [7, 14, 30, 60, 90]

export default function BurnRatePage() {
  const [data, setData] = useState<BurnRateData | null>(null)
  const [days, setDays] = useState(30)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.burnRate(days)
      .then(setData)
      .catch((err: unknown) => setError(getErrorMessage(err, 'Could not load product burn rate.')))
  }, [days])

  const items = useMemo(() => data?.items ?? [], [data?.items])
  const fastestMoving = useMemo(() => {
    return [...items].sort((a, b) => Number(b.averageDailyConsumption) - Number(a.averageDailyConsumption))[0]
  }, [items])

  if (error) return <div className="p-6 text-sm text-red-700">{error}</div>

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900 md:text-3xl">Product Burn Rate</h1>
          <p className="mt-1 text-sm text-neutral-500">Track stock consumption patterns and likely stockout timing.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {periodOptions.map((option) => (
            <Button
              key={option}
              type="button"
              variant={days === option ? 'default' : 'outline'}
              size="sm"
              onClick={() => {
                setData(null)
                setError(null)
                setDays(option)
              }}
            >
              {option}d
            </Button>
          ))}
        </div>
      </div>

      {!data ? (
        <div className="p-2 text-sm text-neutral-500">Loading burn rate...</div>
      ) : (
        <>
          <div className="grid gap-3 md:grid-cols-4">
            <MetricCard title="Tracked Items" value={String(data.summary.trackedItems)} icon={PackageSearch} />
            <MetricCard title="Moving Items" value={String(data.summary.activeBurnItems)} icon={TrendingDown} />
            <MetricCard title="At Risk" value={String(data.summary.atRiskItems)} icon={AlertTriangle} />
            <MetricCard title="Consumed Value" value={formatNaira(data.summary.totalConsumedValue)} icon={CalendarDays} />
          </div>

          {fastestMoving && Number(fastestMoving.averageDailyConsumption) > 0 && (
            <div className="rounded-lg border border-orange-200 bg-orange-50 p-4 text-sm text-orange-900">
              <span className="font-semibold">{fastestMoving.name}</span> is moving fastest at {fastestMoving.averageDailyConsumption} {fastestMoving.unit}/day.
            </div>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Consumption Pattern</CardTitle>
              <CardDescription>
                {new Date(data.period.startDate).toLocaleDateString()} to {new Date(data.period.endDate).toLocaleDateString()}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {items.length === 0 ? (
                <p className="text-sm text-neutral-500">No tracked inventory yet.</p>
              ) : (
                items.map((item) => (
                  <div key={item.itemId} className="grid gap-3 rounded-lg border border-neutral-200 bg-white p-3 md:grid-cols-[1.5fr_1fr_1fr_1fr_auto] md:items-center">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="truncate text-sm font-semibold text-neutral-900">{item.name}</p>
                        <StatusBadge status={item.status} />
                      </div>
                      <p className="mt-1 text-xs text-neutral-500">
                        {item.currentQuantity} {item.unit} on hand, reorder at {item.reorderLevel}
                      </p>
                    </div>
                    <Field label="Consumed" value={`${item.consumedQuantity} ${item.unit}`} />
                    <Field label="Daily burn" value={`${item.averageDailyConsumption} ${item.unit}`} />
                    <Field
                      label="Stockout"
                      value={item.daysUntilStockout === null ? 'No movement' : `${item.daysUntilStockout} days`}
                    />
                    <div className="text-sm font-semibold text-neutral-900">{formatNaira(item.consumedValue)}</div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}

function MetricCard({ title, value, icon: Icon }: { title: string; value: string; icon: LucideIcon }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription className="flex items-center gap-2">
          <Icon className="h-4 w-4 text-orange-500" />
          {title}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-2xl font-bold text-neutral-900">{value}</p>
      </CardContent>
    </Card>
  )
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-neutral-500">{label}</p>
      <p className="mt-1 text-sm font-semibold text-neutral-900">{value}</p>
    </div>
  )
}

function StatusBadge({ status }: { status: BurnRateData['items'][number]['status'] }) {
  const label = {
    out: 'Out',
    at_risk: 'At risk',
    stable: 'Stable',
    no_data: 'No data',
  }[status]
  const className = {
    out: 'border-red-300 text-red-600',
    at_risk: 'border-orange-300 text-orange-600',
    stable: 'border-green-300 text-green-700',
    no_data: 'border-neutral-300 text-neutral-500',
  }[status]

  return <Badge variant="outline" className={className}>{label}</Badge>
}
