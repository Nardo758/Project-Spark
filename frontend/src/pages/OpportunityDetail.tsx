import { useMemo } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { Bookmark, CheckCircle2, Clock, Lock, ShieldCheck } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

type AccessInfo = {
  age_days: number
  days_until_unlock: number
  is_accessible: boolean
  is_unlocked: boolean
  can_pay_to_unlock: boolean
  unlock_price?: number | null
  user_tier?: string | null
  freshness_badge?: { label: string; icon: string; color: string; tier_required: string; description: string }
}

type Opportunity = {
  id: number
  title: string
  description: string
  category: string
  subcategory?: string | null
  severity: number
  market_size?: string | null
  feasibility_score?: number | null
  validation_count: number
  created_at?: string

  is_authenticated: boolean
  is_unlocked: boolean
  access_info?: AccessInfo | null

  ai_analyzed?: boolean
  ai_summary?: string | null
  ai_market_size_estimate?: string | null
  ai_competition_level?: string | null
  ai_target_audience?: string | null

  // Layer 1 gated arrays (when accessible)
  ai_business_model_suggestions?: unknown[] | null
  ai_competitive_advantages?: unknown[] | null
  ai_key_risks?: unknown[] | null
  ai_next_steps?: unknown[] | null
}

type WatchlistCheck = { in_watchlist: boolean; watchlist_item_id: number | null }
type WatchlistItem = { id: number; opportunity_id: number }

type Validation = { id: number; user_id: number; opportunity_id: number }

function fmtCents(cents?: number | null) {
  if (!cents) return null
  return `$${(cents / 100).toFixed(0)}`
}

