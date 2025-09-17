const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Import Supabase client
import { supabase } from './supabaseAuth'

// Types
export interface User {
  id: number
  username: string
  email: string
  is_admin: boolean
  created_at: string
}

export interface PostSummary {
  id: number
  title: string
  slug: string
  excerpt?: string
  status: 'draft' | 'published' | 'archived'
  verification_status: 'unverified' | 'verified' | 'disputed'
  category?: string
  document_url?: string
  author: {
    id: number
    username: string
  }
  created_at: string
  published_at?: string
  impact_count?: number
}

export interface Post extends PostSummary {
  content: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface PostCreateData {
  title: string
  content: string
  excerpt?: string
  status?: 'draft' | 'published' | 'archived'
  verification_status?: 'unverified' | 'verified' | 'disputed'
  category?: string
  document_url?: string
}

export interface PostUpdateData extends Partial<PostCreateData> {}

// Chat Types
export interface ChatMessage {
  id: string
  session_id: string
  type: 'user_query' | 'research_plan' | 'status_update' | 'section_draft' | 'qa_flag' | 'export_ready' | 'system_message'
  content: string
  timestamp: string
  research_id?: string
  phase?: string
  progress_percentage?: number
  metadata?: Record<string, any>
  reasoning_trail?: Array<{step: string, notes: string}>
  citations?: Array<{id: string, title: string, url: string, court_or_source: string, date: string, type: string, trust_score: number, pin_number: number}>
  followup_questions?: string[]
  action_chips?: Array<{id: string, label: string, action: string, parameters?: Record<string, any>, enabled?: boolean}>
}

export interface ChatSession {
  id: string
  user_id?: string
  created_at: string
  updated_at: string
  active_research_id?: string
  research_scope?: Record<string, any>
  is_active: boolean
  message_count: number
}

export interface ChatRequest {
  session_id?: string
  message: string
  message_type?: 'user_query' | 'research_plan' | 'status_update' | 'section_draft' | 'qa_flag' | 'export_ready' | 'system_message'
  research_scope?: Record<string, any>
}

export interface ChatResponse {
  session_id: string
  message_id: string
  message: ChatMessage
  success: boolean
  timestamp: string
}

export interface Impact {
  id: number
  title: string
  description: string
  date: string
  type: 'legal_action' | 'policy_change' | 'investigation' | 'resignation' | 'reform'
  status: 'pending' | 'in_progress' | 'completed'
  post_id: number
  created_at: string
  updated_at?: string
}

export interface ImpactCreateData {
  title: string
  description: string
  date: string
  type: 'legal_action' | 'policy_change' | 'investigation' | 'resignation' | 'reform'
  status: 'pending' | 'in_progress' | 'completed'
  post_id: number
}

export interface ImpactUpdateData extends Partial<Omit<ImpactCreateData, 'post_id'>> {}

// Auth utilities
const getAuthToken = async (): Promise<string | null> => {
  if (typeof window === 'undefined') return null
  
  try {
    // First try to get Supabase token
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.access_token) {
      return session.access_token
    }
    
    // Fallback to legacy token
    return localStorage.getItem('auth_token')
  } catch (error) {
    console.error('Error getting auth token:', error)
    return localStorage.getItem('auth_token')
  }
}

const setAuthToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth_token', token)
  }
}

const removeAuthToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token')
  }
}

// API request helper
const apiRequest = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<any> => {
  const token = await getAuthToken()
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  }

  let response = await fetch(`${API_BASE_URL}${endpoint}`, config)

  // If token expired, try to refresh it
  if (response.status === 401 && token) {
    const newToken = await refreshToken()
    if (newToken) {
      // Retry the request with new token
      config.headers = {
        ...config.headers,
        'Authorization': `Bearer ${newToken}`
      }
      response = await fetch(`${API_BASE_URL}${endpoint}`, config)
    }
  }
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
  }

  // Handle 204 No Content responses
  if (response.status === 204) {
    return null
  }

  return response.json()
}

