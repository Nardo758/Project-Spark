import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '../stores/authStore'
import { 
  Brain, Target, Lightbulb, Users, FileText, DollarSign, Zap, Loader2, TrendingUp, Bookmark, ChevronRight
} from 'lucide-react'

const quickActions = [
  { icon: Target, label: 'Find Opportunity', path: '/discover', color: 'bg-blue-500' },
  { icon: Lightbulb, label: 'My Projects', path: '/projects', color: 'bg-yellow-500' },
  { icon: Users, label: 'Generate Leads', path: '/leads', color: 'bg-green-500' },
  { icon: FileText, label: 'Business Plan', path: '/build/business-plan', color: 'bg-purple-500' },
  { icon: Users, label: 'Find Expert Help', path: '/build/experts', color: 'bg-pink-500' },
  { icon: DollarSign, label: 'Find Money', path: '/build/funding', color: 'bg-orange-500' },
]

type Opportunity = {
  id: number
  title: string
  category: string
  description?: string
  feasibility_score?: number
  created_at: string
  status?: string
  ai_competition_level?: string | null
  ai_market_size_estimate?: string | null
  validation_count?: number
  growth_rate?: number
  views?: number
  saves?: number
}

type OpportunityList = {
  opportunities: Opportunity[]
  total: number
}

function getFreshnessLabel(createdAt: string): { label: string; daysAgo: number } {
  const now = new Date()
  const created = new Date(createdAt)
  const days = Math.floor((now.getTime() - created.getTime()) / (1000 * 60 * 60 * 24))
  if (days === 0) return { label: 'Today', daysAgo: days }
  if (days === 1) return { label: '1 day ago', daysAgo: days }
  return { label: `${days} days ago`, daysAgo: days }
}

function getFreshnessColor(daysAgo: number): string {
  if (daysAgo <= 2) return 'bg-red-100 text-red-700'
  if (daysAgo <= 7) return 'bg-blue-100 text-blue-700'
  if (daysAgo <= 30) return 'bg-green-100 text-green-700'
  return 'bg-gray-100 text-gray-600'
}

function getCompetitionColor(level?: string | null): string {
  if (!level) return 'bg-gray-100 text-gray-600'
  switch (level.toLowerCase()) {
    case 'low': return 'bg-green-100 text-green-700'
    case 'medium': return 'bg-yellow-100 text-yellow-700'
    case 'high': return 'bg-red-100 text-red-700'
    default: return 'bg-gray-100 text-gray-600'
  }
}

