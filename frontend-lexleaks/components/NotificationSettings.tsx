'use client'

import { useState, useEffect } from 'react'
import { pushNotifications } from '@/lib/pushNotifications'

export default function NotificationSettings() {
  const [isSupported, setIsSupported] = useState(false)
  const [permission, setPermission] = useState<NotificationPermission>('default')
  const [isSubscribed, setIsSubscribed] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    checkNotificationStatus()
  }, [])

  const checkNotificationStatus = async () => {
    const supported = pushNotifications.isSupported()
    setIsSupported(supported)

    if (supported) {
      const status = await pushNotifications.getSubscriptionStatus()
      setPermission(status.permission)
      setIsSubscribed(status.isSubscribed)
    }
  }

  const handleEnableNotifications = async () => {
    setLoading(true)

    try {
      // Request permission
      const granted = await pushNotifications.init()
      
      if (granted) {
        // Subscribe to push notifications
        const subscription = await pushNotifications.subscribe()
        
        if (subscription) {
          setIsSubscribed(true)
          setPermission('granted')
          
          // Show test notification
          await pushNotifications.showTestNotification()
        }
      } else {
        setPermission('denied')
      }
    } catch (error) {
      console.error('Failed to enable notifications:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDisableNotifications = async () => {
    setLoading(true)

    try {
      const unsubscribed = await pushNotifications.unsubscribe()
      
      if (unsubscribed) {
        setIsSubscribed(false)
      }
    } catch (error) {
      console.error('Failed to disable notifications:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!isSupported) {
    return (
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
        <p className="text-yellow-800 dark:text-yellow-200 text-sm">
          Push notifications are not supported in your browser.
        </p>
      </div>
    )
  }

  return (
    <div className="bg-[#fdf6e3] dark:bg-[#1a1612] border-2 brand-border rounded-lg p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-lg font-bold font-mono-special brand-text mb-2">
            Push Notifications
          </h3>
          <p className="text-sm brand-text opacity-80 mb-4">
            Get notified about new leaks and important updates
          </p>
          
          {permission === 'denied' && (
            <p className="text-sm text-red-600 dark:text-red-400 mb-4">
              Notifications are blocked. Please enable them in your browser settings.
            </p>
          )}
          
          {isSubscribed && (
            <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400 mb-4">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>Notifications enabled</span>
            </div>
          )}
        </div>
        
        <div>
          {!isSubscribed ? (
            <button
              onClick={handleEnableNotifications}
              disabled={loading || permission === 'denied'}
              className="brand-button flex items-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
              )}
              Enable Notifications
            </button>
          ) : (
            <button
              onClick={handleDisableNotifications}
              disabled={loading}
              className="px-4 py-2 border-2 brand-border rounded-sm hover:bg-[#f5f0d8] dark:hover:bg-[#2a251f] transition-colors font-mono-special text-sm flex items-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-gray-600 border-t-transparent rounded-full animate-spin" />
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                </svg>
              )}
              Disable
            </button>
          )}
        </div>
      </div>
      
      {/* Notification Types */}
      {isSubscribed && (
        <div className="mt-6 pt-6 border-t-2 brand-border">
          <h4 className="text-sm font-bold font-mono-special brand-text mb-3">
            Notification Preferences
          </h4>
          <div className="space-y-3">
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                defaultChecked
                className="w-4 h-4 text-[#8B0000] focus:ring-[#8B0000] border-gray-300 rounded"
              />
              <span className="text-sm brand-text">New leak published</span>
            </label>
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                defaultChecked
                className="w-4 h-4 text-[#8B0000] focus:ring-[#8B0000] border-gray-300 rounded"
              />
              <span className="text-sm brand-text">Important updates</span>
            </label>
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                className="w-4 h-4 text-[#8B0000] focus:ring-[#8B0000] border-gray-300 rounded"
              />
              <span className="text-sm brand-text">Weekly digest</span>
            </label>
          </div>
        </div>
      )}
    </div>
  )
} 