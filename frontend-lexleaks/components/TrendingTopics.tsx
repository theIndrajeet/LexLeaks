'use client'

import { useState, useEffect } from 'react'
import { TrendingTopic, getTrendingLegalTopics, refreshTrendingTopics } from '@/lib/api'

interface TrendingTopicsProps {
  onTopicSelect: (topic: TrendingTopic) => void
  className?: string
}

export default function TrendingTopics({ onTopicSelect, className = '' }: TrendingTopicsProps) {
  const [topics, setTopics] = useState<TrendingTopic[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<string | null>(null)

  const fetchTrendingTopics = async () => {
    try {
      setLoading(true)
      const response = await getTrendingLegalTopics()
      setTopics(response.trending_topics)
      setLastUpdated(response.last_updated)
    } catch (error) {
      console.error('Failed to fetch trending topics:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    try {
      setRefreshing(true)
      await refreshTrendingTopics()
      await fetchTrendingTopics()
    } catch (error) {
      console.error('Failed to refresh trends:', error)
    } finally {
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchTrendingTopics()
  }, [])

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'corporate': return '🏢'
      case 'criminal': return ''
      case 'judicial': return '🏛️'
      case 'regulatory': return ''
      case 'legal-tech': return ''
      default: return ''
    }
  }

  const getArticleTypeIcon = (type: string) => {
    switch (type) {
      case 'quick': return ''
      case 'standard': return ''
      case 'deep': return ''
      default: return ''
    }
  }

  const getTemplateIcon = (template: string) => {
    switch (template) {
      case 'internship': return ''
      case 'legal_explainer': return ''
      default: return ''
    }
  }

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm p-6 ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-lg font-bold text-gray-900"> Trending Legal Topics</h3>
          {lastUpdated && (
            <p className="text-sm text-gray-500 mt-1">
              Last updated: {new Date(lastUpdated).toLocaleString()}
            </p>
          )}
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="btn-secondary text-sm disabled:opacity-50"
        >
          {refreshing ? ' Refreshing...' : ' Refresh'}
        </button>
      </div>

      {/* Topics List */}
      <div className="space-y-3">
        {topics.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No trending topics found.</p>
            <button
              onClick={handleRefresh}
              className="text-red-600 hover:text-red-700 mt-2"
            >
              Try refreshing
            </button>
          </div>
        ) : (
          topics.map((topic, index) => (
            <div
              key={index}
              className="border border-gray-200 rounded-lg p-4 hover:border-red-300 hover:shadow-sm transition-all cursor-pointer group"
              onClick={() => onTopicSelect(topic)}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-lg">{getCategoryIcon(topic.category)}</span>
                    <h4 className="font-semibold text-gray-900 group-hover:text-red-700">
                      {topic.topic}
                    </h4>
                    <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded-full">
                      Score: {topic.trend_score}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span className="flex items-center gap-1">
                      {getArticleTypeIcon(topic.suggested_article_type)}
                      {topic.suggested_article_type}
                    </span>
                    <span className="flex items-center gap-1">
                      {getTemplateIcon(topic.suggested_template)}
                      {topic.suggested_template.replace('_', ' ')}
                    </span>
                    {topic.interest_value && (
                      <span className="flex items-center gap-1">
                        📈 {topic.interest_value}% interest
                      </span>
                    )}
                  </div>
                </div>
                
                <button className="opacity-0 group-hover:opacity-100 transition-opacity text-red-600 hover:text-red-700">
                   Use Topic
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="mt-6 pt-4 border-t border-gray-200 text-center">
        <p className="text-sm text-gray-500">
          Click on any topic to use it in the AI Article Generator
        </p>
      </div>
    </div>
  )
}
