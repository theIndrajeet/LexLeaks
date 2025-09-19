/**
 * LexLeaks PWA Notification Manager
 * Handles push notification registration, subscription, and management
 */

interface PushSubscription {
  endpoint: string
  keys: {
    p256dh: string
    auth: string
  }
}

interface NotificationPermission {
  granted: boolean
  denied: boolean
  default: boolean
}

class NotificationManager {
  private static instance: NotificationManager
  private registration: ServiceWorkerRegistration | null = null
  private subscription: PushSubscription | null = null

  private constructor() {}

  public static getInstance(): NotificationManager {
    if (!NotificationManager.instance) {
      NotificationManager.instance = new NotificationManager()
    }
    return NotificationManager.instance
  }

  /**
   * Initialize notification manager
   */
  async initialize(): Promise<boolean> {
    try {
      console.log('🔔 Initializing Notification Manager...')

      // Check if service workers are supported
      if (!('serviceWorker' in navigator)) {
        console.warn('⚠️ Service Workers not supported')
        return false
      }

      // Check if push messaging is supported
      if (!('PushManager' in window)) {
        console.warn('⚠️ Push messaging not supported')
        return false
      }

      // Register service worker
      this.registration = await navigator.serviceWorker.register('/notification-sw.js', {
        scope: '/'
      })

      console.log('✅ Service Worker registered:', this.registration.scope)

      // Wait for service worker to be ready
      await navigator.serviceWorker.ready
      console.log('✅ Service Worker ready')

      // Check current subscription
      this.subscription = await this.registration.pushManager.getSubscription()
      
      if (this.subscription) {
        console.log('✅ Push subscription found')
        await this.updateSubscriptionOnServer(this.subscription)
      } else {
        console.log('ℹ️ No push subscription found')
      }

      return true
    } catch (error) {
      console.error('❌ Error initializing notification manager:', error)
      return false
    }
  }

  /**
   * Request notification permission
   */
  async requestPermission(): Promise<NotificationPermission> {
    try {
      if (!('Notification' in window)) {
        throw new Error('Notifications not supported')
      }

      const permission = await Notification.requestPermission()
      
      return {
        granted: permission === 'granted',
        denied: permission === 'denied',
        default: permission === 'default'
      }
    } catch (error) {
      console.error('❌ Error requesting permission:', error)
      return { granted: false, denied: true, default: false }
    }
  }

  /**
   * Subscribe to push notifications
   */
  async subscribeToPush(): Promise<boolean> {
    try {
      if (!this.registration) {
        throw new Error('Service Worker not registered')
      }

      // Request permission first
      const permission = await this.requestPermission()
      if (!permission.granted) {
        console.warn('⚠️ Notification permission denied')
        return false
      }

      // Get VAPID public key
      const vapidPublicKey = await this.getVapidPublicKey()
      if (!vapidPublicKey) {
        throw new Error('VAPID public key not found')
      }

      // Subscribe to push manager
      this.subscription = await this.registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array(vapidPublicKey)
      })

      console.log('✅ Push subscription created:', this.subscription)

      // Send subscription to server
      await this.updateSubscriptionOnServer(this.subscription)

