import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number
  email: string
  name: string
  avatar_url?: string
  is_verified?: boolean
  is_admin?: boolean
  tier?: 'free' | 'pro' | 'business' | 'enterprise'
  brainTier?: 'basic' | 'business' | 'expert' | 'enterprise'
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  isBootstrapped: boolean
  bootstrap: () => Promise<void>
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, name: string) => Promise<void>
  startReplitAuth: (next?: string) => void
  startGoogleAuth: (next?: string) => Promise<void>
  consumeReplitAuthCookies: () => boolean
  sendMagicLink: (email: string) => Promise<string>
  verifyMagicLink: (token: string) => Promise<void>
  logout: () => void
  setUser: (user: User) => void
  setToken: (token: string) => void
}

const ACCESS_TOKEN_KEYS = ['access_token', 'token'] as const

function setLegacyAccessToken(token: string) {
  try {
    for (const k of ACCESS_TOKEN_KEYS) localStorage.setItem(k, token)
  } catch {
    // ignore storage errors
  }
}

function clearLegacyAccessToken() {
  try {
    for (const k of ACCESS_TOKEN_KEYS) localStorage.removeItem(k)
  } catch {
    // ignore storage errors
  }
}

function parseCookies(): Record<string, string> {
  return document.cookie.split(';').reduce<Record<string, string>>((acc, c) => {
    const [rawKey, ...rest] = c.trim().split('=')
    const key = rawKey?.trim()
    if (!key) return acc
    acc[key] = rest.join('=')
    return acc
  }, {})
}

function clearCookie(name: string) {
  document.cookie = `${name}=; max-age=0; path=/`
}

