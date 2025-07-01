'use client'

import { useState, useEffect } from 'react'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import { format } from 'date-fns'
import { getPostBySlug, Post } from '@/lib/api'

interface PageProps {
  params: {
    slug: string
  }
}

export default function PostPage({ params }: PageProps) {
  const [post, setPost] = useState<Post | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchPost = async () => {
      try {
        const postData = await getPostBySlug(params.slug)
        
        // Check if post is published (for public access)
        if (postData.status !== 'published') {
          notFound()
          return
        }
        
        setPost(postData)
      } catch (err: any) {
        if (err.status === 404) {
          notFound()
        } else {
          setError('Failed to load post')
          console.error('Error fetching post:', err)
        }
      } finally {
        setLoading(false)
      }
    }

    fetchPost()
  }, [params.slug])

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
          <div className="space-y-4">
            <div className="loading-skeleton h-4 w-1/3 mb-2 rounded"></div>
            <div className="loading-skeleton h-10 w-full mb-6 rounded"></div>
            {[...Array(8)].map((_, i) => (
              <div key={i} className="loading-skeleton h-4 w-full rounded"></div>
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
            <h3 className="text-xl font-bold text-red-800 mb-4">Error Loading Article</h3>
            <p className="text-red-700 mb-6">{error}</p>
            <Link href="/" className="brand-button">
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    )
  }

  if (!post) {
    notFound()
    return null
  }

  const generateCaseFile = () => {
    const fileNumber = String(post.id).padStart(3, '0')
    const alphaCode = String.fromCharCode(65 + (post.id % 26)) // A-Z
    return `#LL-${fileNumber}-${alphaCode}${alphaCode}${alphaCode}`
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

      {/* Main Article Content */}
      <main>
        <article className="mb-16">
          {/* Article Meta */}
          <div className="case-file">
            <span>Published: {format(new Date(post.published_at || post.created_at), 'dd MMM yyyy')}</span>
            {' | '}
            <span>Case File: {generateCaseFile()}</span>
            {' | '}
            <span>By: {post.author.username}</span>
          </div>

          {/* Article Title */}
          <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-6 brand-text">
            {post.title}
          </h1>

          {/* Article Excerpt */}
          {post.excerpt && (
            <div className="border-l-4 brand-border pl-6 mb-8">
              <p className="text-xl italic leading-relaxed text-gray-600">
                {post.excerpt}
              </p>
            </div>
          )}

          {/* Article Content */}
          <div className="prose prose-lg max-w-none text-justify leading-relaxed">
            <div 
              className="article-content"
              dangerouslySetInnerHTML={{ 
                __html: post.content.replace(/\n/g, '<br /><br />') 
              }} 
            />
          </div>

          {/* Back to Stories Link */}
          <div className="mt-12 pt-8 border-t-2 brand-border">
            <Link
              href="/"
              className="read-more hover:underline"
            >
              ← Back to All Stories
            </Link>
          </div>
        </article>

        {/* Call to Action */}
        <div className="border-2 brand-border rounded-lg p-8 text-center">
          <h3 className="text-2xl font-bold mb-4">Expose the Truth</h3>
          <p className="text-lg leading-relaxed mb-6">
            Have evidence of legal industry misconduct? Your story could protect others 
            and bring accountability to those who abuse their power.
          </p>
          <Link href="/submit" className="brand-button">
            Submit Your Leak
          </Link>
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