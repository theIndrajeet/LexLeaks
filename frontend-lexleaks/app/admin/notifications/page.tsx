"use client"

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabaseAuth'

interface NotificationTemplate {
  id: number
  name: string
  style: string
  template_text: string
  emoji_set: string[]
  tone: string
  created_at: string
}

interface NotificationAnalytics {
  total_sent: number
  total_opened: number
  total_clicked: number
  open_rate: number
  click_rate: number
  style_performance: Array<{
    style: string
    total: number
    opened: number
    clicked: number
    open_rate: number
    click_rate: number
  }>
  period_days: number
}

interface ABTest {
  id: number
  test_name: string
  variant_a: string
  variant_b: string
  winner: string | null
  confidence_level: number | null
  total_sends: number
  variant_a_opens: number
  variant_b_opens: number
  variant_a_clicks: number
  variant_b_clicks: number
  created_at: string
  completed_at: string | null
}

interface Post {
  id: number
  title: string
  category: string
  verification_status: string
  author?: string
  excerpt?: string
  published_at?: string
}

export default function NotificationDashboard() {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState('overview')
  const [templates, setTemplates] = useState<NotificationTemplate[]>([])
  const [analytics, setAnalytics] = useState<NotificationAnalytics | null>(null)
  const [abTests, setABTests] = useState<ABTest[]>([])
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // AI Agent States
  const [aiTestPost, setAiTestPost] = useState<Post | null>(null)
  const [aiTestStyle, setAiTestStyle] = useState('breaking')
  const [aiTestResult, setAiTestResult] = useState<string | null>(null)
  const [aiTestLoading, setAiTestLoading] = useState(false)

  // Notification Creation States
  const [selectedPost, setSelectedPost] = useState<number | null>(null)
  const [selectedStyle, setSelectedStyle] = useState('breaking')
  const [createLoading, setCreateLoading] = useState(false)
  const [availablePosts, setAvailablePosts] = useState<Post[]>([])
  const [postsLoading, setPostsLoading] = useState(false)

  useEffect(() => {
    if (user?.is_admin) {
      fetchDashboardData()
    }
  }, [user])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Get Supabase session token
      const { data: { session } } = await supabase.auth.getSession()
      const authToken = session?.access_token
      
      if (!authToken) {
        setError('Not authenticated')
        return
      }
      
      const [templatesRes, analyticsRes, abTestsRes, postsRes, availablePostsRes] = await Promise.all([
        fetch('/api/notifications/templates', {
          headers: { 'Authorization': `Bearer ${authToken}` }
        }),
        fetch('/api/notifications/analytics?days=7', {
          headers: { 'Authorization': `Bearer ${authToken}` }
        }),
        fetch('/api/notifications/ab-tests', {
          headers: { 'Authorization': `Bearer ${authToken}` }
        }),
        fetch('/api/posts/?limit=50', {
          headers: { 'Authorization': `Bearer ${authToken}` }
        }),
        fetch('/api/notifications/posts', {
          headers: { 'Authorization': `Bearer ${authToken}` }
        })
      ])

      if (templatesRes.ok) setTemplates(await templatesRes.json())
      if (analyticsRes.ok) setAnalytics(await analyticsRes.json())
      if (abTestsRes.ok) setABTests(await abTestsRes.json())
      if (postsRes.ok) {
        const postsData = await postsRes.json()
        setPosts(postsData)
        if (postsData.length > 0) setAiTestPost(postsData[0])
      }
      if (availablePostsRes.ok) {
        const availablePostsData = await availablePostsRes.json()
        setAvailablePosts(availablePostsData)
        if (availablePostsData.length > 0 && !selectedPost) {
          setSelectedPost(availablePostsData[0].id)
        }
      }
    } catch (err) {
      setError('Failed to load dashboard data')
      console.error('Dashboard error:', err)
    } finally {
      setLoading(false)
    }
  }

  const testAIAgent = async () => {
    if (!aiTestPost) return

    try {
      setAiTestLoading(true)
      // Get Supabase session token
      const { data: { session } } = await supabase.auth.getSession()
      const authToken = session?.access_token
      
      if (!authToken) {
        setError('Not authenticated')
        return
      }
      
      const response = await fetch('/api/notifications/ai-agent/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
          post_data: {
            id: aiTestPost.id,
            title: aiTestPost.title,
            content: `Test content for ${aiTestPost.title}`,
            category: aiTestPost.category,
            verification_status: aiTestPost.verification_status
          },
          style: aiTestStyle
        })
      })

      if (response.ok) {
        const result = await response.json()
        setAiTestResult(result.notification.content)
      } else {
        setError('Failed to test AI agent')
      }
    } catch (err) {
      setError('Failed to test AI agent')
      console.error('AI test error:', err)
    } finally {
      setAiTestLoading(false)
    }
  }

  const createNotification = async () => {
    if (!selectedPost) return

    try {
      setCreateLoading(true)
      
      // Get Supabase session token
      const { data: { session } } = await supabase.auth.getSession()
      const authToken = session?.access_token
      
      if (!authToken) {
        setError('Not authenticated')
        return
      }
      
      const response = await fetch('/api/notifications/send-manual', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
          post_id: selectedPost,
          style: selectedStyle
        })
      })

      if (response.ok) {
        const result = await response.json()
        alert(`✅ Notification sent to ${result.sent_count} users!\n\nPost: ${result.post_title}\nStyle: ${result.style}`)
        fetchDashboardData() // Refresh data
      } else {
        const errorData = await response.json()
        setError(`Failed to create notification: ${errorData.error || 'Unknown error'}`)
      }
    } catch (err) {
      setError('Failed to create notification')
      console.error('Create notification error:', err)
    } finally {
      setCreateLoading(false)
    }
  }

  if (!user?.is_admin) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
          <p className="text-gray-600">You need admin privileges to access this page.</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading notification dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">🔔 Notification Dashboard</h1>
          <p className="text-gray-600 mt-2">Manage AI-powered notifications and analytics</p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p className="text-red-800">{error}</p>
            <button 
              onClick={() => setError(null)}
              className="text-red-600 hover:text-red-800 mt-2"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', name: '📊 Overview', icon: '📊' },
              { id: 'create', name: '🎨 Create Notification', icon: '🎨' },
              { id: 'ai-agent', name: '🤖 AI Agent', icon: '🤖' },
              { id: 'analytics', name: '📈 Analytics', icon: '📈' },
              { id: 'ab-tests', name: '🧪 A/B Tests', icon: '🧪' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Analytics Cards */}
            {analytics && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white p-6 rounded-lg shadow">
                  <div className="flex items-center">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <span className="text-2xl">📤</span>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Total Sent</p>
                      <p className="text-2xl font-bold text-gray-900">{analytics.total_sent}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                  <div className="flex items-center">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <span className="text-2xl">👁️</span>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Open Rate</p>
                      <p className="text-2xl font-bold text-gray-900">{analytics.open_rate}%</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                  <div className="flex items-center">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <span className="text-2xl">👆</span>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Click Rate</p>
                      <p className="text-2xl font-bold text-gray-900">{analytics.click_rate}%</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                  <div className="flex items-center">
                    <div className="p-2 bg-orange-100 rounded-lg">
                      <span className="text-2xl">🧪</span>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Active A/B Tests</p>
                      <p className="text-2xl font-bold text-gray-900">{abTests.filter(t => !t.completed_at).length}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Recent Templates */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">📝 Recent Templates</h3>
              </div>
              <div className="p-6">
                {templates.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {templates.slice(0, 6).map((template) => (
                      <div key={template.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900">{template.name}</h4>
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            template.style === 'breaking' ? 'bg-red-100 text-red-800' :
                            template.style === 'mystery' ? 'bg-purple-100 text-purple-800' :
                            template.style === 'urgent' ? 'bg-orange-100 text-orange-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {template.style}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{template.template_text.substring(0, 100)}...</p>
                        <p className="text-xs text-gray-500">Tone: {template.tone}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-8">No templates found</p>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'create' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">🎨 Send Notification for Post</h3>
            
            <div className="space-y-6">
              {/* Post Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  📰 Select Post to Send Notification
                </label>
                {availablePosts.length > 0 ? (
                  <div className="space-y-2">
                    <select
                      value={selectedPost || ''}
                      onChange={(e) => setSelectedPost(Number(e.target.value))}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Choose a post...</option>
                      {availablePosts.map((post) => (
                        <option key={post.id} value={post.id}>
                          {post.title} ({post.category}) - {post.verification_status}
                        </option>
                      ))}
                    </select>
                    
                    {/* Selected Post Preview */}
                    {selectedPost && (
                      <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
                        {(() => {
                          const post = availablePosts.find(p => p.id === selectedPost)
                          return post ? (
                            <div>
                              <h4 className="font-medium text-gray-900 mb-2">{post.title}</h4>
                              <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
                                <span className={`px-2 py-1 rounded-full text-xs ${
                                  post.category === 'corporate' ? 'bg-blue-100 text-blue-800' :
                                  post.category === 'judicial' ? 'bg-purple-100 text-purple-800' :
                                  post.category === 'government' ? 'bg-green-100 text-green-800' :
                                  'bg-gray-100 text-gray-800'
                                }`}>
                                  {post.category}
                                </span>
                                <span className={`px-2 py-1 rounded-full text-xs ${
                                  post.verification_status === 'verified' ? 'bg-green-100 text-green-800' :
                                  post.verification_status === 'high_impact' ? 'bg-orange-100 text-orange-800' :
                                  'bg-yellow-100 text-yellow-800'
                                }`}>
                                  {post.verification_status}
                                </span>
                                <span>By: {post.author || 'Unknown'}</span>
                              </div>
                              <p className="text-sm text-gray-700">{post.excerpt || 'No excerpt available'}</p>
                            </div>
                          ) : null
                        })()}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <p>📭 No published posts available for notifications</p>
                    <p className="text-sm mt-1">Publish some posts first to send notifications</p>
                  </div>
                )}
              </div>

              {/* Style Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notification Style
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { value: 'breaking', label: '🚨 Breaking News', desc: 'Urgent, attention-grabbing' },
                    { value: 'mystery', label: '🤔 Mystery/Teaser', desc: 'Curious, suspenseful' },
                    { value: 'urgent', label: '⚡ Urgent Action', desc: 'Time-sensitive, actionable' },
                    { value: 'community', label: '👥 Community Update', desc: 'Friendly, engaging' }
                  ].map((style) => (
                    <label key={style.value} className="relative">
                      <input
                        type="radio"
                        name="style"
                        value={style.value}
                        checked={selectedStyle === style.value}
                        onChange={(e) => setSelectedStyle(e.target.value)}
                        className="sr-only"
                      />
                      <div className={`border-2 rounded-lg p-4 cursor-pointer transition-colors ${
                        selectedStyle === style.value
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}>
                        <div className="font-medium text-gray-900">{style.label}</div>
                        <div className="text-sm text-gray-600 mt-1">{style.desc}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Create Button */}
              <div className="flex justify-end">
                <button
                  onClick={createNotification}
                  disabled={!selectedPost || createLoading}
                  className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  {createLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Creating...
                    </>
                  ) : (
                    '🚀 Send Notification'
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'ai-agent' && (
          <div className="space-y-6">
            {/* AI Agent Test */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-6">🤖 AI Creative Agent Test</h3>
              
              <div className="space-y-4">
                {/* Post Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Test Post
                  </label>
                  <select
                    value={aiTestPost?.id || ''}
                    onChange={(e) => {
                      const post = posts.find(p => p.id === Number(e.target.value))
                      setAiTestPost(post || null)
                    }}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {posts.map((post) => (
                      <option key={post.id} value={post.id}>
                        {post.title} ({post.category})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Style Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Test Style
                  </label>
                  <select
                    value={aiTestStyle}
                    onChange={(e) => setAiTestStyle(e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="breaking">🚨 Breaking News</option>
                    <option value="mystery">🤔 Mystery/Teaser</option>
                    <option value="urgent">⚡ Urgent Action</option>
                    <option value="community">👥 Community Update</option>
                  </select>
                </div>

                {/* Test Button */}
                <button
                  onClick={testAIAgent}
                  disabled={!aiTestPost || aiTestLoading}
                  className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  {aiTestLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Testing AI...
                    </>
                  ) : (
                    '🧠 Test AI Agent'
                  )}
                </button>

                {/* AI Test Result */}
                {aiTestResult && (
                  <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">AI Generated Notification:</h4>
                    <div className="bg-white p-4 rounded border">
                      <p className="text-gray-800">{aiTestResult}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Available Styles */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">🎨 Available AI Styles</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { 
                    style: 'breaking', 
                    name: 'Breaking News', 
                    emojis: ['🚨', '⚡', '🔥', '💥'],
                    description: 'Urgent, attention-grabbing notifications for breaking news'
                  },
                  { 
                    style: 'mystery', 
                    name: 'Mystery/Teaser', 
                    emojis: ['🤔', '🔍', '💡', '🎭'],
                    description: 'Curious, suspenseful notifications that create intrigue'
                  },
                  { 
                    style: 'urgent', 
                    name: 'Urgent Action', 
                    emojis: ['⚡', '🚨', '⏰', '🎯'],
                    description: 'Time-sensitive notifications requiring immediate attention'
                  },
                  { 
                    style: 'community', 
                    name: 'Community Update', 
                    emojis: ['👥', '📰', '💬', '🎉'],
                    description: 'Friendly, engaging notifications for community updates'
                  }
                ].map((style) => (
                  <div key={style.style} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900">{style.name}</h4>
                      <div className="flex space-x-1">
                        {style.emojis.map((emoji, idx) => (
                          <span key={idx} className="text-lg">{emoji}</span>
                        ))}
                      </div>
                    </div>
                    <p className="text-sm text-gray-600">{style.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && analytics && (
          <div className="space-y-6">
            {/* Performance Metrics */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-6">📈 Performance Metrics (Last {analytics.period_days} days)</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">{analytics.total_sent}</div>
                  <div className="text-sm text-gray-600">Total Sent</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">{analytics.total_opened}</div>
                  <div className="text-sm text-gray-600">Total Opened</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600">{analytics.total_clicked}</div>
                  <div className="text-sm text-gray-600">Total Clicked</div>
                </div>
              </div>
            </div>

            {/* Style Performance */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-6">🎨 Style Performance</h3>
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Style</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Opened</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Clicked</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Open Rate</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Click Rate</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {analytics.style_performance.map((style, idx) => (
                      <tr key={idx}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            style.style === 'breaking' ? 'bg-red-100 text-red-800' :
                            style.style === 'mystery' ? 'bg-purple-100 text-purple-800' :
                            style.style === 'urgent' ? 'bg-orange-100 text-orange-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {style.style}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{style.total}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{style.opened}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{style.clicked}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{style.open_rate}%</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{style.click_rate}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'ab-tests' && (
          <div className="space-y-6">
            {/* A/B Tests List */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-6">🧪 A/B Tests</h3>
              
              {abTests.length > 0 ? (
                <div className="space-y-4">
                  {abTests.map((test) => (
                    <div key={test.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="font-medium text-gray-900">{test.test_name}</h4>
                        <div className="flex items-center space-x-2">
                          {test.winner ? (
                            <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                              Winner: Variant {test.winner}
                            </span>
                          ) : (
                            <span className="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">
                              Running
                            </span>
                          )}
                          <span className="text-sm text-gray-500">
                            {new Date(test.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="border border-gray-200 rounded p-3">
                          <h5 className="font-medium text-gray-900 mb-2">Variant A</h5>
                          <p className="text-sm text-gray-600 mb-2">{test.variant_a}</p>
                          <div className="text-xs text-gray-500">
                            Opens: {test.variant_a_opens} | Clicks: {test.variant_a_clicks}
                          </div>
                        </div>
                        <div className="border border-gray-200 rounded p-3">
                          <h5 className="font-medium text-gray-900 mb-2">Variant B</h5>
                          <p className="text-sm text-gray-600 mb-2">{test.variant_b}</p>
                          <div className="text-xs text-gray-500">
                            Opens: {test.variant_b_opens} | Clicks: {test.variant_b_clicks}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">No A/B tests found</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
