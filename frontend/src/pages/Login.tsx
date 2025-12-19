import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { Loader2, Mail, Zap } from 'lucide-react'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [magicEmail, setMagicEmail] = useState('')
  const [error, setError] = useState('')
  const [magicLinkSent, setMagicLinkSent] = useState(false)
  const [showMagicLink, setShowMagicLink] = useState(false)
  const [sendingMagic, setSendingMagic] = useState(false)
  const { login, isLoading } = useAuthStore()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const errorParam = searchParams.get('error')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch {
      setError('Invalid email or password')
    }
  }

  const handleReplitAuth = () => {
    window.location.href = '/auth/login?redirect_url=/auth/callback'
  }

  const handleMagicLink = async (e: React.FormEvent) => {
    e.preventDefault()
    setSendingMagic(true)
    setError('')

    try {
      const response = await fetch('/api/v1/magic-link/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: magicEmail })
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to send magic link')
      }

      setMagicLinkSent(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send magic link')
    } finally {
      setSendingMagic(false)
    }
  }

  if (magicLinkSent) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Mail className="w-8 h-8 text-purple-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Check your email</h1>
          <p className="text-gray-600 mb-6">
            We sent a magic link to <strong>{magicEmail}</strong>. Click the link in the email to sign in.
          </p>
          <button
            onClick={() => {
              setMagicLinkSent(false)
              setMagicEmail('')
            }}
            className="text-purple-600 hover:text-purple-700 font-medium"
          >
            Use a different email
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome back</h1>
          <p className="text-gray-600">Sign in to your account to continue</p>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-8">
          {(error || errorParam) && (
            <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm mb-6">
              {error || 'Authentication failed. Please try again.'}
            </div>
          )}

          <button
            onClick={handleReplitAuth}
            className="w-full py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium flex items-center justify-center gap-2 mb-4"
          >
            <Zap className="w-5 h-5" />
            Continue with Replit
          </button>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white text-gray-500">Or</span>
            </div>
          </div>

          {showMagicLink ? (
            <form onSubmit={handleMagicLink} className="space-y-4">
              <div>
                <label htmlFor="magic-email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email address
                </label>
                <input
                  id="magic-email"
                  type="email"
                  value={magicEmail}
                  onChange={(e) => setMagicEmail(e.target.value)}
                  required
                  autoComplete="email"
                  className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="you@example.com"
                />
              </div>
              <button
                type="submit"
                disabled={sendingMagic}
                className="w-full py-3 bg-black text-white rounded-lg hover:bg-gray-800 font-medium disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {sendingMagic ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Mail className="w-5 h-5" />
                    Send Magic Link
                  </>
                )}
              </button>
              <button
                type="button"
                onClick={() => setShowMagicLink(false)}
                className="w-full text-sm text-gray-600 hover:text-gray-900"
              >
                Use password instead
              </button>
            </form>
          ) : (
            <>
              <form onSubmit={handleSubmit} className="space-y-4">
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
                    autoComplete="email"
                    className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="you@example.com"
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                    Password
                  </label>
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    autoComplete="current-password"
                    className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="••••••••"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full py-3 bg-black text-white rounded-lg hover:bg-gray-800 font-medium disabled:opacity-50 flex items-center justify-center gap-2"
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

              <button
                onClick={() => setShowMagicLink(true)}
                className="w-full mt-4 py-2.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-sm font-medium text-gray-700 flex items-center justify-center gap-2"
              >
                <Mail className="w-4 h-4" />
                Sign in with Magic Link
              </button>
            </>
          )}

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500">Or continue with</span>
              </div>
            </div>

            <div className="mt-6 grid grid-cols-3 gap-3">
              <button className="w-full py-2.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-sm font-medium text-gray-700">
                Google
              </button>
              <button className="w-full py-2.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-sm font-medium text-gray-700">
                GitHub
              </button>
              <button className="w-full py-2.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-sm font-medium text-gray-700">
                LinkedIn
              </button>
            </div>
          </div>
        </div>

        <p className="mt-6 text-center text-sm text-gray-600">
          Don't have an account?{' '}
          <Link to="/signup" className="text-purple-600 hover:text-purple-700 font-medium">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  )
}
