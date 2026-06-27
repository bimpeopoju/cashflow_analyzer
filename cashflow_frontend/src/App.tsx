import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import type { ReactNode } from 'react'
import PageWrapper from './components/layout/PageWrapper'
import { AuthProvider, ProtectedRoute } from './lib/auth'
import AuthPage from './pages/AuthPage'
import BurnRatePage from './pages/BurnRatePage'
import Dashboard from './pages/Dashboard'
import ExpensesPage from './pages/ExpensesPage'
import ForecastsPage from './pages/ForecastsPage'
import InventoryPage from './pages/InventoryPage'
import LandingPage from './pages/LandingPage'
import ProfilePage from './pages/ProfilePage'
import ReportsPage from './pages/ReportsPage'
import SalesPage from './pages/SalesPage'
import TaxesPage from './pages/TaxesPage'

function AppShell({ children }: { children: ReactNode }) {
  return <PageWrapper>{children}</PageWrapper>
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/login" element={<Navigate to="/auth" replace />} />
          <Route path="/register" element={<Navigate to="/auth" replace />} />
          <Route path="/dashboard" element={<ProtectedApp><Dashboard /></ProtectedApp>} />
          <Route path="/sales" element={<ProtectedApp><SalesPage /></ProtectedApp>} />
          <Route path="/expenses" element={<ProtectedApp><ExpensesPage /></ProtectedApp>} />
          <Route path="/inventory" element={<ProtectedApp><InventoryPage /></ProtectedApp>} />
          <Route path="/planning" element={<ProtectedApp><BurnRatePage /></ProtectedApp>} />
          <Route path="/forecasts" element={<ProtectedApp><ForecastsPage /></ProtectedApp>} />
          <Route path="/reports" element={<ProtectedApp><ReportsPage /></ProtectedApp>} />
          <Route path="/taxes" element={<ProtectedApp><TaxesPage /></ProtectedApp>} />
          <Route path="/profile" element={<ProtectedApp><ProfilePage /></ProtectedApp>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

function ProtectedApp({ children }: { children: ReactNode }) {
  return (
    <ProtectedRoute>
      <AppShell>{children}</AppShell>
    </ProtectedRoute>
  )
}
