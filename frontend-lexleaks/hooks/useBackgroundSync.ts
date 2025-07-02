'use client'

import { useEffect, useState } from 'react'

interface BackgroundSyncOptions {
  onSuccess?: () => void
  onError?: (error: Error) => void
}

export function useBackgroundSync(options: BackgroundSyncOptions = {}) {
  const [isSupported, setIsSupported] = useState(false)
  const [isPending, setIsPending] = useState(false)

  useEffect(() => {
    // Check if background sync is supported
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
      setIsSupported(true)
    }
  }, [])

  const registerSync = async (tag: string, data?: any) => {
    if (!isSupported) {
      console.warn('Background sync is not supported')
      return false
    }

    try {
      const registration = await navigator.serviceWorker.ready

      // Store data in IndexedDB if provided
      if (data) {
        await storeInIndexedDB(data)
      }

      // Register sync event
      await (registration as any).sync.register(tag)
      setIsPending(true)
      
      return true
    } catch (error) {
      console.error('Failed to register background sync:', error)
      options.onError?.(error as Error)
      return false
    }
  }

  const storeInIndexedDB = async (data: any) => {
    const db = await openDB()
    const tx = db.transaction('pending-submissions', 'readwrite')
    const store = tx.objectStore('pending-submissions')
    await store.add({ data, timestamp: Date.now() })
  }

  const checkPendingSync = async () => {
    if (!isSupported) return []

    try {
      const db = await openDB()
      const tx = db.transaction('pending-submissions', 'readonly')
      const store = tx.objectStore('pending-submissions')
      const submissions = await store.getAll()
      return submissions
    } catch (error) {
      console.error('Failed to check pending sync:', error)
      return []
    }
  }

  const clearPendingSync = async () => {
    try {
      const db = await openDB()
      const tx = db.transaction('pending-submissions', 'readwrite')
      const store = tx.objectStore('pending-submissions')
      await store.clear()
      setIsPending(false)
    } catch (error) {
      console.error('Failed to clear pending sync:', error)
    }
  }

  return {
    isSupported,
    isPending,
    registerSync,
    checkPendingSync,
    clearPendingSync
  }
}

// Helper function to open IndexedDB
function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('lexleaks-db', 1)
    
    request.onerror = () => reject(request.error)
    request.onsuccess = () => resolve(request.result)
    
    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result
      if (!db.objectStoreNames.contains('pending-submissions')) {
        db.createObjectStore('pending-submissions', { keyPath: 'id', autoIncrement: true })
      }
    }
  })
} 