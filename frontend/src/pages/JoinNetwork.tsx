import { useState, useEffect } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { 
  Users, 
  TrendingUp, 
  Briefcase, 
  Building2, 
  CheckCircle,
  ArrowLeft,
  Linkedin,
  Loader2
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

const roleConfig = {
  expert: {
    title: 'Expert',
    description: 'Share your expertise, mentor entrepreneurs, and earn by validating ideas',
    icon: Users,
    benefits: [
      'Set your own hourly rates',
      'Build your professional reputation',
      'Access exclusive consulting opportunities',
      'Connect with founders seeking guidance'
    ],
    color: 'indigo'
  },
  investor: {
    title: 'Investor',
    description: 'Discover vetted opportunities and connect with promising entrepreneurs',
    icon: TrendingUp,
    benefits: [
      'Early access to validated opportunities',
      'Connect with pre-vetted founders',
      'AI-powered deal flow analysis',
      'Direct introductions to startups'
    ],
    color: 'green'
  },
  partner: {
    title: 'Partner',
    description: 'Offer your services to a network of growing businesses',
    icon: Briefcase,
    benefits: [
      'Access to startup ecosystem',
      'Inbound leads from qualified businesses',
      'Partnership opportunities',
      'Platform visibility and promotion'
    ],
    color: 'blue'
  },
  lender: {
    title: 'Lender',
    description: 'Connect with businesses seeking financing for acquisitions and growth',
    icon: Building2,
    benefits: [
      'Qualified borrower leads',
      'Pre-screened opportunity data',
      'Direct applicant connections',
      'Market intelligence insights'
    ],
    color: 'amber'
  }
}

type RoleKey = keyof typeof roleConfig

export default function JoinNetwork() {
  const { role } = useParams<{ role: string }>()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { setToken } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const currentRole = (role as RoleKey) || 'expert'
  const config = roleConfig[currentRole] || roleConfig.expert
  const Icon = config.icon

  useEffect(() => {
    const code = searchParams.get('code')
    const name = searchParams.get('name')
    const error = searchParams.get('error')

    if (error) {
      setErrorMessage(decodeURIComponent(error))
      return
    }

    if (code) {
      const redeemCode = async () => {
        try {
          const response = await fetch(`/api/v1/auth/linkedin/redeem?code=${code}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
          })
          
          if (!response.ok) {
            const data = await response.json()
            setErrorMessage(data.detail || 'Authentication failed. Please try again.')
            return
          }
          
          const data = await response.json()
          const token = data.access_token
          
          localStorage.setItem('token', token)
          setToken(token)
          setSuccessMessage(`Welcome, ${decodeURIComponent(name || data.user?.name || 'new member')}! You've successfully joined as a ${config.title}.`)
          
          setTimeout(() => {
            navigate(`/network/${currentRole}`)
          }, 2000)
        } catch (err) {
          setErrorMessage('Authentication failed. Please try again.')
        }
      }
      
      redeemCode()
    }
  }, [searchParams, setToken, navigate, currentRole, config.title])

  const handleLinkedInLogin = () => {
    setIsLoading(true)
    window.location.href = `/api/v1/auth/linkedin/login?role=${currentRole}`
  }

  const colorClasses = {
    indigo: {
      bg: 'bg-indigo-600',
      hover: 'hover:bg-indigo-700',
      light: 'bg-indigo-50',
      text: 'text-indigo-600',
      border: 'border-indigo-200'
    },
    green: {
      bg: 'bg-green-600',
      hover: 'hover:bg-green-700',
      light: 'bg-green-50',
      text: 'text-green-600',
      border: 'border-green-200'
    },
    blue: {
      bg: 'bg-blue-600',
      hover: 'hover:bg-blue-700',
      light: 'bg-blue-50',
      text: 'text-blue-600',
      border: 'border-blue-200'
    },
    amber: {
      bg: 'bg-amber-600',
      hover: 'hover:bg-amber-700',
      light: 'bg-amber-50',
      text: 'text-amber-600',
      border: 'border-amber-200'
    }
  }

  const colors = colorClasses[config.color as keyof typeof colorClasses] || colorClasses.indigo

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <button
          onClick={() => navigate('/network')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-8"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Network
        </button>

        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          <div className={`${colors.bg} px-8 py-12 text-white`}>
            <div className="flex items-center gap-4 mb-4">
              <div className="w-16 h-16 bg-white/20 rounded-xl flex items-center justify-center">
                <Icon className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-3xl font-bold">Join as {config.title}</h1>
                <p className="text-white/80 mt-1">{config.description}</p>
              </div>
            </div>
          </div>

          <div className="p-8">
            {successMessage && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                <p className="text-green-800">{successMessage}</p>
              </div>
            )}

            {errorMessage && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800">{errorMessage}</p>
              </div>
            )}

            <div className="mb-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">What you'll get:</h2>
              <ul className="space-y-3">
                {config.benefits.map((benefit, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <CheckCircle className={`w-5 h-5 ${colors.text} flex-shrink-0 mt-0.5`} />
                    <span className="text-gray-700">{benefit}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="border-t border-gray-200 pt-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 text-center">
                Continue with your professional profile
              </h2>

              <button
                onClick={handleLinkedInLogin}
                disabled={isLoading}
                className="w-full flex items-center justify-center gap-3 bg-[#0A66C2] text-white py-4 px-6 rounded-xl font-semibold hover:bg-[#004182] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    <Linkedin className="w-6 h-6" />
                    Sign in with LinkedIn
                  </>
                )}
              </button>

              <p className="text-center text-sm text-gray-500 mt-4">
                By signing in, you agree to our Terms of Service and Privacy Policy.
                Your LinkedIn profile will be used to create your {config.title.toLowerCase()} profile.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-8 text-center">
          <p className="text-gray-600">
            Want to join as a different role?{' '}
            <button
              onClick={() => navigate('/network')}
              className={`${colors.text} font-medium hover:underline`}
            >
              View all options
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}
