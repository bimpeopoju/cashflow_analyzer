import { useEffect, useMemo, useState } from 'react'
import { Activity, AlertTriangle, BarChart3, CalendarClock, Save, TrendingUp, Wallet, type LucideIcon } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ApiError, type ForecastData, type ForecastHistoryDay, type ForecastPeriod, api, formatNaira, getErrorMessage } from '@/lib/api'

const lookbackOptions = [7, 30, 60, 90]
const horizonOptions = [7, 14, 30]

export default function ForecastsPage() {
  const [forecast, setForecast] = useState<ForecastData | null>(null)
  const [lookbackDays, setLookbackDays] = useState(30)
  const [horizonDays, setHorizonDays] = useState(14)
  const [error, setError] = useState<string | null>(null)
  const [emptyState, setEmptyState] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    api.forecast(lookbackDays, horizonDays)
      .then((response) => {
        setForecast(response.forecast)
        setEmptyState(false)
      })
      .catch((err: unknown) => {
        if (err instanceof ApiError && err.status === 409) {
          setEmptyState(true)
          setError(err.message)
          return
        }
        setError(getErrorMessage(err, 'Could not load forecast.'))
      })
  }, [lookbackDays, horizonDays])

  const chartMax = useMemo(() => {
    if (!forecast) return 1
    return Math.max(
      1,
      ...forecast.history.flatMap((day) => [Number(day.sales), Number(day.expenses), Math.abs(Number(day.netProfit))]),
      ...forecast.periods.flatMap((period) => [
        Number(period.projectedSales),
        Number(period.projectedExpenses),
        Math.abs(Number(period.projectedNetProfit)),
      ]),
    )
  }, [forecast])

  const saveForecast = async () => {
    setIsSaving(true)
    setError(null)
    try {
      const response = await api.saveForecast(lookbackDays, horizonDays)
      setForecast(response.forecast)
      setEmptyState(false)
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Could not save forecast.'))
    } finally {
      setIsSaving(false)
    }
  }

  if (emptyState) {
    return (
      <div className="space-y-6 p-4 md:p-6">
        <ForecastHeader
          lookbackDays={lookbackDays}
          horizonDays={horizonDays}
          onLookbackChange={setLookbackDays}
          onHorizonChange={setHorizonDays}
        />
        <div className="rounded-lg border border-orange-200 bg-orange-50 p-4 text-sm text-orange-900">
          <div className="flex gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
            <div>
              <p className="font-semibold">Forecasting needs transaction history first.</p>
              <p className="mt-1">{error}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                <Button asChild size="sm"><Link to="/sales">Record sales</Link></Button>
                <Button asChild size="sm" variant="outline"><Link to="/expenses">Record expenses</Link></Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error) return <div className="p-6 text-sm text-red-700">{error}</div>
  if (!forecast) return <div className="p-6 text-sm text-neutral-500">Loading forecast...</div>

  return (
    <div className="space-y-6 p-4 md:p-6">
      <ForecastHeader
        lookbackDays={lookbackDays}
        horizonDays={horizonDays}
        onLookbackChange={(value) => {
          setForecast(null)
          setError(null)
          setLookbackDays(value)
        }}
        onHorizonChange={(value) => {
          setForecast(null)
          setError(null)
          setHorizonDays(value)
        }}
        onSave={saveForecast}
        isSaving={isSaving}
        saved={forecast.id !== null}
      />

      <div className="grid gap-4 md:grid-cols-4">
        <Metric title="Projected Sales" value={formatNaira(forecast.summary.projectedSales)} icon={TrendingUp} />
        <Metric title="Projected Expenses" value={formatNaira(forecast.summary.projectedExpenses)} icon={BarChart3} />
        <Metric title="Projected Profit" value={formatNaira(forecast.summary.projectedNetProfit)} icon={Activity} />
        <Metric title="Ending Cash" value={formatNaira(forecast.summary.projectedEndingCash)} icon={Wallet} />
      </div>

      <ConfidencePanel forecast={forecast} />

      <Card>
        <CardHeader>
          <CardTitle>Historical And Projected Trend</CardTitle>
          <CardDescription>{forecast.lookbackDays} day lookback, {forecast.horizonDays} day forecast</CardDescription>
        </CardHeader>
        <CardContent>
          <ForecastChart history={forecast.history} periods={forecast.periods} maxValue={chartMax} />
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Forecast Periods</CardTitle>
            <CardDescription>Daily projected sales, expenses, profit, and cash.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {forecast.periods.slice(0, 14).map((period) => (
              <div key={period.periodStart} className="grid gap-3 rounded-lg border border-neutral-200 bg-white p-3 text-sm md:grid-cols-4 md:items-center">
                <span className="font-semibold text-neutral-900">{new Date(period.periodStart).toLocaleDateString()}</span>
                <span className="text-green-700">Sales {formatNaira(period.projectedSales)}</span>
                <span className="text-red-700">Expenses {formatNaira(period.projectedExpenses)}</span>
                <span className={Number(period.projectedNetProfit) >= 0 ? 'text-green-700' : 'text-red-700'}>
                  Profit {formatNaira(period.projectedNetProfit)}
                </span>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Assumptions</CardTitle>
            <CardDescription>{forecast.method.replace(/_/g, ' ')}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            {Object.entries(forecast.assumptions).map(([key, value]) => (
              <div key={key} className="rounded-lg border border-neutral-200 bg-white p-3">
                <p className="font-semibold text-neutral-900">{labelFromKey(key)}</p>
                <p className="mt-1 text-neutral-600">{value}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function ForecastHeader({
  lookbackDays,
  horizonDays,
  onLookbackChange,
  onHorizonChange,
  onSave,
  isSaving = false,
  saved = false,
}: {
  lookbackDays: number
  horizonDays: number
  onLookbackChange: (value: number) => void
  onHorizonChange: (value: number) => void
  onSave?: () => void
  isSaving?: boolean
  saved?: boolean
}) {
  return (
    <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 md:text-3xl">Financial Forecast</h1>
        <p className="mt-1 text-sm text-neutral-500">Projected sales, expenses, profit, and cash from historical business trends.</p>
      </div>
      <div className="flex flex-col gap-3 md:flex-row md:items-center">
        <OptionGroup label="Lookback" options={lookbackOptions} value={lookbackDays} onChange={onLookbackChange} />
        <OptionGroup label="Horizon" options={horizonOptions} value={horizonDays} onChange={onHorizonChange} />
        {onSave && (
          <Button type="button" onClick={onSave} disabled={isSaving}>
            <Save className="h-4 w-4" />
            {isSaving ? 'Saving...' : saved ? 'Save again' : 'Save forecast'}
          </Button>
        )}
      </div>
    </div>
  )
}

function OptionGroup({ label, options, value, onChange }: { label: string; options: number[]; value: number; onChange: (value: number) => void }) {
  return (
    <div>
      <p className="mb-1 text-xs font-semibold uppercase text-neutral-500">{label}</p>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <Button key={option} type="button" variant={value === option ? 'default' : 'outline'} size="sm" onClick={() => onChange(option)}>
            {option}d
          </Button>
        ))}
      </div>
    </div>
  )
}

function ConfidencePanel({ forecast }: { forecast: ForecastData }) {
  const className = {
    low: 'border-orange-200 bg-orange-50 text-orange-900',
    medium: 'border-amber-200 bg-amber-50 text-amber-900',
    high: 'border-green-200 bg-green-50 text-green-800',
  }[forecast.confidence]

  return (
    <div className={`rounded-lg border p-4 text-sm ${className}`}>
      <div className="flex items-start gap-3">
        <CalendarClock className="mt-0.5 h-5 w-5 shrink-0" />
        <div>
          <p className="font-semibold">Confidence: {forecast.confidence}</p>
          {forecast.warnings.length === 0 ? (
            <p className="mt-1">Forecast is based on enough recent activity for this first-release method.</p>
          ) : (
            <ul className="mt-1 space-y-1">
              {forecast.warnings.map((warning) => <li key={warning}>{warning}</li>)}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}

function Metric({ title, value, icon: Icon }: { title: string; value: string; icon: LucideIcon }) {
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

function ForecastChart({ history, periods, maxValue }: { history: ForecastHistoryDay[]; periods: ForecastPeriod[]; maxValue: number }) {
  const visibleHistory = history.slice(-14)
  const visiblePeriods = periods.slice(0, 14)
  const points = [...visibleHistory, ...visiblePeriods]
  const salesPoints = points.map((point, index) => {
    const value = 'sales' in point ? point.sales : point.projectedSales
    const x = 24 + index * 24
    const y = 132 - (Number(value) / maxValue) * 104
    return `${x},${y}`
  }).join(' ')
  const profitPoints = points.map((point, index) => {
    const value = 'netProfit' in point ? point.netProfit : point.projectedNetProfit
    const x = 24 + index * 24
    const y = 132 - (Math.max(Number(value), 0) / maxValue) * 104
    return `${x},${y}`
  }).join(' ')
  const splitX = 24 + Math.max(visibleHistory.length - 1, 0) * 24

  return (
    <div className="overflow-x-auto">
      <svg viewBox="0 0 690 170" className="h-72 min-w-[690px] w-full">
        <line x1="24" y1="132" x2="660" y2="132" className="stroke-neutral-200" />
        <line x1={splitX} y1="24" x2={splitX} y2="138" className="stroke-neutral-300" strokeDasharray="4 4" />
        <polyline points={salesPoints} fill="none" stroke="#f97316" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        <polyline points={profitPoints} fill="none" stroke="#16a34a" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        {points.map((point, index) => {
          const date = 'date' in point ? point.date : point.periodStart
          const x = 24 + index * 24
          return <text key={`${date}-${index}`} x={x} y="158" textAnchor="middle" className="fill-neutral-500 text-[8px]">{new Date(date).getDate()}</text>
        })}
      </svg>
      <div className="mt-3 flex items-center justify-center gap-6">
        <Legend color="bg-orange-500" label="Sales" />
        <Legend color="bg-green-600" label="Profit" />
      </div>
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

function labelFromKey(value: string) {
  return value.replace(/([A-Z])/g, ' $1').replace(/^./, (first) => first.toUpperCase())
}
