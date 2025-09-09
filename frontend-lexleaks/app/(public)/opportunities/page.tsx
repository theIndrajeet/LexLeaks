'use client'

import { useState, useEffect } from 'react'
import Navigation from '@/components/Navigation'

interface JobOpportunity {
  id: number
  title: string
  company: string
  location?: string
  work_type?: string
  salary_min?: number
  salary_max?: number
  salary_currency?: string
  job_type?: string
  experience_level?: string
  practice_area?: string
  firm_size?: string
  practice_type?: string
  description?: string
  requirements?: string
  benefits?: string
  application_url?: string
  source?: string
  source_url?: string
  posted_date?: string
  expires_date?: string
  quality_score?: number
  is_remote?: boolean
  is_hybrid?: boolean
  is_office?: boolean
  gemini_enhanced?: boolean
  created_at: string
  updated_at: string
}

interface JobSearchResponse {
  jobs: JobOpportunity[]
  total_count: number
  page: number
  limit: number
  total_pages: number
}

interface MarketTrends {
  total_jobs_analyzed: number
  data_period: string
  insights: any
  generated_at: string
}

export default function OpportunitiesPage() {
  const [jobs, setJobs] = useState<JobOpportunity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchParams, setSearchParams] = useState({
    query: '',
    location: '',
    work_type: '',
    practice_area: '',
    experience_level: '',
    salary_min: '',
    salary_max: '',
    page: 1,
    limit: 20
  })
  const [pagination, setPagination] = useState({
    total_count: 0,
    total_pages: 0,
    current_page: 1
  })
  const [marketTrends, setMarketTrends] = useState<MarketTrends | null>(null)
  const [showTrends, setShowTrends] = useState(false)
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(false)

  const searchJobs = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams()
      Object.entries(searchParams).forEach(([key, value]) => {
        if (value && value !== '') {
          params.append(key, value.toString())
        }
      })
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/opportunities/search?${params}`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch job opportunities')
      }
      
      const data: JobSearchResponse = await response.json()
      setJobs(data.jobs)
      setPagination({
        total_count: data.total_count,
        total_pages: data.total_pages,
        current_page: data.page
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    searchJobs()
  }, [searchParams.page])

  const handleSearch = () => {
    setSearchParams(prev => ({ ...prev, page: 1 }))
    searchJobs()
  }

  const handlePageChange = (newPage: number) => {
    setSearchParams(prev => ({ ...prev, page: newPage }))
  }

  const loadMarketTrends = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/opportunities/trends`)
      if (response.ok) {
        const trends: MarketTrends = await response.json()
        setMarketTrends(trends)
        setShowTrends(true)
      }
    } catch (err) {
      console.error('Failed to load market trends:', err)
    }
  }

  const refreshJobData = async () => {
    setLoading(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/opportunities/refresh`, {
        method: 'POST'
      })
      if (response.ok) {
        await searchJobs()
      }
    } catch (err) {
      setError('Failed to refresh job data')
    } finally {
      setLoading(false)
    }
  }

  const formatSalary = (min?: number, max?: number, currency: string = 'USD') => {
    if (!min && !max) return 'Salary not specified'
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()} ${currency}`
    if (min) return `$${min.toLocaleString()}+ ${currency}`
    if (max) return `Up to $${max.toLocaleString()} ${currency}`
    return 'Salary not specified'
  }

  const getWorkTypeBadge = (job: JobOpportunity) => {
    if (job.is_remote) return { text: 'Remote', class: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' }
    if (job.is_hybrid) return { text: 'Hybrid', class: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' }
    if (job.is_office) return { text: 'Office', class: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' }
    return { text: 'Unknown', class: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200' }
  }

  const getQualityBadge = (score?: number) => {
    if (!score) return { text: 'N/A', class: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200' }
    if (score >= 8) return { text: `High (${score.toFixed(1)})`, class: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' }
    if (score >= 6) return { text: `Good (${score.toFixed(1)})`, class: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' }
    return { text: `Fair (${score.toFixed(1)})`, class: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' }
  }

  const generateCaseFile = (index: number) => {
    const fileNumber = String(index + 1).padStart(3, '0')
    const alphaCode = String.fromCharCode(65 + (index % 26))
    return `#LL-${fileNumber}-${alphaCode}${alphaCode}${alphaCode}`
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header Section */}
      <header className="main-header parallax-container">
        <h1 className="main-title">LEGAL OPPORTUNITIES</h1>
        <p className="main-subtitle">Discover Your Next Legal Career.</p>
      </header>

      <Navigation currentPage="/opportunities" />

      {/* Action Buttons */}
      <div className="flex flex-wrap justify-center gap-4 mb-12">
        <button
          onClick={refreshJobData}
          disabled={loading}
          className="brand-button disabled:opacity-50"
        >
          {loading ? 'Refreshing...' : '🔄 Refresh Jobs'}
        </button>
        <button
          onClick={loadMarketTrends}
          className="brand-button"
        >
          📊 Market Trends
        </button>
      </div>

      {/* Market Trends Modal */}
      {showTrends && marketTrends && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-4xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Market Intelligence</h2>
              <button
                onClick={() => setShowTrends(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                ✕
              </button>
            </div>
            <div className="space-y-4">
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Based on {marketTrends.total_jobs_analyzed} jobs from the last {marketTrends.data_period}
              </p>
              <pre className="bg-gray-100 dark:bg-gray-700 p-4 rounded text-sm overflow-x-auto text-gray-900 dark:text-gray-100">
                {JSON.stringify(marketTrends.insights, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}

      {/* Search Section */}
      <div className="mb-12">
        <div className="flex justify-between items-center mb-6">
          <div className="case-file">
            <span>Document: Job Search Interface</span>
            {' | '}
            <span>Classification: Public</span>
          </div>
          <button
            onClick={() => setShowAdvancedSearch(!showAdvancedSearch)}
            className="nav-link text-sm"
          >
            {showAdvancedSearch ? 'Hide' : 'Show'} Advanced Filters
          </button>
        </div>
          
        {/* Basic Search Bar */}
        <div className="relative mb-6">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            value={searchParams.query}
            onChange={(e) => setSearchParams(prev => ({ ...prev, query: e.target.value }))}
            placeholder="Search for legal jobs, companies, or keywords..."
            className="admin-input w-full pl-10 pr-4 py-4 text-lg"
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <div className="absolute inset-y-0 right-0 flex items-center">
            <button
              onClick={handleSearch}
              disabled={loading}
              className="brand-button mr-2 px-6 py-2"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>
          
        {/* Advanced Search (Collapsible) */}
        {showAdvancedSearch && (
          <div className="border-t brand-border pt-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2 case-file">
                  Location
                </label>
                <input
                  type="text"
                  value={searchParams.location}
                  onChange={(e) => setSearchParams(prev => ({ ...prev, location: e.target.value }))}
                  placeholder="City, state, or remote"
                  className="admin-input w-full"
                />
              </div>
                
              <div>
                <label className="block text-sm font-medium mb-2 case-file">
                  Work Type
                </label>
                <select
                  value={searchParams.work_type}
                  onChange={(e) => setSearchParams(prev => ({ ...prev, work_type: e.target.value }))}
                  className="admin-input w-full"
                  aria-label="Work Type"
                >
                  <option value="">All Types</option>
                  <option value="remote">Remote</option>
                  <option value="hybrid">Hybrid</option>
                  <option value="office">Office</option>
                  <option value="flexible">Flexible</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2 case-file">
                  Practice Area
                </label>
                <select
                  value={searchParams.practice_area}
                  onChange={(e) => setSearchParams(prev => ({ ...prev, practice_area: e.target.value }))}
                  className="admin-input w-full"
                  aria-label="Practice Area"
                >
                  <option value="">All Areas</option>
                  <option value="corporate">Corporate Law</option>
                  <option value="criminal">Criminal Law</option>
                  <option value="family">Family Law</option>
                  <option value="ip">Intellectual Property</option>
                  <option value="real-estate">Real Estate</option>
                  <option value="immigration">Immigration</option>
                  <option value="environmental">Environmental</option>
                  <option value="litigation">Litigation</option>
                  <option value="transactional">Transactional</option>
                </select>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2 case-file">
                  Experience Level
                </label>
                <select
                  value={searchParams.experience_level}
                  onChange={(e) => setSearchParams(prev => ({ ...prev, experience_level: e.target.value }))}
                  className="admin-input w-full"
                  aria-label="Experience Level"
                >
                  <option value="">All Levels</option>
                  <option value="entry">Entry Level</option>
                  <option value="mid">Mid Level</option>
                  <option value="senior">Senior Level</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2 case-file">
                  Min Salary
                </label>
                <input
                  type="number"
                  value={searchParams.salary_min}
                  onChange={(e) => setSearchParams(prev => ({ ...prev, salary_min: e.target.value }))}
                  placeholder="e.g., 50000"
                  className="admin-input w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2 case-file">
                  Max Salary
                </label>
                <input
                  type="number"
                  value={searchParams.salary_max}
                  onChange={(e) => setSearchParams(prev => ({ ...prev, salary_max: e.target.value }))}
                  placeholder="e.g., 150000"
                  className="admin-input w-full"
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      {error && (
        <div className="text-center py-12">
          <div className="border border-red-300 dark:border-red-800 bg-red-50 dark:bg-red-950 rounded-lg p-8">
            <h3 className="text-xl font-bold text-red-800 dark:text-red-300 mb-4">Error Loading Opportunities</h3>
            <p className="text-red-700 dark:text-red-400 mb-6">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="brand-button"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {loading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-red-600 dark:border-red-400"></div>
          <p className="mt-2 text-gray-600 dark:text-gray-300">Loading opportunities...</p>
        </div>
      )}

      {!loading && jobs.length === 0 && !error && (
        <div className="text-center py-12">
          <p className="text-xl text-gray-600 dark:text-gray-300">No job opportunities found. Try adjusting your search criteria.</p>
        </div>
      )}

      {!loading && jobs.length > 0 && (
        <>
          <div className="mb-6">
            <div className="case-file">
              <span>Found {pagination.total_count} opportunities</span>
              {pagination.total_pages > 1 && (
                <>
                  {' | '}
                  <span>Page {pagination.current_page} of {pagination.total_pages}</span>
                </>
              )}
            </div>
          </div>

          <div className="space-y-8">
            {jobs.map((job, index) => {
              const workTypeBadge = getWorkTypeBadge(job)
              const qualityBadge = getQualityBadge(job.quality_score)
              
              return (
                <article key={job.id} className="article-card">
                  <div className="case-file">
                    <span>Document: {generateCaseFile(index)}</span>
                    {' | '}
                    <span>Classification: Public</span>
                    {' | '}
                    <span>Posted: {new Date(job.created_at).toLocaleDateString()}</span>
                  </div>
                  
                  <div className="flex flex-wrap items-center gap-2 mb-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${workTypeBadge.class}`}>
                      {workTypeBadge.text}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${qualityBadge.class}`}>
                      {qualityBadge.text}
                    </span>
                    {job.gemini_enhanced && (
                      <span className="px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
                        AI Enhanced
                      </span>
                    )}
                  </div>
                  
                  <h2 className="article-title">{job.title}</h2>
                  
                  <div className="article-excerpt mb-4">
                    <p className="font-semibold brand-accent">{job.company}</p>
                    {job.location && <p className="text-sm">{job.location}</p>}
                  </div>
                  
                  <div className="flex flex-wrap gap-4 text-sm text-gray-500 dark:text-gray-400 mb-4">
                    {job.practice_area && (
                      <span>📋 {job.practice_area}</span>
                    )}
                    {job.experience_level && (
                      <span>👤 {job.experience_level}</span>
                    )}
                    {job.firm_size && (
                      <span>🏢 {job.firm_size}</span>
                    )}
                  </div>
                  
                  <p className="text-gray-700 dark:text-gray-300 mb-4 font-mono-special">
                    {formatSalary(job.salary_min, job.salary_max, job.salary_currency)}
                  </p>
                  
                  {job.description && (
                    <p className="article-excerpt mb-6">
                      {job.description.substring(0, 200)}...
                    </p>
                  )}
                  
                  <div className="flex flex-col gap-2 lg:flex-row lg:justify-between lg:items-center">
                    <div className="flex gap-2">
                      {job.application_url && (
                        <a
                          href={job.application_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="brand-button"
                        >
                          Apply Now
                        </a>
                      )}
                      {job.source_url && (
                        <a
                          href={job.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="read-more"
                        >
                          View on {job.source} →
                        </a>
                      )}
                    </div>
                  </div>
                </article>
              )
            })}
          </div>

          {/* Pagination */}
          {pagination.total_pages > 1 && (
            <div className="flex justify-center mt-12">
              <div className="flex gap-2">
                <button
                  onClick={() => handlePageChange(pagination.current_page - 1)}
                  disabled={pagination.current_page === 1}
                  className="brand-button disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                
                {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                  const page = i + 1
                  return (
                    <button
                      key={page}
                      onClick={() => handlePageChange(page)}
                      className={`brand-button ${
                        page === pagination.current_page
                          ? 'bg-red-600 dark:bg-red-700 text-white'
                          : ''
                      }`}
                    >
                      {page}
                    </button>
                  )
                })}
                
                <button
                  onClick={() => handlePageChange(pagination.current_page + 1)}
                  disabled={pagination.current_page === pagination.total_pages}
                  className="brand-button disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}