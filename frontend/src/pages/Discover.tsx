import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Target, Clock, TrendingUp, Bookmark } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import SaveToWorkhubModal from '../components/SaveToWorkhubModal'

const mockOpportunities = [
  { id: 1, title: 'Healthcare SaaS Platform', match: 94, status: 'HOT', category: 'Healthcare', marketSize: '$15B', competition: 'Medium', timeToMarket: '6 months' },
  { id: 2, title: 'FinTech Payment Solution', match: 88, status: 'FRESH', category: 'FinTech', marketSize: '$8B', competition: 'High', timeToMarket: '4 months' },
  { id: 3, title: 'E-commerce Automation Tool', match: 76, status: 'VALIDATED', category: 'E-commerce', marketSize: '$5B', competition: 'Low', timeToMarket: '3 months' },
  { id: 4, title: 'EdTech Learning Platform', match: 72, status: 'FRESH', category: 'Education', marketSize: '$12B', competition: 'Medium', timeToMarket: '8 months' },
  { id: 5, title: 'PropTech Management System', match: 68, status: 'ARCHIVE', category: 'Real Estate', marketSize: '$3B', competition: 'Low', timeToMarket: '5 months' },
]

const categories = ['All', 'Healthcare', 'FinTech', 'E-commerce', 'Education', 'Real Estate', 'SaaS']
const statuses = ['All', 'HOT', 'FRESH', 'VALIDATED', 'ARCHIVE']

export default function Discover() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [selectedStatus, setSelectedStatus] = useState('All')
  const [saveModalOpen, setSaveModalOpen] = useState(false)
  const [selectedOpp, setSelectedOpp] = useState<{ id: number; title: string } | null>(null)
  const { isAuthenticated } = useAuthStore()
  const navigate = useNavigate()

  const filteredOpportunities = mockOpportunities.filter(opp => {
    const matchesSearch = opp.title.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'All' || opp.category === selectedCategory
    const matchesStatus = selectedStatus === 'All' || opp.status === selectedStatus
    return matchesSearch && matchesCategory && matchesStatus
  })

  const handleSaveClick = (opp: { id: number; title: string }) => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    setSelectedOpp(opp)
    setSaveModalOpen(true)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Discover Opportunities</h1>
        <p className="text-gray-600">AI-validated business opportunities matched to your skills and interests</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search opportunities..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div className="flex gap-3">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {statuses.map(status => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="grid gap-6">
        {filteredOpportunities.map((opp) => (
          <div key={opp.id} className="bg-white rounded-xl border border-gray-200 p-6 hover:border-gray-300 hover:shadow-md transition-all">
            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-3">
                  <span className={`px-2.5 py-1 text-xs font-semibold rounded ${
                    opp.status === 'HOT' ? 'bg-red-100 text-red-700' :
                    opp.status === 'FRESH' ? 'bg-blue-100 text-blue-700' :
                    opp.status === 'VALIDATED' ? 'bg-green-100 text-green-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {opp.status}
                  </span>
                  <span className="text-sm text-gray-500">{opp.category}</span>
                </div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">{opp.title}</h2>
                <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <TrendingUp className="w-4 h-4" />
                    Market: {opp.marketSize}
                  </div>
                  <div className="flex items-center gap-1">
                    <Target className="w-4 h-4" />
                    Competition: {opp.competition}
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    TTM: {opp.timeToMarket}
                  </div>
                </div>
              </div>
              <div className="flex flex-col items-end gap-3">
                <div className="flex items-center gap-2 px-4 py-2 bg-green-50 rounded-lg">
                  <Target className="w-5 h-5 text-green-600" />
                  <span className="text-lg font-bold text-green-700">{opp.match}% Match</span>
                </div>
                <div className="flex items-center gap-2">
                  <button 
                    onClick={() => handleSaveClick(opp)}
                    className="p-2 text-stone-400 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-colors"
                    title="Save to Workhub"
                  >
                    <Bookmark className="w-5 h-5" />
                  </button>
                  <button className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 font-medium">
                    View Details
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredOpportunities.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No opportunities found matching your criteria.</p>
        </div>
      )}

      {selectedOpp && (
        <SaveToWorkhubModal
          opportunityId={selectedOpp.id}
          opportunityTitle={selectedOpp.title}
          isOpen={saveModalOpen}
          onClose={() => setSaveModalOpen(false)}
        />
      )}
    </div>
  )
}
