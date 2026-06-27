import { useEffect, useMemo, useState } from 'react'
import { AlertTriangle, CalendarDays, Gauge, PackageSearch, Target, TrendingDown, type LucideIcon } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { type BreakEvenData, type BurnRateData, api, formatNaira, getErrorMessage } from '@/lib/api'

const periodOptions = [7, 14, 30, 60, 90]
type PlanningView = 'burn-rate' | 'break-even'

export default function BurnRatePage() {
  const [burnRate, setBurnRate] = useState<BurnRateData | null>(null)
  const [breakEven, setBreakEven] = useState<BreakEvenData | null>(null)
  const [days, setDays] = useState(30)
  const [view, setView] = useState<PlanningView>('burn-rate')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([api.burnRate(days), api.breakEven(days)])
      .then(([burnRateData, breakEvenData]) => {
        setBurnRate(burnRateData)
        setBreakEven(breakEvenData)
      })
      .catch((err: unknown) => setError(getErrorMessage(err, 'Could not load planning data.')))
  }, [days])

  const items = useMemo(() => burnRate?.items ?? [], [burnRate?.items])
  const fastestMoving = useMemo(() => {
    return [...items].sort((a, b) => Number(b.averageDailyConsumption) - Number(a.averageDailyConsumption))[0]
  }, [items])

  if (error) return <div className="p-6 text-sm text-red-700">{error}</div>

  const isLoading = !burnRate || !breakEven

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900 md:text-3xl">Planning</h1>
          <p className="mt-1 text-sm text-neutral-500">Track inventory consumption and minimum viability thresholds.</p>
        </div>
        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          <div className="inline-flex w-fit rounded-lg border border-neutral-200 bg-white p-1">
            <Button type="button" variant={view === 'burn-rate' ? 'default' : 'ghost'} size="sm" onClick={() => setView('burn-rate')}>
              Burn rate
            </Button>
            <Button type="button" variant={view === 'break-even' ? 'default' : 'ghost'} size="sm" onClick={() => setView('break-even')}>
              Break-even
            </Button>
          </div>
          <div className="flex flex-wrap gap-2">
            {periodOptions.map((option) => (
              <Button
                key={option}
                type="button"
                variant={days === option ? 'default' : 'outline'}
                size="sm"
                onClick={() => {
                  setBurnRate(null)
                  setBreakEven(null)
                  setError(null)
                  setDays(option)
                }}
              >
                {option}d
              </Button>
            ))}
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="p-2 text-sm text-neutral-500">Loading planning data...</div>
      ) : view === 'burn-rate' ? (
        <BurnRateView data={burnRate} items={items} fastestMoving={fastestMoving} />
      ) : (
        <BreakEvenView data={breakEven} />
      )}
    </div>
  )
}

function BurnRateView({
  data,
  items,
  fastestMoving,
}: {
  data: BurnRateData
  items: BurnRateData['items']
  fastestMoving?: BurnRateData['items'][number]
}) {
  return (
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
          <CardDescription>{dateRange(data.period.startDate, data.period.endDate)}</CardDescription>
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
                <Field label="Stockout" value={item.daysUntilStockout === null ? 'No movement' : `${item.daysUntilStockout} days`} />
                <div className="text-sm font-semibold text-neutral-900">{formatNaira(item.consumedValue)}</div>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </>
  )
}

