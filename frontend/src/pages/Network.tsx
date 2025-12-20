import { useState } from 'react'
import { Link } from 'react-router-dom'
import { 
  Users, 
  Briefcase, 
  TrendingUp, 
  Building2,
  Star,
  MapPin,
  MessageSquare,
  CheckCircle,
  ArrowRight,
  Search,
  Filter
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

const tabs = [
  { id: 'experts', label: 'Experts', icon: Users, count: 234 },
  { id: 'investors', label: 'Investors', icon: TrendingUp, count: 89 },
  { id: 'partners', label: 'Partners', icon: Briefcase, count: 156 },
  { id: 'lenders', label: 'Lenders', icon: Building2, count: 42 },
]

const experts = [
  {
    id: 1,
    name: 'Michael Chen',
    title: 'M&A Advisor',
    company: 'Strategic Advisory Group',
    location: 'San Francisco, CA',
    expertise: ['SaaS', 'Technology', 'Healthcare'],
    rating: 4.9,
    deals: 47,
    verified: true,
    avatar: 'MC',
  },
  {
    id: 2,
    name: 'Sarah Williams',
    title: 'Investment Banker',
    company: 'Williams Capital',
    location: 'New York, NY',
    expertise: ['FinTech', 'E-commerce', 'Manufacturing'],
    rating: 4.8,
    deals: 62,
    verified: true,
    avatar: 'SW',
  },
  {
    id: 3,
    name: 'David Park',
    title: 'Business Broker',
    company: 'Park & Associates',
    location: 'Los Angeles, CA',
    expertise: ['Retail', 'Food & Beverage', 'Services'],
    rating: 4.7,
    deals: 38,
    verified: true,
    avatar: 'DP',
  },
]

const investors = [
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

const partners = [
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

const lenders = [
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
                  {tab.count} available
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
            <button className="px-4 py-3 bg-gray-100 hover:bg-gray-200 rounded-lg flex items-center gap-2 transition-colors">
              <Filter className="w-4 h-4" />
              Filters
            </button>
          </div>
        </div>

        {activeTab === 'experts' && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {experts.map((expert) => (
              <div key={expert.id} className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start gap-4">
                  <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                    {expert.avatar}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-gray-900">{expert.name}</h3>
                      {expert.verified && (
                        <CheckCircle className="w-4 h-4 text-blue-500 fill-blue-500" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600">{expert.title}</p>
                    <p className="text-sm text-gray-500">{expert.company}</p>
                  </div>
                </div>

                <div className="mt-4 flex items-center gap-4 text-sm text-gray-600">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    {expert.location}
                  </span>
                  <span className="flex items-center gap-1">
                    <Star className="w-4 h-4 text-amber-500 fill-amber-500" />
                    {expert.rating}
                  </span>
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  {expert.expertise.map((exp) => (
                    <span key={exp} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                      {exp}
                    </span>
                  ))}
                </div>

                <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
                  <span className="text-sm text-gray-500">{expert.deals} deals closed</span>
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
        )}

        {activeTab === 'investors' && (
          <div className="grid md:grid-cols-2 gap-6">
            {investors.map((investor) => (
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
            {partners.map((partner) => (
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
            {lenders.map((lender) => (
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
