import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export default function AuthCallback() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const { consumeReplitAuthCookies, setToken } = useAuthStore()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const next = params.get('next') || '/dashboard'

    // Primary: Replit Auth cookie handoff (auth_token/auth_user).
    const ok = consumeReplitAuthCookies()
    if (ok) {
      navigate(next, { replace: true })
      return
    }

    // Back-compat: allow ?token=... callbacks if ever used.
    const token = params.get('token')
    if (token) {
      setToken(token)
      navigate(next, { replace: true })
      return
    }

    setError('Authentication callback missing token/cookies. Please try signing in again.')
  }, [consumeReplitAuthCookies, navigate, params, setToken])

  if (error) {
    return (
      <div className="max-w-xl mx-auto px-4 py-10">
        <h1 className="text-xl font-semibold text-gray-900 mb-2">Sign-in error</h1>
        <p className="text-red-700 bg-red-50 border border-red-200 rounded-lg px-4 py-3">{error}</p>
        <div className="mt-4">
          <Link to="/login" className="text-blue-600 hover:text-blue-700 font-medium">
            Back to login
          </Link>
        </div>
      </div>
    )
  }

  return <div className="max-w-xl mx-auto px-4 py-10">Signing you in…</div>
}
