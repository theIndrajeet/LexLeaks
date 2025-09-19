import { useEffect } from 'react'
import { supabase } from '@/lib/supabaseAuth'

export function useAuth() {
  useEffect(() => {
    // Supabase handles token refresh automatically
    // No need for manual token refresh with Supabase Auth
    console.log('Supabase Auth initialized - automatic token management enabled')
  }, [])
}
