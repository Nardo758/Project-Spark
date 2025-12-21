import { useState } from 'react'
import { Link } from 'react-router-dom'
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
  ExternalLink
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

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
    name: 'Starter',
    price: 'Free',
    requests: '100 requests/month',
    features: ['Basic endpoints', 'Community support', 'Rate limited'],
  },
  {
    name: 'Developer',
    price: '$49/mo',
    requests: '10,000 requests/month',
    features: ['All endpoints', 'Priority support', 'Webhooks', 'Higher limits'],
    popular: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    requests: 'Unlimited',
    features: ['Dedicated support', 'Custom integrations', 'SLA guarantee', 'On-premise option'],
  },
]

export default function ApiPortal() {
  const { isAuthenticated } = useAuthStore()
  const [copied, setCopied] = useState(false)

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const exampleCode = `curl -X GET "https://api.oppgrid.com/v1/opportunities" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json"`

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
                <button className="px-6 py-3 bg-white text-gray-900 rounded-lg font-semibold hover:bg-gray-100 transition-colors flex items-center gap-2">
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
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">API Pricing</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {pricingTiers.map((tier) => (
              <div 
                key={tier.name}
                className={`bg-white rounded-xl border p-6 ${
                  tier.popular ? 'border-blue-500 ring-2 ring-blue-500' : 'border-gray-200'
                }`}
              >
                {tier.popular && (
                  <span className="inline-block px-3 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded-full mb-4">
                    Most Popular
                  </span>
                )}
                <h3 className="text-xl font-bold text-gray-900">{tier.name}</h3>
                <div className="mt-2 mb-4">
                  <span className="text-3xl font-bold text-gray-900">{tier.price}</span>
                </div>
                <p className="text-sm text-gray-500 mb-6">{tier.requests}</p>
                <ul className="space-y-3 mb-6">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2 text-sm text-gray-600">
                      <Check className="w-4 h-4 text-green-500" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <button className={`w-full py-2 rounded-lg font-medium transition-colors ${
                  tier.popular
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                }`}>
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
          <Link
            to="/signup"
            className="inline-flex items-center gap-2 px-6 py-3 bg-white text-gray-900 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            Create Free Account
            <ChevronRight className="w-5 h-5" />
          </Link>
        </div>
      </div>
    </div>
  )
}
