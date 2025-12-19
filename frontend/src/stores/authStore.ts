import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  email: string
  name: string
  avatar?: string
  tier: 'free' | 'pro' | 'business' | 'enterprise'
  brainTier?: 'basic' | 'business' | 'expert' | 'enterprise'
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
  setUser: (user: User) => void
  setToken: (token: string) => void
  consumeAuthCookies: () => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      
      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
          })
          
          if (!response.ok) throw new Error('Login failed')
          
          const data = await response.json()
          set({
            user: data.user,
            token: data.access_token,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },
      
      signup: async (email: string, password: string, name: string) => {
        set({ isLoading: true })
        try {
          const response = await fetch('/api/v1/auth/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, name }),
          })
          
          if (!response.ok) throw new Error('Signup failed')
          
          const data = await response.json()
          set({
            user: data.user,
            token: data.access_token,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },
      
      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
      },
      
      setUser: (user: User) => set({ user, isAuthenticated: true }),
      setToken: (token: string) => set({ token }),
      
      consumeAuthCookies: () => {
        const getCookie = (name: string): string | null => {
          const value = `; ${document.cookie}`
          const parts = value.split(`; ${name}=`)
          if (parts.length === 2) return parts.pop()?.split(';').shift() || null
          return null
        }
        
        const deleteCookie = (name: string) => {
          document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`
        }
        
        const authToken = getCookie('auth_token')
        const authUserB64 = getCookie('auth_user')
        
        if (authToken && authUserB64) {
          try {
            const userJson = atob(authUserB64)
            const userData = JSON.parse(userJson)
            
            set({
              token: authToken,
              user: {
                id: String(userData.id),
                email: userData.email,
                name: userData.full_name,
                avatar: userData.avatar_url,
                tier: userData.tier || 'free',
                brainTier: userData.brain_tier
              },
              isAuthenticated: true
            })
            
            deleteCookie('auth_token')
            deleteCookie('auth_user')
            return true
          } catch (error) {
            console.error('Failed to parse auth cookies:', error)
          }
        }
        return false
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
)
