import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { 
  Code, 
  Key, 
  Book, 
  Zap,
  Shield,
  Globe,
  Copy,
  Check,
  ChevronRight,
  Terminal,
  ExternalLink,
  X,
  Loader2
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import EnterpriseContactModal from '../components/EnterpriseContactModal'

const endpoints = [
  {
    method: 'GET',
    path: '/api/v1/opportunities',
    description: 'List all opportunities with filters',
    auth: true,
  },
  {
    method: 'GET',
    path: '/api/v1/opportunities/{id}',
    description: 'Get opportunity details',
    auth: true,
  },
  {
    method: 'POST',
    path: '/api/v1/leads/purchase',
    description: 'Purchase a lead',
    auth: true,
  },
  {
    method: 'GET',
    path: '/api/v1/search',
    description: 'Search opportunities and leads',
    auth: true,
  },
  {
    method: 'POST',
    path: '/api/v1/validate',
    description: 'Validate a business idea with AI',
    auth: true,
  },
]

const pricingTiers = [
  {
    id: 'starter',
    name: 'Starter',
    price: '$20',
    priceLabel: '/mo',
    requests: '1 opportunity slot/month',
    features: [
      'Full API access',
      'All endpoints included',
      'Standard rate limits',
      'Community support',
    ],
    popular: false,
    gradient: 'from-gray-500 to-gray-600',
  },
  {
    id: 'growth',
    name: 'Growth',
    price: '$50',
    priceLabel: '/mo',
    requests: '3 opportunity slots/month',
    features: [
      'Full API access',
      'All endpoints included',
      'Higher rate limits',
      'Priority support',
      '10% off reports',
    ],
    popular: true,
    gradient: 'from-purple-500 to-indigo-600',
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '$99',
    priceLabel: '/mo',
    requests: '5 opportunity slots/month',
    features: [
      'Full API access',
      'All endpoints included',
      'Maximum rate limits',
      'Priority support',
      '15% off reports',
      'Webhooks',
    ],
    popular: false,
    gradient: 'from-emerald-500 to-teal-600',
  },
]

const businessTiers = [
  {
    id: 'team',
    name: 'Team',
    price: '$250',
    priceLabel: '/mo',
    requests: '5 slots + 3 team seats',
    features: [
      'Full API access',
      'White-label reports',
      'Full commercial use',
      'Team API keys',
      'Dedicated support',
    ],
    popular: false,
    gradient: 'from-blue-500 to-cyan-600',
  },
  {
    id: 'business',
    name: 'Business',
    price: '$750',
    priceLabel: '/mo',
    requests: '15 slots + 10 team seats',
    features: [
      'Full API access',
      'White-label reports',
      'Full commercial use',
      'Custom integrations',
      'SLA guarantee',
    ],
    popular: true,
    gradient: 'from-orange-500 to-red-600',
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 'Custom',
    priceLabel: '',
    requests: 'Unlimited slots + seats',
    features: [
      'Full API access',
      'On-premise option',
      'Dedicated infrastructure',
      'Custom SLA',
      '24/7 support',
    ],
    popular: false,
    gradient: 'from-slate-600 to-slate-800',
  },
]

interface PaymentModalProps {
  isOpen: boolean
  onClose: () => void
  tier: typeof pricingTiers[0] | typeof businessTiers[0]
}

function PaymentModal({ isOpen, onClose, tier }: PaymentModalProps) {
  const navigate = useNavigate()
  const { isAuthenticated, token } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!isOpen) return null

  async function handleCheckout() {
    if (!isAuthenticated) {
      onClose()
      navigate(`/signup?plan=${tier.id}`)
      return
    }

    if (tier.id === 'enterprise') {
      onClose()
      return
    }

    if (!token) {
      setError('Please log in again to continue')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const baseUrl = window.location.origin
      const res = await fetch('/api/v1/subscriptions/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          tier: tier.id,
          success_url: `${baseUrl}/developer?success=true`,
          cancel_url: `${baseUrl}/developer?canceled=true`,
        }),
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'Failed to start checkout')
      }

      if (data.url) {
        window.location.href = data.url
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-gray-900">Subscribe to {tier.name}</h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <div className={`bg-gradient-to-r ${tier.gradient} rounded-xl p-6 text-white mb-6`}>
          <div className="text-3xl font-bold mb-1">
            {tier.price}
            <span className="text-lg font-normal opacity-80">{tier.priceLabel}</span>
          </div>
          <p className="text-white/80">{tier.requests}</p>
        </div>

        <div className="mb-6">
          <h4 className="font-semibold text-gray-900 mb-3">What's included:</h4>
          <ul className="space-y-2">
            {tier.features.map((feature) => (
              <li key={feature} className="flex items-center gap-2 text-sm text-gray-600">
                <Check className="w-4 h-4 text-green-500 flex-shrink-0" />
                {feature}
              </li>
            ))}
          </ul>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        <button
          onClick={handleCheckout}
          disabled={isLoading}
          className="w-full py-3 bg-gray-900 text-white rounded-lg font-semibold hover:bg-gray-800 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              Continue to Checkout
              <ChevronRight className="w-5 h-5" />
            </>
          )}
        </button>

        <p className="text-xs text-gray-500 text-center mt-4">
          Secure payment powered by Stripe. Cancel anytime.
        </p>
      </div>
    </div>
  )
}

