'use client'

import { useState } from 'react'
import StatusBadge from './StatusBadge'

interface Impact {
  id: number
  title: string
  description: string
  date: string
  type: 'legal_action' | 'policy_change' | 'investigation' | 'resignation' | 'reform'
  status: 'pending' | 'in_progress' | 'completed'
  post_id: number
  created_at: string
  updated_at?: string
}

interface ImpactTrackerProps {
  impacts: Impact[]
  postId?: number
}

const impactTypeIcons = {
  legal_action: '⚖️',
  policy_change: '📋',
  investigation: '🔍',
  resignation: '🚪',
  reform: '🛠️'
}

const impactTypeLabels = {
  legal_action: 'Legal Action',
  policy_change: 'Policy Change',
  investigation: 'Investigation',
  resignation: 'Resignation',
  reform: 'Reform'
}

export default function ImpactTracker({ impacts, postId }: ImpactTrackerProps) {
  const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set())

  const toggleExpanded = (id: number) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }

  const filteredImpacts = postId 
    ? impacts.filter(impact => impact.post_id === postId)
    : impacts

  if (filteredImpacts.length === 0) {
    return null
  }

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">
        Real-World Impact
      </h3>
      
      <div className="space-y-4">
        {filteredImpacts.map((impact) => (
          <div
            key={impact.id}
            className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 
                     hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-2xl" role="img" aria-label={impactTypeLabels[impact.type]}>
                    {impactTypeIcons[impact.type]}
                  </span>
                  <h4 className="font-semibold text-gray-900 dark:text-gray-100">
                    {impact.title}
                  </h4>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    impact.status === 'completed' 
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                      : impact.status === 'in_progress'
                      ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                  }`}>
                    {impact.status.replace('_', ' ')}
                  </span>
                </div>
                
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {formatDate(impact.date)} • {impactTypeLabels[impact.type]}
                </div>
                
                <p className={`text-gray-700 dark:text-gray-300 ${
                  !expandedItems.has(impact.id) ? 'line-clamp-2' : ''
                }`}>
                  {impact.description}
                </p>
                
                {impact.description.length > 100 && (
                  <button
                    onClick={() => toggleExpanded(impact.id)}
                    className="text-primary-600 hover:text-primary-800 dark:text-primary-400 
                             dark:hover:text-primary-300 text-sm mt-2"
                  >
                    {expandedItems.has(impact.id) ? 'Show less' : 'Read more'}
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {filteredImpacts.filter(i => i.type === 'legal_action').length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Legal Actions</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {filteredImpacts.filter(i => i.type === 'investigation').length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Investigations</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {filteredImpacts.filter(i => i.type === 'policy_change').length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Policy Changes</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {filteredImpacts.filter(i => i.status === 'completed').length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Completed</div>
          </div>
        </div>
      </div>
    </div>
  )
} 