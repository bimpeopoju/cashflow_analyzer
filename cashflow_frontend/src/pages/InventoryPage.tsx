import { useEffect, useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { type InventoryItem, api, formatNaira, getErrorMessage } from '@/lib/api'

export default function InventoryPage() {
  const [items, setItems] = useState<InventoryItem[]>([])
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [form, setForm] = useState({ name: '', quantity: 0, unit: 'pcs', reorderLevel: 5, unitCost: '' })

  useEffect(() => {
    api.inventory()
      .then((data) => setItems(data.items))
      .catch((err: unknown) => setError(getErrorMessage(err, 'Could not load inventory.')))
      .finally(() => setIsLoading(false))
  }, [])

  const addItem = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    try {
      const response = await api.createInventoryItem(form)
      setItems((current) => [...current, response.item])
      setForm({ name: '', quantity: 0, unit: 'pcs', reorderLevel: 5, unitCost: '' })
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Could not save inventory item.'))
    }
  }

  const deleteItem = async (id: number) => {
    await api.deleteInventoryItem(id)
    setItems((current) => current.filter((item) => item.id !== id))
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 md:text-3xl">Inventory</h1>
        <p className="mt-1 text-sm text-neutral-500">Watch stock levels before they interrupt sales.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Add Stock Item</CardTitle>
          <CardDescription>Set reorder levels for low-stock alerts.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={addItem} className="grid gap-3 md:grid-cols-6">
            <Field label="Item" className="md:col-span-2">
              <Input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
            </Field>
            <Field label="Qty">
              <Input type="number" min="0" value={form.quantity} onChange={(event) => setForm({ ...form, quantity: Number(event.target.value) })} required />
            </Field>
            <Field label="Unit">
              <Input value={form.unit} onChange={(event) => setForm({ ...form, unit: event.target.value })} required />
            </Field>
            <Field label="Unit Cost">
              <Input type="number" min="0" step="0.01" value={form.unitCost} onChange={(event) => setForm({ ...form, unitCost: event.target.value })} required />
            </Field>
            <div className="flex items-end">
              <Button type="submit" className="w-full">
                <Plus className="h-4 w-4" />
                Add
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

      <Card>
        <CardHeader>
          <CardTitle>Stock List</CardTitle>
          <CardDescription>{items.length} tracked item{items.length === 1 ? '' : 's'}</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          {isLoading ? (
            <p className="text-sm text-neutral-500">Loading inventory...</p>
          ) : items.length === 0 ? (
            <p className="text-sm text-neutral-500">No inventory items yet.</p>
          ) : (
            items.map((item) => (
              <div key={item.id} className="flex items-center gap-3 rounded-lg border border-neutral-200 bg-white p-3">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="truncate text-sm font-semibold text-neutral-900">{item.name}</p>
                    {item.quantity <= item.reorderLevel && <Badge variant="outline" className="text-orange-600">Low</Badge>}
                  </div>
                  <p className="text-xs text-neutral-500">{item.quantity} {item.unit} · {formatNaira(item.stockValue)} value</p>
                </div>
                <Button type="button" variant="ghost" size="icon" onClick={() => deleteItem(item.id)} aria-label="Delete inventory item">
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
