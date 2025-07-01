'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { format } from 'date-fns'
import { getAllPosts, deletePost, PostSummary } from '@/lib/api'
import { useRouter } from 'next/navigation'

export default function AdminPostsPage() {
  const router = useRouter()
  const [posts, setPosts] = useState<PostSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'published' | 'draft' | 'archived'>('all')
  const [deleting, setDeleting] = useState<number | null>(null)

  useEffect(() => {
    fetchPosts()
  }, [])

  const fetchPosts = async () => {
    try {
      const allPosts = await getAllPosts({ limit: 100 })
      setPosts(allPosts)
    } catch (error) {
      console.error('Failed to fetch posts:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number, title: string) => {
    if (!confirm(`Are you sure you want to delete "${title}"?`)) return
    
    setDeleting(id)
    try {
      await deletePost(id)
      await fetchPosts() // Refresh the list
    } catch (error) {
      console.error('Failed to delete post:', error)
      alert('Failed to delete post')
    } finally {
      setDeleting(null)
    }
  }

  const filteredPosts = posts.filter(post => {
    if (filter === 'all') return true
    return post.status === filter
  })

  if (loading) {
    return (
      <div className="min-h-screen brand-bg p-8">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="bg-white p-6 rounded-lg shadow-sm">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen brand-bg p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold brand-text">All Posts</h1>
            <p className="text-gray-600 mt-2">Manage your LexLeaks content</p>
          </div>
          <div className="flex gap-3">
            <Link href="/admin/dashboard" className="admin-button bg-gray-600 hover:bg-gray-700">
              ← Back to Dashboard
            </Link>
            <Link href="/admin/posts/new" className="admin-button">
              Create New Post
            </Link>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="border-b brand-border">
            <nav className="flex -mb-px">
              <button
                onClick={() => setFilter('all')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  filter === 'all'
                    ? 'border-red-800 text-red-800'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                All ({posts.length})
              </button>
              <button
                onClick={() => setFilter('published')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  filter === 'published'
                    ? 'border-red-800 text-red-800'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Published ({posts.filter(p => p.status === 'published').length})
              </button>
              <button
                onClick={() => setFilter('draft')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  filter === 'draft'
                    ? 'border-red-800 text-red-800'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Drafts ({posts.filter(p => p.status === 'draft').length})
              </button>
              <button
                onClick={() => setFilter('archived')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  filter === 'archived'
                    ? 'border-red-800 text-red-800'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Archived ({posts.filter(p => p.status === 'archived').length})
              </button>
            </nav>
          </div>
        </div>

        {/* Posts Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {filteredPosts.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-gray-500">No posts found in this category.</p>
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Author
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredPosts.map((post) => (
                  <tr key={post.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {post.title}
                        </div>
                        <div className="text-sm text-gray-500">
                          {post.slug}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        post.status === 'published' 
                          ? 'bg-green-100 text-green-800'
                          : post.status === 'draft'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {post.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {format(new Date(post.created_at), 'MMM d, yyyy')}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {post.author.username}
                    </td>
                    <td className="px-6 py-4 text-right text-sm font-medium">
                      <div className="flex justify-end gap-3">
                        {post.status === 'published' && (
                          <Link
                            href={`/${post.slug}`}
                            target="_blank"
                            className="text-gray-600 hover:text-gray-900"
                          >
                            View
                          </Link>
                        )}
                        <Link
                          href={`/admin/posts/${post.id}/edit`}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          Edit
                        </Link>
                        <button
                          onClick={() => handleDelete(post.id, post.title)}
                          disabled={deleting === post.id}
                          className="text-red-600 hover:text-red-900 disabled:opacity-50"
                        >
                          {deleting === post.id ? 'Deleting...' : 'Delete'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}
