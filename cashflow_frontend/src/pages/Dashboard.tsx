// src/pages/Dashboard.tsx

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { TrendingUp, TrendingDown, DollarSign, Receipt, Package, AlertCircle } from 'lucide-react'

export default function Dashboard() {
  return (
    <div className="p-4 md:p-6 space-y-6">
      
      {/* Header */}
      <div>
        <h1 className="text-2xl md:text-3xl font-bold text-neutral-900">Good morning, Amina 👋</h1>
        <p className="text-sm text-neutral-500 mt-1">Here's what's happening with your business today</p>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
        
        {/* Total Sales */}
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-orange-500" />
              Sales Today
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₦47,500</div>
            <div className="flex items-center gap-1 text-xs text-green-600 mt-1">
              <TrendingUp className="w-3 h-3" />
              <span>12% vs yesterday</span>
            </div>
          </CardContent>
        </Card>

        {/* Expenses */}
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <Receipt className="w-4 h-4 text-red-500" />
              Expenses
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₦18,200</div>
            <div className="flex items-center gap-1 text-xs text-green-600 mt-1">
              <TrendingDown className="w-3 h-3" />
              <span>3% lower</span>
            </div>
          </CardContent>
        </Card>

        {/* Net Profit */}
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-green-600" />
              Net Profit
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">₦29,300</div>
            <div className="flex items-center gap-1 text-xs text-green-600 mt-1">
              <TrendingUp className="w-3 h-3" />
              <span>24% increase</span>
            </div>
          </CardContent>
        </Card>

        {/* Transactions */}
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <Package className="w-4 h-4 text-blue-500" />
              Transactions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">34</div>
            <div className="flex items-center gap-1 text-xs text-neutral-500 mt-1">
              <span>+6 more today</span>
            </div>
          </CardContent>
        </Card>

      </div>

      {/* Two Column Layout */}
      <div className="grid md:grid-cols-3 gap-4 md:gap-6">
        
        {/* Recent Activity */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Your latest transactions</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            
            {[
              { type: 'sale', item: 'Onion bulk sale', time: '10:32 AM', amount: '+₦8,500', positive: true },
              { type: 'expense', item: 'Transport cost', time: '9:15 AM', amount: '-₦2,000', positive: false },
              { type: 'sale', item: 'Pepper sale', time: '8:50 AM', amount: '+₦4,200', positive: true },
              { type: 'expense', item: 'Market levy', time: '8:00 AM', amount: '-₦500', positive: false },
            ].map((txn, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  txn.positive ? 'bg-green-50' : 'bg-red-50'
                }`}>
                  {txn.positive ? (
                    <TrendingUp className="w-5 h-5 text-green-600" />
                  ) : (
                    <TrendingDown className="w-5 h-5 text-red-600" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-neutral-900 truncate">{txn.item}</p>
                  <p className="text-xs text-neutral-500">{txn.time}</p>
                </div>
                <div className={`text-sm font-semibold ${
                  txn.positive ? 'text-green-600' : 'text-red-600'
                }`}>
                  {txn.amount}
                </div>
              </div>
            ))}

          </CardContent>
        </Card>

        {/* Quick Stats */}
        <div className="space-y-4">
          
          {/* Capital Status */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Capital Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs text-neutral-500">Initial Capital</span>
                  <span className="text-sm font-semibold">₦100,000</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-neutral-500">Current Capital</span>
                  <span className="text-sm font-semibold text-green-600">₦129,300</span>
                </div>
              </div>
              <Separator />
              <div className="flex items-center gap-2 text-xs text-green-600">
                <TrendingUp className="w-3 h-3" />
                <span>29% growth this month</span>
              </div>
            </CardContent>
          </Card>

          {/* Low Stock Alert */}
          <Card className="border-orange-200 bg-orange-50">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-orange-600" />
                <CardTitle className="text-base">Low Stock Alert</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-neutral-700">Tomatoes</span>
                <Badge variant="outline" className="text-orange-600 border-orange-300">
                  2 days left
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-neutral-700">Peppers</span>
                <Badge variant="outline" className="text-orange-600 border-orange-300">
                  3 days left
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Top Selling Item */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Top Selling</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center">
                <div className="text-3xl mb-1">🍅</div>
                <p className="text-sm font-semibold">Tomatoes</p>
                <p className="text-xs text-neutral-500 mt-1">₦18,000 today</p>
              </div>
            </CardContent>
          </Card>

        </div>

      </div>

      {/* Weekly Performance */}
      <Card>
        <CardHeader>
          <CardTitle>Weekly Performance</CardTitle>
          <CardDescription>Sales vs Expenses — Last 7 days</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-end justify-around gap-2">
            {[
              { day: 'Mon', sales: 65, expenses: 35 },
              { day: 'Tue', sales: 78, expenses: 42 },
              { day: 'Wed', sales: 58, expenses: 38 },
              { day: 'Thu', sales: 92, expenses: 48 },
              { day: 'Fri', sales: 85, expenses: 40 },
              { day: 'Sat', sales: 95, expenses: 52 },
              { day: 'Sun', sales: 70, expenses: 35 },
            ].map((data, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full flex flex-col gap-1 items-center">
                  <div
                    className="w-full bg-orange-500 rounded-t"
                    style={{ height: `${data.sales}%` }}
                  />
                  <div
                    className="w-full bg-green-500 rounded-t"
                    style={{ height: `${data.expenses}%` }}
                  />
                </div>
                <span className="text-xs text-neutral-500">{data.day}</span>
              </div>
            ))}
          </div>
          <div className="flex items-center justify-center gap-6 mt-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-orange-500 rounded" />
              <span className="text-xs text-neutral-600">Sales</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded" />
              <span className="text-xs text-neutral-600">Expenses</span>
            </div>
          </div>
        </CardContent>
      </Card>

    </div>
  )
}