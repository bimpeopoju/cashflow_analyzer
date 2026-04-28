// src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import AuthPage from './pages/AuthPage'
import PageWrapper from './components/layout/PageWrapper'

// Placeholder components — you'll build these next
function Dashboard() {
  return (
    <PageWrapper>
      <div className="p-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-neutral-500">Coming soon...</p>
      </div>
    </PageWrapper>
  )
}

function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-stone-50">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-2">Login</h1>
        <p className="text-neutral-500">Form coming next...</p>
      </div>
    </div>
  )
}

function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-stone-50">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-2">Register</h1>
        <p className="text-neutral-500">Form coming next...</p>
      </div>
    </div>
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
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}