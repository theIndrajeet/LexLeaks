'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { createPost } from '@/lib/api'

export default function NewPostPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    title: '',
    slug: '',
    excerpt: '',
    content: '',
    status: 'draft' as 'draft' | 'published' | 'archived'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

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
      const post = await createPost(formData)
      router.push(`/admin/posts/${post.id}/edit`)
    } catch (err: any) {
      setError(err.message || 'Failed to create post')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen brand-bg p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold brand-text">Create New Post</h1>
            <p className="text-gray-600 mt-2">Write a new article for LexLeaks</p>
          </div>
          <Link href="/admin/dashboard" className="admin-button bg-gray-600 hover:bg-gray-700">
            ← Back to Dashboard
          </Link>
        </div>

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
          <div className="flex justify-end gap-3 mt-8 pt-8 border-t brand-border">
            <Link href="/admin/dashboard" className="admin-button bg-gray-600 hover:bg-gray-700">
              Cancel
            </Link>
            <button
              type="submit"
              disabled={loading}
              className="admin-button disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Create Post'}
            </button>
          </div>
        </form>

        {/* HTML Reference */}
        <div className="mt-8 bg-white rounded-lg shadow-sm p-8">
          <h2 className="text-lg font-bold mb-4 font-mono-special">HTML Reference</h2>
          <div className="space-y-3 font-mono-special text-sm">
            <div>
              <code className="bg-gray-100 px-2 py-1 rounded">&lt;p&gt;Paragraph text&lt;/p&gt;</code>
            </div>
            <div>
              <code className="bg-gray-100 px-2 py-1 rounded">&lt;h2&gt;Section Heading&lt;/h2&gt;</code>
            </div>
            <div>
              <code className="bg-gray-100 px-2 py-1 rounded">&lt;ul&gt;&lt;li&gt;Bullet point&lt;/li&gt;&lt;/ul&gt;</code>
            </div>
            <div>
              <code className="bg-gray-100 px-2 py-1 rounded">&lt;blockquote&gt;Quote text&lt;/blockquote&gt;</code>
            </div>
            <div>
              <code className="bg-gray-100 px-2 py-1 rounded">&lt;strong&gt;Bold text&lt;/strong&gt;</code>
            </div>
            <div>
              <code className="bg-gray-100 px-2 py-1 rounded">&lt;em&gt;Italic text&lt;/em&gt;</code>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
