'use client'

import { useEffect, useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { GoogleAuthService } from '@/lib/googleAuth'

function AuthCallbackContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const code = searchParams.get('code')
        const state = searchParams.get('state')
        
        if (code && state) {
          // We have OAuth code and state, need to exchange for token
          setStatus('loading')
          setMessage('Exchanging authorization code...')
          
          try {
            // Send the code to backend to exchange for token
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
            const response = await fetch(`${apiUrl}/api/auth/google/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state)}`, {
              method: 'GET',
              credentials: 'include'
            })
            
            if (response.ok) {
              // Backend should redirect us to success page with token
              // If we get here, something went wrong
              setStatus('error')
              setMessage('Unexpected response from server')
            } else {
              setStatus('error')
              setMessage('Failed to exchange authorization code')
            }
          } catch (error: any) {
            setStatus('error')
            setMessage('Network error: ' + error.message)
          }
        } else {
          // Check for existing token (legacy flow)
          const googleAuth = GoogleAuthService.getInstance()
          const result = googleAuth.handleAuthCallback()
          
          if (result) {
            setStatus('success')
            setMessage('Login successful! Redirecting...')
            
            // Redirect to appropriate page based on user role
            setTimeout(async () => {
              try {
                const userInfo = await googleAuth.getGoogleUserInfo()
                if (userInfo.is_admin) {
                  router.push('/admin/dashboard')
                } else {
                  router.push('/')
                }
              } catch (error) {
                router.push('/')
              }
            }, 2000)
          } else {
            setStatus('error')
            setMessage('No authorization code or token found')
          }
        }
      } catch (error: any) {
        setStatus('error')
        setMessage('Authentication error: ' + error.message)
      }
    }

    handleCallback()
  }, [router, searchParams])

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10 text-center">
          {status === 'loading' && (
            <>
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Completing authentication...</p>
            </>
          )}
          
          {status === 'success' && (
            <>
              <div className="text-green-600 text-4xl mb-4">✓</div>
              <p className="text-green-600 font-medium">{message}</p>
            </>
          )}
          
          {status === 'error' && (
            <>
              <div className="text-red-600 text-4xl mb-4">✗</div>
              <p className="text-red-600 font-medium">{message}</p>
              <button
                onClick={() => router.push('/admin/login')}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Try Again
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading...</p>
          </div>
        </div>
      </div>
    }>
      <AuthCallbackContent />
    </Suspense>
  )
}
