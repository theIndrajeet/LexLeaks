const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://lexleaks-api-563011146464.asia-south1.run.app'

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
const getAuthToken = (): string | null => {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('auth_token')
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
  const token = getAuthToken()
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config)
  
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
  const token = getAuthToken()
  
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
export const isLoggedIn = (): boolean => {
  return getAuthToken() !== null
}

export const checkAuthStatus = async (): Promise<User | null> => {
  try {
    if (!getAuthToken()) return null
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