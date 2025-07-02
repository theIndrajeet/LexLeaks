// Custom Service Worker for LexLeaks
// This adds background sync and push notification support

self.addEventListener('install', (event) => {
  console.log('[SW] Installing Service Worker');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('[SW] Activating Service Worker');
  event.waitUntil(clients.claim());
});

// Background Sync for offline submissions
self.addEventListener('sync', async (event) => {
  console.log('[SW] Background Sync Event:', event.tag);
  
  if (event.tag === 'submit-leak') {
    event.waitUntil(submitPendingLeaks());
  }
});

async function submitPendingLeaks() {
  try {
    // Get all pending submissions from IndexedDB
    const db = await openDB();
    const tx = db.transaction('pending-submissions', 'readonly');
    const store = tx.objectStore('pending-submissions');
    const submissions = await store.getAll();
    
    for (const submission of submissions) {
      try {
        // Attempt to submit to server
        const response = await fetch('/api/posts', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(submission.data)
        });
        
        if (response.ok) {
          // Remove from pending if successful
          const deleteTx = db.transaction('pending-submissions', 'readwrite');
          await deleteTx.objectStore('pending-submissions').delete(submission.id);
          
          // Show notification
          await self.registration.showNotification('LexLeaks', {
            body: 'Your submission has been sent successfully!',
            icon: '/icon-192x192.png',
            badge: '/icon-96x96.png',
            tag: 'submission-success'
          });
        }
      } catch (error) {
        console.error('[SW] Failed to sync submission:', error);
      }
    }
  } catch (error) {
    console.error('[SW] Background sync error:', error);
  }
}

// Push Notifications
self.addEventListener('push', (event) => {
  console.log('[SW] Push Received');
  
  let data = {
    title: 'LexLeaks Update',
    body: 'You have a new notification',
    icon: '/icon-192x192.png',
    badge: '/icon-96x96.png'
  };
  
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data.body = event.data.text();
    }
  }
  
  const options = {
    body: data.body,
    icon: data.icon || '/icon-192x192.png',
    badge: data.badge || '/icon-96x96.png',
    vibrate: [200, 100, 200],
    data: data.data || {},
    actions: data.actions || [],
    tag: data.tag || 'default',
    requireInteraction: data.requireInteraction || false
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Notification Click Handler
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification clicked:', event.notification.tag);
  event.notification.close();
  
  // Handle action clicks
  if (event.action) {
    // Handle specific actions
    if (event.action === 'view') {
      event.waitUntil(
        clients.openWindow(event.notification.data.url || '/')
      );
    }
  } else {
    // Default action - open the app
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Helper function to open IndexedDB
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('lexleaks-db', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('pending-submissions')) {
        db.createObjectStore('pending-submissions', { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}

// Periodic Background Sync (if supported)
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'check-updates') {
    event.waitUntil(checkForUpdates());
  }
});

async function checkForUpdates() {
  try {
    const response = await fetch('/api/updates/check');
    const data = await response.json();
    
    if (data.hasUpdates) {
      await self.registration.showNotification('LexLeaks', {
        body: 'New leaks have been published!',
        icon: '/icon-192x192.png',
        badge: '/icon-96x96.png',
        tag: 'new-content'
      });
    }
  } catch (error) {
    console.error('[SW] Update check failed:', error);
  }
} 