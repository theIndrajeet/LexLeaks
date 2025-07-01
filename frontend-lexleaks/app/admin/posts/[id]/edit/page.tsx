'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getPost, updatePost, Post } from '@/lib/api'

export default function EditPostPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const postId = parseInt(params.id)
  
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  
  const [formData, setFormData] = useState({
    title: '',
    slug: '',
    excerpt: '',
    content: '',
    status: 'draft' as 'draft' | 'published' | 'archived'
  })

  useEffect(() => {
    const fetchPost = async () => {
      try {
        const post = await getPost(postId)
        setFormData({
          title: post.title,
          slug: post.slug,
          excerpt: post.excerpt || '',
          content: post.content,
          status: post.status
        })
      } catch (err: any) {
        setError('Failed to load post')
        console.error('Error fetching post:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchPost()
  }, [postId])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess(false)
    setSaving(true)

    try {
      await updatePost(postId, formData)
      setSuccess(true)
      // Redirect to dashboard after short delay to show success message
      setTimeout(() => {
        router.push('/admin/dashboard')
      }, 1500)
    } catch (err: any) {
      setError(err.message || 'Failed to update post')
    } finally {
      setSaving(false)
    }
  }

  const handleSaveAndContinue = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess(false)
    setSaving(true)

    try {
      await updatePost(postId, formData)
      setSuccess(true)
      // Just show success message, don't redirect
    } catch (err: any) {
      setError(err.message || 'Failed to update post')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen brand-bg p-8">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/3 mb-8"></div>
            <div className="bg-white rounded-lg shadow-sm p-8 space-y-6">
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
              <div className="h-10 bg-gray-200 rounded"></div>
              <div className="h-32 bg-gray-200 rounded"></div>
              <div className="h-64 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen brand-bg p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold brand-text">Edit Post</h1>
            <p className="text-gray-600 mt-2">Update your article</p>
          </div>
          <div className="flex gap-3">
            <Link href="/admin/posts" className="admin-button bg-gray-600 hover:bg-gray-700">
              ← All Posts
            </Link>
            <Link href="/admin/dashboard" className="admin-button bg-gray-600 hover:bg-gray-700">
              Dashboard
            </Link>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-sm p-8">
          {error && (
            <div className="border border-red-300 bg-red-50 rounded-lg p-4 mb-6">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {success && (
            <div className="border border-green-300 bg-green-50 rounded-lg p-4 mb-6">
              <p className="text-green-700">Post updated successfully!</p>
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
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
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
                Current URL: /{formData.slug}
                {formData.status === 'published' && (
                  <Link href={`/${formData.slug}`} target="_blank" className="ml-2 text-indigo-600 hover:text-indigo-900">
                    View →
                  </Link>
                )}
              </p>
            </div>

            {/* Excerpt */}
            <div>
              <label htmlFor="excerpt" className="block text-sm font-bold font-mono-special uppercase tracking-wide mb-2">
                Excerpt
              </label>
              <textarea
                id="excerpt"
                value={formData.excerpt}
                onChange={(e) => setFormData({ ...formData, excerpt: e.target.value })}
                className="admin-input w-full"
                rows={3}
                placeholder="Brief summary of the article..."
              />
              <p className="text-sm text-gray-500 mt-1">
                This appears on the homepage and in search results
              </p>
            </div>

            {/* Content */}
            <div>
              <label htmlFor="content" className="block text-sm font-bold font-mono-special uppercase tracking-wide mb-2">
                Content *
              </label>
              <textarea
                id="content"
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                className="admin-input w-full font-mono-special text-sm"
                rows={20}
                required
                placeholder="Write your article content here. You can use HTML tags for formatting..."
              />
              <p className="text-sm text-gray-500 mt-1">
                HTML tags supported: &lt;p&gt;, &lt;h2&gt;, &lt;h3&gt;, &lt;ul&gt;, &lt;ol&gt;, &lt;li&gt;, &lt;blockquote&gt;, &lt;strong&gt;, &lt;em&gt;
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
          <div className="flex justify-between mt-8 pt-8 border-t brand-border">
            <Link href="/admin/dashboard" className="admin-button bg-gray-600 hover:bg-gray-700">
              Cancel
            </Link>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={handleSaveAndContinue}
                disabled={saving}
                className="admin-button bg-gray-600 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saving ? 'Saving...' : 'Save & Continue Editing'}
              </button>
              <button
                type="submit"
                disabled={saving}
                className="admin-button disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saving ? 'Saving...' : 'Save & Close'}
              </button>
            </div>
          </div>
        </form>

        {/* Post Info */}
        <div className="mt-8 bg-white rounded-lg shadow-sm p-8">
          <h2 className="text-lg font-bold mb-4 font-mono-special">Post Information</h2>
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between">
              <dt className="font-mono-special uppercase tracking-wide text-gray-500">Post ID:</dt>
              <dd className="font-mono-special">{postId}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="font-mono-special uppercase tracking-wide text-gray-500">Status:</dt>
              <dd>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  formData.status === 'published' 
                    ? 'bg-green-100 text-green-800'
                    : formData.status === 'draft'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {formData.status}
                </span>
              </dd>
            </div>
            {formData.status === 'published' && (
              <div className="flex justify-between">
                <dt className="font-mono-special uppercase tracking-wide text-gray-500">Public URL:</dt>
                <dd>
                  <Link href={`/${formData.slug}`} target="_blank" className="text-indigo-600 hover:text-indigo-900">
                    /{formData.slug} →
                  </Link>
                </dd>
              </div>
            )}
          </dl>
        </div>
      </div>
    </div>
  )
}