      return true
    } catch (error) {
      console.error('❌ Error subscribing to push:', error)
      return false
    }
  }

  /**
   * Unsubscribe from push notifications
   */
  async unsubscribeFromPush(): Promise<boolean> {
    try {
      if (!this.subscription) {
        console.log('ℹ️ No subscription to unsubscribe')
        return true
      }

      const success = await this.subscription.unsubscribe()
      if (success) {
        console.log('✅ Push subscription removed')
        this.subscription = null
        
        // Remove subscription from server
        await this.removeSubscriptionFromServer()
      }

      return success
    } catch (error) {
      console.error('❌ Error unsubscribing from push:', error)
      return false
    }
  }

  /**
   * Check if user is subscribed to push notifications
   */
  async isSubscribed(): Promise<boolean> {
    try {
      if (!this.registration) {
        return false
      }

      this.subscription = await this.registration.pushManager.getSubscription()
      return this.subscription !== null
    } catch (error) {
      console.error('❌ Error checking subscription:', error)
      return false
    }
  }

  /**
   * Get current subscription info
   */
  async getSubscriptionInfo(): Promise<PushSubscription | null> {
    try {
      if (!this.registration) {
        return null
      }

      this.subscription = await this.registration.pushManager.getSubscription()
      return this.subscription
    } catch (error) {
      console.error('❌ Error getting subscription info:', error)
      return null
    }
  }

  /**
   * Show a local notification (for testing)
   */
  async showLocalNotification(title: string, options: NotificationOptions = {}): Promise<void> {
    try {
      if (!this.registration) {
        throw new Error('Service Worker not registered')
      }

      const defaultOptions: NotificationOptions = {
        body: 'This is a test notification from LexLeaks',
        icon: '/icon-192x192.png',
        badge: '/icon-144x144.png',
        tag: `test-${Date.now()}`,
        requireInteraction: false,
        ...options
      }

      await this.registration.showNotification(title, defaultOptions)
      console.log('✅ Local notification shown')
    } catch (error) {
      console.error('❌ Error showing local notification:', error)
    }
  }

  /**
   * Update subscription on server
   */
  private async updateSubscriptionOnServer(subscription: PushSubscription): Promise<void> {
    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        console.warn('⚠️ No auth token found, skipping server update')
        return
      }

      const response = await fetch('/api/notifications/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          endpoint: subscription.endpoint,
          p256dh: this.arrayBufferToBase64(subscription.getKey('p256dh')),
          auth: this.arrayBufferToBase64(subscription.getKey('auth')),
          user_agent: navigator.userAgent
        })
      })

      if (response.ok) {
        console.log('✅ Subscription updated on server')
      } else {
        console.error('❌ Failed to update subscription on server:', response.status)
      }
    } catch (error) {
      console.error('❌ Error updating subscription on server:', error)
    }
  }

  /**
   * Remove subscription from server
   */
  private async removeSubscriptionFromServer(): Promise<void> {
    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        console.warn('⚠️ No auth token found, skipping server update')
        return
      }

      const response = await fetch('/api/notifications/unsubscribe', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        console.log('✅ Subscription removed from server')
      } else {
        console.error('❌ Failed to remove subscription from server:', response.status)
      }
    } catch (error) {
      console.error('❌ Error removing subscription from server:', error)
    }
  }

  /**
   * Get VAPID public key from server
   */
  private async getVapidPublicKey(): Promise<string | null> {
    try {
      const response = await fetch('/api/notifications/vapid-key')
      if (response.ok) {
        const data = await response.json()
        return data.publicKey
      }
      return null
    } catch (error) {
      console.error('❌ Error getting VAPID key:', error)
      return null
    }
  }

  /**
   * Convert VAPID key to Uint8Array
   */
  private urlBase64ToUint8Array(base64String: string): Uint8Array {
    const padding = '='.repeat((4 - base64String.length % 4) % 4)
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/')

    const rawData = window.atob(base64)
    const outputArray = new Uint8Array(rawData.length)

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i)
    }
    return outputArray
  }

  /**
   * Convert ArrayBuffer to base64
   */
  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer)
    let binary = ''
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i])
    }
    return window.btoa(binary)
  }

  /**
   * Get notification permission status
   */
  getPermissionStatus(): NotificationPermission {
    if (!('Notification' in window)) {
      return { granted: false, denied: true, default: false }
    }

    const permission = Notification.permission
    return {
      granted: permission === 'granted',
      denied: permission === 'denied',
      default: permission === 'default'
    }
  }

  /**
   * Check if notifications are supported
   */
  isSupported(): boolean {
    return 'Notification' in window && 'serviceWorker' in navigator && 'PushManager' in window
  }
}

// Export singleton instance
export const notificationManager = NotificationManager.getInstance()

// Export types
export type { PushSubscription, NotificationPermission }
