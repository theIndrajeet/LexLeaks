import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function GET(request: NextRequest) {
  const url = new URL(request.url)
  const code = url.searchParams.get('code')
  const error = url.searchParams.get('error_description') || url.searchParams.get('error')

  // If Supabase returned an error, forward to error page
  if (error) {
    const errorUrl = new URL(`/auth/error?error=${encodeURIComponent(error)}`, url.origin)
    return NextResponse.redirect(errorUrl)
  }

  if (code) {
    try {
      const supabase = await createClient()
      const { error: exchangeError } = await supabase.auth.exchangeCodeForSession(code)
      if (exchangeError) {
        const errUrl = new URL(`/auth/error?error=${encodeURIComponent(exchangeError.message)}`, url.origin)
        return NextResponse.redirect(errUrl)
      }
    } catch (e: any) {
      const errUrl = new URL(`/auth/error?error=${encodeURIComponent(e?.message || 'Authentication failed')}`, url.origin)
      return NextResponse.redirect(errUrl)
    }
  }

  // Clean redirect with no querystring
  return NextResponse.redirect(new URL('/', url.origin))
}


