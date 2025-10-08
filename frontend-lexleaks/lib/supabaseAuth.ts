import { createClient } from './supabase/client'

const siteUrl = (process.env.NEXT_PUBLIC_SITE_URL as string) || (typeof window !== 'undefined' ? window.location.origin : '')

// Create a singleton instance of the Supabase client
export const supabase = createClient()

export interface SupabaseUser {
  id: string;
  email: string;
  name: string;
  picture?: string;
  is_admin: boolean;
}

export class SupabaseAuthService {
  private static instance: SupabaseAuthService;
  
  public static getInstance(): SupabaseAuthService {
    if (!SupabaseAuthService.instance) {
      SupabaseAuthService.instance = new SupabaseAuthService();
    }
    return SupabaseAuthService.instance;
  }

  async signInWithGoogle(): Promise<void> {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${siteUrl}/auth/callback`
      }
    })
    
    if (error) {
      throw new Error(`Google sign-in failed: ${error.message}`)
    }
  }

  async getCurrentUser(): Promise<SupabaseUser | null> {
    const { data: { session }, error } = await supabase.auth.getSession()
    
    if (error || !session?.user) {
      return null
    }

    return {
      id: session.user.id,
      email: session.user.email!,
      name: session.user.user_metadata.full_name || session.user.email!,
      picture: session.user.user_metadata.avatar_url,
      is_admin: session.user.user_metadata.is_admin || false
    }
  }

  async signOut(): Promise<void> {
    const { error } = await supabase.auth.signOut()
    if (error) {
      throw new Error(`Sign out failed: ${error.message}`)
    }
  }

  onAuthStateChange(callback: (user: SupabaseUser | null) => void) {
    return supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.user) {
        const user = await this.getCurrentUser()
        callback(user)
      } else {
        callback(null)
      }
    })
  }
}
