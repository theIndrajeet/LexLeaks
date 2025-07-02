'use client'

import { useState, useEffect } from 'react'
import { pushNotifications } from '@/lib/pushNotifications'

export default function TestPWA() {
  const [status, setStatus] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkStatus()
  }, [])

  const checkStatus = async () => {
    const checks = {
      // Environment Variables
      apiUrl: process.env.NEXT_PUBLIC_API_URL || 'NOT SET',
      vapidKey: process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY ? 'SET ✅' : 'NOT SET ❌',
      
      // PWA Support
      serviceWorker: 'serviceWorker' in navigator,
      pushManager: 'PushManager' in window,
      notification: 'Notification' in window,
      
      // Current Status
      notificationPermission: 'Notification' in window ? Notification.permission : 'not supported',
      
      // URLs
      currentUrl: window.location.origin,
      isProduction: window.location.hostname === 'lexleaks.com',
    }

    // Check service worker registration
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.getRegistration()
        checks.serviceWorkerRegistered = !!registration
        
        if (registration) {
          const subscription = await registration.pushManager.getSubscription()
          checks.pushSubscription = !!subscription
        }
      } catch (e: any) {
        checks.serviceWorkerError = e.message
      }
    }

    setStatus(checks)
    setLoading(false)
  }

  const testSubscribe = async () => {
    try {
      const result = await pushNotifications.init()
      if (result) {
        const subscription = await pushNotifications.subscribe()
        alert(subscription ? 'Subscribed successfully!' : 'Failed to subscribe')
        checkStatus()
      } else {
        alert('Permission denied')
      }
    } catch (error: any) {
      alert(`Error: ${error.message}`)
    }
  }

  const testNotification = async () => {
    try {
      await pushNotifications.showTestNotification()
      alert('Test notification sent!')
    } catch (error: any) {
      alert(`Error: ${error.message}`)
    }
  }

  if (loading) return <div className="p-8">Loading...</div>

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">PWA & Push Notification Test</h1>
        
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Environment Status</h2>
          <div className="space-y-2">
            <div>API URL: <code className="bg-gray-100 px-2 py-1">{status.apiUrl}</code></div>
            <div>VAPID Key: {status.vapidKey}</div>
            <div>Current URL: <code className="bg-gray-100 px-2 py-1">{status.currentUrl}</code></div>
            <div>Is Production: {status.isProduction ? '✅ Yes' : '❌ No'}</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Browser Support</h2>
          <div className="space-y-2">
            <div>Service Worker: {status.serviceWorker ? '✅ Supported' : '❌ Not Supported'}</div>
            <div>Push Manager: {status.pushManager ? '✅ Supported' : '❌ Not Supported'}</div>
            <div>Notifications: {status.notification ? '✅ Supported' : '❌ Not Supported'}</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Current Status</h2>
          <div className="space-y-2">
            <div>Permission: <span className="font-semibold">{status.notificationPermission}</span></div>
            <div>Service Worker: {status.serviceWorkerRegistered ? '✅ Registered' : '❌ Not Registered'}</div>
            <div>Push Subscription: {status.pushSubscription ? '✅ Active' : '❌ Not Subscribed'}</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Actions</h2>
          <div className="space-x-4">
            <button
              onClick={testSubscribe}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Subscribe to Notifications
            </button>
            <button
              onClick={testNotification}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            >
              Send Test Notification
            </button>
            <button
              onClick={checkStatus}
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              Refresh Status
            </button>
          </div>
        </div>

        <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-sm">
            <strong>Note:</strong> This page helps verify your PWA setup. 
            {!status.isProduction && ' You are not on the production site.'}
          </p>
        </div>
      </div>
    </div>
  )
}