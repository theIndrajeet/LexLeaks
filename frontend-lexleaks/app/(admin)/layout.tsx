'use client'

import { ReactNode, useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { supabase } from '@/lib/supabaseAuth'

export default function AdminLayout({ children }: { children: ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const verifyAuth = async () => {
      const { data } = await supabase.auth.getUser()
      const supaUser = data?.user
      const isAdmin = Boolean(supaUser?.user_metadata?.is_admin)

      // Not logged in or not admin → only allow /admin/login
      if ((!supaUser || !isAdmin) && pathname !== '/admin/login') {
        router.replace('/admin/login')
        setLoading(false)
        return
      }

      // Logged in + admin → prevent seeing login page
      if (supaUser && isAdmin && pathname === '/admin/login') {
        router.replace('/admin/dashboard')
        setLoading(false)
        return
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