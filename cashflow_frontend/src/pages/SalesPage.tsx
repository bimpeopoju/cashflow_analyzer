import { useEffect, useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { type InventoryItem, type Sale, api, formatNaira, getErrorMessage } from '@/lib/api'

export default function SalesPage() {
  const [sales, setSales] = useState<Sale[]>([])
  const [inventory, setInventory] = useState<InventoryItem[]>([])
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const [form, setForm] = useState({ inventoryItemId: '', itemName: '', amount: '', quantity: 1, note: '' })

  useEffect(() => {
    let isMounted = true
    Promise.all([api.sales(), api.inventory()])
      .then(([salesData, inventoryData]) => {
        if (isMounted) {
          setSales(salesData.sales)
          setInventory(inventoryData.items)
        }
      })
      .catch((err: unknown) => {
        if (isMounted) setError(getErrorMessage(err, 'Could not load sales.'))
      })
      .finally(() => {
        if (isMounted) setIsLoading(false)
      })
    return () => {
      isMounted = false
    }
  }, [])

  const addSale = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    setIsSaving(true)
    try {
      const response = await api.createSale({
        ...form,
        inventoryItemId: form.inventoryItemId ? Number(form.inventoryItemId) : null,
      })
      setSales((current) => [response.sale, ...current])
      setForm({ inventoryItemId: '', itemName: '', amount: '', quantity: 1, note: '' })
      api.inventory().then((data) => setInventory(data.items)).catch(() => undefined)
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Could not save sale.'))
    } finally {
      setIsSaving(false)
    }
  }

  const deleteSale = async (id: number) => {
    if (!window.confirm('Delete this sale? This cannot be undone.')) return

    setError(null)
    setDeletingId(id)
    try {
      await api.deleteSale(id)
      setSales((current) => current.filter((sale) => sale.id !== id))
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Could not delete sale.'))
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 md:text-3xl">Sales</h1>
        <p className="mt-1 text-sm text-neutral-500">Record each sale as cash comes in.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Add Sale</CardTitle>
          <CardDescription>Use the item name your stall already uses.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={addSale} className="grid gap-3 md:grid-cols-6">
            <Field label="Tracked Stock" className="md:col-span-2">
              <select
                className="h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={form.inventoryItemId}
                onChange={(event) => {
                  const item = inventory.find((candidate) => String(candidate.id) === event.target.value)
                  setForm({
                    ...form,
                    inventoryItemId: event.target.value,
                    itemName: item?.name ?? form.itemName,
                  })
                }}
              >
                <option value="">Manual sale</option>
                {inventory.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name} ({item.quantity} {item.unit})
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Item" className="md:col-span-2">
              <Input value={form.itemName} onChange={(event) => setForm({ ...form, itemName: event.target.value })} required />
            </Field>
            <Field label="Amount">
              <Input type="number" min="0" step="0.01" value={form.amount} onChange={(event) => setForm({ ...form, amount: event.target.value })} required />
            </Field>
            <Field label="Quantity">
              <Input type="number" min="1" value={form.quantity} onChange={(event) => setForm({ ...form, quantity: Number(event.target.value) })} required />
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

      {error && <Notice message={error} />}

      <Card>
        <CardHeader>
          <CardTitle>Recent Sales</CardTitle>
          <CardDescription>{sales.length} recorded sale{sales.length === 1 ? '' : 's'}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading ? (
            <p className="text-sm text-neutral-500">Loading sales...</p>
          ) : sales.length === 0 ? (
            <p className="text-sm text-neutral-500">No sales recorded yet.</p>
          ) : (
            sales.map((sale) => (
              <div key={sale.id} className="flex items-center gap-3 rounded-lg border border-neutral-200 bg-white p-3">
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-semibold text-neutral-900">{sale.itemName}</p>
                  <p className="text-xs text-neutral-500">{sale.quantity} sold - {new Date(sale.createdAt).toLocaleString()}</p>
                </div>
                <p className="text-sm font-bold text-green-600">{formatNaira(sale.amount)}</p>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => deleteSale(sale.id)}
                  aria-label="Delete sale"
                  disabled={deletingId === sale.id}
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

function Notice({ message }: { message: string }) {
  return <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{message}</div>
}
