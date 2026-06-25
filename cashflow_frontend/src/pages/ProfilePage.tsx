import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/lib/auth-context'
import { type DashboardData, type User, api, formatNaira, getErrorMessage } from '@/lib/api'

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null)
  const [dashboard, setDashboard] = useState<DashboardData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [form, setForm] = useState({ entryType: 'owner_deposit', amount: '', note: '' })
  const navigate = useNavigate()
  const { clearUser } = useAuth()

  useEffect(() => {
    Promise.all([api.me(), api.dashboard()])
      .then(([me, capital]) => {
        setUser(me.user)
        setDashboard(capital)
      })
      .catch((err: unknown) => setError(getErrorMessage(err, 'Could not load profile.')))
  }, [])

  const signOut = async () => {
    await api.logout()
    clearUser()
    navigate('/auth')
  }

  const saveCapitalEntry = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    setIsSaving(true)
    try {
      await api.createCapitalEntry({
        entryType: form.entryType as 'owner_deposit' | 'owner_withdrawal',
        amount: form.amount,
        note: form.note,
      })
      setForm({ entryType: 'owner_deposit', amount: '', note: '' })
      const refreshed = await api.dashboard()
      setDashboard(refreshed)
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Could not save capital movement.'))
    } finally {
      setIsSaving(false)
    }
  }

  if (error) return <div className="p-6 text-sm text-red-700">{error}</div>
  if (!user) return <div className="p-6 text-sm text-neutral-500">Loading profile...</div>

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 md:text-3xl">Profile</h1>
        <p className="mt-1 text-sm text-neutral-500">Account and business details.</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>{user.fullName}</CardTitle>
          <CardDescription>{user.email}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-3">
            <Info label="Business" value={user.businessName} />
            <Info label="Stall" value={user.stallName || 'Market stall'} />
            <Info label="Initial Capital" value={formatNaira(user.initialCapital)} />
          </div>
          {dashboard && (
            <div className="grid gap-3 md:grid-cols-3">
              <Info label="Protected Floor" value={formatNaira(dashboard.summary.protectedCapitalFloor)} />
              <Info label="Equity Position" value={formatNaira(dashboard.summary.currentCapital)} />
              <Info label="Available Profit" value={formatNaira(dashboard.summary.availableProfit)} />
            </div>
          )}
          <div className="rounded-lg border border-neutral-200 bg-white p-4">
            <div className="mb-4">
              <h2 className="text-base font-semibold text-neutral-900">Capital Movement</h2>
              <p className="mt-1 text-sm text-neutral-500">Record owner deposits and withdrawals against the profit buffer.</p>
            </div>
            <form onSubmit={saveCapitalEntry} className="grid gap-3 md:grid-cols-4">
              <div className="space-y-2">
                <Label>Type</Label>
                <select
                  className="h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={form.entryType}
                  onChange={(event) => setForm({ ...form, entryType: event.target.value })}
                >
                  <option value="owner_deposit">Owner deposit</option>
                  <option value="owner_withdrawal">Owner withdrawal</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label>Amount</Label>
                <Input type="number" min="0" step="0.01" value={form.amount} onChange={(event) => setForm({ ...form, amount: event.target.value })} required />
              </div>
              <div className="space-y-2 md:col-span-2">
                <Label>Note</Label>
                <Input value={form.note} onChange={(event) => setForm({ ...form, note: event.target.value })} />
              </div>
              <div className="md:col-span-4">
                <Button type="submit" disabled={isSaving}>
                  {isSaving ? 'Saving...' : 'Save capital movement'}
                </Button>
              </div>
            </form>
          </div>
          <Button type="button" variant="outline" onClick={signOut}>Sign Out</Button>
        </CardContent>
      </Card>
    </div>
  )
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-3">
      <p className="text-xs text-neutral-500">{label}</p>
      <p className="mt-1 text-sm font-semibold text-neutral-900">{value}</p>
    </div>
  )
}