// Auth API
export const login = async (username: string, password: string): Promise<AuthResponse> => {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)

  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || 'Login failed')
  }

  const data = await response.json()
  setAuthToken(data.access_token)
  return data
}

export const logout = (): void => {
  removeAuthToken()
}

export const getCurrentUser = async (): Promise<User> => {
  return apiRequest('/api/auth/me')
}

// Posts API
export const getPublishedPosts = async (params: {
  limit?: number
  skip?: number
  search?: string
  status?: string
  verification_status?: string
  category?: string
  author?: string
  date_from?: string
  date_to?: string
  sort_by?: 'newest' | 'oldest' | 'impact'
  impact_level?: 'high' | 'medium' | 'low'
} = {}): Promise<PostSummary[]> => {
  const queryParams = new URLSearchParams()
  if (params.limit) queryParams.append('limit', params.limit.toString())
  if (params.skip) queryParams.append('skip', params.skip.toString())
  if (params.search) queryParams.append('search', params.search)
  if (params.status) queryParams.append('status', params.status)
  if (params.verification_status) queryParams.append('verification_status', params.verification_status)
  if (params.category) queryParams.append('category', params.category)
  if (params.author) queryParams.append('author', params.author)
  if (params.date_from) queryParams.append('date_from', params.date_from)
  if (params.date_to) queryParams.append('date_to', params.date_to)
  if (params.sort_by) queryParams.append('sort_by', params.sort_by)
  if (params.impact_level) queryParams.append('impact_level', params.impact_level)

  const endpoint = `/api/posts/${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
  return apiRequest(endpoint)
}

export const getPostBySlug = async (slug: string): Promise<Post> => {
  return apiRequest(`/api/posts/slug/${slug}`)
}

export const getAllPosts = async (params: {
  limit?: number
  skip?: number
  search?: string
} = {}): Promise<PostSummary[]> => {
  const queryParams = new URLSearchParams()
  if (params.limit) queryParams.append('limit', params.limit.toString())
  if (params.skip) queryParams.append('skip', params.skip.toString())
  if (params.search) queryParams.append('search', params.search)

  const endpoint = `/api/posts/${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
  return apiRequest(endpoint)
}

export const getPost = async (id: number): Promise<Post> => {
  return apiRequest(`/api/posts/${id}`)
}

export const createPost = async (data: PostCreateData): Promise<Post> => {
  return apiRequest('/api/posts/', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export const updatePost = async (id: number, data: PostUpdateData): Promise<Post> => {
  return apiRequest(`/api/posts/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export const deletePost = async (id: number): Promise<void> => {
  const token = await getAuthToken()
  
  const response = await fetch(`${API_BASE_URL}/api/posts/${id}`, {
    method: 'DELETE',
    headers: {
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  })
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
  }
  
  // DELETE endpoints typically return 204 No Content with no body
  // So we don't try to parse JSON
}

// Admin utilities
export const isLoggedIn = async (): Promise<boolean> => {
  const token = await getAuthToken()
  return token !== null
}

export const checkAuthStatus = async (): Promise<User | null> => {
  try {
    const token = await getAuthToken()
    if (!token) return null
    return await getCurrentUser()
  } catch (error) {
    removeAuthToken()
    return null
  }
}

// Impact API
export const getImpacts = async (params: {
  limit?: number
  skip?: number
  post_id?: number
  type?: string
  status?: string
} = {}): Promise<Impact[]> => {
  const queryParams = new URLSearchParams()
  if (params.limit) queryParams.append('limit', params.limit.toString())
  if (params.skip) queryParams.append('skip', params.skip.toString())
  if (params.post_id) queryParams.append('post_id', params.post_id.toString())
  if (params.type) queryParams.append('type', params.type)
  if (params.status) queryParams.append('status', params.status)

  const endpoint = `/api/impacts${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
  return apiRequest(endpoint)
}

export const getImpact = async (id: number): Promise<Impact> => {
  return apiRequest(`/api/impacts/${id}`)
}

export const createImpact = async (data: ImpactCreateData): Promise<Impact> => {
  return apiRequest('/api/impacts/', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export const updateImpact = async (id: number, data: ImpactUpdateData): Promise<Impact> => {
  return apiRequest(`/api/impacts/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export const deleteImpact = async (id: number): Promise<void> => {
  return apiRequest(`/api/impacts/${id}`, {
    method: 'DELETE',
  })
}

// AI API
export interface AIGenerateRequest {
  topic: string
  article_type: 'quick' | 'standard' | 'deep'
  ai_provider: 'gemini' | 'perplexity' | 'both'
  template: 'internship' | 'legal_explainer'
  publish_option: 'now' | 'draft' | 'schedule'
  scheduled_for?: string
  category?: string
}

export interface AIGenerateResponse {
  success: boolean
  post_id: number
  title: string
  status: string
  word_count: number
  provider: string
  scheduled_for?: string
  preview_url?: string
}

export const generateAIArticle = async (data: AIGenerateRequest): Promise<AIGenerateResponse> => {
  return apiRequest('/api/ai/generate', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}


export const publishScheduledPosts = async (): Promise<any> => {
  return apiRequest('/api/ai/publish-scheduled', {
    method: 'POST',
  })
}

// Trends API
export interface TrendingTopic {
  topic: string
  category: string
  trend_score: number
  suggested_article_type: 'quick' | 'standard' | 'deep'
  suggested_template: 'internship' | 'legal_explainer'
  interest_value?: number
}

export interface TrendsResponse {
  trending_topics: TrendingTopic[]
  last_updated: string | null
  total_found: number
  categories: string[]
}

export const getTrendingLegalTopics = async (): Promise<TrendsResponse> => {
  return apiRequest('/api/trends/legal-topics', {
    method: 'GET',
  })
}

export const refreshTrendingTopics = async (): Promise<{ message: string }> => {
  return apiRequest('/api/trends/refresh', {
    method: 'POST',
  })
}

// Scheduler API
export interface SchedulerStatus {
  is_running: boolean
  automation_enabled: boolean
  generation_time: string
  publish_time: string
  timezone: string
  next_generation: string
  next_publish: string
}

export interface SchedulerStats {
  total_ai_posts: number
  published_ai_posts: number
  scheduled_posts: number
  posts_today: number
  posts_this_week: number
  success_rate: number
}

export interface ScheduledPost {
  id: number
  title: string
  scheduled_for: string
  category: string
  created_at: string
}

export const getSchedulerStatus = async (): Promise<SchedulerStatus> => {
  return apiRequest('/api/scheduler/status', {
    method: 'GET',
  })
}

export const startScheduler = async (): Promise<any> => {
  return apiRequest('/api/scheduler/start', {
    method: 'POST',
  })
}

export const stopScheduler = async (): Promise<any> => {
  return apiRequest('/api/scheduler/stop', {
    method: 'POST',
  })
}

export const toggleAutomation = async (enabled: boolean): Promise<any> => {
  return apiRequest('/api/scheduler/toggle-automation', {
    method: 'POST',
    body: JSON.stringify({ enabled }),
  })
}

export const updateSchedule = async (generation_time: string, publish_time: string): Promise<any> => {
  return apiRequest('/api/scheduler/update-schedule', {
    method: 'POST',
    body: JSON.stringify({ generation_time, publish_time }),
  })
}

export const manualGenerateArticle = async (topic: string, article_type: string = 'standard', template: string = 'legal_explainer', publish_option: string = 'draft'): Promise<any> => {
  return apiRequest('/api/scheduler/manual-generate', {
    method: 'POST',
    body: JSON.stringify({ topic, article_type, template, publish_option }),
  })
}

export const manualPublishScheduled = async (): Promise<any> => {
  return apiRequest('/api/scheduler/manual-publish', {
    method: 'POST',
  })
}

export const getScheduledPosts = async (): Promise<{ scheduled_posts: ScheduledPost[], total_count: number }> => {
  return apiRequest('/api/scheduler/scheduled-posts', {
    method: 'GET',
  })
}

export const getSchedulerStats = async (): Promise<{ stats: SchedulerStats }> => {
  return apiRequest('/api/scheduler/stats', {
    method: 'GET',
  })
}

// Legal AI API
// Structured message interfaces for conversation routing
export interface StructuredMessage {
  type: 'USER_QUERY' | 'FOLLOWUP' | 'SCOPE_UPDATE' | 'UI_EVENT' | 'META'
  action?: 'RETRY_LAST' | 'WIDEN_SCOPE' | 'NARROW_TO_SC' | 'ADD_CONTEXT' | 'SIMPLIFY_ANSWER' | 'EXPAND_ANSWER'
  text?: string | null
  state_delta?: {
    scope?: {
      court?: string
      date_range?: string
      jurisdiction?: string
    }
  }
}

export interface LegalQueryRequest {
  session_id?: string
  message: StructuredMessage
}

export interface LegalQueryResponse {
  success?: boolean
  error?: string
  session_id: string
  turn_id: string
  answer: {
    summary: string
    text: string
    confidence: 'high' | 'medium' | 'low'
  }
  reasoning_trail: Array<{
    step: string
    notes: string
  }>
  citations: Array<{
    pin: number
    type: 'case' | 'web'
    title: string
    court_or_source: string
    date: string
    url: string
    snippet: string
    lines: string
    weight: 'binding' | 'secondary'
  }>
  followups: string[]
  memory_update: {
    scope: any
    facts: string[]
  }
  telemetry: {
    mode: string
    tools_used: string[]
    duration_ms: number
  }
  timestamp: string
}

// Chat State Types
export interface ChatState {
  sessionId: string
  messages: Array<UserMsg | AIMsg>
  memory: {
    scope: { jurisdiction: string; court: string; date_range: string }
    facts: string[]
    preferences: { style: 'concise' | 'detailed'; export: 'PDF' | 'DOCX' | 'MD' }
  }
  streamingTurnId?: string
}

export interface UserMsg {
  id: string
  type: 'user'
  content: string
  timestamp: string
}

export interface AIMsg {
  id: string
  type: 'ai'
  turn_id: string
  answer: {
    summary: string
    text: string
    confidence: 'high' | 'medium' | 'low'
  }
  reasoning_trail: Array<{
    step: string
    notes: string
  }>
  citations: Array<{
    pin: number
    type: 'case' | 'web'
    title: string
    court_or_source: string
    date: string
    url: string
    snippet: string
    lines: string
    weight: 'binding' | 'secondary'
  }>
  followups: string[]
  timestamp: string
  isStreaming?: boolean
}

export const processLegalQuery = async (data: LegalQueryRequest): Promise<LegalQueryResponse> => {
  return apiRequest('/api/legal-ai/query', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

// Legacy support for simple text queries
export const processLegalQueryLegacy = async (query: string, context?: string, session_id?: string): Promise<LegalQueryResponse> => {
  return processLegalQuery({
    session_id,
    message: {
      type: 'USER_QUERY',
      text: query,
      state_delta: {}
    }
  })
}

// Chat API Functions
export const sendChatMessage = async (data: ChatRequest): Promise<ChatResponse> => {
  return apiRequest('/api/chat/send', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export const getChatMessages = async (sessionId: string, limit: number = 50): Promise<{messages: ChatMessage[], session_id: string, total_count: number}> => {
  return apiRequest(`/api/chat/messages/${sessionId}?limit=${limit}`, {
    method: 'GET',
  })
}

export const getChatSessions = async (): Promise<{sessions: ChatSession[], total_count: number}> => {
  return apiRequest('/api/chat/sessions', {
    method: 'GET',
  })
}

export const getResearchStatus = async (researchId: string): Promise<{
  research_id: string,
  session_id: string,
  current_phase: string,
  progress_percentage: number,
  is_streaming: boolean,
  progress_details: any
}> => {
  return apiRequest(`/api/chat/research-status/${researchId}`, {
    method: 'GET',
  })
}

// New Event-Driven Research API Functions
export interface EventDrivenResearchRequest {
  topic: string
  jurisdictions: string[]
  depth_level: 'quick' | 'comprehensive' | 'exhaustive'
  audience: 'legal_professional' | 'student' | 'general'
  focus_areas: string[]
}

export interface EventDrivenResearchResponse {
  success: boolean
  run_id: string
  message: string
  architecture: string
  estimated_output: string
  estimated_time: string
}

export interface EventDrivenResearchStatus {
  status: string
  started_at: string
  topic: string
  total_tasks: number
  word_target: number
  completed_tasks: number
  progress_percentage: number
  current_phase: string
  estimated_completion: string
  plan?: any
}

export const startEventDrivenResearch = async (request: EventDrivenResearchRequest): Promise<EventDrivenResearchResponse> => {
  return apiRequest('/api/event-driven-research/start-research', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export const getEventDrivenResearchStatus = async (runId: string): Promise<EventDrivenResearchStatus> => {
  return apiRequest(`/api/event-driven-research/status/${runId}`, {
    method: 'GET',
  })
}

export const getEventDrivenResearchResults = async (runId: string): Promise<any> => {
  return apiRequest(`/api/event-driven-research/results/${runId}`, {
    method: 'GET',
  })
}

export const handleChatAction = async (actionId: string, sessionId: string, parameters?: Record<string, any>): Promise<{message: string}> => {
  return apiRequest(`/api/chat/action/${actionId}`, {
    method: 'POST',
    body: JSON.stringify({
      session_id: sessionId,
      parameters: parameters || {}
    }),
  })
}

// WebSocket connection for real-time updates
export const createChatWebSocket = (sessionId: string): WebSocket => {
  const wsUrl = `${API_BASE_URL.replace('http', 'ws')}/api/chat/ws/${sessionId}`
  return new WebSocket(wsUrl)
}

export const getLegalAIHealth = async (): Promise<any> => {
  return apiRequest('/api/legal-ai/health')
}

export const getLegalAIStats = async (): Promise<any> => {
  return apiRequest('/api/legal-ai/stats')
}

export const testLegalQuery = async (): Promise<any> => {
  return apiRequest('/api/legal-ai/test-query', {
    method: 'POST',
  })
}

export const getSessionInfo = async (sessionId: string): Promise<any> => {
  return apiRequest(`/api/legal-ai/session/${sessionId}`)
}

export const clearSession = async (sessionId: string): Promise<any> => {
  return apiRequest(`/api/legal-ai/session/${sessionId}`, {
    method: 'DELETE',
  })
}

// Pipeline API
export interface TrendingTopic {
  title: string
  category: string
  angle: string
  target_audience: string
  trending_reason: string
  suggested_article_type: 'quick' | 'standard' | 'deep'
  suggested_template: 'internship' | 'legal_explainer'
  generated_by: string
  confidence_score: number
  source_links?: string[]
}

export interface PipelineResponse {
  success: boolean
  message: string
  topics?: TrendingTopic[]
  source_articles_count?: number
}

export const getTrendingTopics = async (): Promise<PipelineResponse> => {
  return apiRequest('/api/pipeline/generate-topics', {
    method: 'GET',
  })
}

export const runManualPipeline = async (): Promise<PipelineResponse> => {
  return apiRequest('/api/pipeline/manual-pipeline-run', {
    method: 'POST',
  })
}

export const getScraperStats = async (): Promise<any> => {
  return apiRequest('/api/pipeline/scraper-stats', {
    method: 'GET',
  })
}

export const getGeminiStats = async (): Promise<any> => {
  return apiRequest('/api/pipeline/gemini-stats', {
    method: 'GET',
  })
} 
export const refreshToken = async (): Promise<string | null> => {
  try {
    const token = await getAuthToken()
    if (!token) return null

    const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      removeAuthToken()
      return null
    }

    const data = await response.json()
    setAuthToken(data.access_token)
    return data.access_token
  } catch (error) {
    removeAuthToken()
    return null
  }
}
