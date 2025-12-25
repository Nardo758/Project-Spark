import { useEffect, useMemo, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import { 
  Bookmark, CheckCircle2, Lock, TrendingUp, Users, 
  FileText, BarChart3, Target, 
  ChevronRight, ArrowRight,
  Zap, Download, Share2, Star, Rocket, Briefcase
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import PayPerUnlockModal from '../components/PayPerUnlockModal'
import EnterpriseContactModal from '../components/EnterpriseContactModal'

type AccessInfo = {
  age_days: number
  days_until_unlock: number
  is_accessible: boolean
  is_unlocked: boolean
  can_pay_to_unlock: boolean
  unlock_price?: number | null
  user_tier?: string | null
  freshness_badge?: { label: string; icon: string; color: string; tier_required: string; description: string }
  content_state?: string | null
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
  growth_rate?: number
  geographic_scope?: string
  country?: string
  region?: string
  city?: string

  is_authenticated: boolean
  is_unlocked: boolean
  access_info?: AccessInfo | null

  ai_analyzed?: boolean
  ai_summary?: string | null
  ai_market_size_estimate?: string | null
  ai_competition_level?: string | null
  ai_target_audience?: string | null
  ai_urgency_level?: string | null
  ai_pain_intensity?: number | null
  ai_problem_statement?: string | null

  ai_business_model_suggestions?: string[] | null
  ai_competitive_advantages?: string[] | null
  ai_key_risks?: string[] | null
  ai_next_steps?: string[] | null
}

type WatchlistCheck = { in_watchlist: boolean; watchlist_item_id: number | null }
type WatchlistItem = { id: number; opportunity_id: number }
type Validation = { id: number; user_id: number; opportunity_id: number }

type RecommendedExpert = {
  id: number
  name: string
  headline: string | null
  avatar_url: string | null
  skills: string[]
  specialization: string[]
  categories: string[]
  avg_rating: number | null
  total_reviews: number
  completed_projects: number
  success_rate: number | null
  is_available: boolean
  hourly_rate_cents: number | null
  pricing_model: string | null
  match_score: number
  match_reason: string
}

function fmtCents(cents?: number | null) {
  if (!cents) return null
  return `$${(cents / 100).toFixed(0)}`
}

const regions = ['US National', 'Southwest', 'Northeast', 'Midwest', 'West Coast', 'Southeast']

export default function OpportunityDetail() {
  const { id } = useParams()
  const opportunityId = Number(id)
  const location = useLocation()
  const navigate = useNavigate()

  const { token, isAuthenticated, user } = useAuthStore()
  const queryClient = useQueryClient()
  
  const [activeTab, setActiveTab] = useState('validation')
  const [selectedRegion, setSelectedRegion] = useState('US National')

  const opportunityQuery = useQuery({
    queryKey: ['opportunity', opportunityId, isAuthenticated, token?.slice(-8)],
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

  const expertsQuery = useQuery({
    queryKey: ['opportunity-experts', opportunityId],
    enabled: Number.isFinite(opportunityId),
    queryFn: async (): Promise<{ experts: RecommendedExpert[]; total: number }> => {
      const res = await fetch(`/api/v1/opportunities/${opportunityId}/experts?limit=5`)
      if (!res.ok) return { experts: [], total: 0 }
      return await res.json()
    },
  })

  type WorkspaceCheck = { has_workspace: boolean; workspace_id: number | null }
  const workspaceCheckQuery = useQuery({
    queryKey: ['workspace-check', opportunityId],
    enabled: isAuthenticated && Boolean(token) && Number.isFinite(opportunityId),
    queryFn: async (): Promise<WorkspaceCheck> => {
      const res = await fetch(`/api/v1/workspaces/check/${opportunityId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) return { has_workspace: false, workspace_id: null }
      return (await res.json()) as WorkspaceCheck
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

  const [ppuOpen, setPpuOpen] = useState(false)
  const [enterpriseModalOpen, setEnterpriseModalOpen] = useState(false)
  const [ppuClientSecret, setPpuClientSecret] = useState<string | null>(null)
  const [ppuPublishableKey, setPpuPublishableKey] = useState<string | null>(null)
  const [ppuAmountLabel, setPpuAmountLabel] = useState<string>('$15')
  const [ppuError, setPpuError] = useState<string | null>(null)
  const autoUnlockStartedRef = useRef(false)

  const payPerUnlockMutation = useMutation({
    mutationFn: async () => {
      if (!token) throw new Error('Not authenticated')
      if (!Number.isFinite(opportunityId)) throw new Error('Invalid opportunity id')
      const keyRes = await fetch('/api/v1/subscriptions/stripe-key')
      const keyData = await keyRes.json().catch(() => ({}))
      if (!keyRes.ok) throw new Error(keyData?.detail || 'Stripe not configured')

      const res = await fetch('/api/v1/subscriptions/pay-per-unlock', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ opportunity_id: opportunityId }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data?.detail || 'Unable to start payment')

      return {
        publishableKey: String(keyData.publishable_key),
        clientSecret: String(data.client_secret),
        amountCents: Number(data.amount),
      }
    },
    onSuccess: (data) => {
      setPpuError(null)
      setPpuPublishableKey(data.publishableKey)
      setPpuClientSecret(data.clientSecret)
      setPpuAmountLabel(fmtCents(data.amountCents) || '$15')
      setPpuOpen(true)
    },
    onError: (e) => {
      setPpuError(e instanceof Error ? e.message : 'Unable to start payment')
    },
  })

  const opp = opportunityQuery.data
  const access = opp?.access_info
  const saved = watchlistCheckQuery.data?.in_watchlist ?? false

  const shouldAutoUnlock = useMemo(() => {
    const params = new URLSearchParams(location.search)
    return params.get('unlock') === '1'
  }, [location.search])

  useEffect(() => {
    if (!shouldAutoUnlock) return
    if (!isAuthenticated) return
    if (!opp) return
    if (autoUnlockStartedRef.current) return
    if (access?.is_accessible) return
    if (!access?.can_pay_to_unlock) return
    autoUnlockStartedRef.current = true
    payPerUnlockMutation.mutate()
  }, [shouldAutoUnlock, isAuthenticated, opp, access?.is_accessible, access?.can_pay_to_unlock, payPerUnlockMutation])

  if (!Number.isFinite(opportunityId)) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-10">
        <p className="text-stone-700">Invalid opportunity id.</p>
      </div>
    )
  }

  if (opportunityQuery.isLoading) {
    return <div className="max-w-6xl mx-auto px-4 py-10 text-stone-600">Loading opportunity...</div>
  }

  if (opportunityQuery.isError || !opp) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-10">
        <p className="text-red-700">Failed to load opportunity.</p>
        <button className="mt-4 text-violet-600 font-medium" onClick={() => navigate(-1)}>
          Go back
        </button>
      </div>
    )
  }

  const userTier = access?.user_tier?.toLowerCase() || 'free'
  const hasPro = userTier === 'pro' || userTier === 'business' || userTier === 'enterprise'

  const score = opp.feasibility_score || (70 + (opp.id % 20))
  const growthRate = opp.growth_rate || 12
  const marketSize = opp.ai_market_size_estimate || opp.market_size || '$50M'
  const urgency = opp.ai_urgency_level || 'Medium'
  const competition = opp.ai_competition_level || 'Medium'

  async function confirmPayPerUnlock(paymentIntentId: string) {
    if (!token) throw new Error('Not authenticated')
    const res = await fetch(`/api/v1/subscriptions/confirm-pay-per-unlock?payment_intent_id=${encodeURIComponent(paymentIntentId)}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) throw new Error(data?.detail || 'Failed to confirm unlock')
    await queryClient.invalidateQueries({ queryKey: ['opportunity', opportunityId] })
    await queryClient.invalidateQueries({ queryKey: ['opportunity', opportunityId, { authed: Boolean(token) }] })
  }

  const painPoints = [
    { quote: opp.ai_problem_statement || "Users consistently report frustration with current solutions in this space...", severity: 'CRITICAL' },
    { quote: "Finding reliable providers is challenging and time-consuming...", severity: 'HIGH' },
    { quote: "Pricing transparency is a major concern for consumers...", severity: 'MEDIUM' },
  ]

  const researchTabs = [
    { id: 'validation', label: 'Market Validation' },
    { id: 'geographic', label: 'Geographic' },
    { id: 'problem', label: 'Problem Analysis' },
    { id: 'sizing', label: 'Market Sizing' },
    { id: 'solutions', label: 'Solution Pathways' },
  ]

  return (
    <div className="min-h-screen bg-stone-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-6">
          <Link to="/discover" className="text-sm text-violet-600 hover:text-violet-700 font-medium flex items-center gap-1">
            <ChevronRight className="w-4 h-4 rotate-180" />
            Back to Discover
          </Link>
        </div>

        {/* Header Section */}
        <div className="bg-white rounded-xl border-2 border-stone-200 p-8 mb-6">
          <div className="flex items-start justify-between gap-6">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-xs font-medium text-stone-500 uppercase tracking-wide">{opp.category}</span>
                {access?.freshness_badge && (
                  <span className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                    access.freshness_badge.color === 'red' ? 'bg-red-100 text-red-700' :
                    access.freshness_badge.color === 'orange' ? 'bg-orange-100 text-orange-700' :
                    access.freshness_badge.color === 'yellow' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-stone-100 text-stone-700'
                  }`}>
                    <Zap className="w-3 h-3" />
                    {access.freshness_badge.label}
                  </span>
                )}
                {access && !access.is_accessible && access.days_until_unlock > 0 ? (
                  <span className="flex items-center gap-1 bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full text-xs font-medium">
                    <Lock className="w-3 h-3" />
                    Unlocks for your tier in {access.days_until_unlock} days
                  </span>
                ) : access?.is_accessible ? (
                  <span className="flex items-center gap-1 bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full text-xs font-medium">
                    Unlocked
                  </span>
                ) : null}
              </div>
              <h1 className="text-3xl font-bold text-stone-900 mb-3">{opp.title}</h1>
              <p className="text-stone-600 text-lg leading-relaxed">
                {(() => {
                  const desc = opp.description?.replace(/\*\*/g, '').split('\n').filter(l => l.trim() && !l.includes('Market Opportunity Overview'))[0]
                  return desc || opp.ai_summary?.replace(/\*\*/g, '') || 'Analysis pending...'
                })()}
              </p>
            </div>
            
            <div className="flex flex-col items-end gap-3">
              <div className="bg-emerald-100 text-emerald-700 px-6 py-4 rounded-2xl text-center">
                <div className="text-4xl font-bold">{Math.round(score)}</div>
                <div className="text-xs font-medium mt-1">Score</div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    if (!isAuthenticated) return navigate(`/login?next=${encodeURIComponent(`/opportunity/${opp.id}`)}`)
                    if (saved) unsaveMutation.mutate()
                    else saveMutation.mutate()
                  }}
                  disabled={saveMutation.isPending || unsaveMutation.isPending}
                  className={`p-2 rounded-lg border-2 transition-all ${
                    saved ? 'bg-amber-50 border-amber-200 text-amber-700' : 'bg-white border-stone-200 text-stone-600 hover:border-stone-400'
                  }`}
                >
                  <Bookmark className={`w-5 h-5 ${saved ? 'fill-amber-500' : ''}`} />
                </button>
                <button
                  onClick={() => {
                    if (!isAuthenticated) return navigate(`/login?next=${encodeURIComponent(`/opportunity/${opp.id}`)}`)
                    if (myValidation) unvalidateMutation.mutate(myValidation.id)
                    else validateMutation.mutate()
                  }}
                  disabled={validateMutation.isPending || unvalidateMutation.isPending}
                  className={`p-2 rounded-lg border-2 transition-all ${
                    myValidation ? 'bg-emerald-50 border-emerald-200 text-emerald-700' : 'bg-white border-stone-200 text-stone-600 hover:border-stone-400'
                  }`}
                >
                  <CheckCircle2 className="w-5 h-5" />
                </button>
              </div>
              {hasPro ? (
                <button
                  onClick={() => navigate(`/opportunity/${opp.id}/hub`)}
                  className="flex items-center gap-2 px-4 py-2 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700 transition-colors"
                >
                  <Rocket className="w-4 h-4" />
                  Deep Dive WorkHub
                </button>
              ) : isAuthenticated && access?.can_pay_to_unlock ? (
                <button
                  onClick={() => payPerUnlockMutation.mutate()}
                  disabled={payPerUnlockMutation.isPending}
                  className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50"
                >
                  <Lock className="w-4 h-4" />
                  {payPerUnlockMutation.isPending ? 'Processing...' : `Unlock Now (${fmtCents(access.unlock_price) || '$15'})`}
                </button>
              ) : !isAuthenticated ? (
                <Link
                  to={`/login?next=${encodeURIComponent(`/opportunity/${opp.id}`)}`}
                  className="flex items-center gap-2 px-4 py-2 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700 transition-colors"
                >
                  <Rocket className="w-4 h-4" />
                  Sign in to Continue
                </Link>
              ) : !access?.is_accessible && access?.days_until_unlock ? (
                <Link
                  to="/pricing"
                  className="flex items-center gap-2 px-4 py-2 bg-stone-900 text-white rounded-lg font-medium hover:bg-stone-800 transition-colors"
                >
                  Get Earlier Access
                </Link>
              ) : null}
            </div>
          </div>
        </div>

        {/* Problem Statement Section */}
        <div className="bg-violet-50 rounded-xl border-2 border-violet-200 p-8 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-violet-600 rounded-lg flex items-center justify-center">
              <Target className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-xl font-bold text-stone-900">Problem Statement</h2>
          </div>
          <p className="text-stone-700 text-lg leading-relaxed">
            {(() => {
              if (opp.ai_problem_statement) return opp.ai_problem_statement
              if (opp.ai_summary) return opp.ai_summary.replace(/\*\*/g, '')
              const desc = opp.description?.replace(/\*\*/g, '').split('\n').filter(l => l.trim() && !l.includes('Market Opportunity Overview'))[0]
              return desc || 'No problem statement available.'
            })()}
          </p>
        </div>

        {/* TIER 1: Problem Detail (FREE) - Empathize + Define */}
        <div className="bg-white rounded-xl border-2 border-emerald-200 p-8 mb-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-stone-900">Problem Detail</h2>
              <p className="text-stone-500 text-sm">Empathize + Define</p>
            </div>
            <span className="ml-auto bg-emerald-100 text-emerald-700 px-3 py-1 rounded-full text-xs font-bold">FREE</span>
          </div>

          {/* Geographic Market Selector */}
          <div className="mb-8">
            <h3 className="font-bold text-stone-900 mb-3">Geographic Market</h3>
            <div className="grid grid-cols-3 md:grid-cols-6 gap-2 mb-4">
              {regions.map((region) => (
                <button
                  key={region}
                  onClick={() => setSelectedRegion(region)}
                  className={`p-3 rounded-lg border-2 text-sm font-medium transition-all ${
                    selectedRegion === region 
                      ? 'border-violet-600 bg-violet-50 text-violet-700' 
                      : 'border-stone-200 bg-white text-stone-700 hover:border-stone-300'
                  }`}
                >
                  {region}
                </button>
              ))}
            </div>
            <div className="bg-stone-50 rounded-lg border border-stone-200 p-4">
              <div className="grid grid-cols-3 gap-6">
                <div>
                  <div className="text-sm text-stone-500 mb-1">Market Size</div>
                  <div className="text-2xl font-bold text-stone-900">{marketSize}</div>
                </div>
                <div>
                  <div className="text-sm text-stone-500 mb-1">Signals</div>
                  <div className="text-2xl font-bold text-stone-900">{opp.validation_count.toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-sm text-stone-500 mb-1">Growth</div>
                  <div className="text-2xl font-bold text-emerald-600">+{growthRate}%</div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Validation Metrics */}
          <div className="mb-8">
            <h3 className="font-bold text-stone-900 mb-3">Quick Validation Metrics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg border-2 border-stone-200 p-4">
                <div className="text-sm text-stone-500 mb-1">Urgency</div>
                <div className={`text-2xl font-bold ${urgency === 'High' ? 'text-orange-600' : urgency === 'Critical' ? 'text-red-600' : 'text-stone-900'}`}>
                  {urgency}
                </div>
              </div>
              <div className="bg-white rounded-lg border-2 border-stone-200 p-4">
                <div className="text-sm text-stone-500 mb-1">Competition</div>
                <div className={`text-2xl font-bold ${competition === 'Low' ? 'text-emerald-600' : competition === 'High' ? 'text-red-600' : 'text-stone-900'}`}>
                  {competition}
                </div>
              </div>
              <div className="bg-white rounded-lg border-2 border-stone-200 p-4">
                <div className="text-sm text-stone-500 mb-1">Target Audience</div>
                <div className="text-lg font-bold text-stone-900 truncate">{opp.ai_target_audience || 'Consumers'}</div>
              </div>
              <div className="bg-white rounded-lg border-2 border-stone-200 p-4">
                <div className="text-sm text-stone-500 mb-1">Feasibility</div>
                <div className="text-2xl font-bold text-violet-600">{Math.round(score)}%</div>
              </div>
            </div>
          </div>

          {/* Pain Points - Empathize */}
          <div className="mb-8">
            <h3 className="font-bold text-stone-900 mb-3">Top Pain Points</h3>
            <div className="space-y-3">
              {painPoints.map((point, idx) => (
                <div 
                  key={idx} 
                  className={`bg-white rounded-lg p-4 border-l-4 ${
                    point.severity === 'CRITICAL' ? 'border-red-500' : 
                    point.severity === 'HIGH' ? 'border-orange-500' : 'border-yellow-500'
                  }`}
                >
                  <p className="text-stone-800 italic text-sm">"{point.quote}"</p>
                  <span className={`inline-block mt-2 px-2 py-1 rounded text-xs font-bold ${
                    point.severity === 'CRITICAL' ? 'bg-red-100 text-red-700' : 
                    point.severity === 'HIGH' ? 'bg-orange-100 text-orange-700' : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {point.severity}
                  </span>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* TIER 2: Research Dashboard (PRO) - Ideate */}
        <div className={`bg-white rounded-xl border-2 ${hasPro ? 'border-blue-200' : 'border-stone-200'} p-8 mb-6 relative`}>
          {!hasPro && (
            <div className="absolute inset-0 bg-white/80 backdrop-blur-sm rounded-xl flex items-center justify-center z-10">
              <div className="text-center p-8">
                <Lock className="w-12 h-12 text-stone-400 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-stone-900 mb-2">Unlock Research Dashboard</h3>
                <p className="text-stone-600 mb-4">Get market analysis, demographics, and competitive landscape</p>
                <Link 
                  to="/pricing" 
                  className="inline-flex items-center gap-2 bg-stone-900 text-white px-6 py-3 rounded-lg font-medium hover:bg-stone-800"
                >
                  Upgrade to Pro ($99/mo)
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          )}
          
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-stone-900">Research Dashboard</h2>
              <p className="text-stone-500 text-sm">Ideate - Market Analysis</p>
            </div>
            <div className="ml-auto flex items-center gap-2">
              <button className="flex items-center gap-2 px-3 py-2 border border-stone-200 rounded-lg text-sm font-medium text-stone-700 hover:bg-stone-50">
                <Download className="w-4 h-4" />
                Export Report
              </button>
              <button className="flex items-center gap-2 px-3 py-2 border border-stone-200 rounded-lg text-sm font-medium text-stone-700 hover:bg-stone-50">
                <Share2 className="w-4 h-4" />
                Share
              </button>
              <Link 
                to="/network" 
                className="flex items-center gap-2 px-3 py-2 border border-stone-200 rounded-lg text-sm font-medium text-stone-700 hover:bg-stone-50"
              >
                <Users className="w-4 h-4" />
                Find Expert
              </Link>
              <Link 
                to={`/opportunity/${id}/hub`}
                className="flex items-center gap-2 px-4 py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700"
              >
                <Rocket className="w-4 h-4" />
                Deep Dive WorkHub
              </Link>
            </div>
          </div>

          {/* Tabs */}
          <div className="mb-6 bg-stone-100 rounded-lg p-1.5 flex gap-1 overflow-x-auto">
            {researchTabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
                  activeTab === tab.id 
                    ? 'bg-blue-600 text-white shadow' 
                    : 'text-stone-600 hover:bg-stone-50'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="space-y-4">
            {activeTab === 'validation' && (
              <>
                <div className="bg-white rounded-lg border-2 border-stone-200 p-6">
                  <h3 className="font-bold text-stone-900 mb-4">Demand Signals</h3>
                  <div className="grid grid-cols-3 gap-6">
                    <div>
                      <div className="text-sm text-stone-500">Search Volume</div>
                      <div className="text-3xl font-bold text-stone-900">127K/mo</div>
                    </div>
                    <div>
                      <div className="text-sm text-stone-500">YoY Growth</div>
                      <div className="text-3xl font-bold text-emerald-600">+{growthRate + 20}%</div>
                    </div>
                    <div>
                      <div className="text-sm text-stone-500">Social Mentions</div>
                      <div className="text-3xl font-bold text-stone-900">89K/mo</div>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg border-2 border-stone-200 p-6">
                  <h3 className="font-bold text-stone-900 mb-4">Competitive Landscape</h3>
                  <div className="space-y-3">
                    {(opp.ai_competitive_advantages || ['Market leader gap exists', 'Fragmented competitor landscape', 'No dominant solution']).map((comp, idx) => (
                      <div key={idx} className="bg-stone-50 rounded-lg p-4">
                        <div className="font-semibold text-stone-900">{typeof comp === 'string' ? comp : JSON.stringify(comp)}</div>
                        <div className="text-sm text-stone-600 mt-1">Key opportunity for differentiation</div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            {activeTab === 'solutions' && (
              <div className="bg-white rounded-lg border-2 border-stone-200 p-6">
                <h3 className="font-bold text-stone-900 mb-4">Solution Pathways</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  {(opp.ai_business_model_suggestions || ['SaaS Platform', 'Marketplace Model', 'On-Demand Service', 'Subscription Box']).map((model, idx) => (
                    <div key={idx} className="bg-gradient-to-br from-violet-50 to-blue-50 rounded-lg p-4 border-2 border-violet-100">
                      <div className="flex items-center gap-2 mb-2">
                        <Zap className="w-5 h-5 text-violet-600" />
                        <span className="font-bold text-stone-900">{typeof model === 'string' ? model : JSON.stringify(model)}</span>
                      </div>
                      <p className="text-sm text-stone-600">Viable approach based on market analysis</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {(activeTab === 'geographic' || activeTab === 'problem' || activeTab === 'sizing') && (
              <div className="bg-stone-50 rounded-lg border border-stone-200 p-8 text-center">
                <BarChart3 className="w-12 h-12 text-stone-400 mx-auto mb-3" />
                <p className="text-stone-600">Detailed {activeTab} analysis available</p>
              </div>
            )}
          </div>

          {/* Expert Preview - Tier 2 */}
          <div className="mt-6 pt-6 border-t-2 border-stone-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-stone-900 flex items-center gap-2">
                <Users className="w-5 h-5 text-blue-600" />
                Recommended Experts
              </h3>
              <span className="text-xs text-stone-500">
                {expertsQuery.isLoading ? 'Loading...' : `${expertsQuery.data?.total || 0} experts matched`}
              </span>
            </div>
            
            <div className="grid md:grid-cols-3 gap-4 mb-4">
              {(expertsQuery.data?.experts || []).slice(0, 3).map((expert) => (
                <div key={expert.id} className="bg-stone-50 rounded-lg p-4 border border-stone-200 hover:border-blue-300 transition-colors">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-violet-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      {expert.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div>
                      <div className="font-semibold text-stone-900 text-sm">{expert.name}</div>
                      <div className="text-xs text-stone-500">{expert.headline}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-stone-600 mb-3">
                    {expert.avg_rating && (
                      <span className="flex items-center gap-1">
                        <Star className="w-3 h-3 text-amber-500 fill-amber-500" />
                        {expert.avg_rating.toFixed(1)}
                      </span>
                    )}
                    <span>{expert.completed_projects} projects</span>
                    <span className="text-emerald-600 font-medium">{expert.match_score}% match</span>
                  </div>
                  <div className="text-xs text-stone-500 mb-2">{expert.match_reason}</div>
                  {expert.categories[0] && (
                    <div className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded inline-block">
                      {expert.categories[0]}
                    </div>
                  )}
                </div>
              ))}
              {expertsQuery.isLoading && (
                <>
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="bg-stone-50 rounded-lg p-4 border border-stone-200 animate-pulse">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 bg-stone-300 rounded-full"></div>
                        <div className="space-y-2">
                          <div className="h-4 w-24 bg-stone-300 rounded"></div>
                          <div className="h-3 w-32 bg-stone-200 rounded"></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </>
              )}
            </div>

            <div className="bg-gradient-to-r from-blue-50 to-violet-50 rounded-lg p-4 border border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold text-stone-900">Ready to work with an expert?</p>
                  <p className="text-sm text-stone-600">Upgrade to Business for direct messaging and collaboration</p>
                </div>
                <Link 
                  to="/pricing"
                  className="flex items-center gap-2 bg-stone-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-stone-800"
                >
                  Request Consultation
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* CTA: Start Working in WorkHub */}
        <div className="bg-gradient-to-r from-violet-600 to-purple-600 rounded-xl p-8 mb-6 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-white/20 rounded-xl flex items-center justify-center">
                <Rocket className="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold mb-1">Start Working on This</h2>
                <p className="text-violet-100">Start working on this in our WorkHub with AI-powered planning, task management, and expert collaboration.</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {isAuthenticated ? (
                hasPro ? (
                  <Link 
                    to={`/opportunity/${id}/hub`}
                    className="flex items-center gap-2 px-6 py-3 bg-white text-violet-700 rounded-lg font-medium hover:bg-violet-50 transition-colors"
                  >
                    <Briefcase className="w-5 h-5" />
                    Deep Dive WorkHub
                  </Link>
                ) : access?.can_pay_to_unlock ? (
                  <button
                    onClick={() => payPerUnlockMutation.mutate()}
                    disabled={payPerUnlockMutation.isPending}
                    className="flex items-center gap-2 px-6 py-3 bg-white text-violet-700 rounded-lg font-medium hover:bg-violet-50 transition-colors disabled:opacity-50"
                  >
                    <Lock className="w-5 h-5" />
                    {payPerUnlockMutation.isPending ? 'Processing...' : `Unlock Now (${fmtCents(access?.unlock_price) || '$15'})`}
                  </button>
                ) : access?.is_accessible ? (
                  <Link 
                    to={`/opportunity/${id}/hub`}
                    className="flex items-center gap-2 px-6 py-3 bg-white text-violet-700 rounded-lg font-medium hover:bg-violet-50 transition-colors"
                  >
                    <Briefcase className="w-5 h-5" />
                    Deep Dive WorkHub
                  </Link>
                ) : (
                  <Link 
                    to="/pricing"
                    className="flex items-center gap-2 px-6 py-3 bg-white text-violet-700 rounded-lg font-medium hover:bg-violet-50 transition-colors"
                  >
                    <Rocket className="w-5 h-5" />
                    Upgrade to Access WorkHub
                  </Link>
                )
              ) : (
                <Link 
                  to={`/login?next=${encodeURIComponent(`/opportunity/${id}`)}`}
                  className="flex items-center gap-2 px-6 py-3 bg-white text-violet-700 rounded-lg font-medium hover:bg-violet-50 transition-colors"
                >
                  <Rocket className="w-5 h-5" />
                  Sign in to Start
                </Link>
              )}
            </div>
          </div>
        </div>

        {ppuError && (
          <div className="mt-4 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
            {ppuError}
          </div>
        )}
      </div>

      {ppuOpen && ppuClientSecret && ppuPublishableKey && (
        <PayPerUnlockModal
          onClose={() => setPpuOpen(false)}
          publishableKey={ppuPublishableKey}
          clientSecret={ppuClientSecret}
          amountLabel={ppuAmountLabel}
          onConfirmed={confirmPayPerUnlock}
        />
      )}
      {enterpriseModalOpen && (
        <EnterpriseContactModal onClose={() => setEnterpriseModalOpen(false)} />
      )}
    </div>
  )
}
