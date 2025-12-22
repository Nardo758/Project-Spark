import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { 
  Search, 
  Users, 
  TrendingUp, 
  Briefcase, 
  Building2, 
  Star, 
  MapPin, 
  MessageSquare,
  CheckCircle,
  ArrowRight,
  Loader2
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

interface Expert {
  id: number
  name: string
  headline: string | null
  bio: string | null
  skills: string[]
  specialization: string[]
  pricing_model: string
  hourly_rate_cents: number | null
  is_active: boolean
}

const tabs = [
  { id: 'experts', label: 'Experts', icon: Users, count: 234 },
  { id: 'investors', label: 'Investors', icon: TrendingUp, count: 89 },
  { id: 'partners', label: 'Partners', icon: Briefcase, count: 156 },
  { id: 'lenders', label: 'Lenders', icon: Building2, count: 42 },
]

const sampleInvestors = [
  {
    id: 1,
    name: 'Venture Growth Partners',
    type: 'Private Equity',
    location: 'Boston, MA',
    focus: ['SaaS', 'Healthcare Tech', 'FinTech'],
    checkSize: '$5M - $50M',
    portfolio: 23,
    verified: true,
  },
  {
    id: 2,
    name: 'Horizon Capital',
    type: 'Growth Equity',
    location: 'Chicago, IL',
    focus: ['E-commerce', 'Consumer', 'D2C Brands'],
    checkSize: '$10M - $100M',
    portfolio: 18,
    verified: true,
  },
]

const samplePartners = [
  {
    id: 1,
    name: 'Startup Legal LLP',
    type: 'Legal Services',
    location: 'San Francisco, CA',
    services: ['M&A Documentation', 'Due Diligence', 'Contract Review'],
    clients: 340,
    verified: true,
  },
  {
    id: 2,
    name: 'GrowthMetrics Analytics',
    type: 'Business Intelligence',
    location: 'Austin, TX',
    services: ['Market Analysis', 'Competitor Research', 'Valuation'],
    clients: 156,
    verified: true,
  },
  {
    id: 3,
    name: 'TechBridge Consulting',
    type: 'Technical Due Diligence',
    location: 'Seattle, WA',
    services: ['Code Audits', 'Architecture Review', 'Security Assessment'],
    clients: 89,
    verified: true,
  },
]

const sampleLenders = [
  {
    id: 1,
    name: 'Acquisition Finance Corp',
    type: 'SBA Lender',
    location: 'Dallas, TX',
    loanTypes: ['SBA 7(a)', 'Acquisition Loans', 'Working Capital'],
    loanRange: '$500K - $5M',
    approvalRate: '78%',
    verified: true,
  },
  {
    id: 2,
    name: 'Bridge Capital Partners',
    type: 'Alternative Lender',
    location: 'Miami, FL',
    loanTypes: ['Bridge Loans', 'Mezzanine', 'Asset-Based'],
    loanRange: '$1M - $25M',
    approvalRate: '65%',
    verified: true,
  },
]

export default function Network() {
  const { isAuthenticated } = useAuthStore()
  const [activeTab, setActiveTab] = useState('experts')
  const [searchQuery, setSearchQuery] = useState('')
  const [experts, setExperts] = useState<Expert[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (activeTab === 'experts') {
      fetchExperts()
    }
  }, [activeTab])

  const fetchExperts = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/v1/experts/')
      if (response.ok) {
        const data = await response.json()
        setExperts(data)
      }
    } catch (error) {
      console.error('Failed to fetch experts:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatPrice = (cents: number | null) => {
    if (!cents) return 'Contact for pricing'
    return `$${(cents / 100).toFixed(0)}/hr`
  }

  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }

  const filteredExperts = experts.filter(expert => 
    !searchQuery || 
    expert.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    expert.headline?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    expert.specialization.some(s => s.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-gradient-to-br from-indigo-900 via-purple-900 to-black text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-4">Network Hub</h1>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Connect with verified experts, investors, and partners. Build relationships that accelerate your business.
            </p>
          </div>

          <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`p-4 rounded-xl text-center transition-all ${
                  activeTab === tab.id
                    ? 'bg-white text-gray-900'
                    : 'bg-white/10 backdrop-blur hover:bg-white/20'
                }`}
              >
                <tab.icon className={`w-6 h-6 mx-auto mb-2 ${activeTab === tab.id ? 'text-indigo-600' : ''}`} />
                <div className="font-semibold">{tab.label}</div>
                <div className={`text-sm ${activeTab === tab.id ? 'text-gray-500' : 'text-gray-400'}`}>
                  {tab.id === 'experts' ? experts.length || tab.count : tab.count} available
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder={`Search ${activeTab}...`}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {activeTab === 'experts' && (
          loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
            </div>
          ) : filteredExperts.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
              <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No experts found</h3>
              <p className="text-gray-600">
                {searchQuery ? 'Try adjusting your search query' : 'Experts will appear here as they join the platform'}
              </p>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredExperts.map((expert) => (
                <div key={expert.id} className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-700 font-semibold">
                      {getInitials(expert.name)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-gray-900">{expert.name}</h3>
                        {expert.is_active && (
                          <CheckCircle className="w-4 h-4 text-blue-500 fill-blue-500" />
                        )}
                      </div>
                      <p className="text-sm text-gray-600">{expert.headline || 'Expert Consultant'}</p>
                    </div>
                  </div>

                  <div className="mt-4 flex items-center gap-4 text-sm text-gray-600">
                    <span className="flex items-center gap-1">
                      <Star className="w-4 h-4 text-amber-500 fill-amber-500" />
                      4.8
                    </span>
                    <span className="font-medium text-indigo-600">
                      {formatPrice(expert.hourly_rate_cents)}
                    </span>
                  </div>

                  <div className="mt-4 flex flex-wrap gap-2">
                    {expert.specialization.slice(0, 3).map((spec) => (
                      <span key={spec} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                        {spec}
                      </span>
                    ))}
                  </div>

                  <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
                    <span className="text-sm text-gray-500">{expert.pricing_model}</span>
                    {isAuthenticated ? (
                      <button className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2">
                        <MessageSquare className="w-4 h-4" />
                        Connect
                      </button>
                    ) : (
                      <Link
                        to="/signup"
                        className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 transition-colors"
                      >
                        Sign Up to Connect
                      </Link>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )
        )}

        {activeTab === 'investors' && (
          <div className="grid md:grid-cols-2 gap-6">
            {sampleInvestors.map((investor) => (
              <div key={investor.id} className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-gray-900 text-lg">{investor.name}</h3>
                      {investor.verified && (
                        <CheckCircle className="w-4 h-4 text-blue-500 fill-blue-500" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600">{investor.type}</p>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900">{investor.checkSize}</div>
                    <div className="text-sm text-gray-500">check size</div>
                  </div>
                </div>

                <div className="mt-4 flex items-center gap-4 text-sm text-gray-600">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    {investor.location}
                  </span>
                  <span className="flex items-center gap-1">
                    <Briefcase className="w-4 h-4" />
                    {investor.portfolio} portfolio companies
                  </span>
                </div>

                <div className="mt-4">
                  <p className="text-sm text-gray-500 mb-2">Investment Focus:</p>
                  <div className="flex flex-wrap gap-2">
                    {investor.focus.map((f) => (
                      <span key={f} className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded-full">
                        {f}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-100">
                  {isAuthenticated ? (
                    <button className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2">
                      Request Introduction
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  ) : (
                    <Link
                      to="/signup"
                      className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
                    >
                      Sign Up to Connect
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'partners' && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {samplePartners.map((partner) => (
              <div key={partner.id} className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="font-semibold text-gray-900">{partner.name}</h3>
                  {partner.verified && (
                    <CheckCircle className="w-4 h-4 text-blue-500 fill-blue-500" />
                  )}
                </div>
                <p className="text-sm text-gray-600 mb-4">{partner.type}</p>
                
                <div className="flex items-center gap-1 text-sm text-gray-600 mb-4">
                  <MapPin className="w-4 h-4" />
                  {partner.location}
                </div>

                <div className="mb-4">
                  <p className="text-sm text-gray-500 mb-2">Services:</p>
                  <div className="flex flex-wrap gap-2">
                    {partner.services.map((s) => (
                      <span key={s} className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-full">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-100 flex items-center justify-between">
                  <span className="text-sm text-gray-500">{partner.clients} clients served</span>
                  {isAuthenticated ? (
                    <button className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 transition-colors">
                      Contact
                    </button>
                  ) : (
                    <Link to="/signup" className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 transition-colors">
                      Sign Up
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'lenders' && (
          <div className="grid md:grid-cols-2 gap-6">
            {sampleLenders.map((lender) => (
              <div key={lender.id} className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-gray-900 text-lg">{lender.name}</h3>
                      {lender.verified && (
                        <CheckCircle className="w-4 h-4 text-blue-500 fill-blue-500" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600">{lender.type}</p>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900">{lender.loanRange}</div>
                    <div className="text-sm text-gray-500">loan range</div>
                  </div>
                </div>

                <div className="mt-4 flex items-center gap-4 text-sm text-gray-600">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    {lender.location}
                  </span>
                  <span className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded-full">
                    {lender.approvalRate} approval rate
                  </span>
                </div>

                <div className="mt-4">
                  <p className="text-sm text-gray-500 mb-2">Loan Types:</p>
                  <div className="flex flex-wrap gap-2">
                    {lender.loanTypes.map((t) => (
                      <span key={t} className="px-2 py-1 bg-amber-50 text-amber-700 text-xs rounded-full">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-100">
                  {isAuthenticated ? (
                    <button className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2">
                      Apply for Financing
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  ) : (
                    <Link
                      to="/signup"
                      className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
                    >
                      Sign Up to Apply
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-12 bg-gradient-to-br from-indigo-900 to-purple-900 rounded-2xl p-8 text-white">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-2xl font-bold mb-4">Become a Verified Expert</h2>
            <p className="text-indigo-200 mb-6">
              Join our network of trusted advisors, brokers, and consultants. Get matched with qualified opportunities and grow your practice.
            </p>
            <Link
              to="/signup?type=expert"
              className="inline-flex items-center gap-2 px-6 py-3 bg-white text-indigo-900 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
            >
              Apply as Expert
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
