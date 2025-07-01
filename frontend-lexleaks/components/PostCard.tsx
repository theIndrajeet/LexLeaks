import Link from 'next/link'
import { format } from 'date-fns'

interface PostCardProps {
  post: {
    id: number
    title: string
    slug: string
    excerpt?: string
    status: string
    verification_status?: 'unverified' | 'verified' | 'disputed'
    category?: string
    document_url?: string
    published_at?: string
    created_at: string
    author: {
      id: number
      username: string
    }
    impact_count?: number
  }
  showStatus?: boolean
}

const categoryColors: Record<string, string> = {
  corporate: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
  criminal: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
  judicial: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
  regulatory: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
  ethics: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
  discrimination: 'bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300',
  financial: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
}

export default function PostCard({ post, showStatus = false }: PostCardProps) {
  return (
    <article className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
            <time dateTime={post.published_at || post.created_at}>
              {format(
                new Date(post.published_at || post.created_at),
                'MMMM d, yyyy'
              )}
            </time>
            <span className="mx-2">•</span>
            <span>By {post.author.username}</span>
            {post.impact_count !== undefined && post.impact_count > 0 && (
              <>
                <span className="mx-2">•</span>
                <span className="font-medium text-orange-600 dark:text-orange-400">
                  {post.impact_count} impact{post.impact_count !== 1 ? 's' : ''}
                </span>
              </>
            )}
          </div>
          <div className="flex items-center gap-2">
            {post.verification_status === 'verified' && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300">
                <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Verified
              </span>
            )}
            {post.category && (
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                categoryColors[post.category] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
              }`}>
                {post.category.charAt(0).toUpperCase() + post.category.slice(1).replace('_', ' ')}
              </span>
            )}
          </div>
        </div>

        <Link href={`/${post.slug}`} className="group">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors mb-3">
            {post.title}
          </h3>
        </Link>

        {post.excerpt && (
          <p className="text-gray-600 dark:text-gray-300 mb-4 leading-relaxed">
            {post.excerpt}
          </p>
        )}

        <div className="flex items-center justify-between">
          <Link
            href={`/${post.slug}`}
            className="text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-300 font-medium text-sm"
          >
            Read full story →
          </Link>
          
          {showStatus && (
            <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                post.status === 'published' 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                  : post.status === 'draft'
                  ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
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