export default function OpportunityDetail() {
  const { id } = useParams()
  const opportunityId = Number(id)
  const navigate = useNavigate()

  const { token, isAuthenticated, user } = useAuthStore()
  const queryClient = useQueryClient()

  const opportunityQuery = useQuery({
    queryKey: ['opportunity', opportunityId, { authed: Boolean(token) }],
    enabled: Number.isFinite(opportunityId),
    queryFn: async (): Promise<Opportunity> => {
      const headers: Record<string, string> = {}
      if (token) headers.Authorization = `Bearer ${token}`
      const res = await fetch(`/api/v1/opportunities/${opportunityId}`, { headers })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data?.detail || 'Failed to load opportunity')
      return data as Opportunity
    },
  })

  const watchlistCheckQuery = useQuery({
    queryKey: ['watchlist-check', opportunityId],
    enabled: isAuthenticated && Boolean(token) && Number.isFinite(opportunityId),
    queryFn: async (): Promise<WatchlistCheck> => {
      const res = await fetch(`/api/v1/watchlist/check/${opportunityId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to check watchlist')
      return (await res.json()) as WatchlistCheck
    },
  })

  const validationsQuery = useQuery({
    queryKey: ['validations', opportunityId],
    enabled: Number.isFinite(opportunityId),
    queryFn: async (): Promise<Validation[]> => {
      const res = await fetch(`/api/v1/validations/opportunity/${opportunityId}`)
      if (!res.ok) return []
      return (await res.json()) as Validation[]
    },
  })

  const myValidation = useMemo(() => {
    const uid = user?.id
    if (!uid) return null
    return (validationsQuery.data ?? []).find((v) => v.user_id === uid) ?? null
  }, [user?.id, validationsQuery.data])

  const saveMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/v1/watchlist/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ opportunity_id: opportunityId }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data?.detail || 'Failed to save')
      return data as WatchlistItem
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] })
      queryClient.invalidateQueries({ queryKey: ['watchlist-check', opportunityId] })
    },
  })

  const unsaveMutation = useMutation({
    mutationFn: async () => {
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
      queryClient.invalidateQueries({ queryKey: ['watchlist-check', opportunityId] })
    },
  })

  const validateMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/v1/validations/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ opportunity_id: opportunityId }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data?.detail || 'Failed to validate')
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['validations', opportunityId] })
      queryClient.invalidateQueries({ queryKey: ['opportunity', opportunityId] })
    },
  })

  const unvalidateMutation = useMutation({
    mutationFn: async (validationId: number) => {
      const res = await fetch(`/api/v1/validations/${validationId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok && res.status !== 204) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data?.detail || 'Failed to remove validation')
      }
      return true
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['validations', opportunityId] })
      queryClient.invalidateQueries({ queryKey: ['opportunity', opportunityId] })
    },
  })

  const unlockMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/v1/subscriptions/unlock', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ opportunity_id: opportunityId }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data?.detail || 'Unable to unlock')
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunity', opportunityId] })
    },
  })

  const opp = opportunityQuery.data
  const access = opp?.access_info
  const saved = watchlistCheckQuery.data?.in_watchlist ?? false

  if (!Number.isFinite(opportunityId)) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-10">
        <p className="text-gray-700">Invalid opportunity id.</p>
      </div>
    )
  }

  if (opportunityQuery.isLoading) {
    return <div className="max-w-4xl mx-auto px-4 py-10">Loading opportunity…</div>
  }

  if (opportunityQuery.isError || !opp) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-10">
        <p className="text-red-700">Failed to load opportunity.</p>
        <div className="mt-4">
          <button className="text-blue-600 font-medium" onClick={() => navigate(-1)}>
            Go back
          </button>
        </div>
      </div>
    )
  }

  const isAccessible = Boolean(access?.is_accessible)
  const canPay = Boolean(access?.can_pay_to_unlock)
  const daysUntil = access?.days_until_unlock ?? 0
  const payPrice = fmtCents(access?.unlock_price ?? null)

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="mb-6">
        <Link to="/discover" className="text-sm text-blue-600 hover:text-blue-700 font-medium">
          ← Back to Discover
        </Link>
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-sm text-gray-500 mb-2">{opp.category}</div>
            <h1 className="text-2xl font-bold text-gray-900">{opp.title}</h1>
            <p className="mt-3 text-gray-700 leading-relaxed">{opp.description}</p>
          </div>

          <div className="flex flex-col gap-2 items-end">
            <button
              type="button"
              disabled={!isAuthenticated || saveMutation.isPending || unsaveMutation.isPending}
              onClick={() => {
                if (!isAuthenticated) return navigate(`/login?next=${encodeURIComponent(`/opportunity/${opp.id}`)}`)
                if (saved) unsaveMutation.mutate()
                else saveMutation.mutate()
              }}
              className={`px-3 py-2 rounded-lg border font-medium flex items-center gap-2 ${
                saved ? 'bg-yellow-50 border-yellow-200 text-yellow-800 hover:bg-yellow-100' : 'bg-white border-gray-200 text-gray-800 hover:bg-gray-50'
              } ${!isAuthenticated ? 'opacity-50 cursor-not-allowed' : ''}`}
              title={!isAuthenticated ? 'Sign in to save' : saved ? 'Remove from saved' : 'Save for later'}
            >
              <Bookmark className="w-4 h-4" />
              {saved ? 'Saved' : 'Save'}
            </button>

            <button
              type="button"
              disabled={!isAuthenticated || validateMutation.isPending || unvalidateMutation.isPending}
              onClick={() => {
                if (!isAuthenticated) return navigate(`/login?next=${encodeURIComponent(`/opportunity/${opp.id}`)}`)
                if (myValidation) unvalidateMutation.mutate(myValidation.id)
                else validateMutation.mutate()
              }}
              className={`px-3 py-2 rounded-lg border font-medium flex items-center gap-2 ${
                myValidation ? 'bg-green-50 border-green-200 text-green-800 hover:bg-green-100' : 'bg-white border-gray-200 text-gray-800 hover:bg-gray-50'
              } ${!isAuthenticated ? 'opacity-50 cursor-not-allowed' : ''}`}
              title={!isAuthenticated ? 'Sign in to validate' : myValidation ? 'Remove validation' : 'Validate'}
            >
              <CheckCircle2 className="w-4 h-4" />
              {myValidation ? 'Validated' : 'Validate'}
            </button>
          </div>
        </div>

        <div className="mt-6 grid sm:grid-cols-3 gap-4 text-sm">
          <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
            <div className="text-gray-500">Feasibility</div>
            <div className="text-gray-900 font-semibold">{opp.feasibility_score?.toFixed?.(1) ?? '—'}</div>
          </div>
          <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
            <div className="text-gray-500">Validations</div>
            <div className="text-gray-900 font-semibold">{opp.validation_count}</div>
          </div>
          <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
            <div className="text-gray-500">Market size</div>
            <div className="text-gray-900 font-semibold">{opp.market_size || opp.ai_market_size_estimate || '—'}</div>
          </div>
        </div>

        <div className="mt-8">
          <div className="flex items-center gap-2 mb-2">
            {isAccessible ? <ShieldCheck className="w-5 h-5 text-green-600" /> : <Lock className="w-5 h-5 text-gray-500" />}
            <h2 className="text-lg font-semibold text-gray-900">Access</h2>
          </div>

          {access ? (
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
              <div className="text-sm text-gray-700">
                {isAccessible ? (
                  <span className="font-medium text-green-700">You have access to the Problem Overview.</span>
                ) : (
                  <span className="font-medium text-gray-800">This content is gated.</span>
                )}
              </div>

              {!isAccessible && (
                <div className="mt-3 text-sm text-gray-700">
                  {daysUntil > 0 ? (
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      Unlocks for your tier in <span className="font-semibold">{daysUntil} days</span>.
                    </div>
                  ) : canPay ? (
                    <div>Pay-per-unlock available: <span className="font-semibold">{payPrice}</span> (Stripe UI is next).</div>
                  ) : (
                    <div>Upgrade or unlock to access.</div>
                  )}
                </div>
              )}

              {!isAccessible && isAuthenticated && (
                <div className="mt-4 flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => unlockMutation.mutate()}
                    disabled={unlockMutation.isPending}
                    className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 font-medium disabled:opacity-50"
                  >
                    {unlockMutation.isPending ? 'Unlocking…' : 'Unlock (subscription)'}
                  </button>
                  <Link to="/pricing" className="px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 font-medium">
                    View plans
                  </Link>
                </div>
              )}
              {!isAccessible && !isAuthenticated && (
                <div className="mt-4">
                  <Link
                    to={`/login?next=${encodeURIComponent(`/opportunity/${opp.id}`)}`}
                    className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 font-medium inline-flex"
                  >
                    Sign in to unlock
                  </Link>
                </div>
              )}
            </div>
          ) : (
            <div className="text-sm text-gray-600">No access metadata available.</div>
          )}
        </div>

        <div className="mt-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">AI Summary</h2>
          <div className="bg-white border border-gray-200 rounded-xl p-4">
            <p className="text-gray-700">{opp.ai_summary || 'No AI summary available yet.'}</p>
            <div className="mt-4 text-sm text-gray-600 grid sm:grid-cols-2 gap-2">
              <div>Competition: <span className="font-medium text-gray-800">{opp.ai_competition_level || '—'}</span></div>
              <div>Target audience: <span className="font-medium text-gray-800">{opp.ai_target_audience || '—'}</span></div>
            </div>
          </div>
        </div>

        <div className="mt-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">Problem Overview</h2>
          {isAccessible ? (
            <div className="grid gap-3">
              <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
                <div className="font-semibold text-gray-900 mb-2">Business model suggestions</div>
                <pre className="text-xs text-gray-700 whitespace-pre-wrap">{JSON.stringify(opp.ai_business_model_suggestions ?? [], null, 2)}</pre>
              </div>
              <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
                <div className="font-semibold text-gray-900 mb-2">Competitive advantages</div>
                <pre className="text-xs text-gray-700 whitespace-pre-wrap">{JSON.stringify(opp.ai_competitive_advantages ?? [], null, 2)}</pre>
              </div>
              <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
                <div className="font-semibold text-gray-900 mb-2">Key risks</div>
                <pre className="text-xs text-gray-700 whitespace-pre-wrap">{JSON.stringify(opp.ai_key_risks ?? [], null, 2)}</pre>
              </div>
              <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
                <div className="font-semibold text-gray-900 mb-2">Next steps</div>
                <pre className="text-xs text-gray-700 whitespace-pre-wrap">{JSON.stringify(opp.ai_next_steps ?? [], null, 2)}</pre>
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-gray-700">
              This section is locked until you have access.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

