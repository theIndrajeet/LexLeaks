"use client"

import { useState, useEffect } from 'react'
import { notificationManager, type NotificationPermission } from '@/lib/notificationManager'

interface NotificationManagerProps {
  onPermissionChange?: (permission: NotificationPermission) => void
}

export default function NotificationManager({ onPermissionChange }: NotificationManagerProps) {
  const [isSupported, setIsSupported] = useState(false)
  const [permission, setPermission] = useState<NotificationPermission>({ granted: false, denied: false, default: true })
  const [isSubscribed, setIsSubscribed] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    initializeNotifications()
  }, [])

  const initializeNotifications = async () => {
    try {
      setIsLoading(true)
      setError(null)

      // Check if notifications are supported
      const supported = notificationManager.isSupported()
      setIsSupported(supported)

      if (!supported) {
        setError('Notifications are not supported in this browser')
        return
      }

      // Initialize notification manager
      const initialized = await notificationManager.initialize()
      if (!initialized) {
        setError('Failed to initialize notification manager')
        return
      }

      // Get current permission status
      const currentPermission = notificationManager.getPermissionStatus()
      setPermission(currentPermission)
      onPermissionChange?.(currentPermission)

      // Check if user is subscribed
      const subscribed = await notificationManager.isSubscribed()
      setIsSubscribed(subscribed)

    } catch (err) {
      console.error('Error initializing notifications:', err)
      setError('Failed to initialize notifications')
    } finally {
      setIsLoading(false)
    }
  }

  const requestPermission = async () => {
    try {
      setIsLoading(true)
      setError(null)

      const newPermission = await notificationManager.requestPermission()
      setPermission(newPermission)
      onPermissionChange?.(newPermission)

      if (newPermission.granted) {
        // Auto-subscribe after permission is granted
        await subscribeToNotifications()
      } else if (newPermission.denied) {
        setError('Notification permission was denied. You can enable it in your browser settings.')
      }

    } catch (err) {
      console.error('Error requesting permission:', err)
      setError('Failed to request notification permission')
    } finally {
      setIsLoading(false)
    }
  }

  const subscribeToNotifications = async () => {
    try {
      setIsLoading(true)
      setError(null)

      const success = await notificationManager.subscribeToPush()
      if (success) {
        setIsSubscribed(true)
      } else {
        setError('Failed to subscribe to notifications')
      }

    } catch (err) {
      console.error('Error subscribing to notifications:', err)
      setError('Failed to subscribe to notifications')
    } finally {
      setIsLoading(false)
    }
  }

  const unsubscribeFromNotifications = async () => {
    try {
      setIsLoading(true)
      setError(null)

      const success = await notificationManager.unsubscribeFromPush()
      if (success) {
        setIsSubscribed(false)
      } else {
        setError('Failed to unsubscribe from notifications')
      }

    } catch (err) {
      console.error('Error unsubscribing from notifications:', err)
      setError('Failed to unsubscribe from notifications')
    } finally {
      setIsLoading(false)
    }
  }

  const testNotification = async () => {
    try {
      await notificationManager.showLocalNotification(
        '🔔 Test Notification',
        {
          body: 'This is a test notification from LexLeaks!',
          icon: '/icon-192x192.png',
          tag: 'test-notification'
        }
      )
    } catch (err) {
      console.error('Error showing test notification:', err)
      setError('Failed to show test notification')
    }
  }

  if (!isSupported) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-center">
          <span className="text-yellow-600 text-xl mr-3">⚠️</span>
          <div>
            <h3 className="text-yellow-800 font-medium">Notifications Not Supported</h3>
            <p className="text-yellow-700 text-sm mt-1">
              Your browser doesn't support push notifications. Please use a modern browser like Chrome, Firefox, or Safari.
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <span className="text-red-600 text-xl mr-3">❌</span>
            <div>
              <h3 className="text-red-800 font-medium">Error</h3>
              <p className="text-red-700 text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Permission Status */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-medium text-gray-900">🔔 Push Notifications</h3>
            <p className="text-gray-600 text-sm mt-1">
              {permission.granted && isSubscribed && '✅ Enabled - You\'ll receive notifications'}
              {permission.granted && !isSubscribed && '⚠️ Permission granted but not subscribed'}
              {permission.denied && '❌ Disabled - Permission denied'}
              {permission.default && 'ℹ️ Not configured - Click to enable'}
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            {permission.granted && isSubscribed ? (
              <>
                <button
                  onClick={testNotification}
                  disabled={isLoading}
                  className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 disabled:opacity-50"
                >
                  🧪 Test
                </button>
                <button
                  onClick={unsubscribeFromNotifications}
                  disabled={isLoading}
                  className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200 disabled:opacity-50"
                >
                  Disable
                </button>
              </>
            ) : permission.granted && !isSubscribed ? (
              <button
                onClick={subscribeToNotifications}
                disabled={isLoading}
                className="px-4 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
              >
                {isLoading ? '⏳' : '✅'} Subscribe
              </button>
            ) : permission.denied ? (
              <button
                onClick={requestPermission}
                disabled={isLoading}
                className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 disabled:opacity-50"
              >
                {isLoading ? '⏳' : '🔧'} Enable in Settings
              </button>
            ) : (
              <button
                onClick={requestPermission}
                disabled={isLoading}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {isLoading ? '⏳' : '🔔'} Enable Notifications
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Notification Features */}
      {permission.granted && isSubscribed && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="font-medium text-green-800 mb-2">🎉 You're all set!</h3>
          <div className="text-sm text-green-700 space-y-1">
            <p>✅ You'll receive breaking news notifications</p>
            <p>✅ Get notified about new legal leaks</p>
            <p>✅ Stay updated with community news</p>
            <p>✅ Customize your notification preferences in Settings</p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-4">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-2"></div>
          <span className="text-gray-600">Loading...</span>
        </div>
      )}
    </div>
  )
}
