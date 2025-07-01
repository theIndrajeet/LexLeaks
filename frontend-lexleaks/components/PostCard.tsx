import Link from 'next/link'
import { format } from 'date-fns'

interface PostCardProps {
  post: {
    id: number
    title: string
    slug: string
    excerpt?: string
    status: string
    published_at?: string
    created_at: string
    author: {
      id: number
      username: string
    }
  }
  showStatus?: boolean
}

export default function PostCard({ post, showStatus = false }: PostCardProps) {
  return (
    <article className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-center text-sm text-gray-500 mb-3">
          <time dateTime={post.published_at || post.created_at}>
            {format(
              new Date(post.published_at || post.created_at),
              'MMMM d, yyyy'
            )}
          </time>
          <span className="mx-2">•</span>
          <span>By {post.author.username}</span>
        </div>

        <Link href={`/${post.slug}`} className="group">
          <h3 className="text-xl font-semibold text-gray-900 group-hover:text-primary-600 transition-colors mb-3">
            {post.title}
          </h3>
        </Link>

        {post.excerpt && (
          <p className="text-gray-600 mb-4 leading-relaxed">
            {post.excerpt}
          </p>
        )}

        <div className="flex items-center justify-between">
          <Link
            href={`/${post.slug}`}
            className="text-primary-600 hover:text-primary-800 font-medium text-sm"
          >
            Read full story →
          </Link>
          
          {showStatus && (
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                post.status === 'published' 
                  ? 'bg-green-100 text-green-800'
                  : post.status === 'draft'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {post.status}
              </span>
            </div>
          )}
        </div>
      </div>
    </article>
  )
} 