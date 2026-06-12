const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'

export interface User {
  id: number
  email: string
  fullName: string
  businessName: string
  stallName: string
  initialCapital: string
}

export interface Sale {
  id: number
  itemName: string
  amount: string
  quantity: number
  note: string
  createdAt: string
}

export interface Expense {
  id: number
  category: string
  amount: string
  note: string
  createdAt: string
}

export interface InventoryItem {
  id: number
  name: string
  quantity: number
  unit: string
  reorderLevel: number
  unitCost: string
  stockValue: string
}

export interface DashboardData {
  user: User
  summary: {
    salesToday: string
    expensesToday: string
    netProfit: string
    transactionsToday: number
    initialCapital: string
    currentCapital: string
    inventoryValue: string
  }
  recentActivity: Array<{
    id: string
    kind: 'sale' | 'expense'
    label: string
    amount: string
    createdAt: string
  }>
  lowStock: InventoryItem[]
  topSelling: {
    name: string
    amount: string
  }
  weeklyPerformance: Array<{
    day: string
    sales: string
    expenses: string
  }>
}

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  })

  const contentType = response.headers.get('content-type')
  const body = contentType?.includes('application/json') ? await response.json() : {}

  if (!response.ok) {
    throw new ApiError(body.message ?? 'Request failed. Please try again.', response.status)
  }

  return body as T
}

export function getErrorMessage(error: unknown, fallback: string) {
  if (error instanceof ApiError || error instanceof Error) {
    return error.message
  }
  return fallback
}

export const api = {
  register: (payload: { fullName: string; email: string; password: string }) =>
    request<{ user: User }>('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  login: (payload: { email: string; password: string }) =>
    request<{ user: User }>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  logout: () => request<{ message: string }>('/auth/logout/', { method: 'POST' }),
  me: () => request<{ user: User }>('/auth/me/'),
  dashboard: () => request<DashboardData>('/dashboard/'),
  sales: () => request<{ sales: Sale[] }>('/sales/'),
  createSale: (payload: { itemName: string; amount: string; quantity: number; note?: string }) =>
    request<{ sale: Sale }>('/sales/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  deleteSale: (id: number) => request<{ message: string }>(`/sales/${id}/`, { method: 'DELETE' }),
  expenses: () => request<{ expenses: Expense[] }>('/expenses/'),
  createExpense: (payload: { category: string; amount: string; note?: string }) =>
    request<{ expense: Expense }>('/expenses/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  deleteExpense: (id: number) => request<{ message: string }>(`/expenses/${id}/`, { method: 'DELETE' }),
  inventory: () => request<{ items: InventoryItem[] }>('/inventory/'),
  createInventoryItem: (payload: {
    name: string
    quantity: number
    unit: string
    reorderLevel: number
    unitCost: string
  }) =>
    request<{ item: InventoryItem }>('/inventory/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  deleteInventoryItem: (id: number) =>
    request<{ message: string }>(`/inventory/${id}/`, { method: 'DELETE' }),
}

export function formatNaira(value: string | number) {
  const amount = Number(value)
  return new Intl.NumberFormat('en-NG', {
    style: 'currency',
    currency: 'NGN',
    maximumFractionDigits: 0,
  }).format(Number.isFinite(amount) ? amount : 0)
}
