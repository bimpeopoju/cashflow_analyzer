// src/pages/AuthPage.tsx

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import LoginForm from '@/components/auth/LoginForm'
import RegisterForm from '@/components/auth/RegisterForm'

type AuthMode = 'login' | 'register'

export default function AuthPage() {
  const [mode, setMode] = useState<AuthMode>('login')
  const navigate = useNavigate()

  const handleSuccess = () => {
    // After successful login/register, redirect to dashboard
    navigate('/dashboard')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-50 via-white to-green-50 p-4">
      <div className="w-full max-w-md">
        
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-orange-500 rounded-lg mx-auto mb-3" />
          <h1 className="text-2xl font-bold">MarketFlow</h1>
          <p className="text-sm text-neutral-500">Cash tracker for Nigerian traders</p>
        </div>

        <Card>
          <CardHeader>
            <div className="flex gap-1 mb-4 bg-stone-100 p-1 rounded-lg">
              <button
                onClick={() => setMode('login')}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  mode === 'login'
                    ? 'bg-white shadow-sm text-neutral-900'
                    : 'text-neutral-600 hover:text-neutral-900'
                }`}
              >
                Sign In
              </button>
              <button
                onClick={() => setMode('register')}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  mode === 'register'
                    ? 'bg-white shadow-sm text-neutral-900'
                    : 'text-neutral-600 hover:text-neutral-900'
                }`}
              >
                Create Account
              </button>
            </div>

            <CardTitle>
              {mode === 'login' ? 'Welcome back' : 'Get started'}
            </CardTitle>
            <CardDescription>
              {mode === 'login'
                ? 'Enter your credentials to access your account'
                : 'Create an account to start tracking your sales'}
            </CardDescription>
          </CardHeader>

          <CardContent>
            {mode === 'login' ? (
              <LoginForm onSuccess={handleSuccess} />
            ) : (
              <RegisterForm onSuccess={handleSuccess} />
            )}
          </CardContent>
        </Card>

        {/* Footer link */}
        <p className="text-center text-sm text-neutral-500 mt-6">
          {mode === 'login' ? (
            <>
              Don't have an account?{' '}
              <button
                onClick={() => setMode('register')}
                className="text-orange-600 hover:text-orange-700 font-medium"
              >
                Sign up
              </button>
            </>
          ) : (
            <>
              Already have an account?{' '}
              <button
                onClick={() => setMode('login')}
                className="text-orange-600 hover:text-orange-700 font-medium"
              >
                Sign in
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  )
}