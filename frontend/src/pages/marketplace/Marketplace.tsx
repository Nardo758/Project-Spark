import { useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Filter, Search, Star } from 'lucide-react'
import SimplePage from '../../components/SimplePage'
import { fetchMarketplaceLeads } from '../../services/marketplaceApi'

function fmtCents(cents: number) {
  return `$${(cents / 100).toFixed(0)}`
}

export default function Marketplace() {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialQ = searchParams.get('q') || ''
  const [q, setQ] = useState(initialQ)
  const [showFilters, setShowFilters] = useState(false)
  const [industry, setIndustry] = useState(searchParams.get('industry') || '')
  const [location, setLocation] = useState(searchParams.get('location') || '')

  const query = useQuery({
    queryKey: ['marketplace-leads', { q: initialQ, industry, location }],
    queryFn: () =>
      fetchMarketplaceLeads({
        q: initialQ,
        industry: industry || undefined,
        location: location || undefined,
        limit: 24,
        skip: 0,
        status: 'active',
      }),
  })

  const industries = useMemo(() => {
    const set = new Set<string>()
    for (const l of query.data?.leads ?? []) if (l.industry) set.add(l.industry)
    return Array.from(set).sort()
  }, [query.data])

  return (
    <SimplePage
      title="Leads Marketplace"
      subtitle="Browse vetted lead packages tied to opportunities. Purchase access when you’re ready."
      actions={
        <>
          <Link to="/pricing" className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium">
            Compare plans
          </Link>
          <Link to="/services" className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium">
            Explore services
          </Link>
        </>
      }
    >
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex flex-col lg:flex-row gap-3 lg:items-center lg:justify-between">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search leads…"
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setShowFilters((v) => !v)}
              className="inline-flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <Filter className="w-4 h-4" />
              Filters
            </button>
            <button
              type="button"
              onClick={() => {
                const next = new URLSearchParams(searchParams)
                if (q.trim()) next.set('q', q.trim())
                else next.delete('q')
                if (industry) next.set('industry', industry)
                else next.delete('industry')
                if (location) next.set('location', location)
                else next.delete('location')
                setSearchParams(next)
              }}
              className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium"
            >
              Apply
            </button>
          </div>
        </div>

        {showFilters ? (
          <div className="mt-4 grid md:grid-cols-3 gap-3">
            <div>
              <div className="text-sm text-gray-600 mb-1">Industry</div>
              <select
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All</option>
                {industries.map((i) => (
                  <option key={i} value={i}>
                    {i}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">Location</div>
              <input
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. US, Remote, NYC"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        ) : null}
      </div>

      <div className="mt-6">
        {query.isLoading ? (
          <div className="bg-white border border-gray-200 rounded-2xl p-6 text-gray-600">Loading leads…</div>
        ) : null}
        {query.isError ? (
          <div className="bg-white border border-gray-200 rounded-2xl p-6 text-red-700">Failed to load leads.</div>
        ) : null}

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(query.data?.leads ?? []).map((lead) => (
            <div key={lead.id} className="bg-white border border-gray-200 rounded-2xl p-6">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-xs text-gray-500">{lead.public_id}</div>
                  <div className="mt-1 text-lg font-semibold text-gray-900">{lead.public_title}</div>
                </div>
                <div className="text-sm font-semibold text-gray-900">{fmtCents(lead.lead_price_cents)}</div>
              </div>

              <div className="mt-2 text-sm text-gray-700 line-clamp-3">{lead.anonymized_summary}</div>

              <div className="mt-4 flex flex-wrap gap-2 text-xs text-gray-600">
                {lead.industry ? <span className="px-2 py-1 bg-gray-50 border border-gray-200 rounded-lg">{lead.industry}</span> : null}
                {lead.location ? <span className="px-2 py-1 bg-gray-50 border border-gray-200 rounded-lg">{lead.location}</span> : null}
                <span className="px-2 py-1 bg-purple-50 border border-purple-200 rounded-lg text-purple-800 inline-flex items-center gap-1">
                  <Star className="w-3 h-3" /> {lead.quality_score}/10
                </span>
              </div>

              <div className="mt-5 flex gap-2">
                <Link
                  to={`/marketplace/lead/${lead.id}`}
                  className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium text-sm"
                >
                  View
                </Link>
                <Link to="/cart" className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium text-sm">
                  Add to cart
                </Link>
              </div>
            </div>
          ))}
        </div>

        {query.data && query.data.leads.length === 0 ? (
          <div className="mt-6 bg-white border border-gray-200 rounded-2xl p-6 text-gray-600">No leads found.</div>
        ) : null}
      </div>
    </SimplePage>
  )
}

