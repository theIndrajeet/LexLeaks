'use client'

import { useState, useEffect } from 'react'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import { format } from 'date-fns'
import { getPostBySlug, Post, getImpacts, Impact } from '@/lib/api'
import ThemeToggle from '@/components/ThemeToggle'
import StatusBadge from '@/components/StatusBadge'
import LanguageSelector from '@/components/LanguageSelector'
import ImpactTracker from '@/components/ImpactTracker'
import DocumentViewer from '@/components/DocumentViewer'

interface PageProps {
  params: {
    slug: string
  }
}

export default function PostPage({ params }: PageProps) {
  const [post, setPost] = useState<Post | null>(null)
  const [impacts, setImpacts] = useState<Impact[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [documentRedactions, setDocumentRedactions] = useState<any[]>([])

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
        
        // Fetch impacts for this post
        try {
          const postImpacts = await getImpacts({ post_id: postData.id })
          setImpacts(postImpacts)
        } catch (err) {
          console.error('Error fetching impacts:', err)
          // Don't fail the whole page if impacts can't be loaded
        }
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

  // Format content with typography enhancements
  const formatContent = (content: string) => {
    // Split into paragraphs
    const paragraphs = content.split('\n\n')
    
    return paragraphs.map((paragraph, index) => {
      // Add drop cap to first paragraph
      if (index === 0) {
        return `<p class="drop-cap">${paragraph}</p>`
      }
      
      // Example: Create pull quotes for paragraphs starting with ">"
      if (paragraph.startsWith('>')) {
        return `<blockquote class="pull-quote">${paragraph.substring(1).trim()}</blockquote>`
      }
      
      return `<p>${paragraph}</p>`
    }).join('')
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
          <div className="flex items-center gap-4">
            <Link href="/submit" className="brand-button">
              Submit a Leak
            </Link>
            <LanguageSelector />
            <ThemeToggle />
          </div>
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
          <div className="border border-red-300 dark:border-red-800 bg-red-50 dark:bg-red-950 rounded-lg p-8">
            <h3 className="text-xl font-bold text-red-800 dark:text-red-300 mb-4">Error Loading Article</h3>
            <p className="text-red-700 dark:text-red-400 mb-6">{error}</p>
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

  // Determine if post is recent
  const isRecent = () => {
    const publishDate = new Date(post.published_at || post.created_at)
    const now = new Date()
    const hoursSincePublish = (now.getTime() - publishDate.getTime()) / (1000 * 60 * 60)
    return hoursSincePublish < 72
  }

  // Check if post has a document URL (you'll need to add this field to your Post model)
  const documentUrl = (post as any).document_url

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
        <div className="flex items-center gap-4">
          <Link href="/submit" className="brand-button">
            Submit a Leak
          </Link>
          <LanguageSelector />
          <ThemeToggle />
        </div>
      </div>

      {/* Main Article Content */}
      <main>
        <article className="mb-16">
          {/* Article Meta */}
          <div className="flex items-center justify-between mb-4">
            <div className="case-file">
              <span>Published: {format(new Date(post.published_at || post.created_at), 'dd MMM yyyy')}</span>
              {' | '}
              <span>Case File: {generateCaseFile()}</span>
              {' | '}
              <span>By: {post.author.username}</span>
              {(post as any).category && (
                <>
                  {' | '}
                  <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded-md text-sm">
                    {(post as any).category}
                  </span>
                </>
              )}
            </div>
            {isRecent() && <StatusBadge type="new" />}
          </div>

          {/* Article Title */}
          <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-6 brand-text">
            {post.title}
          </h1>

          {/* Article Excerpt */}
          {post.excerpt && (
            <div className="border-l-4 brand-border pl-6 mb-8">
              <p className="text-xl italic leading-relaxed text-gray-600 dark:text-gray-400">
                {post.excerpt}
              </p>
            </div>
          )}

          {/* Article Content with Enhanced Typography */}
          <div 
            className="prose prose-lg dark:prose-invert max-w-none text-justify leading-relaxed"
            dangerouslySetInnerHTML={{ 
              __html: formatContent(post.content)
            }} 
          />

          {/* Document Viewer if document URL exists */}
          {documentUrl && (
            <div className="mt-12">
              <h3 className="text-2xl font-bold mb-6">Supporting Documents</h3>
              <DocumentViewer
                documentUrl={documentUrl}
                title={`${post.title} - Evidence`}
                redactedSections={documentRedactions}
                onRedactionsChange={setDocumentRedactions}
                allowRedaction={false}
              />
              {documentRedactions.length > 0 && (
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  This document contains {documentRedactions.length} redacted sections to protect sensitive information.
                </p>
              )}
            </div>
          )}

          {/* Impact Tracker */}
          {impacts.length > 0 && (
            <div className="mt-12">
              <ImpactTracker impacts={impacts} />
            </div>
          )}

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
          <p className="text-lg leading-relaxed mb-6 dark:text-gray-300">
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