import { useMemo, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search, Target, Clock, TrendingUp, Bookmark } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

const categories = ['All', 'Healthcare', 'FinTech', 'E-commerce', 'Education', 'Real Estate', 'SaaS']
const statuses = ['All', 'HOT', 'FRESH', 'VALIDATED', 'ARCHIVE']

type Opportunity = {
  id: number
  title: string
  description: string
  category: string
  market_size?: string | null
  ai_competition_level?: string | null
  feasibility_score?: number | null
  created_at?: string
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

function getStatusFromAge(createdAt?: string): 'HOT' | 'FRESH' | 'VALIDATED' | 'ARCHIVE' {
  if (!createdAt) return 'ARCHIVE'
  const created = new Date(createdAt).getTime()
  if (Number.isNaN(created)) return 'ARCHIVE'
  const ageDays = Math.floor((Date.now() - created) / (1000 * 60 * 60 * 24))
  if (ageDays <= 7) return 'HOT'
  if (ageDays <= 30) return 'FRESH'
  if (ageDays <= 90) return 'VALIDATED'
  return 'ARCHIVE'
}

export default function Discover() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [selectedStatus, setSelectedStatus] = useState('All')

  const { token, isAuthenticated } = useAuthStore()
  const queryClient = useQueryClient()

  const opportunitiesQuery = useQuery({
    queryKey: ['opportunities', { q: searchQuery, category: selectedCategory, status: selectedStatus }],
    queryFn: async (): Promise<OpportunityList> => {
      // Server-side search exists, but to keep this minimal and robust, we fetch a page and filter client-side.
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
      const status = getStatusFromAge(opp.created_at)
      const matchesStatus = selectedStatus === 'All' || status === selectedStatus
      return matchesSearch && matchesCategory && matchesStatus
    })
  }, [opportunitiesQuery.data, searchQuery, selectedCategory, selectedStatus])

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
        {opportunitiesQuery.isLoading && (
          <div className="bg-white rounded-xl border border-gray-200 p-6">Loading opportunities…</div>
        )}
        {opportunitiesQuery.isError && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 text-red-700">
            Failed to load opportunities. Please try again.
          </div>
        )}
        {filteredOpportunities.map((opp) => (
          (() => {
            const status = getStatusFromAge(opp.created_at)
            const saved = watchlistByOppId.has(opp.id)
            const marketSize = opp.market_size || '—'
            const competition = opp.ai_competition_level || '—'
            const ttm = '—'

            const saving = addToWatchlist.isPending || removeFromWatchlist.isPending

            return (
          <div key={opp.id} className="bg-white rounded-xl border border-gray-200 p-6 hover:border-gray-300 hover:shadow-md transition-all">
            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-3">
                  <span className={`px-2.5 py-1 text-xs font-semibold rounded ${
                    status === 'HOT' ? 'bg-red-100 text-red-700' :
                    status === 'FRESH' ? 'bg-blue-100 text-blue-700' :
                    status === 'VALIDATED' ? 'bg-green-100 text-green-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {status}
                  </span>
                  <span className="text-sm text-gray-500">{opp.category}</span>
                </div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">{opp.title}</h2>
                <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <TrendingUp className="w-4 h-4" />
                    Market: {marketSize}
                  </div>
                  <div className="flex items-center gap-1">
                    <Target className="w-4 h-4" />
                    Competition: {competition}
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    TTM: {ttm}
                  </div>
                </div>
              </div>
              <div className="flex flex-col items-end gap-3">
                <div className="flex items-center gap-2 px-4 py-2 bg-green-50 rounded-lg">
                  <Target className="w-5 h-5 text-green-600" />
                  <span className="text-lg font-bold text-green-700">
                    {Math.round((opp.feasibility_score ?? 0) as number)}% Match
                  </span>
                </div>
                <div className="flex gap-2">
                  <button
                    className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 font-medium"
                    type="button"
                    onClick={() => alert('Opportunity details page is next to implement')}
                  >
                    View Details
                  </button>
                  <button
                    type="button"
                    disabled={!isAuthenticated || saving}
                    onClick={() => {
                      if (!isAuthenticated) return
                      if (saved) removeFromWatchlist.mutate(opp.id)
                      else addToWatchlist.mutate(opp.id)
                    }}
                    className={`px-3 py-2 rounded-lg border font-medium flex items-center gap-2 ${
                      saved ? 'bg-yellow-50 border-yellow-200 text-yellow-800 hover:bg-yellow-100' : 'bg-white border-gray-200 text-gray-800 hover:bg-gray-50'
                    } ${!isAuthenticated ? 'opacity-50 cursor-not-allowed' : ''}`}
                    title={!isAuthenticated ? 'Sign in to save opportunities' : saved ? 'Remove from saved' : 'Save for later'}
                  >
                    <Bookmark className="w-4 h-4" />
                    {saved ? 'Saved' : 'Save'}
                  </button>
                </div>
              </div>
            </div>
          </div>
            )
          })()
        ))}
      </div>

      {filteredOpportunities.length === 0 && !opportunitiesQuery.isLoading && (
        <div className="text-center py-12">
          <p className="text-gray-500">No opportunities found matching your criteria.</p>
        </div>
      )}
    </div>
  )
}
