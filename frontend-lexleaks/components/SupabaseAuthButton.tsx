'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useSupabaseAuth } from '@/hooks/useSupabaseAuth'

interface SupabaseAuthButtonProps {
  className?: string
  showUserInfo?: boolean
}

export default function SupabaseAuthButton({ className = '', showUserInfo = true }: SupabaseAuthButtonProps) {
  const { user, loading: authLoading, signInWithGoogle, signOut } = useSupabaseAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGoogleLogin = async () => {
    try {
      setLoading(true)
      setError(null)
      await signInWithGoogle()
    } catch (err: any) {
      setError(err.message || 'Login failed')
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    try {
      await signOut()
      // Redirect to home page
      window.location.href = '/'
    } catch (err: any) {
      console.error('Logout error:', err)
    }
  }

  if (user) {
    const isAdmin = user.user_metadata?.is_admin || false
    const userName = user.user_metadata?.full_name || user.email || 'User'
    const userPicture = user.user_metadata?.avatar_url || user.user_metadata?.picture

    return (
      <div className={`flex items-center gap-3 ${className}`}>
        {showUserInfo && (
          <div className="flex items-center gap-2">
            {userPicture && (
              <img 
                src={userPicture} 
                alt={userName} 
                className="w-8 h-8 rounded-full border-2 border-gray-300 dark:border-gray-600"
              />
            )}
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {userName}
            </span>
            {isAdmin && (
              <span className="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full">
                Admin
              </span>
            )}
          </div>
        )}
        {isAdmin && (
          <Link
            href="/admin/dashboard"
            className="px-3 py-2 text-sm font-medium brand-button rounded-md transition-all duration-200 hover:shadow-md"
          >
            Admin Panel
          </Link>
        )}
        <button
          onClick={handleLogout}
          className="px-4 py-2 text-sm font-medium brand-text bg-transparent border border-brand-accent/30 hover:bg-brand-accent/10 rounded-md transition-all duration-200"
        >
          Logout
        </button>
      </div>
    )
  }

  if (authLoading) {
    return (
      <div className={className}>
        <div className="flex items-center gap-3 px-6 py-3 text-sm font-medium brand-button border border-brand-accent/20 opacity-50">
          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
          <span>Loading...</span>
        </div>
      </div>
    )
  }

  return (
    <div className={className}>
      <button
        onClick={handleGoogleLogin}
        disabled={loading}
        className="flex items-center gap-3 px-6 py-3 text-sm font-medium brand-button border border-brand-accent/20 hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
            <span>Signing in...</span>
          </>
        ) : (
          <>
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="currentColor"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="currentColor"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="currentColor"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            <span>Continue with Google</span>
          </>
        )}
      </button>
      {error && (
        <p className="mt-2 text-sm text-red-600 dark:text-red-400">{error}</p>
      )}
    </div>
  )
}