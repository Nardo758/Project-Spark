import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'

export default function MagicCallback() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { setUser, setToken } = useAuthStore()
  const [error, setError] = useState<string | null>(null)
  const [isVerifying, setIsVerifying] = useState(true)

  useEffect(() => {
    const token = searchParams.get('token')
    
    if (!token) {
      setError('No magic link token provided')
      setIsVerifying(false)
      return
    }

    const verifyToken = async () => {
      try {
        const response = await fetch('/api/v1/magic-link/verify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token })
        })

        if (!response.ok) {
          const data = await response.json()
          throw new Error(data.detail || 'Verification failed')
        }

        const data = await response.json()
        
        setToken(data.access_token)
        setUser({
          id: String(data.user.id),
          email: data.user.email,
          name: data.user.full_name,
          avatar: data.user.avatar_url,
          tier: data.user.tier || 'free',
          brainTier: data.user.brain_tier
        })

        navigate('/dashboard', { replace: true })
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Verification failed')
        setIsVerifying(false)
      }
    }

    verifyToken()
  }, [searchParams, navigate, setUser, setToken])

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Link Expired or Invalid</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => navigate('/login')}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Back to Login
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Verifying magic link...</p>
      </div>
    </div>
  )
}
