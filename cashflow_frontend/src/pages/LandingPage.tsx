// src/pages/LandingPage.tsx

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useNavigate } from 'react-router-dom'

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-green-50">
      
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-orange-500 rounded-lg" />
            <span className="font-bold text-lg">MarketFlow</span>
          </div>
          <div className="flex gap-2">
            <Button variant="ghost" onClick={() => navigate('/auth')}>
              Login
            </Button>
            <Button onClick={() => navigate('/auth')}>
              Get Started
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl font-bold mb-4 text-neutral-900">
          Cash Flow Made Simple for<br />
          <span className="text-orange-500">Nigerian Market Traders</span>
        </h1>
        <p className="text-lg text-neutral-600 mb-8 max-w-2xl mx-auto">
          Track daily sales, manage expenses, separate capital from profit, and stay compliant with FIRS tax regulations — all in one simple app.
        </p>
        <div className="flex gap-4 justify-center">
          <Button size="lg" onClick={() => navigate('/auth')}>
            Start Free Trial
          </Button>
          <Button size="lg" variant="outline" onClick={() => navigate('/login')}>
            Sign In
          </Button>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-2">
                <span className="text-2xl">💰</span>
              </div>
              <CardTitle>Capital Protection</CardTitle>
              <CardDescription>
                Never confuse business capital with daily profit again
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-2">
                <span className="text-2xl">📊</span>
              </div>
              <CardTitle>Real Profit Tracking</CardTitle>
              <CardDescription>
                See actual profit after all costs — not just sales minus expenses
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-2">
                <span className="text-2xl">🧾</span>
              </div>
              <CardTitle>Tax Compliance</CardTitle>
              <CardDescription>
                Get FIRS-aligned tax estimates so you're never caught off guard
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* Problem Section */}
      <section className="bg-white py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">
            Built for the problems Nigerian traders actually face
          </h2>
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center flex-shrink-0">
                ✕
              </div>
              <div>
                <h3 className="font-semibold mb-1">Capital confusion</h3>
                <p className="text-sm text-neutral-600">
                  Traders spend business money on personal needs without realizing it
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center flex-shrink-0">
                ✕
              </div>
              <div>
                <h3 className="font-semibold mb-1">No profit tracking</h3>
                <p className="text-sm text-neutral-600">
                  Sales are tracked mentally or not at all — true profit is never calculated
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center flex-shrink-0">
                ✕
              </div>
              <div>
                <h3 className="font-semibold mb-1">Tax non-compliance</h3>
                <p className="text-sm text-neutral-600">
                  Unaware of FIRS obligations until it's too late
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center flex-shrink-0">
                ✕
              </div>
              <div>
                <h3 className="font-semibold mb-1">No burn rate awareness</h3>
                <p className="text-sm text-neutral-600">
                  Don't know how fast stock is moving or when to restock
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-white py-8">
        <div className="container mx-auto px-4 text-center text-sm text-neutral-500">
          <p>© 2026 MarketFlow · Built for informal traders across Nigeria</p>
        </div>
      </footer>

    </div>
  )
}