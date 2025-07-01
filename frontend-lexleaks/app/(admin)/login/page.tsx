'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { login } from '@/lib/api'

export default function AdminLoginPage() {
  const router = useRouter()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(username, password)
      router.push('/admin/dashboard')
    } catch (err: any) {
      setError(err.message || 'Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">LEXLEAKS</h1>
          <p className="font-mono-special text-sm uppercase tracking-wide text-gray-600">
            Administrative Access
          </p>
        </div>

        {/* Login Form */}
        <div className="border-2 brand-border rounded-lg p-8 bg-white">
          <div className="mb-6">
            <div className="case-file text-center">
              <span>Secure Login Portal</span>
              {' | '}
              <span>Authorized Personnel Only</span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-bold font-mono-special uppercase tracking-wide mb-2">
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="admin-input w-full"
                required
                autoComplete="username"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-bold font-mono-special uppercase tracking-wide mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="admin-input w-full"
                required
                autoComplete="current-password"
              />
            </div>

            {error && (
              <div className="border border-red-300 bg-red-50 rounded p-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full brand-button disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Authenticating...' : 'Access Dashboard'}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t brand-border">
            <p className="text-center text-sm text-gray-600">
              <Link href="/" className="nav-link">
                ← Return to Public Site
              </Link>
            </p>
          </div>
        </div>

        {/* Security Notice */}
        <div className="mt-8 text-center">
          <p className="text-xs font-mono-special text-gray-500">
            This area is restricted to authorized administrators only.<br />
            All access attempts are logged for security purposes.
          </p>
        </div>
      </div>
    </div>
  )
} 