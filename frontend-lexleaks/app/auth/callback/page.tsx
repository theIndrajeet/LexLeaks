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
        const googleAuth = GoogleAuthService.getInstance()
        const result = googleAuth.handleAuthCallback()
        
        if (result) {
          setStatus('success')
          setMessage('Login successful! Redirecting...')
          
          // Redirect to appropriate page based on user role
          setTimeout(async () => {
            // Check if user is admin
            try {
              const userInfo = await googleAuth.getGoogleUserInfo()
              if (userInfo.is_admin) {
                router.push('/admin/dashboard')
              } else {
                router.push('/')
              }
            } catch (error) {
              // If we can't get user info, redirect to home
              router.push('/')
            }
          }, 2000)
        } else {
          setStatus('error')
          setMessage('Authentication failed. Please try again.')
        }
      } catch (error: any) {
        setStatus('error')
        setMessage('Authentication error: ' + error.message)
      }
    }

    handleCallback()
  }, [router])

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
