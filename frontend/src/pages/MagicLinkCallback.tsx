import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export default function MagicLinkCallback() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const { verifyMagicLink } = useAuthStore()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const token = params.get('token')
    const next = params.get('next') || '/dashboard'
    if (!token) {
      setError('Missing magic link token. Please request a new link.')
      return
    }

    ;(async () => {
      try {
        await verifyMagicLink(token)
        navigate(next, { replace: true })
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to verify magic link.')
      }
    })()
  }, [navigate, params, verifyMagicLink])

  if (error) {
    return (
      <div className="max-w-xl mx-auto px-4 py-10">
        <h1 className="text-xl font-semibold text-gray-900 mb-2">Sign-in link error</h1>
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

