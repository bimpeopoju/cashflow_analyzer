import { useEffect, useMemo, useState } from 'react'
import { AlertCircle, DollarSign, Package, Receipt, TrendingDown, TrendingUp, type LucideIcon } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { type DashboardData, api, formatNaira, getErrorMessage } from '@/lib/api'

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    api.dashboard()
      .then(setData)
      .catch((err: unknown) => setError(getErrorMessage(err, 'Could not load dashboard.')))
      .finally(() => setIsLoading(false))
  }, [])

  const maxWeeklyValue = useMemo(() => {
    if (!data) return 1
    return Math.max(
      1,
      ...data.weeklyPerformance.flatMap((day) => [Number(day.sales), Number(day.expenses)]),
    )
  }, [data])

  if (isLoading) {
    return <div className="p-6 text-sm text-neutral-500">Loading dashboard...</div>
  }

  if (error || !data) {
    return (
      <div className="p-6">
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error ?? 'Dashboard data is unavailable.'}
        </div>
      </div>
    )
  }

  const summary = data.summary

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 md:text-3xl">
          Good morning, {data.user.fullName}
        </h1>
        <p className="mt-1 text-sm text-neutral-500">
          Here is what is happening with {data.user.businessName} today.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4 md:gap-4">
        <MetricCard title="Sales Today" value={formatNaira(summary.salesToday)} icon={DollarSign} tone="orange" />
        <MetricCard title="Expenses" value={formatNaira(summary.expensesToday)} icon={Receipt} tone="red" />
        <MetricCard title="Net Profit" value={formatNaira(summary.netProfit)} icon={TrendingUp} tone="green" />
        <MetricCard title="Transactions" value={String(summary.transactionsToday)} icon={Package} tone="blue" />
      </div>

      <div className="grid gap-4 md:grid-cols-3 md:gap-6">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Your latest sales and expenses</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {data.recentActivity.length === 0 ? (
              <p className="text-sm text-neutral-500">No transactions yet. Add your first sale or expense.</p>
            ) : (
              data.recentActivity.map((txn) => {
                const positive = txn.kind === 'sale'
                return (
                  <div key={txn.id} className="flex items-center gap-3">
                    <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${positive ? 'bg-green-50' : 'bg-red-50'}`}>
                      {positive ? (
                        <TrendingUp className="h-5 w-5 text-green-600" />
                      ) : (
                        <TrendingDown className="h-5 w-5 text-red-600" />
                      )}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-neutral-900">{txn.label}</p>
                      <p className="text-xs text-neutral-500">{new Date(txn.createdAt).toLocaleString()}</p>
                    </div>
                    <div className={`text-sm font-semibold ${positive ? 'text-green-600' : 'text-red-600'}`}>
                      {positive ? '+' : '-'}{formatNaira(txn.amount)}
                    </div>
                  </div>
                )
              })
            )}
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Capital Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="mb-1 flex items-center justify-between">
                  <span className="text-xs text-neutral-500">Initial Capital</span>
                  <span className="text-sm font-semibold">{formatNaira(summary.initialCapital)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-neutral-500">Cash Position</span>
                  <span className="text-sm font-semibold text-green-600">{formatNaira(summary.cashPosition)}</span>
                </div>
              </div>
              <Separator />
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <p className="text-neutral-500">Cash In</p>
                  <p className="font-semibold text-green-700">{formatNaira(summary.cashInflow)}</p>
                </div>
                <div>
                  <p className="text-neutral-500">Cash Out</p>
                  <p className="font-semibold text-red-700">{formatNaira(summary.cashOutflow)}</p>
                </div>
              </div>
              <Separator />
              <div className="flex items-center justify-between text-xs">
                <span className="text-neutral-500">Outstanding Sales</span>
                <span className="font-semibold">{formatNaira(summary.outstandingSales)}</span>
              </div>
              <Separator />
              <div className="flex items-center gap-2 text-xs text-neutral-600">
                <Package className="h-3 w-3" />
                <span>{formatNaira(summary.inventoryValue)} held in inventory</span>
              </div>
            </CardContent>
          </Card>

          <Card className="border-orange-200 bg-orange-50">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-orange-600" />
                <CardTitle className="text-base">Low Stock Alert</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              {data.lowStock.length === 0 ? (
                <p className="text-sm text-neutral-600">All tracked items are above reorder level.</p>
              ) : (
                data.lowStock.map((item) => (
                  <div key={item.id} className="flex items-center justify-between">
                    <span className="text-sm text-neutral-700">{item.name}</span>
                    <Badge variant="outline" className="border-orange-300 text-orange-600">
                      {item.quantity} {item.unit} left
                    </Badge>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Top Selling</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center">
                <p className="text-sm font-semibold">{data.topSelling.name}</p>
                <p className="mt-1 text-xs text-neutral-500">{formatNaira(data.topSelling.amount)} this week</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Weekly Performance</CardTitle>
          <CardDescription>Sales vs expenses, last 7 days</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-64 items-end justify-around gap-2">
            {data.weeklyPerformance.map((day) => (
              <div key={day.day} className="flex flex-1 flex-col items-center gap-2">
                <div className="flex h-52 w-full items-end justify-center gap-1">
                  <div
                    className="w-full rounded-t bg-orange-500"
                    style={{ height: `${(Number(day.sales) / maxWeeklyValue) * 100}%` }}
                  />
                  <div
                    className="w-full rounded-t bg-green-500"
                    style={{ height: `${(Number(day.expenses) / maxWeeklyValue) * 100}%` }}
                  />
                </div>
                <span className="text-xs text-neutral-500">{day.day}</span>
              </div>
            ))}
          </div>
          <div className="mt-4 flex items-center justify-center gap-6">
            <Legend color="bg-orange-500" label="Sales" />
            <Legend color="bg-green-500" label="Expenses" />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function MetricCard({
  title,
  value,
  icon: Icon,
  tone,
}: {
  title: string
  value: string
  icon: LucideIcon
  tone: 'orange' | 'red' | 'green' | 'blue'
}) {
  const toneClass = {
    orange: 'text-orange-500',
    red: 'text-red-500',
    green: 'text-green-600',
    blue: 'text-blue-500',
  }[tone]

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription className="flex items-center gap-2">
          <Icon className={`h-4 w-4 ${toneClass}`} />
          {title}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
      </CardContent>
    </Card>
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