export default function ApiPortal() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()
  const [copied, setCopied] = useState(false)
  const [selectedTier, setSelectedTier] = useState<typeof pricingTiers[0] | typeof businessTiers[0] | null>(null)
  const [showEnterpriseModal, setShowEnterpriseModal] = useState(false)
  const [activeTab, setActiveTab] = useState<'individual' | 'business'>('individual')

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleTierClick = (tier: typeof pricingTiers[0] | typeof businessTiers[0]) => {
    if (tier.id === 'enterprise') {
      setShowEnterpriseModal(true)
    } else {
      setSelectedTier(tier)
    }
  }

  const exampleCode = `curl -X GET "https://api.oppgrid.com/v1/opportunities" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json"`

  const displayTiers = activeTab === 'individual' ? pricingTiers : businessTiers

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-black text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/10 rounded-full text-sm mb-6">
              <Code className="w-4 h-4" />
              Developer Platform
            </div>
            <h1 className="text-4xl font-bold mb-4">OppGrid API</h1>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Build powerful integrations with our RESTful API. Access opportunities, leads, and AI-powered insights programmatically.
            </p>
          </div>

          <div className="mt-8 flex justify-center gap-4">
            {isAuthenticated ? (
              <>
                <button 
                  onClick={() => navigate('/settings/api')}
                  className="px-6 py-3 bg-white text-gray-900 rounded-lg font-semibold hover:bg-gray-100 transition-colors flex items-center gap-2"
                >
                  <Key className="w-5 h-5" />
                  Get API Key
                </button>
                <a
                  href="/docs/api"
                  className="px-6 py-3 border border-white/30 rounded-lg font-semibold hover:bg-white/10 transition-colors flex items-center gap-2"
                >
                  <Book className="w-5 h-5" />
                  View Docs
                </a>
              </>
            ) : (
              <>
                <Link
                  to="/signup"
                  className="px-6 py-3 bg-white text-gray-900 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                >
                  Get Started Free
                </Link>
                <a
                  href="#pricing"
                  className="px-6 py-3 border border-white/30 rounded-lg font-semibold hover:bg-white/10 transition-colors"
                >
                  View Pricing
                </a>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
              <Zap className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Fast & Reliable</h3>
            <p className="text-gray-600">
              Sub-100ms response times with 99.9% uptime SLA. Built for production workloads.
            </p>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-4">
              <Shield className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Secure by Default</h3>
            <p className="text-gray-600">
              OAuth 2.0 authentication, encrypted data transfer, and SOC 2 compliant infrastructure.
            </p>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
              <Globe className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Global Coverage</h3>
            <p className="text-gray-600">
              Edge servers worldwide for low-latency access from any location.
            </p>
          </div>
        </div>

        <div className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Start</h2>
          <div className="bg-slate-900 rounded-xl overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 bg-slate-800">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-400">bash</span>
              </div>
              <button
                onClick={() => handleCopy(exampleCode)}
                className="flex items-center gap-1 text-sm text-gray-400 hover:text-white transition-colors"
              >
                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
            <pre className="p-4 text-sm text-gray-300 overflow-x-auto">
              <code>{exampleCode}</code>
            </pre>
          </div>
        </div>

        <div className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Available Endpoints</h2>
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left px-6 py-3 text-sm font-semibold text-gray-900">Method</th>
                  <th className="text-left px-6 py-3 text-sm font-semibold text-gray-900">Endpoint</th>
                  <th className="text-left px-6 py-3 text-sm font-semibold text-gray-900">Description</th>
                  <th className="text-left px-6 py-3 text-sm font-semibold text-gray-900">Auth</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {endpoints.map((endpoint, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs font-mono font-bold rounded ${
                        endpoint.method === 'GET' ? 'bg-blue-100 text-blue-700' :
                        endpoint.method === 'POST' ? 'bg-green-100 text-green-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {endpoint.method}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono text-sm text-gray-900">{endpoint.path}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{endpoint.description}</td>
                    <td className="px-6 py-4">
                      {endpoint.auth && (
                        <span className="flex items-center gap-1 text-sm text-gray-500">
                          <Key className="w-3 h-3" />
                          Required
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
              <a 
                href="/docs/api" 
                className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
              >
                View full API documentation
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>

        <div id="pricing" className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-2 text-center">API Pricing</h2>
          <p className="text-gray-600 text-center mb-8">
            API access is included with all paid plans. Choose the plan that fits your needs.
          </p>

          <div className="flex justify-center mb-8">
            <div className="inline-flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setActiveTab('individual')}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'individual'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Individual
              </button>
              <button
                onClick={() => setActiveTab('business')}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'business'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Business
              </button>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {displayTiers.map((tier) => (
              <div 
                key={tier.id}
                className={`bg-white rounded-xl border-2 p-6 transition-all ${
                  tier.popular ? 'border-purple-500 ring-2 ring-purple-500/20' : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                {tier.popular && (
                  <span className="inline-block px-3 py-1 bg-purple-100 text-purple-700 text-xs font-semibold rounded-full mb-4">
                    Most Popular
                  </span>
                )}
                <h3 className="text-xl font-bold text-gray-900">{tier.name}</h3>
                <div className="mt-2 mb-4">
                  <span className="text-3xl font-bold text-gray-900">{tier.price}</span>
                  <span className="text-gray-500">{tier.priceLabel}</span>
                </div>
                <p className="text-sm text-gray-500 mb-6">{tier.requests}</p>
                <ul className="space-y-3 mb-6">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2 text-sm text-gray-600">
                      <Check className="w-4 h-4 text-green-500 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <button 
                  onClick={() => handleTierClick(tier)}
                  className={`w-full py-3 rounded-lg font-medium transition-colors ${
                    tier.popular
                      ? 'bg-purple-600 text-white hover:bg-purple-700'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  }`}
                >
                  {tier.price === 'Custom' ? 'Contact Sales' : 'Get Started'}
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gradient-to-br from-slate-900 to-black rounded-2xl p-8 text-white text-center">
          <h2 className="text-2xl font-bold mb-4">Ready to Build?</h2>
          <p className="text-gray-300 mb-6 max-w-xl mx-auto">
            Get your API key in seconds and start integrating OppGrid data into your applications.
          </p>
          {isAuthenticated ? (
            <button
              onClick={() => navigate('/settings/api')}
              className="inline-flex items-center gap-2 px-6 py-3 bg-white text-gray-900 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
            >
              Get Your API Key
              <ChevronRight className="w-5 h-5" />
            </button>
          ) : (
            <Link
              to="/signup"
              className="inline-flex items-center gap-2 px-6 py-3 bg-white text-gray-900 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
            >
              Create Free Account
              <ChevronRight className="w-5 h-5" />
            </Link>
          )}
        </div>
      </div>

      {selectedTier && (
        <PaymentModal
          isOpen={!!selectedTier}
          onClose={() => setSelectedTier(null)}
          tier={selectedTier}
        />
      )}

      {showEnterpriseModal && (
        <EnterpriseContactModal
          onClose={() => setShowEnterpriseModal(false)}
          source="api"
        />
      )}
    </div>
  )
}
