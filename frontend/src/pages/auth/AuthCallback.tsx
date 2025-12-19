import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() || null
  }
  return null
}

function deleteCookie(name: string) {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`
}

export default function AuthCallback() {
  const navigate = useNavigate()
  const { setUser, setToken } = useAuthStore()

  useEffect(() => {
    const authToken = getCookie('auth_token')
    const authUserB64 = getCookie('auth_user')

    if (authToken && authUserB64) {
      try {
        const userJson = atob(authUserB64)
        const userData = JSON.parse(userJson)

        setToken(authToken)
        setUser({
          id: String(userData.id),
          email: userData.email,
          name: userData.full_name,
          avatar: userData.avatar_url,
          tier: userData.tier || 'free',
          brainTier: userData.brain_tier
        })

        deleteCookie('auth_token')
        deleteCookie('auth_user')

        navigate('/dashboard', { replace: true })
      } catch (error) {
        console.error('Failed to parse auth cookies:', error)
        navigate('/login?error=auth_failed', { replace: true })
      }
    } else {
      navigate('/login?error=no_auth', { replace: true })
    }
  }, [navigate, setUser, setToken])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Completing sign in...</p>
      </div>
    </div>
  )
}
