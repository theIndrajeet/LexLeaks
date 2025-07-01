'use client'

import { ReactNode, useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { checkAuthStatus } from '@/lib/api'

export default function AdminLayout({ children }: { children: ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const verifyAuth = async () => {
      const user = await checkAuthStatus()
      
      // If not logged in and not on login page, redirect to login
      if (!user && pathname !== '/admin/login') {
        router.push('/admin/login')
      }
      // If logged in and on login page, redirect to dashboard
      else if (user && pathname === '/admin/login') {
        router.push('/admin/dashboard')
      }
      
      setLoading(false)
    }

    verifyAuth()
  }, [pathname, router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center brand-bg">
        <div className="text-center">
          <div className="loading-skeleton h-8 w-32 mx-auto mb-4 rounded"></div>
          <div className="loading-skeleton h-4 w-24 mx-auto rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen brand-bg">
      {children}
    </div>
  )
} 