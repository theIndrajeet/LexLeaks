'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { generateAIArticle, getPost, AIGenerateRequest, AIGenerateResponse } from '@/lib/api'

type GenerationResult = AIGenerateResponse

export default function AIWriterPage() {
  const router = useRouter()
  const [topic, setTopic] = useState('')
  const [articleType, setArticleType] = useState<'quick' | 'standard' | 'deep'>('standard')
  const [aiProvider, setAiProvider] = useState<'gemini' | 'perplexity' | 'both'>('gemini')
  const [publishOption, setPublishOption] = useState<'now' | 'draft' | 'schedule'>('draft')
  const [scheduledFor, setScheduledFor] = useState('')
  const [category, setCategory] = useState('ai-generated')
  
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<GenerationResult | null>(null)
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    if (!topic.trim()) {
      setError('Please enter a topic')
      return
    }

    if (publishOption === 'schedule' && !scheduledFor) {
      setError('Please select a date and time for scheduling')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const data = await generateAIArticle({
        topic,
        article_type: articleType,
        ai_provider: aiProvider,
        publish_option: publishOption,
        scheduled_for: publishOption === 'schedule' ? scheduledFor : undefined,
        category
      })

      setResult(data)
      // Clear form
      setTopic('')
      setScheduledFor('')
    } catch (err: any) {
      setError(err.message || 'Failed to generate article')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleEditArticle = async () => {
    if (!result) return
    
    try {
      // Fetch the full post data
      const postData = await getPost(result.post_id)
      
      // Store the post data in localStorage for the Create New Post page
      localStorage.setItem('ai_edit_data', JSON.stringify({
        title: postData.title,
        slug: postData.slug,
        excerpt: postData.excerpt,
        content: postData.content,
        status: postData.status,
        isAIEdit: true,
        originalPostId: result.post_id
      }))
      
      // Redirect to Create New Post page
      router.push('/admin/posts/new?ai_edit=true')
    } catch (err: any) {
      setError('Failed to load article for editing: ' + err.message)
    }
  }

  return (
    <div className="min-h-screen brand-bg p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold brand-text">🤖 AI Article Generator</h1>
          <p className="text-gray-600 mt-2">Generate high-quality articles using AI</p>
        </div>

        {/* Main Form */}
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="space-y-6">
            {/* Topic Input */}
            <div>
              <label className="block text-sm font-bold font-mono-special uppercase tracking-wide mb-2">
                Topic / Prompt *
              </label>
              <textarea
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="admin-input w-full"
                rows={3}
                placeholder="e.g., 'Apple's antitrust case and its implications for tech companies' or 'Latest Supreme Court ruling on privacy rights'"
              />
              <p className="text-sm text-gray-500 mt-1">
                Be specific for better results. Include context, companies, or legal areas you want covered.
              </p>
            </div>

            {/* Article Type */}
            <div>
              <label className="block text-sm font-bold font-mono-special uppercase tracking-wide mb-2">
                Article Type
              </label>
              <div className="grid grid-cols-3 gap-4">
                <div 
                  className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                    articleType === 'quick' 
                      ? 'border-red-800 bg-red-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setArticleType('quick')}
                >
                  <div className="font-semibold">📰 Quick Take</div>
                  <div className="text-sm text-gray-600 mt-1">300-500 words</div>
                  <div className="text-xs text-gray-500 mt-1">1-2 minute read</div>
                </div>
                
                <div 
                  className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                    articleType === 'standard' 
                      ? 'border-red-800 bg-red-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setArticleType('standard')}
                >
                  <div className="font-semibold">📄 Standard</div>
                  <div className="text-sm text-gray-600 mt-1">800-1200 words</div>
                  <div className="text-xs text-gray-500 mt-1">5 minute read</div>
                </div>
                
                <div 
                  className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                    articleType === 'deep' 
                      ? 'border-red-800 bg-red-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setArticleType('deep')}
                >
                  <div className="font-semibold">📚 Deep Dive</div>
                  <div className="text-sm text-gray-600 mt-1">1500-2000 words</div>
                  <div className="text-xs text-gray-500 mt-1">10 minute read</div>
                </div>
              </div>
            </div>

            {/* AI Provider */}
            <div>
              <label className="block text-sm font-bold font-mono-special uppercase tracking-wide mb-2">
                AI Provider
              </label>
              <select
                value={aiProvider}
                onChange={(e) => setAiProvider(e.target.value as any)}
                className="admin-input w-full"
              >
                <option value="gemini">🤖 Gemini (Fast & Creative)</option>
                <option value="perplexity">🔍 Perplexity (Research-Heavy)</option>
                <option value="both">⚡ Both (Gemini first, Perplexity fallback)</option>
              </select>
            </div>

            {/* Publishing Options */}
            <div>
              <label className="block text-sm font-bold font-mono-special uppercase tracking-wide mb-2">
                Publishing
              </label>
              <div className="space-y-3">
                <div className="flex items-center">
                  <input
                    type="radio"
                    id="publish-now"
                    name="publishOption"
                    value="now"
                    checked={publishOption === 'now'}
                    onChange={(e) => setPublishOption(e.target.value as any)}
                    className="mr-3"
                  />
                  <label htmlFor="publish-now">🚀 Publish immediately</label>
                </div>
                
                <div className="flex items-center">
                  <input
                    type="radio"
                    id="save-draft"
                    name="publishOption"
                    value="draft"
                    checked={publishOption === 'draft'}
                    onChange={(e) => setPublishOption(e.target.value as any)}
                    className="mr-3"
                  />
                  <label htmlFor="save-draft">📝 Save as draft</label>
                </div>
                
                <div className="flex items-center">
                  <input
                    type="radio"
                    id="schedule"
                    name="publishOption"
                    value="schedule"
                    checked={publishOption === 'schedule'}
                    onChange={(e) => setPublishOption(e.target.value as any)}
                    className="mr-3"
                  />
                  <label htmlFor="schedule">⏰ Schedule for later</label>
                </div>
                
                {publishOption === 'schedule' && (
                  <div className="ml-6 mt-3">
                    <input
                      type="datetime-local"
                      value={scheduledFor}
                      onChange={(e) => setScheduledFor(e.target.value)}
                      className="admin-input"
                      min={new Date().toISOString().slice(0, 16)}
                    />
                  </div>
                )}
              </div>
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-bold font-mono-special uppercase tracking-wide mb-2">
                Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="admin-input w-full"
              >
                <option value="ai-generated">AI Generated</option>
                <option value="corporate">Corporate</option>
                <option value="judicial">Judicial</option>
                <option value="criminal">Criminal</option>
                <option value="regulatory">Regulatory</option>
                <option value="ethics">Ethics</option>
              </select>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mt-6 border border-red-300 bg-red-50 rounded-lg p-4">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 mt-8 pt-8 border-t brand-border">
            <Link href="/admin/dashboard" className="admin-button bg-gray-600 hover:bg-gray-700">
              Cancel
            </Link>
            <button
              onClick={handleGenerate}
              disabled={loading || !topic.trim()}
              className="admin-button disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '🤖 Generating...' : '✨ Generate Article'}
            </button>
          </div>
        </div>

        {/* Success Result */}
        {result && (
          <div className="mt-8 bg-green-50 border border-green-200 rounded-lg p-6">
            <h3 className="text-lg font-bold text-green-800 mb-4">✅ Article Generated Successfully!</h3>
            <div className="space-y-2 text-sm">
              <p><strong>Title:</strong> {result.title}</p>
              <p><strong>Status:</strong> {result.status}</p>
              <p><strong>Word Count:</strong> {result.word_count}</p>
              <p><strong>AI Provider:</strong> {result.provider}</p>
              {result.scheduled_for && (
                <p><strong>Scheduled for:</strong> {new Date(result.scheduled_for).toLocaleString()}</p>
              )}
            </div>
            <div className="flex gap-3 mt-4">
              <button
                onClick={handleEditArticle}
                className="admin-button"
              >
                Edit Article
              </button>
              {result.preview_url && (
                <a
                  href={result.preview_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="admin-button bg-green-600 hover:bg-green-700"
                >
                  View Live
                </a>
              )}
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
              <div>
                <h3 className="font-semibold text-blue-800">Generating your article...</h3>
                <p className="text-blue-600 text-sm mt-1">This may take 30-60 seconds</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