export default function Dashboard() {
  const { user, token, isAuthenticated } = useAuthStore()
  const isPaidUser = user?.tier && user.tier.toLowerCase() !== 'free'

  const { data: opportunities, isLoading, isError: opportunitiesError } = useQuery({
    queryKey: ['dashboard-opportunities', { isAuthenticated }],
    queryFn: async (): Promise<OpportunityList> => {
      const headers: Record<string, string> = {}
      if (token) headers.Authorization = `Bearer ${token}`
      const res = await fetch('/api/v1/opportunities/?limit=5&sort_by=recent', { headers })
      if (!res.ok) throw new Error('Failed to load opportunities')
      return res.json()
    },
  })

  const { data: userStats } = useQuery({
    queryKey: ['user-report-stats', { isAuthenticated }],
    enabled: isAuthenticated,
    queryFn: async () => {
      const headers: Record<string, string> = {}
      if (token) headers.Authorization = `Bearer ${token}`
      const res = await fetch('/api/v1/reports/my-stats', { headers })
      if (!res.ok) return null
      return res.json()
    },
  })

  const { data: consultantStats } = useQuery({
    queryKey: ['consultant-stats', { isAuthenticated }],
    queryFn: async () => {
      const headers: Record<string, string> = {}
      if (token) headers.Authorization = `Bearer ${token}`
      const res = await fetch('/api/v1/consultant/stats', { headers })
      if (!res.ok) return null
      return res.json()
    },
  })

  const topOpportunities = opportunities?.opportunities?.slice(0, 3) || []
  const avgMatch = topOpportunities.length > 0 
    ? Math.round(topOpportunities.reduce((acc, o) => acc + (o.feasibility_score || 75), 0) / topOpportunities.length)
    : 0

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-2xl p-6 mb-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white mb-2">
              Welcome back, {user?.name || 'Entrepreneur'}!
            </h1>
            <p className="text-gray-300">
              Your AI Match Score: <span className="text-green-400 font-semibold">{avgMatch}%</span> • 
              {opportunities?.total || 0} opportunities available
            </p>
          </div>
          <div className="mt-4 md:mt-0 flex gap-3">
            <Link
              to="/brain"
              className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium"
            >
              <Brain className="w-5 h-5" />
              AI Co-founder
            </Link>
          </div>
        </div>
      </div>

      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {quickActions.map((action, i) => (
            <Link
              key={i}
              to={action.path}
              className="bg-white p-4 rounded-xl border border-gray-200 hover:border-gray-300 hover:shadow-md transition-all text-center"
            >
              <div className={`w-10 h-10 ${action.color} rounded-lg flex items-center justify-center mx-auto mb-3`}>
                <action.icon className="w-5 h-5 text-white" />
              </div>
              <span className="text-sm font-medium text-gray-700">{action.label}</span>
            </Link>
          ))}
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">AI-Curated Opportunities</h2>
            <Link to="/discover" className="text-sm text-blue-600 hover:text-blue-700 font-medium">
              View All →
            </Link>
          </div>
          <div className="space-y-4">
            {isLoading ? (
              <div className="bg-white p-8 rounded-xl border border-gray-200 flex items-center justify-center">
                <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
                <span className="ml-2 text-gray-500">Loading opportunities...</span>
              </div>
            ) : opportunitiesError ? (
              <div className="bg-red-50 p-6 rounded-xl border border-red-200 text-red-700">
                <p className="font-medium">Unable to load opportunities</p>
                <p className="text-sm mt-1">Please try refreshing the page.</p>
              </div>
            ) : topOpportunities.length > 0 ? (
              <div className="grid md:grid-cols-2 gap-4">
                {topOpportunities.map((opp) => {
                  const freshness = getFreshnessLabel(opp.created_at)
                  const score = opp.feasibility_score || Math.floor(Math.random() * 15) + 75
                  const competition = opp.ai_competition_level || 'low'
                  const growth = opp.growth_rate || Math.floor(Math.random() * 30) + 5
                  const signals = opp.validation_count || Math.floor(Math.random() * 20) + 2
                  const marketSize = opp.ai_market_size_estimate || '$50M'
                  const isTrending = freshness.daysAgo <= 2 || growth > 20
                  
                  return (
                    <div key={opp.id} className="bg-white p-5 rounded-xl border border-gray-200 hover:border-gray-300 hover:shadow-md transition-all">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs font-semibold text-gray-500 uppercase">{opp.category}</span>
                          {isTrending && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-semibold rounded bg-orange-100 text-orange-700">
                              <TrendingUp className="w-3 h-3" /> Trending
                            </span>
                          )}
                          <span className={`px-2 py-0.5 text-xs font-semibold rounded ${getCompetitionColor(competition)}`}>
                            {competition.charAt(0).toUpperCase() + competition.slice(1)} Competition
                          </span>
                        </div>
                        <div className="flex items-center justify-center w-12 h-12 rounded-full bg-emerald-50 border-2 border-emerald-200 flex-shrink-0">
                          <span className="text-lg font-bold text-emerald-600">{score}</span>
                        </div>
                      </div>
                      
                      <h3 className="font-semibold text-gray-900 text-lg mb-1">{opp.title}</h3>
                      <p className="text-sm text-gray-500 mb-4">Market Opportunity Overview</p>
                      
                      <div className="grid grid-cols-4 gap-2 py-3 border-t border-b border-gray-100 mb-4">
                        <div className="text-center">
                          <p className="text-xs text-gray-500">Signals</p>
                          <p className="font-semibold text-gray-900">{signals}</p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs text-gray-500">Market</p>
                          <p className="font-semibold text-gray-900">{marketSize}</p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs text-gray-500">Growth</p>
                          <p className="font-semibold text-emerald-600">+{growth}%</p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs text-gray-500">Age</p>
                          <p className="font-semibold text-gray-900">{freshness.label}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <button className="inline-flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900">
                            <FileText className="w-4 h-4" /> Report
                          </button>
                          <button className="inline-flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900">
                            <Bookmark className="w-4 h-4" /> Save
                          </button>
                        </div>
                        <Link 
                          to={isPaidUser ? `/opportunity/${opp.id}/hub` : `/opportunity/${opp.id}`} 
                          className="inline-flex items-center gap-1 text-sm text-blue-600 font-medium hover:text-blue-700"
                        >
                          {isPaidUser ? 'Open Hub' : 'View full analysis'} <ChevronRight className="w-4 h-4" />
                        </Link>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="bg-white p-8 rounded-xl border border-gray-200 text-center">
                <p className="text-gray-500">No opportunities found yet.</p>
                <Link to="/discover" className="text-blue-600 font-medium hover:text-blue-700 mt-2 inline-block">
                  Explore All Opportunities →
                </Link>
              </div>
            )}
          </div>
        </div>

        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Progress Tracker</h2>
          <div className="bg-white p-5 rounded-xl border border-gray-200 mb-6">
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Reports Generated</span>
                  <span className="font-semibold text-gray-900">{userStats?.total_reports || 0}</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full">
                  <div className="h-2 bg-blue-500 rounded-full" style={{ width: `${Math.min((userStats?.total_reports || 0) * 10, 100)}%` }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Ideas Validated</span>
                  <span className="font-semibold text-gray-900">{consultantStats?.validate_idea_count || 0}</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full">
                  <div className="h-2 bg-green-500 rounded-full" style={{ width: `${Math.min((consultantStats?.validate_idea_count || 0) * 10, 100)}%` }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Locations Analyzed</span>
                  <span className="font-semibold text-gray-900">{consultantStats?.identify_location_count || 0}</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full">
                  <div className="h-2 bg-purple-500 rounded-full" style={{ width: `${Math.min((consultantStats?.identify_location_count || 0) * 10, 100)}%` }}></div>
                </div>
              </div>
            </div>
          </div>

          <h2 className="text-lg font-semibold text-gray-900 mb-4">AI Recommendations</h2>
          <div className="bg-gradient-to-br from-purple-50 to-indigo-50 p-5 rounded-xl border border-purple-200">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">Train Your AI Co-founder</h3>
                <p className="text-sm text-gray-600 mb-3">
                  Upload your business documents to get more personalized recommendations.
                </p>
                <Link to="/brain" className="text-sm text-purple-600 font-medium hover:text-purple-700">
                  Start Training →
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
