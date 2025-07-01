'use client'

import { useState, useEffect } from 'react'
import { format } from 'date-fns'

interface SearchFilterProps {
  onSearch: (filters: FilterState) => void
  loading?: boolean
}

export interface FilterState {
  query: string
  status: string
  verificationStatus: string
  dateFrom: string
  dateTo: string
  sortBy: 'newest' | 'oldest' | 'relevance' | 'impact'
  category: string
  author: string
  impactLevel: string
}

const categories = [
  { value: '', label: 'All Categories' },
  { value: 'corporate', label: 'Corporate Law' },
  { value: 'criminal', label: 'Criminal Defense' },
  { value: 'judicial', label: 'Judicial Misconduct' },
  { value: 'regulatory', label: 'Regulatory Violations' },
  { value: 'ethics', label: 'Ethics Violations' },
  { value: 'discrimination', label: 'Discrimination' },
  { value: 'financial', label: 'Financial Fraud' }
]

export default function SearchFilter({ onSearch, loading = false }: SearchFilterProps) {
  const [filters, setFilters] = useState<FilterState>({
    query: '',
    status: '',
    verificationStatus: '',
    dateFrom: '',
    dateTo: '',
    sortBy: 'newest',
    category: '',
    author: '',
    impactLevel: ''
  })
  const [isExpanded, setIsExpanded] = useState(false)

  const handleFilterChange = (key: keyof FilterState, value: string) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const handleSearch = (e?: React.FormEvent) => {
    e?.preventDefault()
    onSearch(filters)
  }

  const handleReset = () => {
    const resetFilters = {
      query: '',
      status: '',
      verificationStatus: '',
      dateFrom: '',
      dateTo: '',
      sortBy: 'newest' as const,
      category: '',
      author: '',
      impactLevel: ''
    }
    setFilters(resetFilters)
    onSearch(resetFilters)
  }

  const activeFiltersCount = Object.entries(filters).filter(([key, value]) => {
    return value && value !== 'newest' && key !== 'sortBy'
  }).length

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-8">
      <form onSubmit={handleSearch}>
        {/* Main Search Bar */}
        <div className="flex gap-3 mb-4">
          <div className="flex-1 relative">
            <input
              type="text"
              value={filters.query}
              onChange={(e) => handleFilterChange('query', e.target.value)}
              placeholder="Search leaks, cases, or keywords..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg 
                       bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100
                       focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              disabled={loading}
            />
            <svg
              className="absolute left-3 top-3.5 h-5 w-5 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 
                     disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg 
                     hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors relative"
          >
            <svg
              className={`h-5 w-5 text-gray-600 dark:text-gray-400 transition-transform ${
                isExpanded ? 'rotate-180' : ''
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
              />
            </svg>
            {activeFiltersCount > 0 && (
              <span className="absolute -top-1 -right-1 h-5 w-5 bg-primary-600 text-white text-xs 
                             rounded-full flex items-center justify-center">
                {activeFiltersCount}
              </span>
            )}
          </button>
        </div>

        {/* Advanced Filters */}
        {isExpanded && (
          <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Status
                </label>
                <select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                           bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">All Statuses</option>
                  <option value="published">Published</option>
                  <option value="draft">Draft</option>
                  <option value="archived">Archived</option>
                </select>
              </div>

              {/* Verification Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Verification Status
                </label>
                <select
                  value={filters.verificationStatus}
                  onChange={(e) => handleFilterChange('verificationStatus', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                           bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">All Verifications</option>
                  <option value="verified">Verified</option>
                  <option value="unverified">Unverified</option>
                  <option value="disputed">Disputed</option>
                </select>
              </div>

              {/* Category Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Category
                </label>
                <select
                  value={filters.category}
                  onChange={(e) => handleFilterChange('category', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                           bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  {categories.map(cat => (
                    <option key={cat.value} value={cat.value}>{cat.label}</option>
                  ))}
                </select>
              </div>

              {/* Sort By */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Sort By
                </label>
                <select
                  value={filters.sortBy}
                  onChange={(e) => handleFilterChange('sortBy', e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                           bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="newest">Newest First</option>
                  <option value="oldest">Oldest First</option>
                  <option value="relevance">Most Relevant</option>
                  <option value="impact">Most Impactful</option>
                </select>
              </div>

              {/* Date From */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  From Date
                </label>
                <input
                  type="date"
                  value={filters.dateFrom}
                  onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
                  max={filters.dateTo || format(new Date(), 'yyyy-MM-dd')}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                           bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              {/* Date To */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  To Date
                </label>
                <input
                  type="date"
                  value={filters.dateTo}
                  onChange={(e) => handleFilterChange('dateTo', e.target.value)}
                  min={filters.dateFrom}
                  max={format(new Date(), 'yyyy-MM-dd')}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                           bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              {/* Author Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Author
                </label>
                <input
                  type="text"
                  value={filters.author}
                  onChange={(e) => handleFilterChange('author', e.target.value)}
                  placeholder="Filter by author..."
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                           bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              {/* Impact Level Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Impact Level
                </label>
                <select
                  value={filters.impactLevel}
                  onChange={(e) => handleFilterChange('impactLevel', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                           bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">All Impact Levels</option>
                  <option value="high">High Impact (5+ outcomes)</option>
                  <option value="medium">Medium Impact (2-4 outcomes)</option>
                  <option value="low">Low Impact (0-1 outcomes)</option>
                </select>
              </div>

              {/* Reset Button */}
              <div className="flex items-end">
                <button
                  type="button"
                  onClick={handleReset}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                           text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 
                           transition-colors"
                >
                  Reset Filters
                </button>
              </div>
            </div>

            {/* Active Filters Display */}
            {activeFiltersCount > 0 && (
              <div className="mt-4 flex flex-wrap gap-2">
                {filters.query && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm 
                                 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                    Search: "{filters.query}"
                    <button
                      type="button"
                      onClick={() => handleFilterChange('query', '')}
                      className="ml-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-200"
                    >
                      ×
                    </button>
                  </span>
                )}
                {filters.status && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm 
                                 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                    Status: {filters.status}
                    <button
                      type="button"
                      onClick={() => handleFilterChange('status', '')}
                      className="ml-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-200"
                    >
                      ×
                    </button>
                  </span>
                )}
                {filters.category && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm 
                                 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                    Category: {categories.find(c => c.value === filters.category)?.label}
                    <button
                      type="button"
                      onClick={() => handleFilterChange('category', '')}
                      className="ml-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-200"
                    >
                      ×
                    </button>
                  </span>
                )}
                {filters.verificationStatus && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm 
                                 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                    Verification: {filters.verificationStatus}
                    <button
                      type="button"
                      onClick={() => handleFilterChange('verificationStatus', '')}
                      className="ml-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-200"
                    >
                      ×
                    </button>
                  </span>
                )}
                {filters.author && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm 
                                 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                    Author: {filters.author}
                    <button
                      type="button"
                      onClick={() => handleFilterChange('author', '')}
                      className="ml-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-200"
                    >
                      ×
                    </button>
                  </span>
                )}
                {filters.impactLevel && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm 
                                 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                    Impact: {filters.impactLevel} level
                    <button
                      type="button"
                      onClick={() => handleFilterChange('impactLevel', '')}
                      className="ml-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-200"
                    >
                      ×
                    </button>
                  </span>
                )}
              </div>
            )}
          </div>
        )}
      </form>
    </div>
  )
} 