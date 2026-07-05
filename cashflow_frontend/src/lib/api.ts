const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'
const ACCESS_TOKEN_KEY = 'marketflow.accessToken'
const REFRESH_TOKEN_KEY = 'marketflow.refreshToken'
const ACTIVE_BUSINESS_KEY = 'marketflow.activeBusinessId'

export interface User {
  id: number
  email: string
  fullName: string
  activeBusinessId: number
  businessName: string
  stallName: string
  initialCapital: string
}

export interface Business {
  id: number
  name: string
  stallName: string
  initialCapital: string
  role: 'owner' | 'admin' | 'staff' | 'viewer' | null
  taxProfile: BusinessTaxProfile
}

export interface BusinessTaxProfile {
  tin: string
  entityType: 'company' | 'sole_proprietor' | 'partnership' | ''
  vatRegistered: boolean
  accountingYearEndMonth: number | null
  accountingYearEndDay: number | null
  isComplete: boolean
  missingFields: string[]
}

export interface Sale {
  id: number
  itemName: string
  inventoryItemId: number | null
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

export interface CapitalEntry {
  id: number
  entryType: 'owner_deposit' | 'owner_withdrawal'
  direction: 'inflow' | 'outflow'
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

export interface BurnRateData {
  period: {
    days: number
    startDate: string
    endDate: string
  }
  summary: {
    trackedItems: number
    activeBurnItems: number
    atRiskItems: number
    totalConsumedValue: string
  }
  items: Array<{
    itemId: number
    name: string
    unit: string
    currentQuantity: number
    reorderLevel: number
    periodDays: number
    consumedQuantity: number
    averageDailyConsumption: string
    daysUntilStockout: number | null
    projectedStockoutDate: string | null
    consumedValue: string
    status: 'out' | 'at_risk' | 'stable' | 'no_data'
  }>
}

export interface BreakEvenData {
  period: {
    days: number
    startDate: string
    endDate: string
  }
  summary: {
    status: 'no_data' | 'unviable' | 'below_break_even' | 'above_break_even'
    actualRevenue: string
    actualUnitsSold: number
    fixedCosts: string
    variableCosts: string
    averageSellingPrice: string
    averageUnitVariableCost: string
    contributionMargin: string
    contributionMarginRatio: string
    breakEvenUnits: number | null
    breakEvenRevenue: string | null
    revenueGap: string
    unitsGap: number
  }
}

export interface TrendMetric {
  current: string
  previous: string
  change: string
  growthRate: string | null
  direction: 'up' | 'down' | 'flat' | 'new'
}

export interface TrendData {
  period: {
    currentStartDate: string
    currentEndDate: string
    previousStartDate: string
    previousEndDate: string
  }
  summary: {
    sales: TrendMetric
    expenses: TrendMetric
    netProfit: TrendMetric
    bestSalesDay: TrendDay | null
  }
  daily: TrendDay[]
}

export interface TrendDay {
  date: string
  day: string
  sales: string
  expenses: string
  netProfit: string
  cumulativeSales: string
  cumulativeProfit: string
}

export interface TaxEstimate {
  id: number | null
  period: {
    startDate: string
    endDate: string
  }
  rules: {
    vat: TaxRule | null
    incomeTax: TaxRule | null
  }
  assumptions: Record<string, string>
  result: {
    grossSales: string
    costOfGoodsSold: string
    deductibleExpenses: string
    taxableProfit: string
    outputVat: string
    inputVat: string
    netVatPayable: string
    incomeTax: string
    totalEstimatedTax: string
  }
  createdAt: string | null
}

export interface TaxRule {
  code: string
  name: string
  taxType: 'vat' | 'cit'
  rate: string
  thresholdMin: string | null
  thresholdMax: string | null
  effectiveFrom: string
  effectiveTo: string | null
  sourceUrl: string
  notes: string
}

export interface TaxDeadline {
  code: string
  label: string
  dueDate: string
  daysRemaining: number
  status: 'overdue' | 'urgent' | 'upcoming' | 'normal'
  description: string
}

export interface TaxAlert {
  level: 'info' | 'warning' | 'critical'
  title: string
  message: string
}

export interface TaxSummary {
  status: 'ready' | 'needs_setup' | 'needs_activity' | 'attention'
  profile: BusinessTaxProfile
  estimate: TaxEstimate | null
  deadlines: TaxDeadline[]
  alerts: TaxAlert[]
  lastUpdatedAt: string
}

export interface ForecastData {
  id: number | null
  method: string
  lookbackDays: number
  horizonDays: number
  periodGranularity: 'daily'
  confidence: 'low' | 'medium' | 'high'
  warnings: string[]
  assumptions: Record<string, string>
  history: ForecastHistoryDay[]
  periods: ForecastPeriod[]
  summary: {
    projectedSales: string
    projectedExpenses: string
    projectedGrossProfit: string
    projectedNetProfit: string
    projectedInventoryCost: string
    projectedEndingCash: string
  }
  createdAt: string | null
}

export interface ForecastHistoryDay {
  date: string
  sales: string
  expenses: string
  grossProfit: string
  netProfit: string
  inventoryCost: string
  cashNet: string
}

export interface ForecastPeriod {
  periodStart: string
  periodEnd: string
  projectedSales: string
  projectedExpenses: string
  projectedGrossProfit: string
  projectedNetProfit: string
  projectedCashPosition: string
  projectedInventoryCost: string
}

export interface DashboardData {
  user: User
  summary: {
    salesToday: string
    expensesToday: string
    costOfGoodsSold: string
    grossProfit: string
    netProfit: string
    cashInflow: string
    cashOutflow: string
    cashPosition: string
    outstandingSales: string
    transactionsToday: number
    initialCapital: string
    capitalContributions: string
    capitalWithdrawals: string
    protectedCapitalFloor: string
    retainedProfit: string
    currentCapital: string
    capitalGap: string
    capitalEroded: boolean
    availableProfit: string
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
  taxSummary: TaxSummary
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

function storeActiveBusinessId(id: number) {
  localStorage.setItem(ACTIVE_BUSINESS_KEY, String(id))
}

function readActiveBusinessId() {
  return localStorage.getItem(ACTIVE_BUSINESS_KEY)
}

function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(ACTIVE_BUSINESS_KEY)
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

function businessPath(path: string) {
  const businessId = readActiveBusinessId()
  return businessId ? `/businesses/${businessId}${path}` : path
}

function storeAuthResponse(response: AuthResponse) {
  storeTokens(response.tokens)
  storeActiveBusinessId(response.user.activeBusinessId)
}

function storeUserBusiness(user: User) {
  storeActiveBusinessId(user.activeBusinessId)
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
    storeAuthResponse(response)
    return response
  },
  login: async (payload: { email: string; password: string }) => {
    const response = await request<AuthResponse>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    storeAuthResponse(response)
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
  me: async () => {
    const response = await request<{ user: User }>('/auth/me/')
    storeUserBusiness(response.user)
    return response
  },
  businesses: () => request<{ businesses: Business[] }>('/businesses/'),
  createBusiness: (payload: { name: string; stallName?: string; initialCapital: string }) =>
    request<{ business: Business }>('/businesses/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  dashboard: () => request<DashboardData>(businessPath('/dashboard/')),
  taxProfile: () => request<{ taxProfile: BusinessTaxProfile }>(businessPath('/tax-profile/')),
  updateTaxProfile: (payload: {
    tin: string
    entityType: BusinessTaxProfile['entityType']
    vatRegistered: boolean
    accountingYearEndMonth: number | null
    accountingYearEndDay: number | null
  }) => request<{ taxProfile: BusinessTaxProfile }>(businessPath('/tax-profile/'), {
    method: 'PUT',
    body: JSON.stringify(payload),
  }),
  trends: () => request<TrendData>(businessPath('/reports/trends/')),
  taxEstimate: () => request<{ estimate: TaxEstimate }>(businessPath('/taxes/estimate/')),
  saveTaxEstimate: () => request<{ estimate: TaxEstimate }>(businessPath('/taxes/estimate/'), { method: 'POST' }),
  forecast: (lookbackDays = 30, horizonDays = 14) =>
    request<{ forecast: ForecastData }>(`${businessPath('/forecasts/')}?lookbackDays=${lookbackDays}&horizonDays=${horizonDays}`),
  saveForecast: (lookbackDays = 30, horizonDays = 14) =>
    request<{ forecast: ForecastData }>(`${businessPath('/forecasts/')}?lookbackDays=${lookbackDays}&horizonDays=${horizonDays}`, { method: 'POST' }),
  sales: () => request<{ sales: Sale[] }>(businessPath('/sales/')),
  createSale: (payload: { inventoryItemId?: number | null; itemName: string; amount: string; quantity: number; note?: string }) =>
    request<{ sale: Sale }>(businessPath('/sales/'), {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  deleteSale: (id: number) => request<{ message: string }>(businessPath(`/sales/${id}/`), { method: 'DELETE' }),
  expenses: () => request<{ expenses: Expense[] }>(businessPath('/expenses/')),
  createExpense: (payload: { category: string; amount: string; note?: string }) =>
    request<{ expense: Expense }>(businessPath('/expenses/'), {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  deleteExpense: (id: number) => request<{ message: string }>(businessPath(`/expenses/${id}/`), { method: 'DELETE' }),
  capitalEntries: () => request<{ entries: CapitalEntry[] }>(businessPath('/capital/')),
  createCapitalEntry: (payload: { entryType: 'owner_deposit' | 'owner_withdrawal'; amount: string; note?: string }) =>
    request<{ entry: CapitalEntry }>(businessPath('/capital/'), {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  burnRate: (days = 30) => request<BurnRateData>(`${businessPath('/planning/burn-rate/')}?days=${days}`),
  inventory: () => request<{ items: InventoryItem[] }>(businessPath('/inventory/')),
  createInventoryItem: (payload: {
    name: string
    quantity: number
    unit: string
    reorderLevel: number
    unitCost: string
  }) =>
    request<{ item: InventoryItem }>(businessPath('/inventory/'), {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  deleteInventoryItem: (id: number) =>
    request<{ message: string }>(businessPath(`/inventory/${id}/`), { method: 'DELETE' }),
  breakEven: (days = 30) => request<BreakEvenData>(`${businessPath('/planning/break-even/')}?days=${days}`),
}

export function formatNaira(value: string | number) {
  const amount = Number(value)
  return new Intl.NumberFormat('en-NG', {
    style: 'currency',
    currency: 'NGN',
    maximumFractionDigits: 0,
  }).format(Number.isFinite(amount) ? amount : 0)
}
