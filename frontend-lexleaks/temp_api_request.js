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
