import { useEffect, useState } from 'react'
import { AlertTriangle, Calculator, FileText, ReceiptText, Save, type LucideIcon } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ApiError, type TaxEstimate, api, formatNaira, getErrorMessage } from '@/lib/api'

export default function TaxesPage() {
  const [estimate, setEstimate] = useState<TaxEstimate | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [emptyState, setEmptyState] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    api.taxEstimate()
      .then((data) => setEstimate(data.estimate))
      .catch((err: unknown) => {
        if (err instanceof ApiError && err.status === 409) {
          setEmptyState(true)
          setError(err.message)
          return
        }
        setError(getErrorMessage(err, 'Could not load tax estimate.'))
      })
  }, [])

  const saveEstimate = async () => {
    setIsSaving(true)
    setError(null)
    try {
      const response = await api.saveTaxEstimate()
      setEstimate(response.estimate)
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Could not save tax estimate.'))
    } finally {
      setIsSaving(false)
    }
  }

  if (emptyState) {
    return (
      <div className="space-y-6 p-4 md:p-6">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900 md:text-3xl">Tax Estimate</h1>
          <p className="mt-1 text-sm text-neutral-500">Nigeria VAT and FIRS/NRS estimate workspace.</p>
        </div>
        <div className="rounded-lg border border-orange-200 bg-orange-50 p-4 text-sm text-orange-900">
          <div className="flex gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
            <div>
              <p className="font-semibold">Tax estimates need transaction data first.</p>
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
  if (!estimate) return <div className="p-6 text-sm text-neutral-500">Loading tax estimate...</div>

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900 md:text-3xl">Tax Estimate</h1>
          <p className="mt-1 text-sm text-neutral-500">Nigeria VAT and FIRS/NRS estimate for recorded business activity.</p>
        </div>
        <Button type="button" onClick={saveEstimate} disabled={isSaving}>
          <Save className="h-4 w-4" />
          {isSaving ? 'Saving...' : 'Save estimate'}
        </Button>
      </div>

      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
        This is an estimate for planning, not a filed tax return. Final filing should be reviewed against current FIRS/NRS guidance and your business registration type.
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Metric title="Net VAT Payable" value={formatNaira(estimate.result.netVatPayable)} icon={ReceiptText} />
        <Metric title="Income Tax Estimate" value={formatNaira(estimate.result.incomeTax)} icon={Calculator} />
        <Metric title="Total Estimate" value={formatNaira(estimate.result.totalEstimatedTax)} icon={FileText} />
        <Metric title="Taxable Profit" value={formatNaira(estimate.result.taxableProfit)} icon={Calculator} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>VAT Summary</CardTitle>
            <CardDescription>{dateRange(estimate.period.startDate, estimate.period.endDate)}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <Row label="Gross sales" value={formatNaira(estimate.result.grossSales)} />
            <Row label="Output VAT" value={formatNaira(estimate.result.outputVat)} />
            <Row label="Input VAT" value={formatNaira(estimate.result.inputVat)} />
            <Row label="Net VAT payable" value={formatNaira(estimate.result.netVatPayable)} strong />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Income Tax Summary</CardTitle>
            <CardDescription>{estimate.rules.incomeTax?.name ?? 'No income tax rule selected'}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <Row label="Cost of goods sold" value={formatNaira(estimate.result.costOfGoodsSold)} />
            <Row label="Deductible expenses" value={formatNaira(estimate.result.deductibleExpenses)} />
            <Row label="Taxable profit" value={formatNaira(estimate.result.taxableProfit)} />
            <Row label="Income tax" value={formatNaira(estimate.result.incomeTax)} strong />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Assumptions</CardTitle>
          <CardDescription>Rules and limitations used by this estimate.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          {Object.entries(estimate.assumptions).map(([key, value]) => (
            <div key={key} className="rounded-lg border border-neutral-200 bg-white p-3">
              <p className="font-semibold text-neutral-900">{labelFromKey(key)}</p>
              <p className="mt-1 text-neutral-600">{value}</p>
            </div>
          ))}
        </CardContent>
      </Card>
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

function Row({ label, value, strong = false }: { label: string; value: string; strong?: boolean }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="text-neutral-500">{label}</span>
      <span className={strong ? 'font-bold text-neutral-900' : 'font-semibold text-neutral-800'}>{value}</span>
    </div>
  )
}

function labelFromKey(value: string) {
  return value.replace(/([A-Z])/g, ' $1').replace(/^./, (first) => first.toUpperCase())
}

function dateRange(startDate: string, endDate: string) {
  return `${new Date(startDate).toLocaleDateString()} to ${new Date(endDate).toLocaleDateString()}`
}
