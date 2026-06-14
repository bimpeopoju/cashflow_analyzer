const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'
const ACCESS_TOKEN_KEY = 'marketflow.accessToken'
const REFRESH_TOKEN_KEY = 'marketflow.refreshToken'

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

interface TokenPair {
  access: string
  refresh: string
}

interface AuthResponse {
  user: User
  tokens: TokenPair
}

function readTokens(): TokenPair | null {
  const access = localStorage.getItem(ACCESS_TOKEN_KEY)
  const refresh = localStorage.getItem(REFRESH_TOKEN_KEY)
  return access && refresh ? { access, refresh } : null
}

function storeTokens(tokens: TokenPair) {
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access)
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh)
}

function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

function apiErrorMessage(body: unknown) {
  if (!body || typeof body !== 'object') return 'Request failed. Please try again.'
  const record = body as Record<string, unknown>
  if (typeof record.message === 'string') return record.message
  if (typeof record.detail === 'string') return record.detail

  const firstFieldError = Object.values(record).find(Array.isArray)
  if (Array.isArray(firstFieldError) && typeof firstFieldError[0] === 'string') {
    return firstFieldError[0]
  }
  return 'Request failed. Please try again.'
}

async function refreshTokens() {
  const current = readTokens()
  if (!current) return null

  const response = await fetch(`${API_BASE_URL}/auth/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: current.refresh }),
  })
  if (!response.ok) {
    clearTokens()
    return null
  }

  const tokens = await response.json() as TokenPair
  storeTokens(tokens)
  return tokens
}

async function request<T>(path: string, options: RequestInit = {}, canRetry = true): Promise<T> {
  const tokens = readTokens()
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(tokens ? { Authorization: `Bearer ${tokens.access}` } : {}),
      ...options.headers,
    },
  })

  if (response.status === 401 && canRetry && tokens) {
    const refreshed = await refreshTokens()
    if (refreshed) return request<T>(path, options, false)
  }

  const contentType = response.headers.get('content-type')
  const body = contentType?.includes('application/json') ? await response.json() : {}

  if (!response.ok) {
    throw new ApiError(apiErrorMessage(body), response.status)
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
  register: async (payload: { fullName: string; email: string; password: string }) => {
    const response = await request<AuthResponse>('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    storeTokens(response.tokens)
    return response
  },
  login: async (payload: { email: string; password: string }) => {
    const response = await request<AuthResponse>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    storeTokens(response.tokens)
    return response
  },
  logout: async () => {
    const refresh = readTokens()?.refresh
    try {
      return await request<{ message: string }>('/auth/logout/', {
        method: 'POST',
        body: JSON.stringify(refresh ? { refresh } : {}),
      })
    } finally {
      clearTokens()
    }
  },
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
