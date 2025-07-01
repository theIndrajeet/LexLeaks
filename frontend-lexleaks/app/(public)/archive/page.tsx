'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { format } from 'date-fns'
import { getAllPosts, PostSummary } from '@/lib/api'

export default function ArchivePage() {
  const [posts, setPosts] = useState<PostSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<'all' | 'published' | 'archived'>('all')

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const allPosts = await getAllPosts({ limit: 100 })
        setPosts(allPosts)
      } catch (err) {
        setError('Failed to load archive')
        console.error('Error fetching posts:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchPosts()
  }, [])

  const filteredPosts = posts.filter(post => {
    if (filter === 'all') return true
    return post.status === filter
  })

  const generateCaseFile = (index: number) => {
    const fileNumber = String(index + 1).padStart(3, '0')
    const alphaCode = String.fromCharCode(65 + (index % 26))
    return `#LL-${fileNumber}-${alphaCode}${alphaCode}${alphaCode}`
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <header className="main-header">
          <h1 className="main-title">LEXLEAKS</h1>
          <p className="main-subtitle">Exposing the Fine Print.</p>
        </header>
        
        <div className="flex flex-col sm:flex-row justify-between items-center mb-16">
          <nav className="main-nav space-x-6 text-sm mb-6 sm:mb-0">
            <Link href="/" className="nav-link">Home</Link>
            <Link href="/about" className="nav-link">About</Link>
            <Link href="/archive" className="nav-link brand-accent font-bold">Archive</Link>
          </nav>
          <Link href="/submit" className="brand-button">
            Submit a Leak
          </Link>
        </div>

        <main>
          <div className="space-y-8">
            {[...Array(5)].map((_, i) => (
              <article key={i} className="article-card">
                <div className="loading-skeleton h-4 w-1/3 mb-2 rounded"></div>
                <div className="loading-skeleton h-6 w-full mb-3 rounded"></div>
                <div className="loading-skeleton h-4 w-full rounded"></div>
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
          <h1 className="main-title">LEXLEAKS</h1>
          <p className="main-subtitle">Exposing the Fine Print.</p>
        </header>
        
        <div className="text-center py-12">
          <div className="border border-red-300 bg-red-50 rounded-lg p-8">
            <h3 className="text-xl font-bold text-red-800 mb-4">Error Loading Archive</h3>
            <p className="text-red-700 mb-6">{error}</p>
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
      {/* Header Section */}
      <header className="main-header">
        <h1 className="main-title">LEXLEAKS</h1>
        <p className="main-subtitle">Exposing the Fine Print.</p>
      </header>

      {/* Navigation & Submit Button */}
      <div className="flex flex-col sm:flex-row justify-between items-center mb-16">
        <nav className="main-nav space-x-6 text-sm mb-6 sm:mb-0">
          <Link href="/" className="nav-link">Home</Link>
          <Link href="/about" className="nav-link">About</Link>
          <Link href="/archive" className="nav-link brand-accent font-bold">Archive</Link>
        </nav>
        <Link href="/submit" className="brand-button">
          Submit a Leak
        </Link>
      </div>

      {/* Main Content */}
      <main>
        {/* Archive Header */}
        <div className="mb-12">
          <div className="case-file">
            <span>Complete Archive</span>
            {' | '}
            <span>Total Files: {posts.length}</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-6 brand-text">
            Investigation Archive
          </h1>

          <p className="text-lg leading-relaxed mb-8">
            A complete record of all LexLeaks investigations, including active cases and archived reports.
          </p>

          {/* Filter Buttons */}
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 font-mono-special text-sm uppercase tracking-wide border-2 transition-colors ${
                filter === 'all' 
                  ? 'bg-gray-800 text-white border-gray-800' 
                  : 'bg-transparent brand-text brand-border hover:bg-gray-100'
              }`}
            >
              All Files ({posts.length})
            </button>
            <button
              onClick={() => setFilter('published')}
              className={`px-4 py-2 font-mono-special text-sm uppercase tracking-wide border-2 transition-colors ${
                filter === 'published' 
                  ? 'bg-gray-800 text-white border-gray-800' 
                  : 'bg-transparent brand-text brand-border hover:bg-gray-100'
              }`}
            >
              Active ({posts.filter(p => p.status === 'published').length})
            </button>
            <button
              onClick={() => setFilter('archived')}
              className={`px-4 py-2 font-mono-special text-sm uppercase tracking-wide border-2 transition-colors ${
                filter === 'archived' 
                  ? 'bg-gray-800 text-white border-gray-800' 
                  : 'bg-transparent brand-text brand-border hover:bg-gray-100'
              }`}
            >
              Archived ({posts.filter(p => p.status === 'archived').length})
            </button>
          </div>
        </div>

        {/* Posts Grid */}
        {filteredPosts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-lg">No files found in this category.</p>
          </div>
        ) : (
          <div className="space-y-8">
            {filteredPosts.map((post, index) => (
              <article key={post.id} className="border-b-2 brand-border pb-8">
                <Link href={`/${post.slug}`} className="group article-link">
                  <div className="flex items-start justify-between mb-3">
                    <div className="case-file">
                      <span>{format(new Date(post.published_at || post.created_at), 'dd MMM yyyy')}</span>
                      {' | '}
                      <span>Case File: {generateCaseFile(index)}</span>
                      {' | '}
                      <span className="uppercase">{post.status}</span>
                    </div>
                  </div>
                  <h2 className="article-title text-2xl md:text-3xl leading-tight mb-3 transition-colors duration-300 ease-in-out">
                    {post.title}
                  </h2>
                  {post.excerpt && (
                    <p className="text-base leading-relaxed text-gray-600">
                      {post.excerpt}
                    </p>
                  )}
                  <div className="read-more group-hover:underline mt-4">
                    View Full Report &rarr;
                  </div>
                </Link>
              </article>
            ))}
          </div>
        )}

        {/* Archive Info */}
        <div className="mt-16 border-2 brand-border rounded-lg p-8">
          <h3 className="text-xl font-bold mb-4 font-mono-special">Archive Information</h3>
          <p className="leading-relaxed mb-4">
            This archive contains all LexLeaks investigations since our founding. Active cases 
            represent ongoing investigations or recent exposures. Archived cases are older 
            investigations that remain relevant for historical context and ongoing reforms.
          </p>
          <p className="text-sm font-mono-special text-gray-600">
            For researchers and journalists: Contact us for additional documentation or source verification.
          </p>
        </div>
      </main>

      {/* Footer */}
      <footer className="main-footer">
        <p className="footer-text">&copy; 2025 LexLeaks. All Rights Reserved.</p>
        <p className="footer-text mt-1">Dedicated to transparency and accountability in the legal industry.</p>
      </footer>
    </div>
  )
} 