import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import type { ReactNode } from 'react'
import PageWrapper from './components/layout/PageWrapper'
import AuthPage from './pages/AuthPage'
import Dashboard from './pages/Dashboard'
import ExpensesPage from './pages/ExpensesPage'
import InventoryPage from './pages/InventoryPage'
import LandingPage from './pages/LandingPage'
import ProfilePage from './pages/ProfilePage'
import ReportsPage from './pages/ReportsPage'
import SalesPage from './pages/SalesPage'

function AppShell({ children }: { children: ReactNode }) {
  return <PageWrapper>{children}</PageWrapper>
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/login" element={<Navigate to="/auth" replace />} />
        <Route path="/register" element={<Navigate to="/auth" replace />} />
        <Route path="/dashboard" element={<AppShell><Dashboard /></AppShell>} />
        <Route path="/sales" element={<AppShell><SalesPage /></AppShell>} />
        <Route path="/expenses" element={<AppShell><ExpensesPage /></AppShell>} />
        <Route path="/inventory" element={<AppShell><InventoryPage /></AppShell>} />
        <Route path="/reports" element={<AppShell><ReportsPage /></AppShell>} />
        <Route path="/profile" element={<AppShell><ProfilePage /></AppShell>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
