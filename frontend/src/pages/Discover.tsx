import { useMemo, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Filter, Search, Target } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import { useBrainStore } from '../stores/brainStore'

type Opportunity = {
  id: number
  title: string
  description: string
  category: string
  market_size?: string | null
  feasibility_score?: number | null
  created_at?: string | null
}

type OpportunityList = {
  opportunities: Opportunity[]
  total: number
}

function getAgeInDays(createdAt?: string | null): number {
  if (!createdAt) return 999
  const t = new Date(createdAt).getTime()
  if (Number.isNaN(t)) return 999
  return Math.floor((Date.now() - t) / (1000 * 60 * 60 * 24))
}

export default function Discover() {
  const [searchParams] = useSearchParams()
  const initialQuery = searchParams.get('q') || ''
  const [q, setQ] = useState(initialQuery)
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [showFilters, setShowFilters] = useState(false)
  const [brainFilterOn, setBrainFilterOn] = useState(true)
  const navigate = useNavigate()

  const { isAuthenticated } = useAuthStore()
  const brainEnabled = useBrainStore((s) => s.isEnabled)
  const brainName = useBrainStore((s) => s.brainName)
  const brainFocus = useBrainStore((s) => s.focusTags)

  const opportunitiesQuery = useQuery({
    queryKey: ['opportunities'],
    queryFn: async (): Promise<OpportunityList> => {
      const params = new URLSearchParams()
      params.set('limit', '50')
      params.set('skip', '0')
      const res = await fetch(`/api/v1/opportunities/?${params.toString()}`)
      if (!res.ok) throw new Error('Failed to load opportunities')
      return (await res.json()) as OpportunityList
    },
  })

  const categories = useMemo(() => {
    const set = new Set<string>()
    for (const o of opportunitiesQuery.data?.opportunities ?? []) set.add(o.category)
    return ['All', ...Array.from(set).sort()]
  }, [opportunitiesQuery.data])

  const filtered = useMemo(() => {
    const raw = opportunitiesQuery.data?.opportunities ?? []
    const query = q.trim().toLowerCase()
    return raw.filter((opp) => {
      const matchesQuery =
        !query || opp.title.toLowerCase().includes(query) || (opp.description || '').toLowerCase().includes(query)
      const matchesCategory = selectedCategory === 'All' || opp.category === selectedCategory
      const matchesBrain =
        !brainEnabled ||
        !brainName ||
        !brainFilterOn ||
        brainFocus.length === 0 ||
        brainFocus.some((t) => opp.title.toLowerCase().includes(t.toLowerCase()) || opp.category.toLowerCase().includes(t.toLowerCase()))
      return matchesQuery && matchesCategory && matchesBrain
    })
  }, [opportunitiesQuery.data, q, selectedCategory, brainEnabled, brainName, brainFilterOn, brainFocus])

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Discover</h1>
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
        <div className="flex flex-col lg:flex-row gap-3 lg:items-center lg:justify-between">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search opportunities..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex flex-wrap gap-2 items-center">
            {brainEnabled && brainName ? (
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
            ) : null}

            <button
              type="button"
              onClick={() => setShowFilters((v) => !v)}
              className="inline-flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <Filter className="w-4 h-4" />
              Filters
            </button>
          </div>
        </div>

        {showFilters ? (
          <div className="mt-4 flex flex-wrap gap-2 items-center">
            <div className="text-sm text-gray-600">Category</div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>
        ) : null}
      </div>

      {opportunitiesQuery.isLoading ? (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-500">Loading opportunities…</div>
      ) : null}

      {opportunitiesQuery.isError ? (
        <div className="bg-white rounded-xl border border-gray-200 p-6 text-red-700">Failed to load opportunities. Please try again.</div>
      ) : null}

      <div className="grid lg:grid-cols-3 gap-4">
        {filtered.map((opp) => {
          const age = getAgeInDays(opp.created_at)
          return (
            <div key={opp.id} className="bg-white border border-gray-200 rounded-2xl p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-xs text-gray-500">{opp.category}</div>
                  <div className="mt-1 text-lg font-semibold text-gray-900">{opp.title}</div>
                </div>
                <div className="flex items-center gap-1 px-3 py-1 bg-green-50 rounded-full">
                  <Target className="w-4 h-4 text-green-600" />
                  <span className="text-sm font-semibold text-green-700">{Math.round(opp.feasibility_score ?? 0)}%</span>
                </div>
              </div>

              <div className="mt-3 text-sm text-gray-700 line-clamp-3">{opp.description}</div>

              <div className="mt-4 flex flex-wrap gap-3 text-xs text-gray-600">
                <div>Market: {opp.market_size || '—'}</div>
                <div>Age: {age}d</div>
              </div>

              <div className="mt-5 flex flex-wrap gap-2">
                <Link to={`/opportunity/${opp.id}`} className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium text-sm">
                  View
                </Link>
                <Link
                  to={`/build/reports?type=${encodeURIComponent('market-analysis')}&opp=${encodeURIComponent(String(opp.id))}`}
                  className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium text-sm"
                  title="Paid members: generate a report"
                >
                  Report
                </Link>
                {!isAuthenticated ? (
                  <Link to="/signup" className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium text-sm">
                    Save (free)
                  </Link>
                ) : (
                  <Link to="/saved" className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium text-sm">
                    Saved
                  </Link>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

