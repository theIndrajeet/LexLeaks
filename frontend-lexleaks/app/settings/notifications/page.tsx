"use client"

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import NotificationManager from '@/components/NotificationManager'

interface NotificationPreferences {
  categories: string[]
  frequency: string
  quiet_hours: {
    start: string
    end: string
  }
  impact_level: string
  enabled: boolean
}

interface NotificationHistory {
  id: number
  content: string
  style: string
  sent_at: string
  opened_at: string | null
  clicked_at: string | null
  engagement_score: number
}

export default function NotificationSettings() {
  const { user } = useAuth()
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    categories: [],
    frequency: 'realtime',
    quiet_hours: { start: '22:00', end: '08:00' },
    impact_level: 'all',
    enabled: true
  })
  const [history, setHistory] = useState<NotificationHistory[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const categories = [
    { value: 'corporate', label: '🏢 Corporate Law', description: 'Corporate scandals, mergers, regulations' },
    { value: 'judicial', label: '⚖️ Judicial System', description: 'Court cases, legal precedents, judgments' },
    { value: 'government', label: '🏛️ Government', description: 'Political scandals, policy changes, corruption' },
    { value: 'criminal', label: '🚨 Criminal Law', description: 'Criminal cases, law enforcement, justice' },
    { value: 'civil', label: '📋 Civil Law', description: 'Civil disputes, contracts, property law' },
    { value: 'international', label: '🌍 International Law', description: 'Global legal issues, treaties, diplomacy' }
  ]

  const impactLevels = [
    { value: 'all', label: 'All Notifications', description: 'Receive all notifications regardless of impact' },
    { value: 'high', label: 'High Impact Only', description: 'Only major scandals and breaking news' },
    { value: 'medium', label: 'Medium & High Impact', description: 'Significant news and major stories' },
    { value: 'low', label: 'All Impact Levels', description: 'All news including minor updates' }
  ]

  const frequencies = [
    { value: 'realtime', label: '⚡ Real-time', description: 'Get notified immediately when news breaks' },
    { value: 'daily', label: '📅 Daily Digest', description: 'Receive a summary once per day' },
    { value: 'weekly', label: '📊 Weekly Summary', description: 'Get a weekly roundup of important news' }
  ]

  useEffect(() => {
    if (user) {
      fetchPreferences()
      fetchHistory()
    }
  }, [user])

  const fetchPreferences = async () => {
    try {
      const response = await fetch('/api/notifications/preferences', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        setPreferences(data)
      }
    } catch (err) {
      console.error('Error fetching preferences:', err)
    }
  }

  const fetchHistory = async () => {
    try {
      const response = await fetch('/api/notifications/history?limit=20', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        setHistory(data)
      }
    } catch (err) {
      console.error('Error fetching history:', err)
    } finally {
      setLoading(false)
    }
  }

  const savePreferences = async () => {
    try {
      setSaving(true)
      setError(null)
      
      const response = await fetch('/api/notifications/preferences', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(preferences)
      })
      
      if (response.ok) {
        setSuccess('Preferences saved successfully!')
        setTimeout(() => setSuccess(null), 3000)
      } else {
        setError('Failed to save preferences')
      }
    } catch (err) {
      setError('Failed to save preferences')
      console.error('Save preferences error:', err)
    } finally {
      setSaving(false)
    }
  }

  const handleCategoryChange = (category: string, checked: boolean) => {
    setPreferences(prev => ({
      ...prev,
      categories: checked 
        ? [...prev.categories, category]
        : prev.categories.filter(c => c !== category)
    }))
  }

  const trackEngagement = async (notificationId: number, action: 'open' | 'click') => {
    try {
      await fetch(`/api/notifications/track/${notificationId}?action=${action}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
      })
    } catch (err) {
      console.error('Error tracking engagement:', err)
    }
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Please Log In</h1>
          <p className="text-gray-600">You need to be logged in to manage notification preferences.</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading notification settings...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">🔔 Notification Settings</h1>
          <p className="text-gray-600 mt-2">Customize how you receive LexLeaks notifications</p>
        </div>

        {/* Success/Error Messages */}
        {success && (
          <div className="bg-green-50 border border-green-200 rounded-md p-4 mb-6">
            <p className="text-green-800">{success}</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        <div className="space-y-8">
          {/* Push Notification Manager */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">🔔 Push Notifications</h3>
            <NotificationManager />
          </div>

          {/* Enable/Disable Notifications */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-gray-900">🔔 Enable Notifications</h3>
                <p className="text-gray-600 mt-1">Receive notifications from LexLeaks</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.enabled}
                  onChange={(e) => setPreferences(prev => ({ ...prev, enabled: e.target.checked }))}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>

          {/* Notification Frequency */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">📅 Notification Frequency</h3>
            <div className="space-y-3">
              {frequencies.map((freq) => (
                <label key={freq.value} className="relative">
                  <input
                    type="radio"
                    name="frequency"
                    value={freq.value}
                    checked={preferences.frequency === freq.value}
                    onChange={(e) => setPreferences(prev => ({ ...prev, frequency: e.target.value }))}
                    className="sr-only"
                  />
                  <div className={`border-2 rounded-lg p-4 cursor-pointer transition-colors ${
                    preferences.frequency === freq.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}>
                    <div className="font-medium text-gray-900">{freq.label}</div>
                    <div className="text-sm text-gray-600 mt-1">{freq.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Categories */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">📂 Categories</h3>
            <p className="text-gray-600 mb-4">Choose which types of legal news you want to be notified about</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {categories.map((category) => (
                <label key={category.value} className="relative">
                  <input
                    type="checkbox"
                    checked={preferences.categories.includes(category.value)}
                    onChange={(e) => handleCategoryChange(category.value, e.target.checked)}
                    className="sr-only"
                  />
                  <div className={`border-2 rounded-lg p-4 cursor-pointer transition-colors ${
                    preferences.categories.includes(category.value)
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}>
                    <div className="font-medium text-gray-900">{category.label}</div>
                    <div className="text-sm text-gray-600 mt-1">{category.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Impact Level */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">⚡ Impact Level</h3>
            <p className="text-gray-600 mb-4">Choose the minimum impact level for notifications</p>
            <div className="space-y-3">
              {impactLevels.map((level) => (
                <label key={level.value} className="relative">
                  <input
                    type="radio"
                    name="impact_level"
                    value={level.value}
                    checked={preferences.impact_level === level.value}
                    onChange={(e) => setPreferences(prev => ({ ...prev, impact_level: e.target.value }))}
                    className="sr-only"
                  />
                  <div className={`border-2 rounded-lg p-4 cursor-pointer transition-colors ${
                    preferences.impact_level === level.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}>
                    <div className="font-medium text-gray-900">{level.label}</div>
                    <div className="text-sm text-gray-600 mt-1">{level.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Quiet Hours */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">🌙 Quiet Hours</h3>
            <p className="text-gray-600 mb-4">Set times when you don't want to receive notifications</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Time
                </label>
                <input
                  type="time"
                  value={preferences.quiet_hours.start}
                  onChange={(e) => setPreferences(prev => ({
                    ...prev,
                    quiet_hours: { ...prev.quiet_hours, start: e.target.value }
                  }))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Time
                </label>
                <input
                  type="time"
                  value={preferences.quiet_hours.end}
                  onChange={(e) => setPreferences(prev => ({
                    ...prev,
                    quiet_hours: { ...prev.quiet_hours, end: e.target.value }
                  }))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <button
              onClick={savePreferences}
              disabled={saving}
              className="bg-blue-600 text-white px-8 py-3 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {saving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Saving...
                </>
              ) : (
                '💾 Save Preferences'
              )}
            </button>
          </div>

          {/* Notification History */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">📜 Recent Notifications</h3>
            
            {history.length > 0 ? (
              <div className="space-y-4">
                {history.map((notification) => (
                  <div key={notification.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <p className="text-gray-900 mb-1">{notification.content}</p>
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            notification.style === 'breaking' ? 'bg-red-100 text-red-800' :
                            notification.style === 'mystery' ? 'bg-purple-100 text-purple-800' :
                            notification.style === 'urgent' ? 'bg-orange-100 text-orange-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {notification.style}
                          </span>
                          <span>{new Date(notification.sent_at).toLocaleString()}</span>
                          {notification.opened_at && (
                            <span className="text-green-600">👁️ Opened</span>
                          )}
                          {notification.clicked_at && (
                            <span className="text-blue-600">👆 Clicked</span>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-500">Engagement</div>
                        <div className="text-lg font-bold text-gray-900">{notification.engagement_score}/3</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No notifications received yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
