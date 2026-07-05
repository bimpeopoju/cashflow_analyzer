import { useEffect, useState } from 'react'
import { AlertTriangle, Building2, Calculator, FileText, ReceiptText, Save, ShieldCheck, type LucideIcon } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ApiError, type BusinessTaxProfile, type TaxEstimate, api, formatNaira, getErrorMessage } from '@/lib/api'

export default function TaxesPage() {
  const [estimate, setEstimate] = useState<TaxEstimate | null>(null)
  const [taxProfile, setTaxProfile] = useState<BusinessTaxProfile | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [emptyState, setEmptyState] = useState(false)
  const [emptyMessage, setEmptyMessage] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [isSavingProfile, setIsSavingProfile] = useState(false)
  const [profileForm, setProfileForm] = useState({
    tin: '',
    entityType: '' as BusinessTaxProfile['entityType'],
    vatRegistered: false,
    accountingYearEndMonth: '',
    accountingYearEndDay: '',
  })

  useEffect(() => {
    Promise.allSettled([api.taxProfile(), api.taxEstimate()])
      .then(([profileResult, estimateResult]) => {
        if (profileResult.status === 'fulfilled') {
          setTaxProfile(profileResult.value.taxProfile)
          setProfileForm(profileToForm(profileResult.value.taxProfile))
        } else {
          setError(getErrorMessage(profileResult.reason, 'Could not load tax profile.'))
        }

        if (estimateResult.status === 'fulfilled') {
          setEstimate(estimateResult.value.estimate)
          setEmptyState(false)
          setEmptyMessage(null)
          return
        }

        if (estimateResult.reason instanceof ApiError && estimateResult.reason.status === 409) {
          setEmptyState(true)
          setEmptyMessage(estimateResult.reason.message)
          return
        }

        setError(getErrorMessage(estimateResult.reason, 'Could not load tax estimate.'))
      })
  }, [])

  const saveProfile = async () => {
    setIsSavingProfile(true)
    setError(null)
    try {
      const response = await api.updateTaxProfile({
        tin: profileForm.tin,
        entityType: profileForm.entityType,
        vatRegistered: profileForm.vatRegistered,
        accountingYearEndMonth: profileForm.accountingYearEndMonth ? Number(profileForm.accountingYearEndMonth) : null,
        accountingYearEndDay: profileForm.accountingYearEndDay ? Number(profileForm.accountingYearEndDay) : null,
      })
      setTaxProfile(response.taxProfile)
      setProfileForm(profileToForm(response.taxProfile))
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Could not save tax setup.'))
    } finally {
      setIsSavingProfile(false)
    }
  }

  const saveEstimate = async () => {
    setIsSaving(true)
    setError(null)
    try {
      const response = await api.saveTaxEstimate()
      setEstimate(response.estimate)
      setEmptyState(false)
      setEmptyMessage(null)
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Could not save tax estimate.'))
    } finally {
      setIsSaving(false)
    }
  }

  if (error) return <div className="p-6 text-sm text-red-700">{error}</div>
  if (!taxProfile) return <div className="p-6 text-sm text-neutral-500">Loading tax workspace...</div>
  if (!estimate && !emptyState) return <div className="p-6 text-sm text-neutral-500">Loading tax estimate...</div>

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900 md:text-3xl">Tax Estimate</h1>
          <p className="mt-1 text-sm text-neutral-500">Nigeria VAT and FIRS/NRS estimate for recorded business activity.</p>
        </div>
        <Button type="button" onClick={saveEstimate} disabled={isSaving || emptyState}>
          <Save className="h-4 w-4" />
          {isSaving ? 'Saving...' : 'Save estimate'}
        </Button>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.15fr_0.85fr]">
        <Card className="border-neutral-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-4 w-4 text-orange-500" />
              Tax Setup
            </CardTitle>
            <CardDescription>Add the business identifiers needed for deadline tracking and cleaner tax previews.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {!taxProfile.isComplete && (
              <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
                Missing: {formatMissingFields(taxProfile.missingFields)}
              </div>
            )}
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="tin">Tax Identification Number</Label>
                <Input id="tin" value={profileForm.tin} onChange={(event) => setProfileForm({ ...profileForm, tin: event.target.value.toUpperCase() })} placeholder="20345678-0001" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="entityType">Entity Type</Label>
                <select
                  id="entityType"
                  className="h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={profileForm.entityType}
                  onChange={(event) => setProfileForm({ ...profileForm, entityType: event.target.value as BusinessTaxProfile['entityType'] })}
                >
                  <option value="">Select entity type</option>
                  <option value="company">Company</option>
                  <option value="sole_proprietor">Sole proprietor</option>
                  <option value="partnership">Partnership</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="vatRegistered">VAT Registered</Label>
                <select
                  id="vatRegistered"
                  className="h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={profileForm.vatRegistered ? 'true' : 'false'}
                  onChange={(event) => setProfileForm({ ...profileForm, vatRegistered: event.target.value === 'true' })}
                >
                  <option value="false">No</option>
                  <option value="true">Yes</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="accountingYearEndMonth">Year End Month</Label>
                  <Input id="accountingYearEndMonth" type="number" min="1" max="12" value={profileForm.accountingYearEndMonth} onChange={(event) => setProfileForm({ ...profileForm, accountingYearEndMonth: event.target.value })} placeholder="12" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="accountingYearEndDay">Year End Day</Label>
                  <Input id="accountingYearEndDay" type="number" min="1" max="31" value={profileForm.accountingYearEndDay} onChange={(event) => setProfileForm({ ...profileForm, accountingYearEndDay: event.target.value })} placeholder="31" />
                </div>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Button type="button" onClick={saveProfile} disabled={isSavingProfile}>
                {isSavingProfile ? 'Saving setup...' : 'Save tax setup'}
              </Button>
              <div className="flex items-center gap-2 text-sm text-neutral-500">
                <ShieldCheck className={`h-4 w-4 ${taxProfile.isComplete ? 'text-emerald-600' : 'text-amber-600'}`} />
                {taxProfile.isComplete ? 'Tax setup is complete for this business.' : 'Complete setup to improve deadline tracking.'}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-amber-200 bg-amber-50/60">
          <CardHeader>
            <CardTitle>What this setup unlocks</CardTitle>
            <CardDescription>The dashboard tax card depends on these details.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-neutral-700">
            <div className="rounded-lg border border-white/70 bg-white/80 p-3">
              TIN identifies the business for future filing workflows and reminders.
            </div>
            <div className="rounded-lg border border-white/70 bg-white/80 p-3">
              Entity type controls whether the app can estimate company income tax or must warn that personal income tax is not implemented.
            </div>
            <div className="rounded-lg border border-white/70 bg-white/80 p-3">
              Accounting year end is used to estimate annual company income tax deadlines.
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
        This is an estimate for planning, not a filed tax return. Final filing should be reviewed against current FIRS/NRS guidance and your business registration type.
      </div>

      {emptyState && (
        <div className="rounded-lg border border-orange-200 bg-orange-50 p-4 text-sm text-orange-900">
          <div className="flex gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
            <div>
              <p className="font-semibold">Tax estimates need transaction data first.</p>
              <p className="mt-1">{emptyMessage}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                <Button asChild size="sm"><Link to="/sales">Record sales</Link></Button>
                <Button asChild size="sm" variant="outline"><Link to="/expenses">Record expenses</Link></Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {!estimate ? null : (
        <>
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
                <CardDescription>{estimate.rules.incomeTax?.name ?? 'Income tax rule not active for this business type yet'}</CardDescription>
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
        </>
      )}
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

function profileToForm(profile: BusinessTaxProfile) {
  return {
    tin: profile.tin,
    entityType: profile.entityType,
    vatRegistered: profile.vatRegistered,
    accountingYearEndMonth: profile.accountingYearEndMonth ? String(profile.accountingYearEndMonth) : '',
    accountingYearEndDay: profile.accountingYearEndDay ? String(profile.accountingYearEndDay) : '',
  }
}

function formatMissingFields(fields: string[]) {
  return fields.map((field) => ({
    tin: 'TIN',
    entityType: 'entity type',
    accountingYearEnd: 'accounting year end',
  }[field] ?? field)).join(', ')
}
