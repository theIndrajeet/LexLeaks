export interface GoogleUser {
  id: number;
  email: string;
  name: string;
  picture?: string;
  is_admin: boolean;
  username?: string;
}

export interface GoogleAuthResponse {
  authorization_url: string;
  state: string;
}

export class GoogleAuthService {
  private static instance: GoogleAuthService;
  
  public static getInstance(): GoogleAuthService {
    if (!GoogleAuthService.instance) {
      GoogleAuthService.instance = new GoogleAuthService();
    }
    return GoogleAuthService.instance;
  }

  async initiateGoogleLogin(): Promise<string> {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/auth/google/login`, {
        method: 'GET',
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Failed to initiate Google login');
      }
      
      const data: GoogleAuthResponse = await response.json();
      
      // Store state for verification
      localStorage.setItem('google_oauth_state', data.state);
      
      // Redirect to Google
      window.location.href = data.authorization_url;
      
      return data.authorization_url;
    } catch (error) {
      console.error('Google login initiation failed:', error);
      throw error;
    }
  }

  async getGoogleUserInfo(): Promise<GoogleUser> {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/auth/google/user-info`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get user info');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get Google user info:', error);
      throw error;
    }
  }

  handleAuthCallback(): { token: string; user_id: string } | null {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const user_id = urlParams.get('user_id');
    
    if (token && user_id) {
      // Store token
      localStorage.setItem('auth_token', token);
      localStorage.setItem('user_id', user_id);
      
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
      
      return { token, user_id };
    }
    
    return null;
  }
}
