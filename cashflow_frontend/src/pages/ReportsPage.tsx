import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { type DashboardData, api, formatNaira, getErrorMessage } from '@/lib/api'

export default function ReportsPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.dashboard()
      .then(setData)
      .catch((err: unknown) => setError(getErrorMessage(err, 'Could not load reports.')))
  }, [])

  if (error) return <div className="p-6 text-sm text-red-700">{error}</div>
  if (!data) return <div className="p-6 text-sm text-neutral-500">Loading reports...</div>

  const taxableEstimate = Math.max(Number(data.summary.netProfit), 0) * 0.1
  const capitalEroded = data.summary.capitalEroded

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 md:text-3xl">Reports</h1>
        <p className="mt-1 text-sm text-neutral-500">A simple view of profit, capital protection, and estimated tax exposure.</p>
      </div>
      {capitalEroded && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Equity is below the protected capital floor. Avoid withdrawals until profit recovers.
        </div>
      )}
      <div className="grid gap-4 md:grid-cols-3">
        <ReportCard title="Net Profit" value={formatNaira(data.summary.netProfit)} description="Sales less expenses" />
        <ReportCard title="Equity Position" value={formatNaira(data.summary.currentCapital)} description="Initial capital, contributions, and retained profit" />
        <ReportCard title="Tax Set-Aside" value={formatNaira(taxableEstimate)} description="Conservative 10% profit reserve" />
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Weekly Movement</CardTitle>
          <CardDescription>Use this to spot slow days and high-cost days.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {data.weeklyPerformance.map((day) => (
            <div key={day.day} className="grid grid-cols-3 gap-3 rounded-lg border border-neutral-200 bg-white p-3 text-sm">
              <span className="font-medium">{day.day}</span>
              <span className="text-green-700">Sales {formatNaira(day.sales)}</span>
              <span className="text-red-700">Expenses {formatNaira(day.expenses)}</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

function ReportCard({ title, value, description }: { title: string; value: string; description: string }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-2xl font-bold">{value}</p>
      </CardContent>
    </Card>
  )
}
