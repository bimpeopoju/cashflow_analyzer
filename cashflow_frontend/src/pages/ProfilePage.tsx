import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { type User, api, formatNaira, getErrorMessage } from '@/lib/api'

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    api.me()
      .then((data) => setUser(data.user))
      .catch((err: unknown) => setError(getErrorMessage(err, 'Could not load profile.')))
  }, [])

  const signOut = async () => {
    await api.logout()
    navigate('/auth')
  }

  if (error) return <div className="p-6 text-sm text-red-700">{error}</div>
  if (!user) return <div className="p-6 text-sm text-neutral-500">Loading profile...</div>

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 md:text-3xl">Profile</h1>
        <p className="mt-1 text-sm text-neutral-500">Account and business details.</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>{user.fullName}</CardTitle>
          <CardDescription>{user.email}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-3">
            <Info label="Business" value={user.businessName} />
            <Info label="Stall" value={user.stallName || 'Market stall'} />
            <Info label="Initial Capital" value={formatNaira(user.initialCapital)} />
          </div>
          <Button type="button" variant="outline" onClick={signOut}>Sign Out</Button>
        </CardContent>
      </Card>
    </div>
  )
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-3">
      <p className="text-xs text-neutral-500">{label}</p>
      <p className="mt-1 text-sm font-semibold text-neutral-900">{value}</p>
    </div>
  )
}
