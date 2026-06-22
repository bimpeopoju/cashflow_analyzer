import { useEffect, useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { type Expense, api, formatNaira, getErrorMessage } from '@/lib/api'

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState<Expense[]>([])
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const [form, setForm] = useState({ category: '', amount: '', note: '' })

  useEffect(() => {
    api.expenses()
      .then((data) => setExpenses(data.expenses))
      .catch((err: unknown) => setError(getErrorMessage(err, 'Could not load expenses.')))
      .finally(() => setIsLoading(false))
  }, [])

  const addExpense = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    setIsSaving(true)
    try {
      const response = await api.createExpense(form)
      setExpenses((current) => [response.expense, ...current])
      setForm({ category: '', amount: '', note: '' })
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Could not save expense.'))
    } finally {
      setIsSaving(false)
    }
  }

  const deleteExpense = async (id: number) => {
    if (!window.confirm('Void this expense? The record will be kept for audit history.')) return

    setError(null)
    setDeletingId(id)
    try {
      await api.deleteExpense(id)
      setExpenses((current) => current.filter((expense) => expense.id !== id))
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Could not void expense.'))
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 md:text-3xl">Expenses</h1>
        <p className="mt-1 text-sm text-neutral-500">Track costs that reduce real profit.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Add Expense</CardTitle>
          <CardDescription>Transport, levy, stock handling, and other operating costs.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={addExpense} className="grid gap-3 md:grid-cols-4">
            <Field label="Category" className="md:col-span-2">
              <Input value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })} required />
            </Field>
            <Field label="Amount">
              <Input type="number" min="0" step="0.01" value={form.amount} onChange={(event) => setForm({ ...form, amount: event.target.value })} required />
            </Field>
            <div className="flex items-end">
              <Button type="submit" className="w-full" disabled={isSaving}>
                <Plus className="h-4 w-4" />
                {isSaving ? 'Adding...' : 'Add'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

      <Card>
        <CardHeader>
          <CardTitle>Recent Expenses</CardTitle>
          <CardDescription>{expenses.length} recorded expense{expenses.length === 1 ? '' : 's'}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading ? (
            <p className="text-sm text-neutral-500">Loading expenses...</p>
          ) : expenses.length === 0 ? (
            <p className="text-sm text-neutral-500">No expenses recorded yet.</p>
          ) : (
            expenses.map((expense) => (
              <div key={expense.id} className="flex items-center gap-3 rounded-lg border border-neutral-200 bg-white p-3">
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-semibold text-neutral-900">{expense.category}</p>
                  <p className="text-xs text-neutral-500">{new Date(expense.createdAt).toLocaleString()}</p>
                </div>
                <p className="text-sm font-bold text-red-600">{formatNaira(expense.amount)}</p>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => deleteExpense(expense.id)}
                  aria-label="Void expense"
                  disabled={deletingId === expense.id}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function Field({ label, className, children }: { label: string; className?: string; children: ReactNode }) {
  return (
    <div className={`space-y-2 ${className ?? ''}`}>
      <Label>{label}</Label>
      {children}
    </div>
  )
}
