// Push Notification Manager for LexLeaks

const PUBLIC_VAPID_KEY = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY || 'YOUR_PUBLIC_VAPID_KEY'
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export class PushNotificationManager {
  private static instance: PushNotificationManager
  private permission: NotificationPermission = 'default'
  private subscription: PushSubscription | null = null

  private constructor() {}

  static getInstance(): PushNotificationManager {
    if (!PushNotificationManager.instance) {
      PushNotificationManager.instance = new PushNotificationManager()
    }
    return PushNotificationManager.instance
  }

  async init(): Promise<boolean> {
    if (!this.isSupported()) {
      console.warn('Push notifications are not supported')
      return false
    }

    this.permission = await Notification.requestPermission()
    return this.permission === 'granted'
  }

  isSupported(): boolean {
    return 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window
  }

  getPermission(): NotificationPermission {
    return this.permission
  }

  async subscribe(): Promise<PushSubscription | null> {
    if (!this.isSupported() || this.permission !== 'granted') {
      return null
    }

    try {
      const registration = await navigator.serviceWorker.ready
      
      // Check if already subscribed
      let subscription = await registration.pushManager.getSubscription()
      
      if (!subscription) {
        // Create new subscription
        subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(PUBLIC_VAPID_KEY)
        })
        
        // Send subscription to backend
        await this.sendSubscriptionToServer(subscription)
      }
      
      this.subscription = subscription
      return subscription
    } catch (error) {
      console.error('Failed to subscribe to push notifications:', error)
      return null
    }
  }

  async unsubscribe(): Promise<boolean> {
    if (!this.subscription) {
      const registration = await navigator.serviceWorker.ready
      this.subscription = await registration.pushManager.getSubscription()
    }

    if (this.subscription) {
      try {
        await this.subscription.unsubscribe()
        await this.removeSubscriptionFromServer(this.subscription)
        this.subscription = null
        return true
      } catch (error) {
        console.error('Failed to unsubscribe from push notifications:', error)
        return false
      }
    }

    return false
  }

  async sendSubscriptionToServer(subscription: PushSubscription): Promise<void> {
    try {
      const token = localStorage.getItem('authToken')
      const response = await fetch(`${API_BASE_URL}/api/notifications/subscribe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({
          subscription: subscription.toJSON(),
          userAgent: navigator.userAgent,
          timestamp: new Date().toISOString()
        })
      })

      if (!response.ok) {
        throw new Error('Failed to save subscription on server')
      }

      const data = await response.json()
      // Store subscription ID for later use
      if (data.id) {
        localStorage.setItem('pushSubscriptionId', data.id.toString())
      }
    } catch (error) {
      console.error('Failed to send subscription to server:', error)
    }
  }

  async removeSubscriptionFromServer(subscription: PushSubscription): Promise<void> {
    try {
      const token = localStorage.getItem('authToken')
      const response = await fetch(`${API_BASE_URL}/api/notifications/unsubscribe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({
          endpoint: subscription.endpoint
        })
      })

      if (!response.ok) {
        throw new Error('Failed to remove subscription from server')
      }

      // Clear stored subscription ID
      localStorage.removeItem('pushSubscriptionId')
    } catch (error) {
      console.error('Failed to remove subscription from server:', error)
    }
  }

  // Test notification
  async showTestNotification(): Promise<void> {
    if (this.permission !== 'granted') {
      console.warn('Notification permission not granted')
      return
    }

    const registration = await navigator.serviceWorker.ready
    
    await registration.showNotification('LexLeaks Test', {
      body: 'Push notifications are working! 🎉',
      icon: '/icon-192x192.png',
      badge: '/icon-96x96.png'
    })
  }

  // Check subscription status
  async getSubscriptionStatus(): Promise<{
    isSubscribed: boolean
    subscription: PushSubscription | null
    permission: NotificationPermission
  }> {
    const registration = await navigator.serviceWorker.ready
    const subscription = await registration.pushManager.getSubscription()

    return {
      isSubscribed: !!subscription,
      subscription,
      permission: Notification.permission
    }
  }
}

// Helper function to convert VAPID key
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - base64String.length % 4) % 4)
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/')

  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray
}

// Export singleton instance
export const pushNotifications = PushNotificationManager.getInstance() 