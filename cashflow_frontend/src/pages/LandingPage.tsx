import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-green-50">
      <header className="border-b bg-white/80 backdrop-blur">
        <div className="container mx-auto flex items-center justify-between px-4 py-4">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-orange-500" />
            <span className="text-lg font-bold">MarketFlow</span>
          </div>
          <div className="flex gap-2">
            <Button variant="ghost" onClick={() => navigate('/auth')}>Login</Button>
            <Button onClick={() => navigate('/auth')}>Get Started</Button>
          </div>
        </div>
      </header>

      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="mb-4 text-4xl font-bold text-neutral-900 md:text-5xl">
          Cash Flow Made Simple for<br />
          <span className="text-orange-500">Nigerian Market Traders</span>
        </h1>
        <p className="mx-auto mb-8 max-w-2xl text-lg text-neutral-600">
          Track daily sales, manage expenses, separate capital from profit, and stay ready for FIRS tax obligations - all in one simple app.
        </p>
        <div className="flex justify-center gap-4">
          <Button size="lg" onClick={() => navigate('/auth')}>Start Free Trial</Button>
          <Button size="lg" variant="outline" onClick={() => navigate('/login')}>Sign In</Button>
        </div>
      </section>

      <section className="container mx-auto px-4 py-16">
        <div className="grid gap-6 md:grid-cols-3">
          <FeatureCard marker="NGN" title="Capital Protection" description="Never confuse business capital with daily profit again." />
          <FeatureCard marker="UP" title="Real Profit Tracking" description="See actual profit after all costs, not just sales minus expenses." />
          <FeatureCard marker="TAX" title="Tax Readiness" description="Keep clean records so tax estimates do not catch you off guard." />
        </div>
      </section>

      <section className="bg-white py-16">
        <div className="container mx-auto px-4">
          <h2 className="mb-12 text-center text-3xl font-bold">
            Built for the problems Nigerian traders actually face
          </h2>
          <div className="mx-auto grid max-w-4xl gap-8 md:grid-cols-2">
            <Problem title="Capital confusion" description="Traders spend business money on personal needs without realizing it." />
            <Problem title="No profit tracking" description="Sales are tracked mentally or not at all, so true profit is never calculated." />
            <Problem title="Tax non-compliance" description="Obligations become visible only when records are already missing." />
            <Problem title="No burn-rate awareness" description="Stock runs low before the trader knows when to restock." />
          </div>
        </div>
      </section>

      <footer className="border-t bg-white py-8">
        <div className="container mx-auto px-4 text-center text-sm text-neutral-500">
          <p>Copyright 2026 MarketFlow. Built for informal traders across Nigeria.</p>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ marker, title, description }: { marker: string; title: string; description: string }) {
  return (
    <Card>
      <CardHeader>
        <div className="mb-2 flex h-12 w-12 items-center justify-center rounded-lg bg-orange-100 text-sm font-bold text-orange-700">
          {marker}
        </div>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
    </Card>
  )
}

function Problem({ title, description }: { title: string; description: string }) {
  return (
    <div className="flex gap-4">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-red-100 text-red-600">x</div>
      <div>
        <h3 className="mb-1 font-semibold">{title}</h3>
        <p className="text-sm text-neutral-600">{description}</p>
      </div>
    </div>
  )
}
