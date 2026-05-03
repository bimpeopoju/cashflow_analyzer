// src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import AuthPage from './pages/AuthPage'
import Dashboard from './pages/Dashboard'
import PageWrapper from './components/layout/PageWrapper'

// Placeholder pages
function SalesPage() {
  return (
    <PageWrapper>
      <div className="p-6">
        <h1 className="text-2xl font-bold">Sales</h1>
        <p className="text-neutral-500">Coming soon...</p>
      </div>
    </PageWrapper>
  )
}

function ExpensesPage() {
  return (
    <PageWrapper>
      <div className="p-6">
        <h1 className="text-2xl font-bold">Expenses</h1>
        <p className="text-neutral-500">Coming soon...</p>
      </div>
    </PageWrapper>
  )
}

function InventoryPage() {
  return (
    <PageWrapper>
      <div className="p-6">
        <h1 className="text-2xl font-bold">Inventory</h1>
        <p className="text-neutral-500">Coming soon...</p>
      </div>
    </PageWrapper>
  )
}

function ReportsPage() {
  return (
    <PageWrapper>
      <div className="p-6">
        <h1 className="text-2xl font-bold">Reports</h1>
        <p className="text-neutral-500">Coming soon...</p>
      </div>
    </PageWrapper>
  )
}

function ProfilePage() {
  return (
    <PageWrapper>
      <div className="p-6">
        <h1 className="text-2xl font-bold">Profile</h1>
        <p className="text-neutral-500">Coming soon...</p>
      </div>
    </PageWrapper>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/login" element={<Navigate to="/auth" replace />} />
        <Route path="/register" element={<Navigate to="/auth" replace />} />
        
        <Route path="/dashboard" element={<PageWrapper><Dashboard /></PageWrapper>} />
        <Route path="/sales" element={<SalesPage />} />
        <Route path="/expenses" element={<ExpensesPage />} />
        <Route path="/inventory" element={<InventoryPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}