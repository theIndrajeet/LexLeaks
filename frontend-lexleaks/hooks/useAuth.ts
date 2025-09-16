import { useEffect } from 'react'
import { refreshToken } from '@/lib/api'

export function useAuth() {
  useEffect(() => {
    // Refresh token every 25 minutes (before 30-day expiration)
    const interval = setInterval(async () => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        await refreshToken()
      }
    }, 25 * 60 * 1000) // 25 minutes

    return () => clearInterval(interval)
  }, [])
}
