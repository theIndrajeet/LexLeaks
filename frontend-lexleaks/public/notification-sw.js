/**
 * LexLeaks Notification Service Worker
 * Handles push notifications and background sync
 */

const CACHE_NAME = 'lexleaks-notifications-v1'
const API_BASE_URL = 'https://lexleaks-api-563011146464.asia-south1.run.app'

// Install event
self.addEventListener('install', (event) => {
  console.log('🔔 Notification Service Worker installed')
  self.skipWaiting()
})

// Activate event
self.addEventListener('activate', (event) => {
  console.log('🔔 Notification Service Worker activated')
  event.waitUntil(self.clients.claim())
})

// Push event - Handle incoming push notifications
self.addEventListener('push', (event) => {
  console.log('📨 Push notification received:', event)
  
  if (event.data) {
    try {
      const data = event.data.json()
      console.log('📨 Notification data:', data)
      
      const options = {
        body: data.content || 'New notification from LexLeaks',
        icon: '/icon-192x192.png',
        badge: '/icon-144x144.png',
        image: data.image || null,
        data: {
          url: data.url || '/',
          notificationId: data.notificationId,
          postId: data.postId,
          style: data.style || 'community'
        },
        actions: [
          {
            action: 'open',
            title: '👁️ Read Now',
            icon: '/icon-144x144.png'
          },
          {
            action: 'dismiss',
            title: '❌ Dismiss',
            icon: '/icon-144x144.png'
          }
        ],
        requireInteraction: data.style === 'breaking' || data.style === 'urgent',
        tag: `lexleaks-${data.notificationId || Date.now()}`,
        timestamp: Date.now(),
        vibrate: data.style === 'breaking' ? [200, 100, 200] : [100],
        sound: data.style === 'breaking' ? '/notification-sound.mp3' : null
      }

      // Customize notification based on style
      switch (data.style) {
        case 'breaking':
          options.title = '🚨 BREAKING NEWS - LexLeaks'
          options.requireInteraction = true
          options.vibrate = [300, 100, 300, 100, 300]
          break
        case 'mystery':
          options.title = '🤔 New Mystery - LexLeaks'
          break
        case 'urgent':
          options.title = '⚡ URGENT - LexLeaks'
          options.requireInteraction = true
          break
        case 'community':
          options.title = '👥 Community Update - LexLeaks'
          break
        default:
          options.title = '📰 LexLeaks Update'
      }

      event.waitUntil(
        self.registration.showNotification(options.title, options)
      )
    } catch (error) {
      console.error('❌ Error parsing push data:', error)
      
      // Fallback notification
      event.waitUntil(
        self.registration.showNotification('📰 LexLeaks Update', {
          body: 'You have a new notification from LexLeaks',
          icon: '/icon-192x192.png',
          badge: '/icon-144x144.png',
          data: { url: '/' }
        })
      )
    }
  }
})

// Notification click event
self.addEventListener('notificationclick', (event) => {
  console.log('👆 Notification clicked:', event)
  
  event.notification.close()
  
  const data = event.notification.data || {}
  const action = event.action
  
  if (action === 'dismiss') {
    // Just close the notification
    return
  }
  
  // Track engagement
  if (data.notificationId) {
    fetch(`${API_BASE_URL}/api/notifications/track/${data.notificationId}?action=click`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      }
    }).catch(error => {
      console.error('❌ Error tracking click:', error)
    })
  }
  
  // Open the app
  const urlToOpen = data.url || '/'
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      // Check if app is already open
      for (const client of clientList) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          client.focus()
          client.navigate(urlToOpen)
          return
        }
      }
      
      // Open new window if app is not open
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen)
      }
    })
  )
})

// Notification close event
self.addEventListener('notificationclose', (event) => {
  console.log('❌ Notification closed:', event)
  
  const data = event.notification.data || {}
  
  // Track that notification was opened (even if just closed)
  if (data.notificationId) {
    fetch(`${API_BASE_URL}/api/notifications/track/${data.notificationId}?action=open`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      }
    }).catch(error => {
      console.error('❌ Error tracking open:', error)
    })
  }
})

// Background sync for offline notification preferences
self.addEventListener('sync', (event) => {
  console.log('🔄 Background sync:', event.tag)
  
  if (event.tag === 'notification-preferences') {
    event.waitUntil(syncNotificationPreferences())
  }
})

// Sync notification preferences when back online
async function syncNotificationPreferences() {
  try {
    const token = await getAuthToken()
    if (!token) return
    
    const response = await fetch(`${API_BASE_URL}/api/notifications/preferences`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      const preferences = await response.json()
      // Store preferences in IndexedDB for offline use
      await storePreferences(preferences)
    }
  } catch (error) {
    console.error('❌ Error syncing preferences:', error)
  }
}

// Get auth token from storage
async function getAuthToken() {
  try {
    // Try to get token from IndexedDB or localStorage
    return localStorage.getItem('auth_token')
  } catch (error) {
    console.error('❌ Error getting auth token:', error)
    return null
  }
}

// Store preferences in IndexedDB
async function storePreferences(preferences) {
  try {
    const db = await openDB()
    const transaction = db.transaction(['preferences'], 'readwrite')
    const store = transaction.objectStore('preferences')
    await store.put(preferences, 'user-preferences')
  } catch (error) {
    console.error('❌ Error storing preferences:', error)
  }
}

// Open IndexedDB
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('LexLeaksNotifications', 1)
    
    request.onerror = () => reject(request.error)
    request.onsuccess = () => resolve(request.result)
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result
      if (!db.objectStoreNames.contains('preferences')) {
        db.createObjectStore('preferences')
      }
    }
  })
}

// Message event for communication with main thread
self.addEventListener('message', (event) => {
  console.log('💬 Message received:', event.data)
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting()
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME })
  }
})

// Error handling
self.addEventListener('error', (event) => {
  console.error('❌ Service Worker error:', event.error)
})

self.addEventListener('unhandledrejection', (event) => {
  console.error('❌ Unhandled promise rejection:', event.reason)
})

console.log('🔔 LexLeaks Notification Service Worker loaded successfully')
