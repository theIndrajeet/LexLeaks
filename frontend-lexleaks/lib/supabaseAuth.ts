import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL as string
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY as string
const siteUrl = (process.env.NEXT_PUBLIC_SITE_URL as string) || (typeof window !== 'undefined' ? window.location.origin : '')

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Supabase env vars missing. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

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
    const { data: { user }, error } = await supabase.auth.getUser()
    
    if (error || !user) {
      return null
    }

    return {
      id: user.id,
      email: user.email!,
      name: user.user_metadata.full_name || user.email!,
      picture: user.user_metadata.avatar_url,
      is_admin: user.user_metadata.is_admin || false
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
