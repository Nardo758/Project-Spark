import { useState } from 'react'
import { Link } from 'react-router-dom'
import { 
  Search, 
  Filter, 
  MapPin, 
  DollarSign, 
  Building2, 
  TrendingUp,
  Star,
  Lock,
  Eye,
  ShoppingCart,
  Bell,
  ChevronRight
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

const sampleLeads = [
  {
    id: 'LD-78421',
    title: 'Profitable SaaS Business in Healthcare',
    industry: 'Healthcare Tech',
    dealSize: '$1M - $5M',
    location: 'Texas, USA',
    revenueRange: '$500K - $1M ARR',
    qualityScore: 8.5,
    price: 299,
    views: 142,
    status: 'active',
    daysListed: 3,
  },
  {
    id: 'LD-78422',
    title: 'E-commerce Brand with Strong D2C Presence',
    industry: 'E-commerce',
    dealSize: '$2M - $10M',
    location: 'California, USA',
    revenueRange: '$2M - $5M',
    qualityScore: 9.2,
    price: 499,
    views: 89,
    status: 'active',
    daysListed: 7,
  },
  {
    id: 'LD-78423',
    title: 'Manufacturing Business Seeking Strategic Buyer',
    industry: 'Manufacturing',
    dealSize: '$5M - $20M',
    location: 'Ohio, USA',
    revenueRange: '$3M - $8M',
    qualityScore: 7.8,
    price: 399,
    views: 56,
    status: 'active',
    daysListed: 14,
  },
  {
    id: 'LD-78424',
    title: 'FinTech Startup with Patented Technology',
    industry: 'FinTech',
    dealSize: '$10M - $50M',
    location: 'New York, USA',
    revenueRange: '$1M - $3M ARR',
    qualityScore: 9.5,
    price: 799,
    views: 203,
    status: 'premium',
    daysListed: 1,
  },
]

const industries = ['All Industries', 'Healthcare Tech', 'E-commerce', 'FinTech', 'SaaS', 'Manufacturing', 'Real Estate']
const dealSizes = ['Any Size', '$100K - $500K', '$500K - $1M', '$1M - $5M', '$5M - $20M', '$20M+']
const locations = ['All Locations', 'United States', 'California', 'Texas', 'New York', 'Florida', 'International']

export default function Leads() {
  const { isAuthenticated } = useAuthStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedIndustry, setSelectedIndustry] = useState('All Industries')
  const [selectedDealSize, setSelectedDealSize] = useState('Any Size')
  const [selectedLocation, setSelectedLocation] = useState('All Locations')

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-4">Leads Marketplace</h1>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Access vetted, high-intent business opportunities. Purchase leads with full contact details and financials.
            </p>
          </div>

          <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto">
            <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-center">
              <div className="text-2xl font-bold">847</div>
              <div className="text-sm text-gray-400">Active Leads</div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-center">
              <div className="text-2xl font-bold">$2.4B</div>
              <div className="text-sm text-gray-400">Total Deal Value</div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-center">
              <div className="text-2xl font-bold">92%</div>
              <div className="text-sm text-gray-400">Response Rate</div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-center">
              <div className="text-2xl font-bold">156</div>
              <div className="text-sm text-gray-400">Closed This Month</div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search leads by keyword, industry, or location..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent"
              />
            </div>
            <div className="flex gap-2 flex-wrap">
              <select
                value={selectedIndustry}
                onChange={(e) => setSelectedIndustry(e.target.value)}
                className="px-4 py-3 border border-gray-200 rounded-lg bg-white focus:ring-2 focus:ring-black"
              >
                {industries.map(ind => <option key={ind} value={ind}>{ind}</option>)}
              </select>
              <select
                value={selectedDealSize}
                onChange={(e) => setSelectedDealSize(e.target.value)}
                className="px-4 py-3 border border-gray-200 rounded-lg bg-white focus:ring-2 focus:ring-black"
              >
                {dealSizes.map(size => <option key={size} value={size}>{size}</option>)}
              </select>
              <select
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
                className="px-4 py-3 border border-gray-200 rounded-lg bg-white focus:ring-2 focus:ring-black"
              >
                {locations.map(loc => <option key={loc} value={loc}>{loc}</option>)}
              </select>
              <button className="px-4 py-3 bg-gray-100 hover:bg-gray-200 rounded-lg flex items-center gap-2 transition-colors">
                <Filter className="w-4 h-4" />
                More Filters
              </button>
            </div>
          </div>
        </div>

        <div className="flex gap-6">
          <div className="flex-1">
            <div className="flex items-center justify-between mb-4">
              <p className="text-gray-600">Showing {sampleLeads.length} leads</p>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">Sort by:</span>
                <select className="text-sm border border-gray-200 rounded-lg px-3 py-2">
                  <option>Newest First</option>
                  <option>Quality Score</option>
                  <option>Price: Low to High</option>
                  <option>Price: High to Low</option>
                </select>
              </div>
            </div>

            <div className="space-y-4">
              {sampleLeads.map((lead) => (
                <div 
                  key={lead.id} 
                  className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-mono text-gray-400">{lead.id}</span>
                        {lead.status === 'premium' && (
                          <span className="px-2 py-0.5 bg-amber-100 text-amber-700 text-xs font-medium rounded-full">
                            Premium
                          </span>
                        )}
                        {lead.daysListed <= 3 && (
                          <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                            New
                          </span>
                        )}
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">{lead.title}</h3>
                      
                      <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-4">
                        <span className="flex items-center gap-1">
                          <Building2 className="w-4 h-4" />
                          {lead.industry}
                        </span>
                        <span className="flex items-center gap-1">
                          <DollarSign className="w-4 h-4" />
                          {lead.dealSize}
                        </span>
                        <span className="flex items-center gap-1">
                          <MapPin className="w-4 h-4" />
                          {lead.location}
                        </span>
                        <span className="flex items-center gap-1">
                          <TrendingUp className="w-4 h-4" />
                          {lead.revenueRange}
                        </span>
                      </div>

                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1">
                          <Star className="w-4 h-4 text-amber-500 fill-amber-500" />
                          <span className="font-medium">{lead.qualityScore}</span>
                          <span className="text-gray-400 text-sm">quality</span>
                        </div>
                        <div className="flex items-center gap-1 text-gray-500 text-sm">
                          <Eye className="w-4 h-4" />
                          {lead.views} views
                        </div>
                        <div className="text-gray-400 text-sm">
                          Listed {lead.daysListed} days ago
                        </div>
                      </div>
                    </div>

                    <div className="text-right ml-6">
                      <div className="text-2xl font-bold text-gray-900">${lead.price}</div>
                      <div className="text-sm text-gray-500 mb-3">one-time</div>
                      
                      {isAuthenticated ? (
                        <button className="w-full px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors flex items-center justify-center gap-2">
                          <ShoppingCart className="w-4 h-4" />
                          Purchase Lead
                        </button>
                      ) : (
                        <Link
                          to="/signup"
                          className="w-full px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors flex items-center justify-center gap-2"
                        >
                          <Lock className="w-4 h-4" />
                          Sign Up to Buy
                        </Link>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="hidden lg:block w-80">
            <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6 sticky top-24">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Bell className="w-5 h-5" />
                Save This Search
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Get notified when new leads match your criteria.
              </p>
              {isAuthenticated ? (
                <button className="w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors font-medium">
                  Create Alert
                </button>
              ) : (
                <Link
                  to="/signup"
                  className="block w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors font-medium text-center"
                >
                  Sign Up for Alerts
                </Link>
              )}
            </div>

            <div className="bg-gradient-to-br from-gray-900 to-black rounded-xl p-6 text-white">
              <h3 className="font-semibold mb-2">How It Works</h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center text-xs font-bold">1</div>
                  <p className="text-gray-300">Browse anonymized leads with key metrics</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center text-xs font-bold">2</div>
                  <p className="text-gray-300">Purchase to unlock full contact & financials</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center text-xs font-bold">3</div>
                  <p className="text-gray-300">Connect directly with the opportunity</p>
                </div>
              </div>
              <Link 
                to="/leads/how-it-works"
                className="mt-4 inline-flex items-center gap-1 text-sm text-white/80 hover:text-white"
              >
                Learn more <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
