'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { 
  getSchedulerStatus, 
  getSchedulerStats, 
  getScheduledPosts,
  toggleAutomation,
  manualGenerateArticle,
  manualPublishScheduled,
  refreshTrendingTopics,
  getTrendingTopics,
  runManualPipeline,
  runAutomationNow,
  SchedulerStatus,
  SchedulerStats,
  ScheduledPost,
  TrendingTopic,
  PipelineResponse
} from '@/lib/api'

export default function SchedulerPage() {
  const [status, setStatus] = useState<SchedulerStatus | null>(null)
  const [stats, setStats] = useState<SchedulerStats | null>(null)
  const [scheduledPosts, setScheduledPosts] = useState<ScheduledPost[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [manualTopic, setManualTopic] = useState('')
  
  // Enhanced Pipeline states
  const [trendingTopics, setTrendingTopics] = useState<TrendingTopic[]>([])
  const [selectedTopic, setSelectedTopic] = useState<TrendingTopic | null>(null)
  const [pipelineLoading, setPipelineLoading] = useState(false)
  const [showTopicSelection, setShowTopicSelection] = useState(false)
  const [showPublishOptions, setShowPublishOptions] = useState(false)
  const [generatedArticle, setGeneratedArticle] = useState<any>(null)
  const [includeFallback, setIncludeFallback] = useState(false)

  const fetchData = async () => {
    try {
      setLoading(true)
      const [statusData, statsData, postsData] = await Promise.all([
        getSchedulerStatus(),
        getSchedulerStats(),
        getScheduledPosts()
      ])
      
      setStatus(statusData)
      setStats(statsData.stats)
      setScheduledPosts(postsData.scheduled_posts)
      setError(null)
    } catch (err: any) {
      setError('Failed to fetch scheduler data: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    // Refresh data every 30 seconds
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const handleToggleAutomation = async () => {
    if (!status) return
    
    try {
      await toggleAutomation(!status.automation_enabled)
      await fetchData() // Refresh data
    } catch (err: any) {
      setError('Failed to toggle automation: ' + err.message)
    }
  }

  const handleManualGenerate = async () => {
    if (!manualTopic.trim()) {
      alert('Please enter a topic')
      return
    }
    
    try {
      await manualGenerateArticle(manualTopic.trim())
      setManualTopic('')
      await fetchData() // Refresh data
      alert('Article generated successfully!')
    } catch (err: any) {
      setError('Failed to generate article: ' + err.message)
    }
  }

  const handleManualPublish = async () => {
    try {
      await manualPublishScheduled()
      await fetchData() // Refresh data
      alert('Scheduled articles published!')
    } catch (err: any) {
      setError('Failed to publish articles: ' + err.message)
    }
  }

  const handleRefreshTrends = async () => {
    try {
      await refreshTrendingTopics()
      alert('Trends refreshed successfully!')
    } catch (err: any) {
      setError('Failed to refresh trends: ' + err.message)
    }
  }

  // Enhanced Pipeline Functions
  const handleRunEnhancedPipeline = async () => {
    try {
      setPipelineLoading(true)
      setError(null)
      
      // Step 1: Get trending topics
      const topicsResponse = await getTrendingTopics()
      
      if (topicsResponse.success && topicsResponse.topics) {
        setTrendingTopics(topicsResponse.topics)
        setShowTopicSelection(true)
      } else {
        setError('Failed to generate trending topics')
      }
    } catch (err: any) {
      setError('Failed to run enhanced pipeline: ' + err.message)
    } finally {
      setPipelineLoading(false)
    }
  }

  const handleSelectTopic = async (topic: TrendingTopic) => {
    try {
      setSelectedTopic(topic)
      setShowTopicSelection(false)
      setShowPublishOptions(true)
    } catch (err: any) {
      setError('Failed to select topic: ' + err.message)
    }
  }

  const handleCloseTopicSelection = () => {
    setShowTopicSelection(false)
    setSelectedTopic(null)
    setTrendingTopics([])
  }

  const handlePublishChoice = async (publishOption: 'draft' | 'live') => {
    try {
      setPipelineLoading(true)
      
      if (selectedTopic) {
        // Generate the article with the chosen publish option
        const result = await manualGenerateArticle(
          selectedTopic.title,
          selectedTopic.suggested_article_type,
          selectedTopic.suggested_template,
          publishOption
        )
        
        if (result.success) {
          alert(`Article ${publishOption === 'live' ? 'published live' : 'saved as draft'} successfully! Topic: ${selectedTopic.title}`)
        } else {
          setError('Failed to process article: ' + result.message)
        }
      }
      
      // Reset all states
      setShowPublishOptions(false)
      setSelectedTopic(null)
      setGeneratedArticle(null)
      setTrendingTopics([])
      
      // Refresh the data to show the new article
      fetchData()
    } catch (err: any) {
      setError('Failed to process article: ' + err.message)
    } finally {
      setPipelineLoading(false)
    }
  }

  const handleClosePublishOptions = () => {
    setShowPublishOptions(false)
    setSelectedTopic(null)
    setGeneratedArticle(null)
    setTrendingTopics([])
  }

  if (loading) {
    return (
      <div className="min-h-screen brand-bg p-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading scheduler data...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen brand-bg p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold brand-text">Article Scheduler</h1>
              <p className="text-gray-600 mt-2">Automated article generation and publishing</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => {
                  if (window.history.length > 1) window.history.back();
                  else window.location.href = '/admin/dashboard'
                }}
                className="px-6 py-3 border-2 border-gray-400 text-gray-700 rounded-lg hover:bg-gray-50 hover:border-gray-500 font-medium flex items-center gap-2"
              >
                ← Back to Dashboard
              </button>
              <button
                onClick={async () => {
                  try {
                    setPipelineLoading(true)
                    await runAutomationNow('generate')
                    await fetchData()
                    alert('Automation run started: generation triggered.')
                  } catch (err: any) {
                    setError('Failed to run automation: ' + err.message)
                  } finally {
                    setPipelineLoading(false)
                  }
                }}
                className="px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 font-medium flex items-center gap-2 shadow-lg"
                disabled={pipelineLoading}
              >
                {pipelineLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Generating...
                  </>
                ) : (
                  <>
                    ⚡ Generate Now
                  </>
                )}
              </button>
            </div>
          </div>
          
          {/* Quick Actions Bar */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-gray-800">Quick Actions</h3>
                <p className="text-sm text-gray-600">Common tasks at your fingertips</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={async () => {
                    try {
                      setPipelineLoading(true)
                      await runAutomationNow('generate')
                      await fetchData()
                      alert('Article generation started!')
                    } catch (err: any) {
                      setError('Failed to generate: ' + err.message)
                    } finally {
                      setPipelineLoading(false)
                    }
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm font-medium"
                  disabled={pipelineLoading}
                >
                  {pipelineLoading ? 'Generating...' : '🚀 Generate Article'}
                </button>
                <button
                  onClick={handleRefreshTrends}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium"
                >
                  📈 Refresh Trends
                </button>
                <button
                  onClick={handleManualPublish}
                  className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 text-sm font-medium"
                >
                  📤 Publish All
                </button>
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Status Overview */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">System Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className={`text-2xl font-bold ${status?.automation_enabled ? 'text-green-600' : 'text-red-600'}`}>
                {status?.automation_enabled ? 'Active' : 'Paused'}
              </div>
              <div className="text-sm text-gray-600">Automation Status</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{stats?.posts_today || 0}</div>
              <div className="text-sm text-gray-600">Generated Today</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{scheduledPosts.length}</div>
              <div className="text-sm text-gray-600">Scheduled Posts</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{stats?.success_rate || 0}%</div>
              <div className="text-sm text-gray-600">Success Rate</div>
            </div>
          </div>
        </div>

        {/* Schedule Info */}
        {status && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Schedule Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-600">Generation Time</div>
                <div className="text-lg font-medium">{status.generation_time} IST</div>
                <div className="text-sm text-gray-500">Next: {new Date(status.next_generation).toLocaleString()}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Publish Time</div>
                <div className="text-lg font-medium">{status.publish_time} IST</div>
                <div className="text-sm text-gray-500">Next: {new Date(status.next_publish).toLocaleString()}</div>
              </div>
            </div>
          </div>
        )}

        {/* Controls */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">System Controls</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <button
              onClick={handleToggleAutomation}
              className={`px-6 py-3 rounded-lg font-medium text-lg flex items-center justify-center gap-2 ${
                status?.automation_enabled 
                  ? 'bg-red-600 text-white hover:bg-red-700 shadow-lg' 
                  : 'bg-green-600 text-white hover:bg-green-700 shadow-lg'
              }`}
            >
              {status?.automation_enabled ? (
                <>
                  ⏸️ Pause Automation
                </>
              ) : (
                <>
                  ▶️ Start Automation
                </>
              )}
            </button>
            <button
              onClick={async () => {
                try {
                  setPipelineLoading(true)
                  await runAutomationNow('generate_and_publish')
                  await fetchData()
                  alert('Automation ran: generated and published due items.')
                } catch (err: any) {
                  setError('Failed to run automation now: ' + err.message)
                } finally {
                  setPipelineLoading(false)
                }
              }}
              className="px-6 py-3 bg-emerald-700 text-white rounded-lg font-medium hover:bg-emerald-800 disabled:opacity-50 text-lg flex items-center justify-center gap-2 shadow-lg"
              disabled={pipelineLoading}
            >
              {pipelineLoading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Running...
                </>
              ) : (
                <>
                  ⚡ Run Now (Gen+Publish)
                </>
              )}
            </button>
            <button
              onClick={handleRefreshTrends}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 text-lg flex items-center justify-center gap-2 shadow-lg"
            >
              📈 Refresh Trends
            </button>
            <button
              onClick={handleManualPublish}
              className="px-6 py-3 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 text-lg flex items-center justify-center gap-2 shadow-lg"
            >
              📤 Manual Publish All
            </button>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 text-lg flex items-center justify-center gap-2 shadow-lg"
            >
              🔄 Refresh Data
            </button>
            <button
              onClick={async () => {
                try {
                  setPipelineLoading(true)
                  await runAutomationNow('generate')
                  await fetchData()
                  alert('Article generation started!')
                } catch (err: any) {
                  setError('Failed to generate: ' + err.message)
                } finally {
                  setPipelineLoading(false)
                }
              }}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50 text-lg flex items-center justify-center gap-2 shadow-lg"
              disabled={pipelineLoading}
            >
              {pipelineLoading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Generating...
                </>
              ) : (
                <>
                  🚀 Generate Now
                </>
              )}
            </button>
          </div>
        </div>

        {/* Manual Article Generation */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Manual Article Generation</h2>
          <div className="flex gap-4">
            <input
              type="text"
              value={manualTopic}
              onChange={(e) => setManualTopic(e.target.value)}
              placeholder="Enter article topic..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={handleManualGenerate}
              className="px-6 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700"
            >
              Generate Article
            </button>
          </div>
        </div>

        {/* Enhanced Pipeline - Research-Based Article Generation */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4"> Enhanced Pipeline - Research-Based Articles</h2>
          <p className="text-gray-600 mb-4">
            Run the complete pipeline: Scrape legal news → Generate trending topics → Choose topic → Generate article with research data
          </p>
          <div className="flex gap-4">
            <button
              onClick={handleRunEnhancedPipeline}
              disabled={pipelineLoading}
              className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {pipelineLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Running Pipeline...
                </>
              ) : (
                <>
                   Run Enhanced Pipeline
                </>
              )}
            </button>
            {showTopicSelection && (
              <button
                onClick={handleCloseTopicSelection}
                className="px-4 py-2 bg-gray-500 text-white rounded-lg font-medium hover:bg-gray-600"
              >
                Cancel
              </button>
            )}
          </div>
        </div>

        {/* Topic Selection Modal */}
        {showTopicSelection && trendingTopics.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8 border-2 border-blue-200">
            <div className="flex items-start justify-between mb-4">
              <h3 className="text-lg font-semibold text-blue-600">
                Choose a Trending Topic ({trendingTopics.length} topics found)
              </h3>
              <label className="flex items-center gap-2 text-sm text-gray-700">
                <input
                  type="checkbox"
                  checked={includeFallback}
                  onChange={(e) => setIncludeFallback(e.target.checked)}
                />
                Include fallback topics
              </label>
            </div>
            <p className="text-gray-600 mb-4">
              Select a topic to generate an article with research data from legal news sources:
            </p>
            <div className="grid gap-4">
              {(includeFallback ? trendingTopics : (trendingTopics as any[]).filter(t => t.generated_by === 'gemini_ai')).map((topic: any, index: number) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-semibold text-lg text-gray-800">{topic.title}</h4>
                    <div className="flex items-center gap-2">
                      {topic.generated_by && topic.generated_by !== 'gemini_ai' && (
                        <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                          {topic.generated_by.replace('_', ' ')}
                        </span>
                      )}
                      <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {topic.category}
                      </span>
                    </div>
                  </div>
                  <p className="text-gray-600 mb-2">{topic.angle}</p>
                  <div className="flex justify-between items-center text-sm text-gray-500 mb-3">
                    <span> {topic.target_audience}</span>
                    <span>Confidence: {Math.round((topic.confidence_score || 0) * 100)}%</span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    <strong>Why trending:</strong> {topic.trending_reason}
                  </p>
                  <div className="flex gap-2 items-center flex-wrap">
                    <button
                      onClick={() => handleSelectTopic(topic)}
                      disabled={pipelineLoading}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {pipelineLoading && selectedTopic === topic ? (
                        <span className="flex items-center gap-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          Generating...
                        </span>
                      ) : (
                        'Generate Article'
                      )}
                    </button>
                    <span className="text-xs text-gray-500 self-center">
                      Type: {topic.suggested_article_type} | Template: {topic.suggested_template}
                    </span>
                    {topic.source_links && topic.source_links.length > 0 && (
                      <span className="text-xs text-gray-600 flex items-center gap-2">
                        <strong>Sources:</strong>
                        {topic.source_links.slice(0, 2).map((link: string, i: number) => (
                          <a
                            key={i}
                            href={link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="underline text-blue-700 hover:text-blue-900"
                          >
                            {(() => { try { return new URL(link).hostname.replace('www.', '') } catch { return 'source' } })()}
                          </a>
                        ))}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Publish Options Modal */}
        {showPublishOptions && selectedTopic && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8 border-2 border-green-200">
            <h3 className="text-lg font-semibold mb-4 text-green-600">
               Topic Selected - Choose Publish Option
            </h3>
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <h4 className="font-semibold text-lg text-gray-800 mb-2">{selectedTopic.title}</h4>
              <p className="text-gray-600 mb-2">{selectedTopic.angle}</p>
              <div className="text-sm text-gray-500">
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded mr-2">{selectedTopic.category}</span>
                <span>Confidence: {Math.round(selectedTopic.confidence_score * 100)}%</span>
              </div>
            </div>
            <p className="text-gray-600 mb-4">
              Ready to generate an article with research data from legal news sources. Choose how you want to publish it:
            </p>
            <div className="flex gap-4">
              <button
                onClick={() => handlePublishChoice('draft')}
                disabled={pipelineLoading}
                className="flex-1 px-6 py-3 bg-yellow-600 text-white rounded-lg font-medium hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {pipelineLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Generating...
                  </>
                ) : (
                  <>
                     Generate & Save as Draft
                  </>
                )}
              </button>
              <button
                onClick={() => handlePublishChoice('live')}
                disabled={pipelineLoading}
                className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {pipelineLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Generating...
                  </>
                ) : (
                  <>
                     Generate & Publish Live
                  </>
                )}
              </button>
            </div>
            <div className="mt-4 text-center">
              <button
                onClick={handleClosePublishOptions}
                className="text-gray-500 hover:text-gray-700 text-sm underline"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Scheduled Posts */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Scheduled Posts ({scheduledPosts.length})</h2>
          {scheduledPosts.length === 0 ? (
            <p className="text-gray-600">No posts scheduled for publishing.</p>
          ) : (
            <div className="space-y-3">
              {scheduledPosts.map((post) => (
                <div key={post.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-medium">{post.title}</div>
                    <div className="text-sm text-gray-600">
                      Scheduled for: {new Date(post.scheduled_for).toLocaleString()}
                    </div>
                  </div>
                  <div className="text-yellow-600 font-medium">Scheduled</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Statistics */}
        {stats && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Statistics</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{stats.total_ai_posts}</div>
                <div className="text-sm text-gray-600">Total AI Posts</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{stats.published_ai_posts}</div>
                <div className="text-sm text-gray-600">Published Posts</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{stats.posts_this_week}</div>
                <div className="text-sm text-gray-600">This Week</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}