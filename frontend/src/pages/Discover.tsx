import { useMemo, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search, Clock, Bookmark, Eye, Star, Filter, FileText, ChevronRight } from 'lucide-react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

const categories = ['All', 'Healthcare', 'FinTech', 'E-commerce', 'Education', 'Real Estate', 'SaaS', 'Technology']
const statuses = ['All', 'FRESH', 'OLD']

type Opportunity = {
  id: number
  title: string
  description: string
  category: string
  market_size?: string | null
  ai_competition_level?: string | null
  feasibility_score?: number | null
  created_at?: string
  views?: number
  saves?: number
  growth_rate?: number
  tags?: string[]
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

function getFreshnessStatus(createdAt?: string): { label: string; isFresh: boolean; daysAgo: number } {
  const days = getAgeInDays(createdAt)
  if (days <= 7) return { label: 'FRESH', isFresh: true, daysAgo: days }
  return { label: `OLD • ${days} days`, isFresh: false, daysAgo: days }
}

function getStarRating(score?: number | null): number {
  if (!score) return 3
  if (score >= 90) return 5
  if (score >= 75) return 4.5
  if (score >= 60) return 4
  if (score >= 45) return 3.5
  return 3
}

export default function Discover() {
  const [searchParams] = useSearchParams()
  const initialQuery = searchParams.get('q') || ''
  const [searchQuery, setSearchQuery] = useState(initialQuery)
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [selectedStatus, setSelectedStatus] = useState('All')
  const [showFilters, setShowFilters] = useState(false)
  const navigate = useNavigate()

  const { token, isAuthenticated } = useAuthStore()
  const queryClient = useQueryClient()

  const opportunitiesQuery = useQuery({
    queryKey: ['opportunities', { q: searchQuery, category: selectedCategory, status: selectedStatus }],
    queryFn: async (): Promise<OpportunityList> => {
      const params = new URLSearchParams()
      params.set('limit', '50')
      params.set('skip', '0')
      if (selectedCategory !== 'All') params.set('category', selectedCategory)
      const res = await fetch(`/api/v1/opportunities/?${params.toString()}`)
      if (!res.ok) throw new Error('Failed to load opportunities')
      return (await res.json()) as OpportunityList
    },
  })

  const watchlistQuery = useQuery({
    queryKey: ['watchlist'],
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
      const freshness = getFreshnessStatus(opp.created_at)
      const matchesStatus = selectedStatus === 'All' || 
        (selectedStatus === 'FRESH' && freshness.isFresh) ||
        (selectedStatus === 'OLD' && !freshness.isFresh)
      return matchesSearch && matchesCategory && matchesStatus
    })
  }, [opportunitiesQuery.data, searchQuery, selectedCategory, selectedStatus])

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
        {selectedStatus !== 'All' && (
          <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-blue-100 text-blue-700 rounded-full text-sm">
            {selectedStatus}
            <button onClick={() => setSelectedStatus('All')} className="hover:text-blue-900">×</button>
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
                    value={selectedStatus}
                    onChange={(e) => setSelectedStatus(e.target.value)}
                    className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    {statuses.map(status => (
                      <option key={status} value={status}>{status}</option>
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

          {filteredOpportunities.map((opp) => {
            const freshness = getFreshnessStatus(opp.created_at)
            const stars = getStarRating(opp.feasibility_score)
            const aiMatch = opp.feasibility_score || Math.floor(Math.random() * 20) + 75
            const views = opp.views || Math.floor(Math.random() * 200) + 50
            const saves = opp.saves || Math.floor(Math.random() * 50) + 10
            const growthRate = opp.growth_rate || Math.floor(Math.random() * 30) + 5
            const marketSize = opp.market_size || '$50M - $100M'
            const maturity = growthRate > 20 ? 'Growing' : growthRate > 10 ? 'Stable' : 'Mature'

            return (
              <div 
                key={opp.id} 
                className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:border-gray-300 hover:shadow-md transition-all"
              >
                <div className="flex">
                  {/* Main Content */}
                  <div className="flex-1 p-6">
                    {/* Freshness Badge & Rating */}
                    <div className="flex items-center gap-3 mb-3">
                      <span className={`px-2.5 py-1 text-xs font-semibold rounded ${
                        freshness.isFresh 
                          ? 'bg-emerald-100 text-emerald-700' 
                          : 'bg-gray-100 text-gray-600'
                      }`}>
                        {freshness.label}
                      </span>
                      <div className="flex items-center gap-1">
                        {[...Array(5)].map((_, i) => (
                          <Star 
                            key={i} 
                            className={`w-4 h-4 ${
                              i < Math.floor(stars) 
                                ? 'text-amber-400 fill-amber-400' 
                                : i < stars 
                                  ? 'text-amber-400 fill-amber-200'
                                  : 'text-gray-300'
                            }`} 
                          />
                        ))}
                        <span className="text-sm text-gray-500 ml-1">{stars.toFixed(1)}</span>
                      </div>
                    </div>

                    {/* Title */}
                    <h2 className="text-xl font-semibold text-gray-900 mb-2">{opp.title}</h2>

                    {/* Description */}
                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">{opp.description}</p>

                    {/* Tags */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                        #{opp.category.toLowerCase().replace(/\s/g, '')}
                      </span>
                      {opp.tags?.slice(0, 3).map((tag, i) => (
                        <span key={i} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                          #{tag}
                        </span>
                      ))}
                    </div>

                    {/* Metrics */}
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <Eye className="w-4 h-4" />
                        {views} views
                      </span>
                      <span className="flex items-center gap-1">
                        <Bookmark className="w-4 h-4" />
                        {saves} saves
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {freshness.daysAgo === 0 ? 'Today' : `${freshness.daysAgo}d ago`}
                      </span>
                    </div>
                  </div>

                  {/* Right Sidebar */}
                  <div className="w-48 border-l border-gray-100 bg-gray-50 p-4 flex flex-col justify-between">
                    <div className="space-y-3">
                      <div className="text-center p-3 bg-purple-100 rounded-xl">
                        <div className="text-xs text-purple-600 font-medium">AI Match</div>
                        <div className="text-2xl font-bold text-purple-700">{aiMatch}%</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500">Market</div>
                        <div className="text-sm font-semibold text-gray-900">{marketSize}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500">Growth</div>
                        <div className={`text-sm font-semibold ${growthRate > 15 ? 'text-emerald-600' : 'text-gray-700'}`}>
                          {maturity} (+{growthRate}%/yr)
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2 mt-4">
                      <button
                        onClick={() => navigate(`/opportunity/${opp.id}`)}
                        className="w-full px-4 py-2 bg-black text-white text-sm font-medium rounded-lg hover:bg-gray-800"
                      >
                        View
                      </button>
                      <button
                        onClick={() => navigate(`/build/reports?opp=${opp.id}`)}
                        className="w-full px-4 py-2 border border-gray-200 bg-white text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 flex items-center justify-center gap-1"
                      >
                        <FileText className="w-4 h-4" />
                        Report
                      </button>
                      {isAuthenticated && (
                        <button
                          onClick={() => {
                            const saved = watchlistByOppId.has(opp.id)
                            if (saved) {
                              removeFromWatchlist.mutate(opp.id)
                            } else {
                              addToWatchlist.mutate(opp.id)
                            }
                          }}
                          disabled={addToWatchlist.isPending || removeFromWatchlist.isPending}
                          className={`w-full px-4 py-2 text-sm font-medium rounded-lg flex items-center justify-center gap-1 ${
                            watchlistByOppId.has(opp.id)
                              ? 'bg-amber-50 border border-amber-200 text-amber-700 hover:bg-amber-100'
                              : 'border border-gray-200 bg-white text-gray-700 hover:bg-gray-50'
                          }`}
                        >
                          <Bookmark className={`w-4 h-4 ${watchlistByOppId.has(opp.id) ? 'fill-amber-500' : ''}`} />
                          {watchlistByOppId.has(opp.id) ? 'Saved' : 'Save'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}

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
