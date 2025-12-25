import { useMemo, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search, Bookmark, Filter, FileText, ChevronRight, Lock } from 'lucide-react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

const freshnessOptions = [
  { value: 'All', label: 'All', maxDays: Infinity },
  { value: '0-7', label: '0-7 days', maxDays: 7 },
  { value: '8-30', label: '8-30 days', minDays: 8, maxDays: 30 },
  { value: '31-90', label: '31-90 days', minDays: 31, maxDays: 90 },
  { value: '91+', label: '91+ days', minDays: 91 },
]

type Opportunity = {
  id: number
  title: string
  description: string
  category: string
  validation_count?: number | null
  market_size?: string | null
  ai_market_size_estimate?: string | null
  ai_competition_level?: string | null
  feasibility_score?: number | null
  created_at?: string
  views?: number
  saves?: number
  growth_rate?: number
  tags?: string[]
}

type AccessInfo = {
  age_days: number
  days_until_unlock: number
  is_accessible: boolean
  working_on_count?: number
  is_unlocked: boolean
  can_pay_to_unlock: boolean
  unlock_price?: number | null
  user_tier?: string | null
  content_state?: string | null
}


type OpportunityList = {
  opportunities: Opportunity[]
  total: number
  page: number
  page_size: number
}

type WatchlistItem = {
  id: number
  opportunity_id: number
  created_at: string
  opportunity?: Opportunity | null
}

function getAgeInDays(createdAt?: string): number {
  if (!createdAt) return 999
  const created = new Date(createdAt).getTime()
  if (Number.isNaN(created)) return 999
  return Math.floor((Date.now() - created) / (1000 * 60 * 60 * 24))
}

function formatMarketSize(size?: string | null): string {
  if (!size) return '~$50M'
  const cleaned = size.replace(/\s/g, '')
  if (cleaned.includes('-')) {
    const parts = cleaned.split('-')
    const first = parts[0].replace(/[^0-9.BMK$]/gi, '')
    return `~${first}`
  }
  return size.startsWith('~') ? size : `~${size}`
}