function BreakEvenView({ data }: { data: BreakEvenData }) {
  const summary = data.summary
  const breakEvenRevenue = Number(summary.breakEvenRevenue ?? 0)
  const actualRevenue = Number(summary.actualRevenue)
  const progress = breakEvenRevenue > 0 ? Math.min((actualRevenue / breakEvenRevenue) * 100, 100) : 100

  if (summary.status === 'no_data') {
    return (
      <div className="rounded-lg border border-orange-200 bg-orange-50 p-4 text-sm text-orange-900">
        <div className="flex gap-3">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
          <div>
            <p className="font-semibold">Break-even needs sales data first.</p>
            <p className="mt-1">Record sales with quantity and product cost, then add operating expenses such as rent, staff, utilities, or transport.</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <Button asChild size="sm"><Link to="/sales">Record sales</Link></Button>
              <Button asChild size="sm" variant="outline"><Link to="/expenses">Record expenses</Link></Button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <>
      <BreakEvenStatus data={data} />

      <div className="grid gap-3 md:grid-cols-4">
        <MetricCard title="Break-even Revenue" value={summary.breakEvenRevenue ? formatNaira(summary.breakEvenRevenue) : 'Unavailable'} icon={Target} />
        <MetricCard title="Break-even Units" value={summary.breakEvenUnits === null ? 'Unavailable' : String(summary.breakEvenUnits)} icon={Gauge} />
        <MetricCard title="Actual Revenue" value={formatNaira(summary.actualRevenue)} icon={CalendarDays} />
        <MetricCard title="Revenue Gap" value={formatNaira(summary.revenueGap)} icon={AlertTriangle} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Minimum Viability Threshold</CardTitle>
          <CardDescription>{dateRange(data.period.startDate, data.period.endDate)}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          <div>
            <div className="mb-2 flex items-center justify-between gap-3 text-sm">
              <span className="text-neutral-500">Revenue progress</span>
              <span className="font-semibold text-neutral-900">{Math.round(progress)}%</span>
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-neutral-100">
              <div className="h-full rounded-full bg-orange-500 transition-all" style={{ width: `${progress}%` }} />
            </div>
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <Row label="Fixed operating costs" value={formatNaira(summary.fixedCosts)} />
            <Row label="Variable product costs" value={formatNaira(summary.variableCosts)} />
            <Row label="Average selling price" value={formatNaira(summary.averageSellingPrice)} />
            <Row label="Average unit cost" value={formatNaira(summary.averageUnitVariableCost)} />
            <Row label="Contribution margin" value={formatNaira(summary.contributionMargin)} strong />
            <Row label="Contribution ratio" value={`${Math.round(Number(summary.contributionMarginRatio) * 100)}%`} strong />
          </div>
        </CardContent>
      </Card>
    </>
  )
}

function BreakEvenStatus({ data }: { data: BreakEvenData }) {
  const statusMap = {
    above_break_even: {
      title: 'Business is above break-even for this period.',
      body: 'Recorded revenue has covered the fixed operating cost threshold.',
      className: 'border-green-200 bg-green-50 text-green-800',
    },
    below_break_even: {
      title: 'Business is below break-even for this period.',
      body: `${formatNaira(data.summary.revenueGap)} more revenue or ${data.summary.unitsGap} more units are needed to reach minimum viability.`,
      className: 'border-orange-200 bg-orange-50 text-orange-900',
    },
    unviable: {
      title: 'Contribution margin is not viable yet.',
      body: 'Average product cost is equal to or higher than the selling price, so break-even cannot be reached without pricing or cost changes.',
      className: 'border-red-200 bg-red-50 text-red-800',
    },
    no_data: {
      title: 'Break-even needs sales data first.',
      body: 'Record sales and operating expenses to calculate the threshold.',
      className: 'border-neutral-200 bg-neutral-50 text-neutral-700',
    },
  }[data.summary.status]

  return (
    <div className={`rounded-lg border p-4 text-sm ${statusMap.className}`}>
      <p className="font-semibold">{statusMap.title}</p>
      <p className="mt-1">{statusMap.body}</p>
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

function Row({ label, value, strong = false }: { label: string; value: string; strong?: boolean }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-lg border border-neutral-200 bg-white p-3">
      <span className="text-neutral-500">{label}</span>
      <span className={strong ? 'font-bold text-neutral-900' : 'font-semibold text-neutral-800'}>{value}</span>
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

function dateRange(startDate: string, endDate: string) {
  return `${new Date(startDate).toLocaleDateString()} to ${new Date(endDate).toLocaleDateString()}`
}
