import { useState } from 'react'
import { Link } from 'react-router-dom'
import { 
  DollarSign, Building2, Users, Landmark, Gift, FileText,
  ExternalLink, ChevronRight, Search, Filter, Sparkles
} from 'lucide-react'

const fundingSources = [
  {
    id: 1,
    name: 'SBA Microloans',
    type: 'Government',
    icon: Landmark,
    amount: 'Up to $50,000',
    description: 'Small Business Administration microloans for startups and small businesses.',
    requirements: ['Business plan', '2+ years credit history', 'Collateral preferred'],
    timeline: '2-4 weeks',
    link: 'https://www.sba.gov/funding-programs/loans/microloans'
  },
  {
    id: 2,
    name: 'Angel Investors',
    type: 'Equity',
    icon: Users,
    amount: '$25K - $500K',
    description: 'Connect with angel investors looking for early-stage opportunities.',
    requirements: ['Pitch deck', 'MVP or prototype', 'Market validation'],
    timeline: '1-3 months',
    link: '/network/investor'
  },
  {
    id: 3,
    name: 'SBIR/STTR Grants',
    type: 'Grant',
    icon: Gift,
    amount: 'Up to $1.5M',
    description: 'Federal research grants for technology and innovation startups.',
    requirements: ['US-based company', 'R&D focused', 'Technical proposal'],
    timeline: '3-6 months',
    link: 'https://www.sbir.gov/'
  },
  {
    id: 4,
    name: 'Revenue-Based Financing',
    type: 'Alternative',
    icon: DollarSign,
    amount: '$10K - $5M',
    description: 'Non-dilutive funding based on your monthly recurring revenue.',
    requirements: ['$10K+ MRR', '6+ months history', 'SaaS or subscription model'],
    timeline: '1-2 weeks',
    link: '#'
  },
  {
    id: 5,
    name: 'Bank Business Loans',
    type: 'Debt',
    icon: Building2,
    amount: '$5K - $500K',
    description: 'Traditional bank loans for established businesses with good credit.',
    requirements: ['2+ years in business', 'Good credit score', 'Financial statements'],
    timeline: '2-6 weeks',
    link: '#'
  },
  {
    id: 6,
    name: 'Crowdfunding',
    type: 'Alternative',
    icon: Users,
    amount: 'Varies',
    description: 'Raise funds from the public through platforms like Kickstarter or Wefunder.',
    requirements: ['Compelling story', 'Product/prototype', 'Marketing plan'],
    timeline: '30-60 days campaign',
    link: '#'
  }
]

const fundingTypes = ['All', 'Government', 'Grant', 'Equity', 'Debt', 'Alternative']

export default function Funding() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState('All')

  const filteredSources = fundingSources.filter(source => {
    const matchesSearch = !searchQuery || 
      source.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      source.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = selectedType === 'All' || source.type === selectedType
    return matchesSearch && matchesType
  })

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Find Money</h1>
        <p className="text-gray-600">Discover funding options matched to your business stage and needs.</p>
      </div>

      <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl p-6 mb-8 border border-green-200">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 bg-green-600 rounded-xl flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900 mb-1">AI Funding Advisor</h2>
            <p className="text-sm text-gray-600 mb-3">
              Get personalized funding recommendations based on your business profile, stage, and goals.
            </p>
            <Link 
              to="/brain" 
              className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 text-sm"
            >
              <Sparkles className="w-4 h-4" />
              Get AI Recommendations
            </Link>
          </div>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search funding sources..."
            className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-400" />
          <div className="flex gap-2 flex-wrap">
            {fundingTypes.map(type => (
              <button
                key={type}
                onClick={() => setSelectedType(type)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                  selectedType === type
                    ? 'bg-gray-900 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {filteredSources.map((source) => {
          const IconComponent = source.icon
          return (
            <div key={source.id} className="bg-white rounded-xl border border-gray-200 p-6 hover:border-gray-300 hover:shadow-md transition-all">
              <div className="flex items-start gap-4 mb-4">
                <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center">
                  <IconComponent className="w-6 h-6 text-gray-700" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-gray-900">{source.name}</h3>
                    <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">
                      {source.type}
                    </span>
                  </div>
                  <p className="text-lg font-bold text-green-600">{source.amount}</p>
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-4">{source.description}</p>

              <div className="mb-4">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Requirements</p>
                <ul className="space-y-1">
                  {source.requirements.map((req, i) => (
                    <li key={i} className="text-sm text-gray-600 flex items-center gap-2">
                      <ChevronRight className="w-3 h-3 text-gray-400" />
                      {req}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <span className="text-sm text-gray-500">Timeline: {source.timeline}</span>
                {source.link.startsWith('http') ? (
                  <a
                    href={source.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-sm font-medium text-green-600 hover:text-green-700"
                  >
                    Learn More
                    <ExternalLink className="w-4 h-4" />
                  </a>
                ) : (
                  <Link
                    to={source.link}
                    className="inline-flex items-center gap-1 text-sm font-medium text-green-600 hover:text-green-700"
                  >
                    Explore
                    <ChevronRight className="w-4 h-4" />
                  </Link>
                )}
              </div>
            </div>
          )
        })}
      </div>

      <div className="bg-white rounded-2xl border border-gray-200 p-8">
        <div className="flex items-start gap-4 mb-6">
          <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
            <FileText className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-1">Need Help with Your Application?</h2>
            <p className="text-gray-600">
              Our AI can help you prepare funding applications, pitch decks, and financial projections.
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-3">
          <Link
            to="/build/business-plan"
            className="px-4 py-2 bg-black text-white rounded-lg font-medium hover:bg-gray-800"
          >
            Generate Business Plan
          </Link>
          <Link
            to="/build/reports"
            className="px-4 py-2 border border-gray-200 rounded-lg font-medium hover:bg-gray-50"
          >
            Consultant Studio
          </Link>
          <Link
            to="/build/experts"
            className="px-4 py-2 border border-gray-200 rounded-lg font-medium hover:bg-gray-50"
          >
            Find a Funding Expert
          </Link>
        </div>
      </div>
    </div>
  )
}