function normalizeUser(raw: unknown): User | null {
  if (!raw || typeof raw !== 'object') return null
  const obj = raw as Record<string, unknown>

  const id = Number(obj.id)
  if (!Number.isFinite(id)) return null

  const email = typeof obj.email === 'string' ? obj.email : ''
  const nameCandidate =
    (typeof obj.name === 'string' && obj.name) ||
    (typeof obj.full_name === 'string' && obj.full_name) ||
    email.split('@')[0] ||
    'User'
  const name = String(nameCandidate)

  const tierRaw = typeof obj.tier === 'string' ? obj.tier.toLowerCase() : ''
  const validTiers = ['free', 'pro', 'business', 'enterprise'] as const
  const tier: User['tier'] = validTiers.includes(tierRaw as (typeof validTiers)[number]) ? (tierRaw as User['tier']) : undefined

  const brainTierRaw =
    typeof obj.brainTier === 'string'
      ? obj.brainTier.toLowerCase()
      : typeof obj.brain_tier === 'string'
        ? obj.brain_tier.toLowerCase()
        : ''
  const validBrainTiers = ['basic', 'business', 'expert', 'enterprise'] as const
  const brainTier: User['brainTier'] = validBrainTiers.includes(brainTierRaw as (typeof validBrainTiers)[number])
    ? (brainTierRaw as User['brainTier'])
    : undefined

  return {
    id,
    email,
    name,
    avatar_url:
      typeof obj.avatar_url === 'string'
        ? obj.avatar_url
        : typeof obj.avatar === 'string'
          ? obj.avatar
          : undefined,
    is_verified: typeof obj.is_verified === 'boolean' ? obj.is_verified : undefined,
    is_admin: typeof obj.is_admin === 'boolean' ? obj.is_admin : undefined,
    tier,
    brainTier,
  }
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      isBootstrapped: false,

      bootstrap: async () => {
        try {
          // 1) Pick up Replit Auth cookies if present.
          if (!get().token) {
            get().consumeReplitAuthCookies()
          }

          const token = get().token
          if (!token) {
            set({ isAuthenticated: false, user: null })
            return
          }

          // 2) Hydrate user from backend (authoritative) if missing.
          if (!get().user) {
            const res = await fetch('/api/v1/users/me', {
              headers: { Authorization: `Bearer ${token}` },
            })
            if (!res.ok) {
              throw new Error('Unauthorized')
            }
            const data = await res.json().catch(() => ({}))
            const user = normalizeUser(data)
            if (user) {
              set({ user, isAuthenticated: true })
              try {
                localStorage.setItem('user', JSON.stringify(user))
              } catch {
                // ignore
              }
            }
          } else {
            // Ensure flags line up if token exists.
            set({ isAuthenticated: true })
          }
        } catch {
          // Token invalid/expired; clear local auth state
          clearLegacyAccessToken()
          try {
            localStorage.removeItem('user')
          } catch {
            // ignore
          }
          set({ user: null, token: null, isAuthenticated: false })
        } finally {
          set({ isBootstrapped: true })
        }
      },
      
      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          // Backend uses OAuth2PasswordRequestForm (x-www-form-urlencoded).
          const body = new URLSearchParams()
          body.set('username', email)
          body.set('password', password)

          const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body,
          })
          
          if (!response.ok) throw new Error('Login failed')
          
          const data = await response.json()
          if (data?.requires_2fa) {
            throw new Error('Two-factor authentication required')
          }

          const user = normalizeUser(data.user)
          if (data.access_token) setLegacyAccessToken(data.access_token)
          set({
            user,
            token: data.access_token,
            isAuthenticated: true,
            isLoading: false,
          })
          try {
            if (user) localStorage.setItem('user', JSON.stringify(user))
          } catch {
            // ignore
          }
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },
      
      signup: async (email: string, password: string, name: string) => {
        set({ isLoading: true })
        try {
          const response = await fetch('/api/v1/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, name }),
          })
          
          if (!response.ok) throw new Error('Signup failed')
          
          // Register returns user; it may not return a token (password login still needed).
          const data = await response.json().catch(() => ({}))
          const user = normalizeUser(data)
          set({ user, isAuthenticated: Boolean(user), isLoading: false })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      startReplitAuth: (next?: string) => {
        const dest = next || '/dashboard'
        const redirectUrl = `/auth/callback?next=${encodeURIComponent(dest)}`
        window.location.href = `/auth/login?redirect_url=${encodeURIComponent(redirectUrl)}`
      },

      startGoogleAuth: async (next?: string) => {
        const dest = next || '/dashboard'
        const callbackUrl = `${window.location.origin}/auth/oauth-callback?next=${encodeURIComponent(dest)}`
        try {
          const res = await fetch(`/api/v1/oauth/google/login?redirect_uri=${encodeURIComponent(callbackUrl)}`)
          const data = await res.json()
          if (data.authorization_url) {
            window.location.href = data.authorization_url
          } else {
            throw new Error('Failed to get authorization URL')
          }
        } catch (error) {
          console.error('Google auth error:', error)
          throw error
        }
      },

      consumeReplitAuthCookies: () => {
        try {
          const cookies = parseCookies()
          const tokenCookie = cookies.auth_token
          const userCookie = cookies.auth_user

          let token: string | null = null
          let user: User | null = null

          if (tokenCookie) {
            token = decodeURIComponent(tokenCookie)
            clearCookie('auth_token')
          }

          if (userCookie) {
            try {
              const b64 = decodeURIComponent(userCookie)
              const json = atob(b64)
              const raw = JSON.parse(json)
              user = normalizeUser(raw)
            } catch {
              // ignore parse failure
            } finally {
              clearCookie('auth_user')
            }
          }

          if (token) {
            setLegacyAccessToken(token)
            set({
              token,
              user,
              isAuthenticated: true,
            })
            try {
              if (user) localStorage.setItem('user', JSON.stringify(user))
            } catch {
              // ignore
            }
            return true
          }
          return false
        } catch {
          return false
        }
      },

      sendMagicLink: async (email: string) => {
        const res = await fetch('/api/v1/magic-link/send', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email }),
        })
        const data = await res.json().catch(() => ({}))
        if (!res.ok) throw new Error(data?.detail || 'Failed to send magic link')
        return String(data?.message || 'Magic link sent! Check your email.')
      },

      verifyMagicLink: async (token: string) => {
        const res = await fetch('/api/v1/magic-link/verify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token }),
        })
        const data = await res.json().catch(() => ({}))
        if (!res.ok) throw new Error(data?.detail || 'Failed to verify magic link')
        const user = normalizeUser(data.user)
        if (data.access_token) setLegacyAccessToken(data.access_token)
        set({
          user,
          token: data.access_token,
          isAuthenticated: true,
        })
        try {
          if (user) localStorage.setItem('user', JSON.stringify(user))
        } catch {
          // ignore
        }
      },
      
      logout: () => {
        clearLegacyAccessToken()
        try {
          localStorage.removeItem('user')
          localStorage.removeItem('auth-storage')
        } catch {
          // ignore
        }
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
      },
      
      setUser: (user: User) => set({ user, isAuthenticated: true }),
      setToken: (token: string) => {
        setLegacyAccessToken(token)
        set({ token, isAuthenticated: true })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
)
