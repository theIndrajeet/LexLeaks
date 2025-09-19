import { useEffect } from 'react'
import { refreshToken } from '@/lib/api'

export function useAuth() {
  useEffect(() => {
    // Refresh token every 24 hours for 30-day sessions
    // This ensures the token stays fresh without unnecessary requests
    const interval = setInterval(async () => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        try {
          await refreshToken()
        } catch (error) {
          // If refresh fails, user will need to log in again
          console.warn('Token refresh failed, user may need to log in again')
        }
      }
    }, 24 * 60 * 60 * 1000) // 24 hours

    return () => clearInterval(interval)
  }, [])
}
