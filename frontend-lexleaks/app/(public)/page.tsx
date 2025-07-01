'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { format } from 'date-fns'
import { getPublishedPosts, PostSummary } from '@/lib/api'

export default function HomePage() {
  const [posts, setPosts] = useState<PostSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const publishedPosts = await getPublishedPosts({ limit: 20 })
        setPosts(publishedPosts)
      } catch (err) {
        setError('Failed to load posts')
        console.error('Error fetching posts:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchPosts()
  }, [])

  const generateCaseFile = (index: number) => {
    const fileNumber = String(index + 1).padStart(3, '0')
    const alphaCode = String.fromCharCode(65 + (index % 26)) // A-Z
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
            <Link href="/archive" className="nav-link">Archive</Link>
          </nav>
          <Link href="/submit" className="brand-button">
            Submit a Leak
          </Link>
        </div>

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
          <h1 className="main-title">LEXLEAKS</h1>
          <p className="main-subtitle">Exposing the Fine Print.</p>
        </header>
        
        <div className="text-center py-12">
          <div className="border border-red-300 bg-red-50 rounded-lg p-8">
            <h3 className="text-xl font-bold text-red-800 mb-4">Error Loading Content</h3>
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
          <Link href="/archive" className="nav-link">Archive</Link>
        </nav>
        <Link href="/submit" className="brand-button">
          Submit a Leak
        </Link>
      </div>

      {/* Main Content: Leaks Feed */}
      <main>
        {posts.length === 0 ? (
          <div className="text-center py-20">
            <div className="max-w-md mx-auto">
              <div className="mb-8">
                <svg className="mx-auto h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-4">No Stories Yet</h3>
              <p className="text-lg leading-relaxed mb-8">
                Be the first to expose misconduct in the legal industry. Your courage to speak up can make a difference.
              </p>
              <Link href="/submit" className="brand-button">
                Submit Your Story
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-16">
            {posts.map((post, index) => (
              <article key={post.id} className="article-card">
                <Link href={`/${post.slug}`} className="group article-link">
                  <div className="case-file">
                    <span>Published: {format(new Date(post.published_at || post.created_at), 'dd MMM yyyy')}</span>
                    {' | '}
                    <span>Case File: {generateCaseFile(index)}</span>
                  </div>
                  <h2 className="article-title text-3xl md:text-4xl leading-tight mb-4 transition-colors duration-300 ease-in-out">
                    {post.title}
                  </h2>
                  {post.excerpt && (
                    <p className="article-excerpt">
                      {post.excerpt}
                    </p>
                  )}
                  <div className="read-more group-hover:underline">
                    Read More &rarr;
                  </div>
                </Link>
              </article>
            ))}
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
    </div>
  )
} 