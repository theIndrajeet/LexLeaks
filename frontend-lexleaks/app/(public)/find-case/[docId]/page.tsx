'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { format } from 'date-fns'
import TypewriterTitle from '@/components/TypewriterTitle'
import Navigation from '@/components/Navigation'

interface CaseDetails {
  success: boolean
  doc_id: string
  title: string
  court: string
  date: string
  judges: string[]
  parties: string[]
  content: string
  citations: string[]
  url: string
  related_cases: string[]
  error?: string
}

export default function CaseDetailPage() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const docId = params.docId as string
  
  // Get search context from URL
  const fromSearch = searchParams.get('from')
  
  const [caseDetails, setCaseDetails] = useState<CaseDetails | null>(null)
  
  // Handle back navigation
  const handleBackNavigation = () => {
    if (fromSearch) {
      // Return to search results with preserved state
      router.push(`/find-case?${fromSearch}`)
    } else {
      // Default back behavior
      router.back()
    }
  }
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (docId) {
      fetchCaseDetails()
    }
  }, [docId])

  const fetchCaseDetails = async () => {
    setLoading(true)
    setError('')

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/kanoon/case/${docId}`)
      const data: CaseDetails = await response.json()

      if (data.success) {
        setCaseDetails(data)
      } else {
        setError(data.error || 'Failed to fetch case details')
      }
    } catch (err) {
      setError('Network error. Please try again.')
      console.error('Fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A'
    try {
      return format(new Date(dateString), 'dd MMM yyyy')
    } catch {
      return dateString
    }
  }

  const formatContent = (content: string) => {
    if (!content) return ''
    
    // Use dangerouslySetInnerHTML to render HTML content properly
    return (
      <div 
        className="prose prose-lg max-w-none dark:prose-invert"
        dangerouslySetInnerHTML={{ __html: content }}
      />
    )
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center py-20">
          <div className="loading-skeleton h-8 w-64 mx-auto mb-4"></div>
          <div className="loading-skeleton h-4 w-48 mx-auto mb-8"></div>
          <div className="loading-skeleton h-4 w-32 mx-auto"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center py-20">
          <div className="max-w-md mx-auto">
            <div className="mb-8">
              <svg className="mx-auto h-16 w-16 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold mb-4">Error Loading Case</h2>
            <p className="text-lg leading-relaxed mb-8 dark:text-gray-300">{error}</p>
            <div className="space-x-4">
              <button
                onClick={handleBackNavigation}
                className="brand-button"
              >
                Go Back
              </button>
              <Link
                href="/find-case"
                className="brand-button"
              >
                Search Again
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!caseDetails) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center py-20">
          <div className="max-w-md mx-auto">
            <div className="mb-8">
              <svg className="mx-auto h-16 w-16 text-gray-400 dark:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold mb-4">Case Not Found</h2>
            <p className="text-lg leading-relaxed mb-8 dark:text-gray-300">
              The requested case could not be found.
            </p>
            <Link
              href="/find-case"
              className="brand-button"
            >
              Search Cases
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header Section */}
      <header className="main-header parallax-container mb-16">
        <TypewriterTitle text="CASE DETAILS" className="main-title" delay={150} />
        <p className="main-subtitle">Legal case information and judgment.</p>
      </header>

      {/* Breadcrumb Navigation */}
      {fromSearch && (
        <div className="mb-8">
          <nav className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
            <Link href="/find-case" className="hover:text-brand-accent transition-colors">
              Find Case
            </Link>
            <span>›</span>
            <button 
              onClick={handleBackNavigation}
              className="hover:text-brand-accent transition-colors"
            >
              Search Results
            </button>
            <span>›</span>
            <span className="text-gray-900 dark:text-gray-100">Case Details</span>
          </nav>
        </div>
      )}

      <Navigation currentPage="/find-case" />

      {/* Case Header */}
      <article className="article-card mb-16">
        <div className="article-link">
          <div className="flex items-center justify-between mb-2">
            <div className="case-file">
              <span>Court: {caseDetails.court}</span>
              {' | '}
              <span>Date: {formatDate(caseDetails.date)}</span>
              {' | '}
              <span>Case ID: {caseDetails.doc_id}</span>
            </div>
            <div className="text-xs case-file">
              Document #{docId}
            </div>
          </div>
          <h1 
            className="article-title text-4xl md:text-5xl leading-tight mb-6"
            dangerouslySetInnerHTML={{ __html: caseDetails.title }}
          />
        </div>
      </article>

      {/* Judges */}
      {caseDetails.judges && caseDetails.judges.length > 0 && (
        <div className="mb-16">
          <h2 className="article-title text-2xl mb-6">Presiding Judges</h2>
          <div className="flex flex-wrap gap-3">
            {Array.isArray(caseDetails.judges) ? caseDetails.judges.map((judge, index) => (
              <span
                key={index}
                className="case-file bg-brand-accent/10 border border-brand-accent/20 px-4 py-2 rounded-lg"
              >
                {judge}
              </span>
            )) : (
              <span className="case-file bg-brand-accent/10 border border-brand-accent/20 px-4 py-2 rounded-lg">
                {caseDetails.judges}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Parties */}
      {caseDetails.parties && caseDetails.parties.length > 0 && (
        <div className="mb-16">
          <h2 className="article-title text-2xl mb-6">Parties Involved</h2>
          <div className="prose prose-lg max-w-none dark:prose-invert">
            {Array.isArray(caseDetails.parties) ? caseDetails.parties.map((party, index) => (
              <p key={index} className="article-excerpt">
                {party}
              </p>
            )) : (
              <p className="article-excerpt">
                {caseDetails.parties}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Citations */}
      {caseDetails.citations && caseDetails.citations.length > 0 && (
        <div className="mb-16">
          <h2 className="article-title text-2xl mb-6">Legal Citations</h2>
          <div className="prose prose-lg max-w-none dark:prose-invert">
            {Array.isArray(caseDetails.citations) ? caseDetails.citations.map((citation, index) => (
              <p key={index} className="article-excerpt">
                {citation}
              </p>
            )) : (
              <p className="article-excerpt">
                {caseDetails.citations}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Full Content */}
      <div className="mb-16">
        <h2 className="article-title text-2xl mb-6">Full Judgment</h2>
        <div className="article-card">
          {formatContent(caseDetails.content)}
        </div>
      </div>

      {/* Related Cases */}
      {caseDetails.related_cases && caseDetails.related_cases.length > 0 && (
        <div className="mb-16">
          <h2 className="article-title text-2xl mb-6">Related Cases</h2>
          <div className="prose prose-lg max-w-none dark:prose-invert">
            {Array.isArray(caseDetails.related_cases) ? caseDetails.related_cases.map((relatedCase, index) => (
              <p key={index} className="article-excerpt">
                <button
                  onClick={() => {
                    const contextParam = fromSearch ? `?from=${encodeURIComponent(fromSearch)}` : ''
                    router.push(`/find-case/${relatedCase}${contextParam}`)
                  }}
                  className="text-brand-accent hover:text-brand-accent/80 underline"
                >
                  {relatedCase}
                </button>
              </p>
            )) : (
              <p className="article-excerpt">
                <button
                  onClick={() => {
                    const contextParam = fromSearch ? `?from=${encodeURIComponent(fromSearch)}` : ''
                    router.push(`/find-case/${caseDetails.related_cases}${contextParam}`)
                  }}
                  className="text-brand-accent hover:text-brand-accent/80 underline"
                >
                  {caseDetails.related_cases}
                </button>
              </p>
            )}
          </div>
        </div>
      )}


      {/* Actions */}
      <div className="text-center mb-16">
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <button
            onClick={handleBackNavigation}
            className="brand-button"
          >
            Go Back
          </button>
          <Link
            href="/find-case"
            className="brand-button"
          >
            Search More Cases
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="main-footer">
        <p className="footer-text">&copy; 2025 LexLeaks. All Rights Reserved.</p>
        <p className="footer-text mt-1">Dedicated to transparency and accountability in the legal industry.</p>
      </footer>
    </div>
  )
}