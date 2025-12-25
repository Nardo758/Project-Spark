import { useMemo, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

export default function Login() {
  const location = useLocation()
  const navigate = useNavigate()
  const next = useMemo(() => {
    const params = new URLSearchParams(location.search)
    return params.get('next') || '/dashboard'
  }, [location.search])

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [magicStatus, setMagicStatus] = useState('')
  const [magicSending, setMagicSending] = useState(false)

  const { login, isLoading, startReplitAuth, sendMagicLink } = useAuthStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setMagicStatus('')

    try {
      await login(email, password)
      navigate(next)
    } catch {
      setError('Invalid email or password')
    }
  }

  const handleReplit = () => {
    startReplitAuth(next)
  }

  const handleMagicLink = async () => {
    setError('')
    setMagicStatus('')
    const trimmed = email.trim()
    if (!trimmed) {
      setError('Enter your email to receive a magic link.')
      return
    }
    try {
      setMagicSending(true)
      const message = await sendMagicLink(trimmed)
      setMagicStatus(message || 'Magic link sent. Check your email.')
    } catch {
      setError('Failed to send magic link. Please try again.')
    } finally {
      setMagicSending(false)
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome back</h1>
          <p className="text-gray-600">Sign in to your account to continue</p>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-8">
          <button
            type="button"
            onClick={handleReplit}
            className="w-full py-3 bg-black text-white rounded-lg hover:bg-gray-800 font-medium"
          >
            Continue with Replit
          </button>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500">Or use email</span>
              </div>
            </div>
          </div>

          {magicStatus && (
            <div className="mt-4 bg-green-50 text-green-700 px-4 py-3 rounded-lg text-sm">
              {magicStatus}
            </div>
          )}
          {error && (
            <div className="mt-4 bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="mt-5 space-y-3">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="you@example.com"
              />
            </div>

            <button
              type="button"
              onClick={handleMagicLink}
              disabled={magicSending}
              className="w-full py-3 border border-gray-200 rounded-lg hover:bg-gray-50 font-medium disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {magicSending ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Sending link...
                </>
              ) : (
                'Send magic link'
              )}
            </button>
          </div>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500">Or sign in with password</span>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="mt-5 space-y-4">
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 font-medium disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </button>
          </form>
        </div>

        <p className="mt-6 text-center text-sm text-gray-600">
          Don&apos;t have an account?{' '}
          <Link to="/signup" className="text-blue-600 hover:text-blue-700 font-medium">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  )
}
