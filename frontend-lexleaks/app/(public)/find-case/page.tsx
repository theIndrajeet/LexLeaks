'use client'

import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { format } from 'date-fns'
import TypewriterTitle from '@/components/TypewriterTitle'
import Navigation from '@/components/Navigation'

interface CaseResult {
  doc_id: string
  title: string
  court: string
  date: string
  judges: string[]
  snippet: string
  url: string
  citation: string
}

interface SearchResponse {
  success: boolean
  query: string
  page: number
  total_results: number
  cases: CaseResult[]
  error?: string
}

function FindCaseContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  
  // Initialize state from URL parameters
  const [query, setQuery] = useState(searchParams.get('q') || '')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<SearchResponse | null>(null)
  const [error, setError] = useState('')
  const [currentPage, setCurrentPage] = useState(parseInt(searchParams.get('page') || '0'))
  
  // Advanced search filters
  const [courtType, setCourtType] = useState(searchParams.get('court') || '')
  const [dateFrom, setDateFrom] = useState(searchParams.get('dateFrom') || '')
  const [dateTo, setDateTo] = useState(searchParams.get('dateTo') || '')
  const [showAdvanced, setShowAdvanced] = useState(false)

  // Update URL with search parameters
  const updateURL = (searchQuery: string, page: number = 0) => {
    const params = new URLSearchParams()
    if (searchQuery) params.set('q', searchQuery)
    if (page > 0) params.set('page', page.toString())
    if (courtType) params.set('court', courtType)
    if (dateFrom) params.set('dateFrom', dateFrom)
    if (dateTo) params.set('dateTo', dateTo)
    
    const newURL = params.toString() ? `?${params.toString()}` : ''
    router.replace(`/find-case${newURL}`, { scroll: false })
  }

  // Load search results on page load if URL has search parameters
  useEffect(() => {
    const urlQuery = searchParams.get('q')
    if (urlQuery && urlQuery.trim()) {
      searchCases(parseInt(searchParams.get('page') || '0'))
    }
  }, []) // Only run on mount

  const searchCases = async (page: number = 0) => {
    if (!query.trim()) {
      setError('Please enter a search query')
      return
    }

    setLoading(true)
    setError('')

    try {
      const params = new URLSearchParams({
        query: query.trim(),
        page: page.toString()
      })

      if (courtType) params.append('court_type', courtType)
      if (dateFrom) params.append('date_from', dateFrom)
      if (dateTo) params.append('date_to', dateTo)

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/kanoon/search?${params}`)
      const data: SearchResponse = await response.json()

      if (data.success) {
        setResults(data)
        setCurrentPage(page)
        updateURL(query.trim(), page)
      } else {
        setError(data.error || 'Failed to search cases')
      }
    } catch (err) {
      setError('Network error. Please try again.')
      console.error('Search error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    searchCases(0)
  }

  const handlePageChange = (newPage: number) => {
    searchCases(newPage)
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A'
    try {
      return format(new Date(dateString), 'dd MMM yyyy')
    } catch {
      return dateString
    }
  }

  const generateCaseFile = (index: number) => {
    const fileNumber = String(index + 1).padStart(3, '0')
    const alphaCode = String.fromCharCode(65 + (index % 26)) // A-Z
    return `#LL-${fileNumber}-${alphaCode}${alphaCode}${alphaCode}`
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header Section with Typewriter Animation */}
      <header className="main-header parallax-container">
        <TypewriterTitle text="FIND CASE" className="main-title" delay={150} />
        <p className="main-subtitle">Search Indian Legal Cases & Judgments.</p>
      </header>

      <Navigation currentPage="/find-case" />


      {/* Search Section */}
      <div className="mb-12">
        <form onSubmit={handleSearch} className="space-y-6">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search cases, judgments, or legal terms..."
              className="admin-input w-full pl-10 pr-4 py-4 text-lg"
              required
            />
            <div className="absolute inset-y-0 right-0 flex items-center">
              <button
                type="submit"
                disabled={loading}
                className="brand-button mr-2 px-6 py-2"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </div>

          {/* Advanced Search Toggle */}
          <div className="text-center">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="nav-link text-sm"
            >
              {showAdvanced ? 'Hide' : 'Show'} Advanced Filters
            </button>
          </div>

          {/* Advanced Filters */}
          {showAdvanced && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-6 border-t brand-border">
              <div>
                <label htmlFor="court" className="block text-sm font-medium mb-2 case-file">
                  Court Type
                </label>
                <select
                  id="court"
                  value={courtType}
                  onChange={(e) => setCourtType(e.target.value)}
                  className="admin-input w-full"
                >
                  <option value="">All Courts</option>
                  <option value="supreme">Supreme Court</option>
                  <option value="high">High Court</option>
                  <option value="district">District Court</option>
                </select>
              </div>
              <div>
                <label htmlFor="dateFrom" className="block text-sm font-medium mb-2 case-file">
                  From Date
                </label>
                <input
                  type="date"
                  id="dateFrom"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="admin-input w-full"
                />
              </div>
              <div>
                <label htmlFor="dateTo" className="block text-sm font-medium mb-2 case-file">
                  To Date
                </label>
                <input
                  type="date"
                  id="dateTo"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="admin-input w-full"
                />
              </div>
            </div>
          )}
        </form>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-12 p-6 border border-red-300 dark:border-red-800 bg-red-50 dark:bg-red-950 rounded-lg">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                Search Error
              </h3>
              <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                <p>{error}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search Results */}
      {results && (
        <main>
          {/* Results Header */}
          <div className="mb-8 text-center">
            <h2 className="article-title text-2xl mb-2">
              Search Results
            </h2>
            <p className="case-file">
              Found {results.total_results} cases for "{results.query}"
            </p>
          </div>

          {/* Cases List */}
          <div className="space-y-16">
            {results.cases.map((case_item, index) => (
              <article key={case_item.doc_id} className="article-card group">
                <div className="article-link cursor-pointer" onClick={() => {
                  // Include search context in the URL
                  const searchContext = searchParams.toString()
                  const contextParam = searchContext ? `?from=${encodeURIComponent(searchContext)}` : ''
                  router.push(`/find-case/${case_item.doc_id}${contextParam}`)
                }}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="case-file">
                      <span>Court: {case_item.court || 'N/A'}</span>
                      {' | '}
                      <span>Date: {formatDate(case_item.date)}</span>
                      {' | '}
                      <span>Case File: {generateCaseFile(index)}</span>
                    </div>
                    <div className="text-xs case-file">
                      {case_item.citation || 'No Citation'}
                    </div>
                  </div>
                  <h2 
                    className="article-title text-3xl md:text-4xl leading-tight mb-4 transition-colors duration-300 ease-in-out"
                    dangerouslySetInnerHTML={{ __html: case_item.title }}
                  />
                  {case_item.judges && case_item.judges.length > 0 && (
                    <div className="mb-4">
                      <span className="case-file">Judges: </span>
                      <span className="article-excerpt">
                        {Array.isArray(case_item.judges) ? case_item.judges.join(', ') : case_item.judges}
                      </span>
                    </div>
                  )}
                  {case_item.snippet && (
                    <p 
                      className="article-excerpt drop-cap"
                      dangerouslySetInnerHTML={{ __html: case_item.snippet }}
                    />
                  )}
                  <div className="read-more group-hover:underline">
                    Read Full Judgment &rarr;
                  </div>
                </div>
              </article>
            ))}
          </div>

          {/* Pagination */}
          {results.total_results > 10 && (
            <div className="text-center mt-16">
              <div className="flex justify-center space-x-4">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 0}
                  className="brand-button disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <span className="case-file self-center">
                  Page {currentPage + 1}
                </span>
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={results.cases.length < 10}
                  className="brand-button disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </main>
      )}

      {/* No Results */}
      {results && results.cases.length === 0 && (
        <div className="text-center py-20">
          <div className="max-w-md mx-auto">
            <div className="mb-8">
              <svg className="mx-auto h-16 w-16 text-gray-400 dark:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold mb-4">No Cases Found</h3>
            <p className="text-lg leading-relaxed mb-8 dark:text-gray-300">
              No legal cases found for your search query. Try different keywords or filters.
            </p>
            <button
              onClick={() => {
                setQuery('')
                setResults(null)
                setError('')
              }}
              className="brand-button"
            >
              New Search
            </button>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="main-footer">
        <p className="footer-text">&copy; 2025 LexLeaks. All Rights Reserved.</p>
        <p className="footer-text mt-1">Dedicated to transparency and accountability in the legal industry.</p>
      </footer>
    </div>
  )
}

export default function FindCasePage() {
  return (
    <Suspense fallback={
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <header className="main-header parallax-container">
          <TypewriterTitle text="FIND CASE" className="main-title" delay={150} />
          <p className="main-subtitle">Search Indian Legal Cases & Judgments.</p>
        </header>
        <Navigation currentPage="/find-case" />
        <div className="text-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    }>
      <FindCaseContent />
    </Suspense>
  )
}