export default function Discover() {
  const [searchParams] = useSearchParams()
  const initialQuery = searchParams.get('q') || ''
  const [searchQuery, setSearchQuery] = useState(initialQuery)
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [selectedFreshness, setSelectedFreshness] = useState('All')
  const [showFilters, setShowFilters] = useState(true)
  const navigate = useNavigate()

  const { token, isAuthenticated, user } = useAuthStore()
  const isPaidUser = user?.tier && user.tier.toLowerCase() !== 'free'
  const queryClient = useQueryClient()

  const categoriesQuery = useQuery({
    queryKey: ['opportunity-categories'],
    queryFn: async (): Promise<string[]> => {
      const res = await fetch('/api/v1/opportunities/categories')
      if (!res.ok) return []
      return (await res.json()) as string[]
    },
    staleTime: 5 * 60 * 1000,
  })

  const categories = ['All', ...(categoriesQuery.data || [])]

  const opportunitiesQuery = useQuery({
    queryKey: ['opportunities', { q: searchQuery, category: selectedCategory, status: selectedFreshness, isAuthenticated }],
    queryFn: async (): Promise<OpportunityList> => {
      const params = new URLSearchParams()
      params.set('limit', '50')
      params.set('skip', '0')
      if (selectedCategory !== 'All') params.set('category', selectedCategory)
      const headers: Record<string, string> = {}
      if (token) headers.Authorization = `Bearer ${token}`
      const res = await fetch(`/api/v1/opportunities/?${params.toString()}`, { headers })
      if (!res.ok) throw new Error('Failed to load opportunities')
      return (await res.json()) as OpportunityList
    },
  })

  const watchlistQuery = useQuery({
    queryKey: ['watchlist', { isAuthenticated }],
    enabled: isAuthenticated && Boolean(token),
    queryFn: async (): Promise<WatchlistItem[]> => {
      const res = await fetch('/api/v1/watchlist/', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to load watchlist')
      return (await res.json()) as WatchlistItem[]
    },
  })

  const watchlistByOppId = useMemo(() => {
    const map = new Map<number, WatchlistItem>()
    for (const item of watchlistQuery.data ?? []) {
      map.set(item.opportunity_id, item)
    }
    return map
  }, [watchlistQuery.data])

  const opportunityIds = useMemo(() => 
    (opportunitiesQuery.data?.opportunities ?? []).map(o => o.id),
    [opportunitiesQuery.data]
  )

  const accessInfoQuery = useQuery({
    queryKey: ['batch-access', opportunityIds],
    enabled: opportunityIds.length > 0,
    queryFn: async (): Promise<Record<number, AccessInfo>> => {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' }
      if (token) headers.Authorization = `Bearer ${token}`
      const res = await fetch('/api/v1/opportunities/batch-access', {
        method: 'POST',
        headers,
        body: JSON.stringify(opportunityIds),
      })
      if (!res.ok) return {}
      return (await res.json()) as Record<number, AccessInfo>
    },
    staleTime: 60 * 1000,
  })

  const addToWatchlist = useMutation({
    mutationFn: async (opportunityId: number) => {
      const res = await fetch('/api/v1/watchlist/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ opportunity_id: opportunityId }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data?.detail || 'Failed to save')
      return data as WatchlistItem
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] })
    },
  })

  const removeFromWatchlist = useMutation({
    mutationFn: async (opportunityId: number) => {
      const res = await fetch(`/api/v1/watchlist/opportunity/${opportunityId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok && res.status !== 204) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data?.detail || 'Failed to remove')
      }
      return true
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] })
    },
  })

  const filteredOpportunities = useMemo(() => {
    const raw = opportunitiesQuery.data?.opportunities ?? []
    const q = searchQuery.trim().toLowerCase()
    return raw.filter((opp) => {
      const matchesSearch = !q || opp.title.toLowerCase().includes(q) || opp.description.toLowerCase().includes(q)
      const matchesCategory = selectedCategory === 'All' || opp.category === selectedCategory
      
      // Filter by freshness (time-decay model)
      let matchesFreshness = true
      if (selectedFreshness !== 'All') {
        const ageDays = getAgeInDays(opp.created_at)
        const selectedOption = freshnessOptions.find(opt => opt.value === selectedFreshness)
        if (selectedOption) {
          const minDays = (selectedOption as any).minDays ?? 0
          const maxDays = (selectedOption as any).maxDays ?? Infinity
          matchesFreshness = ageDays >= minDays && ageDays <= maxDays
        }
      }
      
      return matchesSearch && matchesCategory && matchesFreshness
    })
  }, [opportunitiesQuery.data, searchQuery, selectedCategory, selectedFreshness])

  const discoveryMetrics = useMemo(() => {
    const opps = filteredOpportunities
    const avgMatch = opps.length > 0 
      ? Math.round(opps.reduce((sum, o) => sum + (o.feasibility_score || 0), 0) / opps.length)
      : 0
    const avgAge = opps.length > 0
      ? (opps.reduce((sum, o) => sum + getAgeInDays(o.created_at), 0) / opps.length).toFixed(1)
      : '0'
    const topCategory = selectedCategory !== 'All' ? selectedCategory : 
      opps.reduce((acc, o) => {
        acc[o.category] = (acc[o.category] || 0) + 1
        return acc
      }, {} as Record<string, number>)
    const topCat = typeof topCategory === 'string' ? topCategory :
      Object.entries(topCategory).sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A'
    
    return {
      viewed: opps.length,
      avgMatch,
      topInterest: topCat,
      avgFreshness: avgAge
    }
  }, [filteredOpportunities, selectedCategory])

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
            <span>Discover</span>
            <ChevronRight className="w-4 h-4" />
            <span className="text-gray-900">AI-Curated Opportunities</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Opportunity Feed</h1>
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="inline-flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50"
        >
          <Filter className="w-4 h-4" />
          Filters
        </button>
      </div>

      {/* Active Filters */}
      <div className="flex flex-wrap items-center gap-2 mb-6">
        {selectedCategory !== 'All' && (
          <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-purple-100 text-purple-700 rounded-full text-sm">
            {selectedCategory}
            <button onClick={() => setSelectedCategory('All')} className="hover:text-purple-900">×</button>
          </span>
        )}
        {selectedFreshness !== 'All' && (
          <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-blue-100 text-blue-700 rounded-full text-sm">
            {selectedFreshness}
            <button onClick={() => setSelectedFreshness('All')} className="hover:text-blue-900">×</button>
          </span>
        )}
        {searchQuery && (
          <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-full text-sm">
            "{searchQuery}"
            <button onClick={() => setSearchQuery('')} className="hover:text-gray-900">×</button>
          </span>
        )}
      </div>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* Main Content - Opportunity Cards */}
        <div className="lg:col-span-3 space-y-4">
          {/* Search & Filters */}
          {showFilters && (
            <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search opportunities..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                <div className="flex gap-3">
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                  <select
                    value={selectedFreshness}
                    onChange={(e) => setSelectedFreshness(e.target.value)}
                    className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    {freshnessOptions.map(opt => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Opportunity Cards */}
          {opportunitiesQuery.isLoading && (
            <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-500">
              Loading opportunities...
            </div>
          )}

          {opportunitiesQuery.isError && (
            <div className="bg-white rounded-xl border border-gray-200 p-6 text-red-700">
              Failed to load opportunities. Please try again.
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-6">
          {filteredOpportunities.map((opp) => {
            const score = opp.feasibility_score || (70 + (opp.id % 20))
            const growthRate = opp.growth_rate || (5 + (opp.id % 25))
            const marketSize = formatMarketSize(opp.ai_market_size_estimate || opp.market_size)
            const validations = opp.validation_count || 0
            const accessInfo = accessInfoQuery.data?.[opp.id]
            const daysUntilUnlock = accessInfo?.days_until_unlock ?? 0
            const isAccessible = accessInfo?.is_accessible ?? true

            return (
              <div 
                key={opp.id} 
                onClick={() => navigate(isPaidUser ? `/opportunity/${opp.id}/hub` : `/opportunity/${opp.id}`)}
                className="bg-white rounded-xl border-2 border-stone-200 hover:border-stone-900 transition-all p-6 cursor-pointer group"
              >
                {/* Header: Category + Unlock Status + Score */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs font-medium text-stone-500 uppercase tracking-wide">
                        {opp.category}
                      </span>
                      {!isAccessible && daysUntilUnlock > 0 && (
                        <span className="flex items-center gap-1 bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full text-xs font-medium">
                          <Lock className="w-3 h-3" />
                          Unlocks in {daysUntilUnlock}d
                        </span>
                      )}
                      {isAccessible && (
                        <span className="flex items-center gap-1 bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full text-xs font-medium">
                          Unlocked
                        </span>
                      )}
                    </div>
                    <h3 className="text-lg font-bold text-stone-900 group-hover:text-violet-600 transition-colors leading-tight">
                      {opp.title}
                    </h3>
                  </div>
                  <div className="ml-4 bg-emerald-100 text-emerald-700 px-3 py-2 rounded-full flex-shrink-0">
                    <div className="text-2xl font-bold leading-none">{score}</div>
                  </div>
                </div>
                
                {/* Description */}
                <p className="text-stone-600 text-sm mb-4 line-clamp-2">
                  {opp.description?.replace(/\*\*/g, '').split('\n')[0] || 'Opportunity analysis available...'}
                </p>

                {/* Stats Grid */}
                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="bg-stone-50 rounded-lg p-3">
                    <div className="text-xs text-stone-500 mb-1">Signals</div>
                    <div className="text-lg font-bold text-stone-900">{validations.toLocaleString()}</div>
                  </div>
                  <div className="bg-stone-50 rounded-lg p-3">
                    <div className="text-xs text-stone-500 mb-1">Market</div>
                    <div className="text-lg font-bold text-stone-900">{marketSize}</div>
                  </div>
                  <div className="bg-stone-50 rounded-lg p-3">
                    <div className="text-xs text-stone-500 mb-1">Growth</div>
                    <div className="text-lg font-bold text-emerald-600">+{growthRate}%</div>
                  </div>
                </div>

                {/* Footer */}
                <div className="pt-4 border-t border-stone-200 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        navigate(`/build/reports?opp=${opp.id}`)
                      }}
                      className="flex items-center gap-1 text-sm text-stone-600 hover:text-violet-600"
                    >
                      <FileText className="w-4 h-4" />
                      Report
                    </button>
                    {isAuthenticated && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          const saved = watchlistByOppId.has(opp.id)
                          if (saved) {
                            removeFromWatchlist.mutate(opp.id)
                          } else {
                            addToWatchlist.mutate(opp.id)
                          }
                        }}
                        disabled={addToWatchlist.isPending || removeFromWatchlist.isPending}
                        className={`flex items-center gap-1 text-sm ${
                          watchlistByOppId.has(opp.id)
                            ? 'text-amber-600'
                            : 'text-stone-600 hover:text-violet-600'
                        }`}
                      >
                        <Bookmark className={`w-4 h-4 ${watchlistByOppId.has(opp.id) ? 'fill-amber-500' : ''}`} />
                        {watchlistByOppId.has(opp.id) ? 'Saved' : 'Save'}
                      </button>
                    )}
                  </div>
                  <div className="flex items-center gap-1 text-sm text-stone-600 group-hover:text-violet-600 transition-colors">
                    <span>View full analysis</span>
                    <ChevronRight className="w-4 h-4" />
                  </div>
                </div>
              </div>
            )
          })}
          </div>

          {filteredOpportunities.length === 0 && !opportunitiesQuery.isLoading && (
            <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
              <p className="text-gray-500">No opportunities found matching your criteria.</p>
            </div>
          )}
        </div>

        {/* Right Sidebar - Discovery Metrics */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl border border-gray-200 p-6 sticky top-24">
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-4">
              Your Discovery Metrics
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Ideas Viewed</span>
                <span className="text-lg font-bold text-gray-900">{discoveryMetrics.viewed}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Avg. Match Score</span>
                <span className="text-lg font-bold text-purple-600">{discoveryMetrics.avgMatch}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Top Interest</span>
                <span className="text-sm font-semibold text-gray-900">{discoveryMetrics.topInterest}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Avg. Freshness</span>
                <span className="text-sm font-semibold text-gray-900">{discoveryMetrics.avgFreshness} days</span>
              </div>
            </div>
            <div className="mt-6 pt-4 border-t border-gray-100">
              <button
                onClick={() => navigate('/brain')}
                className="w-full px-4 py-2.5 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 flex items-center justify-center gap-2"
              >
                Improve Your Matches
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
