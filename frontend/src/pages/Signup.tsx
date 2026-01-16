import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { Loader2, Check, Crown } from 'lucide-react'

const planDetails: Record<string, { name: string; price: string; color: string }> = {
  'pro': { name: 'Builder', price: '$99/mo', color: 'purple' },
  'builder': { name: 'Builder', price: '$99/mo', color: 'purple' },
  'business': { name: 'Scaler', price: '$499/mo', color: 'emerald' },
  'scaler': { name: 'Scaler', price: '$499/mo', color: 'emerald' },
  'enterprise': { name: 'Enterprise', price: 'Custom', color: 'amber' }
}

export default function Signup() {
  const [searchParams] = useSearchParams()
  const selectedPlan = searchParams.get('plan')
  const planInfo = selectedPlan ? planDetails[selectedPlan.toLowerCase()] : null
  
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [acceptedTerms, setAcceptedTerms] = useState(false)
  const [error, setError] = useState('')
  const { signup, isLoading, startReplitAuth, startGoogleAuth, startLinkedInAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    if (!acceptedTerms) {
      setError('You must accept the Terms of Service and Privacy Policy to continue.')
      return
    }
    
    try {
      await signup(email, password, name)
      if (selectedPlan && planInfo) {
        navigate(`/pricing?checkout=${selectedPlan}`)
      } else {
        navigate('/dashboard')
      }
    } catch {
      setError('Failed to create account. Please try again.')
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {planInfo && (
          <div className={`mb-6 p-4 rounded-xl border-2 ${
            planInfo.color === 'purple' ? 'bg-purple-50 border-purple-200' :
            planInfo.color === 'emerald' ? 'bg-emerald-50 border-emerald-200' :
            'bg-amber-50 border-amber-200'
          }`}>
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${
                planInfo.color === 'purple' ? 'bg-purple-100' :
                planInfo.color === 'emerald' ? 'bg-emerald-100' :
                'bg-amber-100'
              }`}>
                <Crown className={`w-5 h-5 ${
                  planInfo.color === 'purple' ? 'text-purple-600' :
                  planInfo.color === 'emerald' ? 'text-emerald-600' :
                  'text-amber-600'
                }`} />
              </div>
              <div>
                <p className="font-semibold text-gray-900">
                  You're signing up for {planInfo.name}
                </p>
                <p className="text-sm text-gray-600">
                  {planInfo.price} - You'll complete checkout after registration
                </p>
              </div>
            </div>
          </div>
        )}
        
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Create your account</h1>
          <p className="text-gray-600">
            {planInfo ? `Complete registration to activate your ${planInfo.name} plan` : 'Start building your startup today'}
          </p>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Full name
              </label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="John Doe"
              />
            </div>
            
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
                minLength={8}
                className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="••••••••"
              />
              <p className="mt-1 text-xs text-gray-500">Must be at least 8 characters</p>
            </div>

            <div className="flex items-start gap-3">
              <button
                type="button"
                onClick={() => setAcceptedTerms(!acceptedTerms)}
                className={`mt-0.5 w-5 h-5 rounded border-2 flex items-center justify-center shrink-0 transition-colors ${
                  acceptedTerms 
                    ? 'bg-purple-600 border-purple-600' 
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                {acceptedTerms && <Check className="w-3 h-3 text-white" />}
              </button>
              <label 
                onClick={() => setAcceptedTerms(!acceptedTerms)}
                className="text-sm text-gray-600 cursor-pointer select-none"
              >
                I agree to the{' '}
                <Link 
                  to="/terms" 
                  target="_blank"
                  className="text-purple-600 hover:text-purple-700 font-medium"
                  onClick={(e) => e.stopPropagation()}
                >
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link 
                  to="/privacy" 
                  target="_blank"
                  className="text-purple-600 hover:text-purple-700 font-medium"
                  onClick={(e) => e.stopPropagation()}
                >
                  Privacy Policy
                </Link>
              </label>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-black text-white rounded-lg hover:bg-gray-800 font-medium disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Creating account...
                </>
              ) : (
                'Create account'
              )}
            </button>
          </form>

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
              <button 
                type="button"
                onClick={() => startGoogleAuth(selectedPlan ? `/pricing?checkout=${selectedPlan}` : '/dashboard')}
                className="w-full py-2.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-sm font-medium text-gray-700"
              >
                Google
              </button>
              <button 
                type="button"
                onClick={() => startReplitAuth(selectedPlan ? `/pricing?checkout=${selectedPlan}` : '/dashboard')}
                className="w-full py-2.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-sm font-medium text-gray-700"
              >
                Replit
              </button>
              <button 
                type="button"
                onClick={() => startLinkedInAuth(selectedPlan ? `/pricing?checkout=${selectedPlan}` : '/dashboard')}
                className="w-full py-2.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-sm font-medium text-gray-700"
              >
                LinkedIn
              </button>
            </div>
          </div>
        </div>

        <p className="mt-6 text-center text-sm text-gray-600">
          Already have an account?{' '}
          <Link to="/login" className="text-blue-600 hover:text-blue-700 font-medium">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
