import { useMemo, useState } from 'react'
import { useQuery, useMutation, useQueries, useQueryClient } from '@tanstack/react-query'
import { CheckCircle2, Lock, Search, Target, Clock, TrendingUp, Bookmark } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { useBrainStore } from '../stores/brainStore'

const categories = ['All', 'Healthcare', 'FinTech', 'E-commerce', 'Education', 'Real Estate', 'SaaS']
const statuses = ['All', 'HOT', 'FRESH', 'VALIDATED', 'ARCHIVE']

type Opportunity = {
  id: number
  title: string
  description: string
  category: string
  validation_count?: number | null
  market_size?: string | null
  ai_competition_level?: string | null
  feasibility_score?: number | null
  created_at?: string
}

type AccessInfo = {
  age_days: number
  days_until_unlock: number
  is_accessible: boolean
  is_unlocked: boolean
  can_pay_to_unlock: boolean
  unlock_price?: number | null
  user_tier?: string | null
  content_state?: string | null
}

type OpportunityAccessSnapshot = {
  id: number
  access_info?: AccessInfo | null
  is_unlocked?: boolean
  is_authenticated?: boolean
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

function fmtCents(cents?: number | null) {
  if (!cents) return null
  return `$${(cents / 100).toFixed(0)}`
}

export default function Discover() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [selectedStatus, setSelectedStatus] = useState('All')
  const navigate = useNavigate()

  const { token, isAuthenticated } = useAuthStore()
  const brainName = useBrainStore((s) => s.brainName)
  const brainScore = useBrainStore((s) => s.matchScore)
  const brainFocus = useBrainStore((s) => s.focusTags)
  const brainEnabled = useBrainStore((s) => s.isEnabled)
  const saveToBrain = useBrainStore((s) => s.saveOpportunity)
  const [brainFilterOn, setBrainFilterOn] = useState(true)
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
      const matchesBrain =
        !brainEnabled ||
        !brainName ||
        !brainFilterOn ||
        brainFocus.length === 0 ||
        brainFocus.some((t) => opp.title.toLowerCase().includes(t.toLowerCase()) || opp.category.toLowerCase().includes(t.toLowerCase()))
      return matchesSearch && matchesCategory && matchesStatus && matchesBrain
    })
  }, [opportunitiesQuery.data, searchQuery, selectedCategory, selectedStatus, brainEnabled, brainName, brainFilterOn, brainFocus])

  const accessQueries = useQueries({
    queries: filteredOpportunities.map((opp) => ({
      queryKey: ['opportunity-access', opp.id, { authed: Boolean(token) }],
      queryFn: async (): Promise<OpportunityAccessSnapshot> => {
        const headers: Record<string, string> = {}
        if (token) headers.Authorization = `Bearer ${token}`
        const res = await fetch(`/api/v1/opportunities/${opp.id}`, { headers })
        const data = await res.json().catch(() => ({}))
        if (!res.ok) throw new Error(data?.detail || 'Failed to load access metadata')
        return {
          id: opp.id,
          access_info: (data as OpportunityAccessSnapshot).access_info ?? null,
          is_unlocked: Boolean((data as OpportunityAccessSnapshot).is_unlocked),
          is_authenticated: Boolean((data as OpportunityAccessSnapshot).is_authenticated),
        }
      },
      staleTime: 60_000,
      retry: 1,
    })),
  })

  const accessByOppId = useMemo(() => {
    const map = new Map<number, AccessInfo | null>()
    for (const q of accessQueries) {
      const data = q.data
      if (!data) continue
      map.set(data.id, data.access_info ?? null)
    }
    return map
  }, [accessQueries])

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Discover Opportunities</h1>
        <p className="text-gray-600">Browse validated opportunities with free previews and pay‑as‑you‑go unlocks.</p>
      </div>

      {!isAuthenticated && (
        <div className="mb-6 bg-white rounded-xl border border-gray-200 p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div className="text-sm text-gray-700">
            You’re viewing the public feed. Create a free account to save opportunities, and unlock premium analysis when you’re ready.
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => navigate('/services')}
              className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium"
            >
              Explore services
            </button>
            <button
              type="button"
              onClick={() => navigate('/pricing')}
              className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium"
            >
              See pricing
            </button>
            <button
              type="button"
              onClick={() => navigate('/signup')}
              className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium"
            >
              Create account
            </button>
          </div>
        </div>
      )}

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
          {brainEnabled && brainName && (
            <button
              type="button"
              onClick={() => setBrainFilterOn((v) => !v)}
              className={`px-4 py-2 rounded-lg border font-medium ${
                brainFilterOn ? 'bg-purple-50 border-purple-200 text-purple-800' : 'bg-white border-gray-200 text-gray-800 hover:bg-gray-50'
              }`}
              title="Toggle Brain AI filtering"
            >
              🧠 Filter: {brainFilterOn ? 'ON' : 'OFF'}
            </button>
          )}
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
            const saving = addToWatchlist.isPending || removeFromWatchlist.isPending
            const access = accessByOppId.get(opp.id) ?? null
            const isAccessible = Boolean(access?.is_accessible)
            const canPay = Boolean(access?.can_pay_to_unlock)
            const unlockPrice = fmtCents(access?.unlock_price ?? null)
            const brainMatch = brainEnabled && brainName
              ? Math.max(0, Math.min(100, Math.round((brainScore * 0.5) + ((opp.feasibility_score ?? 0) * 0.5))))
              : null

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
                  <span className={`inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded ${
                    isAccessible ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-800'
                  }`}>
                    {isAccessible ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Lock className="w-3.5 h-3.5" />}
                    {isAccessible ? 'Full access' : 'Preview'}
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
                    Access: {isAccessible ? 'Unlocked' : 'Locked'}
                  </div>
                  {brainMatch !== null && (
                    <div className="text-purple-700 font-semibold">🧠 {brainMatch}%</div>
                  )}
                </div>

                <div className="mt-5 grid md:grid-cols-2 gap-4">
                  <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
                    <div className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Preview (free)</div>
                    <ul className="mt-2 text-sm text-gray-700 space-y-1">
                      <li>• Problem statement</li>
                      <li>• Market size estimate</li>
                      <li>• Growth signal snapshot</li>
                      <li>• Geographic breakdown</li>
                      <li>• Validation methodology</li>
                    </ul>
                  </div>
                  <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
                    <div className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Locked (purchase required)</div>
                    <ul className="mt-2 text-sm text-gray-700 space-y-1">
                      <li>• Competitive analysis</li>
                      <li>• TAM / SAM / SOM</li>
                      <li>• Acquisition channels</li>
                      <li>• Revenue projections</li>
                      <li>• Risk assessment</li>
                    </ul>
                    <div className="mt-3 text-xs text-gray-600">
                      Validations: {typeof opp.validation_count === 'number' ? opp.validation_count : '—'}
                    </div>
                    {brainEnabled && brainName && (
                      <div className="mt-3 text-xs text-gray-600">
                        <span className="font-semibold text-gray-700">Brain insights:</span>{' '}
                        Fits your focus on {brainFocus.slice(0, 2).join(', ') || 'your goals'}.
                      </div>
                    )}
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
                <div className="flex gap-2 flex-wrap justify-end">
                  <button
                    className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 font-medium"
                    type="button"
                    onClick={() => navigate(`/opportunity/${opp.id}`)}
                  >
                    View Details
                  </button>
                  {!isAccessible && (
                    <button
                      type="button"
                      onClick={() => {
                        const next = `/opportunity/${opp.id}?unlock=1`
                        if (!isAuthenticated) {
                          navigate(`/login?next=${encodeURIComponent(next)}`)
                          return
                        }
                        if (canPay) {
                          navigate(next)
                        } else {
                          navigate('/pricing')
                        }
                      }}
                      className="px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 font-medium"
                      title={canPay ? 'Unlock full analysis' : 'View plans to unlock'}
                    >
                      {canPay && unlockPrice ? `Unlock ${unlockPrice}` : 'Unlock'}
                    </button>
                  )}

                  {brainEnabled && isAuthenticated && (
                    <button
                      type="button"
                      onClick={() => saveToBrain({ opportunityId: opp.id, category: opp.category, title: opp.title })}
                      className="px-4 py-2 border border-purple-200 rounded-lg bg-purple-50 hover:bg-purple-100 font-medium text-purple-800"
                      title="Save to My Brain"
                    >
                      Save to Brain
                    </button>
                  )}
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
