'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { createPost } from '@/lib/api'
import RichTextEditor from '@/components/RichTextEditor'
import SimpleRichTextEditor from '@/components/SimpleRichTextEditor'

export default function NewPostPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const isAIEdit = searchParams.get('ai_edit') === 'true'
  
  const [formData, setFormData] = useState({
    title: '',
    slug: '',
    excerpt: '',
    content: '',
    status: 'draft' as 'draft' | 'published' | 'archived'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [isAIGenerated, setIsAIGenerated] = useState(false)

  // Load AI-generated content if coming from AI Writer
  useEffect(() => {
    if (isAIEdit) {
      const aiData = localStorage.getItem('ai_edit_data')
      if (aiData) {
        try {
          const parsedData = JSON.parse(aiData)
          setFormData({
            title: parsedData.title || '',
            slug: parsedData.slug || '',
            excerpt: parsedData.excerpt || '',
            content: parsedData.content || '',
            status: parsedData.status || 'draft'
          })
          setIsAIGenerated(true)
          // Clear the data after loading
          localStorage.removeItem('ai_edit_data')
        } catch (err) {
          console.error('Failed to parse AI data:', err)
        }
      }
    }
  }, [isAIEdit])

  const generateSlug = (title: string) => {
    return title
      .toLowerCase()
      .trim()
      .replace(/[^\w\s-]/g, '')
      .replace(/[\s_-]+/g, '-')
      .replace(/^-+|-+$/g, '')
  }

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const title = e.target.value
    setFormData({
      ...formData,
      title,
      slug: generateSlug(title)
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Validate content has actual text
      const tempDiv = document.createElement('div')
      tempDiv.innerHTML = formData.content
      const textContent = tempDiv.textContent || tempDiv.innerText || ''
      
      if (!textContent.trim()) {
        setError('Content cannot be empty')
        setLoading(false)
        return
      }

      // Check content length (backend might have limits)
      console.log('Content length:', formData.content.length)
      console.log('Text content length:', textContent.length)
      
      // No longer checking content length since backend has no limits
      // Just log for debugging
      console.log('Sending post with content length:', formData.content.length)

      // Don't send slug - backend generates it automatically
      const { slug, ...dataToSend } = formData
      
      console.log('Sending data:', {
        ...dataToSend,
        content: dataToSend.content.substring(0, 100) + '...' // Log first 100 chars
      })
      
      const post = await createPost(dataToSend)
      router.push(`/admin/posts/${post.id}/edit`)
    } catch (err: any) {
      console.error('Error creating post:', err)
      console.error('Error details:', err.response?.data)
      
      // More detailed error message
      if (err.response?.status === 422) {
        const errorDetails = err.response?.data?.detail
        if (Array.isArray(errorDetails)) {
          const fieldErrors = errorDetails.map((e: any) => `${e.loc?.join('.')}: ${e.msg}`).join(', ')
          setError(`Validation error: ${fieldErrors}`)
        } else {
          setError('Validation error: Please check your content format')
        }
      } else {
      setError(err.message || 'Failed to create post')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen brand-bg p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold brand-text">
              {isAIGenerated ? '🤖 Edit AI-Generated Article' : 'Create New Post'}
            </h1>
            <p className="text-gray-600 mt-2">
              {isAIGenerated ? 'Fine-tune your AI-generated article' : 'Write a new article for LexLeaks'}
            </p>
          </div>
          <Link href="/admin/dashboard" className="admin-button bg-gray-600 hover:bg-gray-700">
            ← Back to Dashboard
          </Link>
        </div>

        {/* AI Generated Notice */}
        {isAIGenerated && (
          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center">
              <span className="text-2xl mr-3">🤖</span>
              <div>
                <h3 className="font-semibold text-blue-800">AI-Generated Content Loaded</h3>
                <p className="text-blue-600 text-sm mt-1">
                  This article was generated by AI. You can edit any part of it before saving.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-sm p-8">
          {error && (
            <div className="border border-red-300 bg-red-50 rounded-lg p-4 mb-6">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          <div className="space-y-6">
            {/* Title */}
            <div>
              <label htmlFor="title" className="block text-sm font-bold font-mono-special uppercase tracking-wide mb-2">
                Title *
              </label>
              <input
                id="title"
                type="text"
                value={formData.title}
                onChange={handleTitleChange}
                className="admin-input w-full"
                required
                placeholder="Enter post title..."
              />
            </div>

            {/* Slug */}
            <div>
              <label htmlFor="slug" className="block text-sm font-bold font-mono-special uppercase tracking-wide mb-2">
                URL Slug *
              </label>
              <input
                id="slug"
                type="text"
                value={formData.slug}
                onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
                className="admin-input w-full font-mono-special"
                required
                placeholder="url-friendly-slug"
              />
              <p className="text-sm text-gray-500 mt-1">
                This will be the URL: /{formData.slug || 'url-slug'}
              </p>
            </div>

            {/* Excerpt - Simple Rich Text Editor */}
            <div>
              <label className="block text-sm font-bold font-mono-special uppercase tracking-wide mb-2">
                Excerpt
              </label>
              <SimpleRichTextEditor
                content={formData.excerpt}
                onChange={(excerpt) => setFormData({ ...formData, excerpt })}
                placeholder="Brief summary of the article..."
                rows={3}
                className="mb-2"
              />
              <p className="text-sm text-gray-500 mt-1">
                This appears on the homepage and in search results. Use basic formatting for better presentation.
              </p>
            </div>

            {/* Content - Rich Text Editor */}
            <div>
              <label className="block text-sm font-bold font-mono-special uppercase tracking-wide mb-2">
                Content *
              </label>
              <RichTextEditor
                content={formData.content}
                onChange={(content) => setFormData({ ...formData, content })}
                placeholder="Start writing your article..."
                className="mb-2"
              />
              <p className="text-sm text-gray-500 mt-1">
                Use the toolbar above to format your content. Supports headings, lists, links, images, and more.
              </p>
            </div>

            {/* Status */}
            <div>
              <label htmlFor="status" className="block text-sm font-bold font-mono-special uppercase tracking-wide mb-2">
                Status
              </label>
              <select
                id="status"
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
                className="admin-input w-full"
              >
                <option value="draft">Draft</option>
                <option value="published">Published</option>
                <option value="archived">Archived</option>
              </select>
              <p className="text-sm text-gray-500 mt-1">
                Only published posts appear on the public site
              </p>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end gap-3 mt-8 pt-8 border-t brand-border">
            <Link href="/admin/dashboard" className="admin-button bg-gray-600 hover:bg-gray-700">
              Cancel
            </Link>
            <button
              type="submit"
              disabled={loading}
              className="admin-button disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : (isAIGenerated ? 'Save Edited Article' : 'Create Post')}
            </button>
          </div>
        </form>

        {/* Editor Tips */}
        <div className="mt-8 bg-white rounded-lg shadow-sm p-8">
          <h2 className="text-lg font-bold mb-4 font-mono-special">Editor Tips</h2>
          <div className="space-y-3 text-sm text-gray-600">
            <div className="flex items-start">
              <span className="text-[#8B0000] mr-2">•</span>
              <span>Use <kbd className="px-2 py-1 bg-gray-100 rounded text-xs">Cmd/Ctrl + B</kbd> for bold text</span>
            </div>
            <div className="flex items-start">
              <span className="text-[#8B0000] mr-2">•</span>
              <span>Use <kbd className="px-2 py-1 bg-gray-100 rounded text-xs">Cmd/Ctrl + I</kbd> for italic text</span>
            </div>
            <div className="flex items-start">
              <span className="text-[#8B0000] mr-2">•</span>
              <span>Use <kbd className="px-2 py-1 bg-gray-100 rounded text-xs">Cmd/Ctrl + K</kbd> to add links</span>
            </div>
            <div className="flex items-start">
              <span className="text-[#8B0000] mr-2">•</span>
              <span>Drag and drop or paste images directly into the editor</span>
            </div>
            <div className="flex items-start">
              <span className="text-[#8B0000] mr-2">•</span>
              <span>Start a line with <code className="px-2 py-1 bg-gray-100 rounded text-xs">-</code> or <code className="px-2 py-1 bg-gray-100 rounded text-xs">1.</code> for lists</span>
            </div>
            <div className="flex items-start">
              <span className="text-[#8B0000] mr-2">•</span>
              <span>Start a line with <code className="px-2 py-1 bg-gray-100 rounded text-xs">&gt;</code> for quotes</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
