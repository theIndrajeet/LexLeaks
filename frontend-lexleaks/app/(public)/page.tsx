'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { format } from 'date-fns'
import { getPublishedPosts, PostSummary } from '@/lib/api'
import TypewriterTitle from '@/components/TypewriterTitle'
import Navigation from '@/components/Navigation'
import StatusBadge from '@/components/StatusBadge'
import InstallPWA from '@/components/InstallPWA'

import SearchFilter, { FilterState } from '@/components/SearchFilter'

export default function HomePage() {
  const [posts, setPosts] = useState<PostSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filterLoading, setFilterLoading] = useState(false)

  const fetchPosts = async (filters?: Partial<FilterState>) => {
    try {
      setFilterLoading(true)
      setError(null)
      
      // Convert filter state to API params
      const params: any = {
        limit: 20,
        status: 'published', // Always show only published posts on public page
      }
      
      if (filters) {
        if (filters.query) params.search = filters.query
        if (filters.verificationStatus) params.verification_status = filters.verificationStatus
        if (filters.category) params.category = filters.category
        if (filters.author) params.author = filters.author
        if (filters.dateFrom) params.date_from = filters.dateFrom
        if (filters.dateTo) params.date_to = filters.dateTo
        if (filters.sortBy && filters.sortBy !== 'relevance') params.sort_by = filters.sortBy
        if (filters.impactLevel) params.impact_level = filters.impactLevel
      }
      
      const fetchedPosts = await getPublishedPosts(params)
      setPosts(fetchedPosts || []) // Handle null/undefined responses
    } catch (err: any) {
      console.error('Error fetching posts:', err)
      // Don't show error for empty database, just show empty state
      if (err.message?.includes('timeout') || err.message?.includes('Failed to fetch')) {
        setError('Connection timeout - please check your internet connection')
      } else {
        setError('Failed to load posts')
      }
    } finally {
      setLoading(false)
      setFilterLoading(false)
    }
  }

  useEffect(() => {
    // Add a small delay to prevent flash of loading state
    const timer = setTimeout(() => {
      fetchPosts()
    }, 100)
    
    return () => clearTimeout(timer)
  }, [])

  const handleFilterChange = (filters: FilterState) => {
    fetchPosts(filters)
  }

  const generateCaseFile = (index: number) => {
    const fileNumber = String(index + 1).padStart(3, '0')
    const alphaCode = String.fromCharCode(65 + (index % 26)) // A-Z
    return `#LL-${fileNumber}-${alphaCode}${alphaCode}${alphaCode}`
  }

  // Determine badge type based on post age or other criteria
  const getBadgeType = (post: PostSummary, index: number) => {
    const publishDate = new Date(post.published_at || post.created_at)
    const now = new Date()
    const hoursSincePublish = (now.getTime() - publishDate.getTime()) / (1000 * 60 * 60)
    
    if (hoursSincePublish < 24) return 'breaking'
    if (index === 0 && hoursSincePublish < 48) return 'exclusive'
    if (hoursSincePublish < 72) return 'new'
    if (post.verification_status === 'verified') return 'verified'
    if (post.impact_count && post.impact_count >= 5) return 'high-impact'
    return null
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <header className="main-header">
          <h1 className="main-title">LEXLEAKS</h1>
          <p className="main-subtitle">Exposing the Fine Print.</p>
        </header>
        
        <Navigation currentPage="/" />

        <main>
          <div className="space-y-16">
            {[...Array(3)].map((_, i) => (
              <article key={i} className="article-card">
                <div className="loading-skeleton h-4 w-1/3 mb-2 rounded"></div>
                <div className="loading-skeleton h-8 w-full mb-4 rounded"></div>
                <div className="loading-skeleton h-4 w-full mb-2 rounded"></div>
                <div className="loading-skeleton h-4 w-3/4 rounded"></div>
              </article>
            ))}
          </div>
        </main>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <header className="main-header">
          <TypewriterTitle text="LEXLEAKS" className="main-title" delay={150} />
          <p className="main-subtitle">Exposing the Fine Print.</p>
        </header>
        
        <Navigation currentPage="/" />
        
        <div className="text-center py-12">
          <div className="border border-red-300 dark:border-red-800 bg-red-50 dark:bg-red-950 rounded-lg p-8">
            <h3 className="text-xl font-bold text-red-800 dark:text-red-300 mb-4">Error Loading Content</h3>
            <p className="text-red-700 dark:text-red-400 mb-6">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="brand-button"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header Section with Typewriter Animation */}
      <header className="main-header parallax-container">
        <TypewriterTitle text="LEXLEAKS" className="main-title" delay={150} />
        <p className="main-subtitle">Exposing the Fine Print.</p>
      </header>

      <Navigation currentPage="/" />

            {/* Deep Research Promotion */}
            <div className="mb-12">
              <div className="article-card bg-gradient-to-r from-[#C46A5A]/10 to-[#C46A5A]/5 border-2 border-[#C46A5A]/30">
                <div className="p-8 text-center">
                  <div className="flex items-center justify-center mb-4">
                    <div className="text-4xl mr-3"></div>
                    <div>
                      <h2 className="text-2xl font-display font-bold text-brand-dark dark:text-brand-light">
                        Deep Research by JurisBrain
                      </h2>
                      <p className="text-sm text-brand-muted dark:text-brand-light/70">
                        Commission 50-100+ page legal reports
                      </p>
                    </div>
                  </div>
                  <p className="text-lg leading-relaxed mb-6 text-brand-dark dark:text-brand-light">
                    Plan → Source → Extract → Write → QA → Export. Fully cited. Reproducible.
                    Professional legal research reports with real-time progress tracking.
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Link href="/legal-ai" className="bg-[#C46A5A] hover:bg-[#B85A4A] text-white px-8 py-3 rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-xl">
                       Start Deep Research
                    </Link>
                    <div className="flex items-center justify-center space-x-4 text-sm text-brand-muted dark:text-brand-light/70">
                      <span className="flex items-center">
                        <span className="w-2 h-2 bg-[#3FA796] rounded-full mr-2"></span>
                        Fully Cited
                      </span>
                      <span className="flex items-center">
                        <span className="w-2 h-2 bg-[#D97706] rounded-full mr-2"></span>
                        Real-time Progress
                      </span>
                      <span className="flex items-center">
                        <span className="w-2 h-2 bg-[#64748B] rounded-full mr-2"></span>
                        Professional Quality
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

      {/* Search and Filter Section */}
      {posts.length > 0 && (
        <div className="mb-12">
          <SearchFilter onSearch={handleFilterChange} loading={filterLoading} />
        </div>
      )}

      {/* Main Content: Leaks Feed */}
      <main>
        {posts.length === 0 ? (
          <div className="text-center py-20">
            <div className="max-w-md mx-auto">
              <div className="mb-8">
                <svg className="mx-auto h-16 w-16 text-gray-400 dark:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-4">No Stories Yet</h3>
              <p className="text-lg leading-relaxed mb-8 dark:text-gray-300">
                Be the first to expose misconduct in the legal industry. Your courage to speak up can make a difference.
              </p>
              <Link href="/submit" className="brand-button">
                Submit Your Story
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-16">
            {posts.map((post, index) => {
              const badgeType = getBadgeType(post, index)
              return (
                <article key={post.id} className="article-card group">
                  <Link href={`/${post.slug}`} className="article-link">
                    <div className="flex items-center justify-between mb-2">
                      <div className="case-file">
                        <span>Published: {format(new Date(post.published_at || post.created_at), 'dd MMM yyyy')}</span>
                        {' | '}
                        <span>Case File: {generateCaseFile(index)}</span>
                      </div>
                      {badgeType && <StatusBadge type={badgeType as any} />}
                    </div>
                    <h2 className="article-title text-3xl md:text-4xl leading-tight mb-4 transition-colors duration-300 ease-in-out">
                      {post.title}
                    </h2>
                    {post.excerpt && (
                      <p className="article-excerpt drop-cap">
                        {post.excerpt}
                      </p>
                    )}
                    <div className="read-more group-hover:underline">
                      Read More &rarr;
                    </div>
                  </Link>
                </article>
              )
            })}
          </div>
        )}

        {/* Load More Button */}
        {posts.length >= 20 && (
          <div className="text-center mt-16">
            <button className="brand-button">
              Load More Stories
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="main-footer">
        <p className="footer-text">&copy; 2025 LexLeaks. All Rights Reserved.</p>
        <p className="footer-text mt-1">Dedicated to transparency and accountability in the legal industry.</p>
      </footer>

      {/* PWA Install Prompt */}
      <InstallPWA />
    </div>
  )
} 