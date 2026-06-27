import { useEffect, useMemo, useState } from 'react'
import { Activity, ArrowDownRight, ArrowUpRight, BarChart3, Minus, TrendingUp, type LucideIcon } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { type DashboardData, type TrendData, type TrendDay, type TrendMetric, api, formatNaira, getErrorMessage } from '@/lib/api'

export default function ReportsPage() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null)
  const [trends, setTrends] = useState<TrendData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([api.dashboard(), api.trends()])
      .then(([dashboardData, trendData]) => {
        setDashboard(dashboardData)
        setTrends(trendData)
      })
      .catch((err: unknown) => setError(getErrorMessage(err, 'Could not load reports.')))
  }, [])

  const chartMax = useMemo(() => {
    if (!trends) return 1
    return Math.max(
      1,
      ...trends.daily.flatMap((day) => [
        Number(day.sales),
        Number(day.expenses),
        Math.abs(Number(day.netProfit)),
      ]),
    )
  }, [trends])

  if (error) return <div className="p-6 text-sm text-red-700">{error}</div>
  if (!dashboard || !trends) return <div className="p-6 text-sm text-neutral-500">Loading reports...</div>

  const taxableEstimate = Math.max(Number(dashboard.summary.netProfit), 0) * 0.1

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 md:text-3xl">Growth Trends</h1>
        <p className="mt-1 text-sm text-neutral-500">
          Weekly growth, trading direction, and sales patterns for {dashboard.user.businessName}.
        </p>
      </div>

      {dashboard.summary.capitalEroded && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Equity is below the protected capital floor. Avoid withdrawals until profit recovers.
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <TrendCard title="Sales Growth" metric={trends.summary.sales} icon={TrendingUp} />
        <TrendCard title="Expense Trend" metric={trends.summary.expenses} icon={BarChart3} invertGood />
        <TrendCard title="Profit Growth" metric={trends.summary.netProfit} icon={Activity} />
        <ReportCard title="Tax Set-Aside" value={formatNaira(taxableEstimate)} description="Conservative 10% profit reserve" />
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Weekly Growth Curve</CardTitle>
            <CardDescription>
              {dateRange(trends.period.currentStartDate, trends.period.currentEndDate)}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <LineChart days={trends.daily} maxValue={chartMax} />
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Sales Vs Expenses</CardTitle>
            <CardDescription>Daily movement for the current week</CardDescription>
          </CardHeader>
          <CardContent>
            <BarChart days={trends.daily} maxValue={chartMax} />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Daily Trend Detail</CardTitle>
          <CardDescription>
            Compared with {dateRange(trends.period.previousStartDate, trends.period.previousEndDate)}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {trends.daily.map((day) => (
            <div key={day.date} className="grid gap-3 rounded-lg border border-neutral-200 bg-white p-3 text-sm md:grid-cols-5 md:items-center">
              <span className="font-semibold text-neutral-900">{day.day}</span>
              <span className="text-green-700">Sales {formatNaira(day.sales)}</span>
              <span className="text-red-700">Expenses {formatNaira(day.expenses)}</span>
              <span className={Number(day.netProfit) >= 0 ? 'text-green-700' : 'text-red-700'}>
                Profit {formatNaira(day.netProfit)}
              </span>
              <span className="text-neutral-500">Cumulative {formatNaira(day.cumulativeProfit)}</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

function TrendCard({ title, metric, icon: Icon, invertGood = false }: { title: string; metric: TrendMetric; icon: LucideIcon; invertGood?: boolean }) {
  const growth = metric.growthRate === null ? 'New' : `${Number(metric.growthRate).toFixed(1)}%`
  const positive = metric.direction === 'up' || metric.direction === 'new'
  const isGood = invertGood ? !positive : positive
  const IconDirection = metric.direction === 'down' ? ArrowDownRight : metric.direction === 'flat' ? Minus : ArrowUpRight

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription className="flex items-center gap-2">
          <Icon className="h-4 w-4 text-orange-500" />
          {title}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="text-2xl font-bold text-neutral-900">{formatNaira(metric.current)}</p>
            <p className="mt-1 text-xs text-neutral-500">Previous {formatNaira(metric.previous)}</p>
          </div>
          <div className={`flex items-center gap-1 rounded-md px-2 py-1 text-xs font-semibold ${isGood ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
            <IconDirection className="h-3 w-3" />
            {growth}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function ReportCard({ title, value, description }: { title: string; value: string; description: string }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{title}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-2xl font-bold">{value}</p>
        <p className="mt-1 text-xs text-neutral-500">{description}</p>
      </CardContent>
    </Card>
  )
}

function LineChart({ days, maxValue }: { days: TrendDay[]; maxValue: number }) {
  const points = days.map((day, index) => {
    const x = 24 + index * 42
    const y = 132 - (Number(day.sales) / maxValue) * 104
    return `${x},${y}`
  }).join(' ')
  const profitPoints = days.map((day, index) => {
    const x = 24 + index * 42
    const y = 132 - (Math.max(Number(day.netProfit), 0) / maxValue) * 104
    return `${x},${y}`
  }).join(' ')

  return (
    <div className="overflow-x-auto">
      <svg viewBox="0 0 300 170" className="h-72 min-w-[520px] w-full">
        <line x1="24" y1="132" x2="276" y2="132" className="stroke-neutral-200" />
        <polyline points={points} fill="none" stroke="#f97316" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        <polyline points={profitPoints} fill="none" stroke="#16a34a" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        {days.map((day, index) => {
          const x = 24 + index * 42
          return (
            <g key={day.date}>
              <text x={x} y="158" textAnchor="middle" className="fill-neutral-500 text-[9px]">{day.day}</text>
            </g>
          )
        })}
      </svg>
      <div className="mt-3 flex items-center justify-center gap-6">
        <Legend color="bg-orange-500" label="Sales" />
        <Legend color="bg-green-600" label="Profit" />
      </div>
    </div>
  )
}

function BarChart({ days, maxValue }: { days: TrendDay[]; maxValue: number }) {
  return (
    <div className="flex h-72 items-end justify-around gap-2">
      {days.map((day) => (
        <div key={day.date} className="flex flex-1 flex-col items-center gap-2">
          <div className="flex h-56 w-full items-end justify-center gap-1">
            <div className="w-full rounded-t bg-orange-500" style={{ height: `${Math.max((Number(day.sales) / maxValue) * 100, 2)}%` }} />
            <div className="w-full rounded-t bg-red-500" style={{ height: `${Math.max((Number(day.expenses) / maxValue) * 100, 2)}%` }} />
          </div>
          <span className="text-xs text-neutral-500">{day.day}</span>
        </div>
      ))}
    </div>
  )
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className={`h-3 w-3 rounded ${color}`} />
      <span className="text-xs text-neutral-600">{label}</span>
    </div>
  )
}

function dateRange(startDate: string, endDate: string) {
  return `${new Date(startDate).toLocaleDateString()} to ${new Date(endDate).toLocaleDateString()}`
}
