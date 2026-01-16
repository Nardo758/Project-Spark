import { useEffect, useMemo, useState } from 'react'
import { 
  Check, 
  X,
  Loader2, 
  Zap, 
  TrendingUp, 
  FileText,
  BarChart3,
  Target,
  Lightbulb,
  Globe,
  Clock,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Users,
  Database
} from 'lucide-react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import PayPerUnlockModal from '../components/PayPerUnlockModal'
import EnterpriseContactModal from '../components/EnterpriseContactModal'

type MySubscriptionResponse = {
  tier?: string | null
  status?: string | null
  is_active?: boolean | null
  period_end?: string | null
}

const subscriptionTiers = [
  {
    id: 'explorer',
    name: 'Explorer',
    price: 0,
    priceLabel: 'Free',
    description: 'Try quality, pay for what you need',
    accessWindow: '91+ days',
    tier: 'explorer',
    features: [
      { text: 'Browse validated opportunities', included: true },
      { text: 'Layer 1 access ($15 per unlock)', included: true },
      { text: 'Pay-per-report access (from $25)', included: true },
      { text: 'Layer 2 Deep Dive', included: false },
      { text: 'Layer 3 Execution Package', included: false },
      { text: 'Real-time opportunity alerts', included: false },
    ],
    cta: 'Get Started Free',
    popular: false,
    gradient: 'from-gray-500 to-gray-600',
  },
  {
    id: 'builder',
    name: 'Builder',
    price: 99,
    priceLabel: '$99/mo',
    description: 'Unlimited research, professional execution',
    accessWindow: '31+ days',
    tier: 'pro',
    features: [
      { text: 'Browse validated opportunities', included: true },
      { text: 'Layer 1 unlimited access', included: true },
      { text: 'Pay-per-report access (from $25)', included: true },
      { text: 'Layer 2 Deep Dive', included: false },
      { text: 'Layer 3 Execution Package', included: false },
      { text: 'Priority support', included: true },
    ],
    cta: 'Start Building',
    popular: true,
    gradient: 'from-purple-500 to-indigo-600',
  },
  {
    id: 'scaler',
    name: 'Scaler',
    price: 499,
    priceLabel: '$499/mo',
    description: 'Move faster with deep intelligence',
    accessWindow: '8+ days',
    tier: 'business',
    features: [
      { text: 'Browse validated opportunities', included: true },
      { text: 'Layer 1 unlimited access', included: true },
      { text: 'Pay-per-report access (from $25)', included: true },
      { text: 'Layer 2 Deep Dive unlimited', included: true },
      { text: 'Layer 3 Execution Package (5/month)', included: true },
      { text: 'Priority support', included: true },
    ],
    cta: 'Scale Up',
    popular: false,
    gradient: 'from-emerald-500 to-teal-600',
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 2500,
    priceLabel: '$2,500+/mo',
    description: 'First-mover advantage + unlimited execution',
    accessWindow: '0+ days (real-time)',
    tier: 'enterprise',
    features: [
      { text: 'Real-time opportunity access', included: true },
      { text: 'All layers unlimited', included: true },
      { text: 'Pay-per-report access (from $25)', included: true },
      { text: 'Layer 2 Deep Dive unlimited', included: true },
      { text: 'Layer 3 Execution Package unlimited', included: true },
      { text: 'Dedicated success manager', included: true },
    ],
    cta: 'Contact Sales',
    popular: false,
    gradient: 'from-amber-500 to-orange-600',
  },
]

const layerDetails = [
  {
    layer: 'Layer 1',
    name: 'Problem Overview',
    access: 'Explorer: $15/unlock | Builder+: Unlimited',
    features: [
      'Problem statement and consumer pain points',
      'Basic market size estimate',
      'Competition level (Low/Medium/High)',
      'Top 3 geographic markets',
      'Source count and validation score',
    ],
  },
  {
    layer: 'Layer 2',
    name: 'Deep Dive Analysis',
    access: 'Scaler+ Only',
    features: [
      'Complete source compilation (all discussions)',
      'TAM/SAM/SOM detailed estimates',
      'Competitive landscape analysis',
      'All geographic markets',
      'Customer acquisition channel recommendations',
      'Pricing strategy insights',
    ],
  },
  {
    layer: 'Layer 3',
    name: 'Execution Package',
    access: 'Scaler: 5/month | Enterprise: Unlimited',
    features: [
      '90-day execution playbook',
      'MVP feature recommendations',
      'Go-to-market timeline',
      'Launch checklist',
      'Initial team structure recommendations',
    ],
  },
]

const reports = [
  { id: 'feasibility', name: 'Feasibility Study', price: 25, priceLabel: '$25', description: 'Quick viability check', consultantPrice: '$1,500-$15,000', icon: Target },
  { id: 'pitch-deck', name: 'Pitch Deck Assistant', price: 79, priceLabel: '$79', description: 'Investor presentation outline', consultantPrice: '$2,000-$5,000', icon: Sparkles },
  { id: 'strategic-assessment', name: 'Strategic Assessment', price: 89, priceLabel: '$89', description: 'SWOT + strategic positioning', consultantPrice: '$2,000-$8,000', icon: Lightbulb },
  { id: 'market-analysis', name: 'Market Analysis', price: 99, priceLabel: '$99', description: 'TAM/SAM/SOM + competitive landscape', consultantPrice: '$5,000-$50,000', icon: TrendingUp },
  { id: 'pestle', name: 'PESTLE Analysis', price: 99, priceLabel: '$99', description: 'Macro-environmental factors affecting your opportunity', consultantPrice: '$5,000-$25,000', icon: Globe },
  { id: 'financials', name: 'Financial Model', price: 129, priceLabel: '$129', description: '5-year projections & unit economics', consultantPrice: '$3,000-$10,000', icon: BarChart3 },
  { id: 'business-plan', name: 'Business Plan', price: 149, priceLabel: '$149', description: 'Comprehensive strategy document', consultantPrice: '$2,000-$5,000', icon: FileText },
]

const bundles = [
  {
    id: 'strategic',
    name: 'Strategic Analysis Bundle',
    price: 229,
    savings: 58,
    description: 'Complete competitive and environmental intelligence',
    includes: ['Market Analysis ($99)', 'PESTLE Analysis ($99)', 'Strategic Assessment ($89)'],
    consultantValue: '$12,000-$83,000',
    popular: true,
  },
  {
    id: 'starter',
    name: 'Starter Bundle',
    price: 329,
    savings: 53,
    description: 'Validation + Pitch (for fundraising)',
    includes: ['Feasibility Study ($25)', 'Business Plan ($149)', 'Financial Model ($129)', 'Pitch Deck ($79)'],
    consultantValue: '$8,500-$35,000',
    popular: false,
  },
  {
    id: 'professional',
    name: 'Professional Bundle',
    price: 549,
    savings: 120,
    description: 'Complete execution package - replaces $30,000+ in consulting',
    includes: ['All 7 reports included ($669 value)', 'Feasibility + Business Plan + Financials', 'Pitch Deck + Market Analysis', 'PESTLE + Strategic Assessment', '30-day email support', 'One revision round per report'],
    consultantValue: '$17,000-$98,000',
    popular: false,
    featured: true,
  },
  {
    id: 'consultant',
    name: 'Consultant License',
    price: 2499,
    savings: 0,
    priceLabel: '$2,499/year',
    description: 'White-label tool for professionals',
    includes: ['Unlimited reports (25 opps/year)', 'White-label branding', 'API access', 'Priority support'],
    consultantValue: '~$12,500 value',
    popular: false,
  },
]

const faqs = [
  {
    question: "What's the difference between subscriptions and reports?",
    answer: "Subscriptions give you ACCESS to opportunity intelligence (discovery). Reports give you EXECUTION tools (turning opportunities into businesses). They're complementary - discover with subscriptions, execute with reports.",
  },
  {
    question: "How does time-based access work?",
    answer: "Opportunities become available to different tiers based on age. Enterprise gets real-time access (0+ days), Scaler gets 8+ day old opportunities, Builder gets 31+ days, and Explorer gets 91+ days. Earlier access = first-mover advantage.",
  },
  {
    question: "Why are your reports so affordable?",
    answer: "AI automation replaces 90% of traditional consulting work. Our Feasibility Study costs $25 vs $1,500-$15K from consultants. You get the same quality analysis in minutes instead of weeks - at a fraction of the cost.",
  },
  {
    question: "Can I purchase reports without a subscription?",
    answer: "Yes! Reports can be purchased for ANY opportunity you have Layer 1 access to. Explorer users can unlock Layer 1 for $15, then purchase any reports they need.",
  },
  {
    question: "What's included in the Strategic Analysis Bundle?",
    answer: "The Strategic Analysis Bundle ($229) includes Market Analysis, PESTLE Analysis, and Strategic Assessment - $287 value with $58 savings. Perfect for comprehensive competitive and environmental intelligence.",
  },
]

export default function Pricing() {
  const { token, isAuthenticated } = useAuthStore()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const autoCheckout = searchParams.get('checkout')
  const [autoCheckoutTriggered, setAutoCheckoutTriggered] = useState(false)

  const [billingLoading, setBillingLoading] = useState<'pro' | 'business' | 'portal' | null>(null)
  const [billingError, setBillingError] = useState<string | null>(null)
  const [billingSuccess, setBillingSuccess] = useState<string | null>(null)
  const [billingSyncing, setBillingSyncing] = useState(false)
  const [subscriptionInfo, setSubscriptionInfo] = useState<null | {
    tier: string
    status: string
    is_active: boolean
    period_end: string | null
  }>(null)

  const [subOpen, setSubOpen] = useState(false)
  const [subClientSecret, setSubClientSecret] = useState<string | null>(null)
  const [subPublishableKey, setSubPublishableKey] = useState<string | null>(null)
  const [subPlanLabel, setSubPlanLabel] = useState<string>('')
  const [enterpriseModalOpen, setEnterpriseModalOpen] = useState(false)
  const [subPendingTier, setSubPendingTier] = useState<'pro' | 'business' | null>(null)
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null)

  async function startSubscription(tier: 'pro' | 'business') {
    if (!token) {
      navigate(`/login?next=${encodeURIComponent('/pricing')}`)
      return
    }
    setBillingError(null)
    setBillingSuccess(null)
    setBillingLoading(tier)
    try {
      const keyRes = await fetch('/api/v1/subscriptions/stripe-key')
      const keyData = await keyRes.json().catch(() => ({}))
      if (!keyRes.ok) throw new Error(keyData?.detail || 'Stripe not configured')

      const res = await fetch('/api/v1/subscriptions/subscription-intent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ tier }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data?.detail || 'Unable to start subscription')
      if (!data?.client_secret) throw new Error('Missing payment client secret')

      setSubPublishableKey(String(keyData.publishable_key))
      setSubClientSecret(String(data.client_secret))
      setSubPlanLabel(tier === 'pro' ? '$99/mo' : '$499/mo')
      setSubPendingTier(tier)
      setSubOpen(true)
    } catch (e) {
      setBillingError(e instanceof Error ? e.message : 'Unable to start subscription')
    } finally {
      setBillingLoading(null)
    }
  }

  const expectedTierLabel = useMemo(() => {
    if (subPendingTier === 'pro') return 'pro'
    if (subPendingTier === 'business') return 'business'
    return null
  }, [subPendingTier])

  async function fetchMySubscription() {
    if (!token) throw new Error('Not authenticated')
    const res = await fetch('/api/v1/subscriptions/my-subscription', { headers: { Authorization: `Bearer ${token}` } })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) throw new Error(data?.detail || 'Failed to load subscription status')
    setSubscriptionInfo({
      tier: String(data?.tier || ''),
      status: String(data?.status || ''),
      is_active: Boolean(data?.is_active),
      period_end: (data?.period_end ? String(data.period_end) : null) as string | null,
    })
    return data as MySubscriptionResponse
  }

  async function confirmSubscriptionPayment(paymentIntentId: string) {
    void paymentIntentId
    setBillingSuccess('Payment confirmed. Syncing your plan…')
    setBillingSyncing(true)
  }

  async function openBillingPortal() {
    if (!token) {
      navigate(`/login?next=${encodeURIComponent('/pricing')}`)
      return
    }
    setBillingError(null)
    setBillingSuccess(null)
    setBillingLoading('portal')
    try {
      const returnUrl = window.location.href
      const res = await fetch('/api/v1/subscriptions/portal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ return_url: returnUrl }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data?.detail || 'Unable to open billing portal')
      if (!data?.url) throw new Error('Portal URL missing')
      window.location.href = String(data.url)
    } catch (e) {
      setBillingError(e instanceof Error ? e.message : 'Unable to open billing portal')
    } finally {
      setBillingLoading(null)
    }
  }

  useEffect(() => {
    if (!isAuthenticated || !token) return
    fetchMySubscription().catch(() => {})
  }, [isAuthenticated, token])

  useEffect(() => {
    if (!autoCheckout || autoCheckoutTriggered || !isAuthenticated || !token) return
    const tier = autoCheckout.toLowerCase()
    if (tier === 'pro' || tier === 'builder') {
      setAutoCheckoutTriggered(true)
      const newParams = new URLSearchParams(searchParams)
      newParams.delete('checkout')
      setSearchParams(newParams, { replace: true })
      startSubscription('pro')
    } else if (tier === 'business' || tier === 'scaler') {
      setAutoCheckoutTriggered(true)
      const newParams = new URLSearchParams(searchParams)
      newParams.delete('checkout')
      setSearchParams(newParams, { replace: true })
      startSubscription('business')
    }
  }, [autoCheckout, autoCheckoutTriggered, isAuthenticated, token, searchParams, setSearchParams])

  useEffect(() => {
    if (!billingSyncing) return
    if (!token) return

    let cancelled = false
    const startedAt = Date.now()
    const timeoutMs = 60_000
    const intervalMs = 3_000

    async function tick() {
      try {
        const res = await fetch('/api/v1/subscriptions/my-subscription', { headers: { Authorization: `Bearer ${token}` } })
        const data = await res.json().catch(() => ({}))
        if (!res.ok) throw new Error(data?.detail || 'Failed to load subscription status')
        if (cancelled) return
        setSubscriptionInfo({
          tier: String(data?.tier || ''),
          status: String(data?.status || ''),
          is_active: Boolean(data?.is_active),
          period_end: (data?.period_end ? String(data.period_end) : null) as string | null,
        })

        if (isExpectedTierActive(data, expectedTierLabel)) {
          setBillingSuccess('Your plan is active.')
          setBillingSyncing(false)
          setSubPendingTier(null)
        } else if (Date.now() - startedAt > timeoutMs) {
          setBillingSuccess('Payment confirmed. Plan sync is taking longer than usual — please refresh in a moment.')
          setBillingSyncing(false)
        }
      } catch (e) {
        if (cancelled) return
        if (Date.now() - startedAt > timeoutMs) {
          setBillingError(e instanceof Error ? e.message : 'Failed to sync subscription status')
          setBillingSyncing(false)
        }
      }
    }

    const id = window.setInterval(tick, intervalMs)
    tick()
    return () => {
      cancelled = true
      window.clearInterval(id)
    }
  }, [billingSyncing, token, expectedTierLabel])

  const handleTierClick = (tier: typeof subscriptionTiers[0]) => {
    if (tier.id === 'explorer') {
      navigate(isAuthenticated ? '/discover' : '/signup')
    } else if (tier.id === 'enterprise') {
      setEnterpriseModalOpen(true)
    } else if (tier.tier === 'pro') {
      if (!isAuthenticated) {
        navigate(`/login?next=${encodeURIComponent('/pricing?plan=builder')}`)
      } else {
        startSubscription('pro')
      }
    } else if (tier.tier === 'business') {
      if (!isAuthenticated) {
        navigate(`/login?next=${encodeURIComponent('/pricing?plan=scaler')}`)
      } else {
        startSubscription('business')
      }
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-100 text-purple-700 rounded-full text-sm font-medium mb-6">
            <Sparkles className="w-4 h-4" />
            Professional Business Intelligence. AI Speed.
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Consultant-Quality Reports at AI Prices
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-6">
            Get a <span className="font-semibold text-purple-600">Feasibility Study for just $25</span>{' '}
            (vs $1,500-15K from traditional consultants).
          </p>
          <p className="text-lg text-gray-500">
            Professional reports from $25-$149. Save 95% compared to consulting firms.
          </p>
        </div>

        {billingError && (
          <div className="mb-10 max-w-3xl mx-auto bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
            {billingError}
          </div>
        )}
        {billingSuccess && (
          <div className="mb-10 max-w-3xl mx-auto bg-green-50 border border-green-200 text-green-800 rounded-xl px-4 py-3 text-sm">
            {billingSuccess}
          </div>
        )}
        {subscriptionInfo && (
          <div className="mb-10 max-w-3xl mx-auto bg-white border border-gray-200 text-gray-700 rounded-xl px-4 py-3 text-sm">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
              <div>
                <span className="font-medium">Current plan:</span>{' '}
                <span className="font-semibold">{subscriptionInfo.tier || '—'}</span>{' '}
                <span className="text-gray-500">({subscriptionInfo.status || '—'})</span>
                {subscriptionInfo.period_end && (
                  <span className="text-gray-500"> • Renews/ends {new Date(subscriptionInfo.period_end).toLocaleDateString()}</span>
                )}
              </div>
              {isAuthenticated && (
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => fetchMySubscription().catch((e) => setBillingError(e instanceof Error ? e.message : 'Failed to refresh'))}
                    className="px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 font-medium"
                    disabled={billingSyncing}
                  >
                    Refresh
                  </button>
                  <button
                    type="button"
                    onClick={openBillingPortal}
                    disabled={billingLoading !== null}
                    className="px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 font-medium disabled:opacity-50"
                  >
                    {billingLoading === 'portal' ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Manage Billing'}
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-20">
          {subscriptionTiers.map((tier) => (
            <div
              key={tier.id}
              className={`relative bg-white rounded-2xl border-2 ${
                tier.popular ? 'border-purple-500 shadow-xl' : 'border-gray-200'
              } overflow-hidden`}
            >
              {tier.popular && (
                <div className="absolute top-0 left-0 right-0 bg-purple-500 text-white text-center text-sm py-1 font-medium">
                  Most Popular
                </div>
              )}
              <div className={`bg-gradient-to-r ${tier.gradient} p-6 text-white ${tier.popular ? 'mt-7' : ''}`}>
                <h3 className="text-xl font-bold">{tier.name}</h3>
                <div className="mt-2">
                  <span className="text-3xl font-bold">{tier.priceLabel}</span>
                </div>
                <p className="text-white/80 text-sm mt-2">{tier.description}</p>
              </div>
              <div className="p-6">
                <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                  <div className="text-xs text-gray-500 uppercase tracking-wider">Access Window</div>
                  <div className="font-medium text-gray-900 flex items-center gap-2">
                    <Clock className="w-4 h-4 text-gray-400" />
                    {tier.accessWindow}
                  </div>
                </div>
                <ul className="space-y-3 mb-6">
                  {tier.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-2">
                      {feature.included ? (
                        <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                      ) : (
                        <X className="w-5 h-5 text-gray-300 flex-shrink-0 mt-0.5" />
                      )}
                      <span className={feature.included ? 'text-gray-700 text-sm' : 'text-gray-400 text-sm'}>
                        {feature.text}
                      </span>
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => handleTierClick(tier)}
                  disabled={billingLoading !== null}
                  className={`block w-full py-3 rounded-lg text-center font-medium transition-colors disabled:opacity-50 ${
                    tier.popular
                      ? 'bg-purple-600 text-white hover:bg-purple-700'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {(billingLoading === 'pro' && tier.tier === 'pro') || (billingLoading === 'business' && tier.tier === 'business') ? (
                    <span className="inline-flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Processing...
                    </span>
                  ) : (
                    tier.cta
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="mb-20">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">What's in Each Layer?</h2>
            <p className="text-gray-600">Progressive intelligence that deepens as you commit</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {layerDetails.map((layer, i) => (
              <div key={i} className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    i === 0 ? 'bg-blue-100 text-blue-600' :
                    i === 1 ? 'bg-purple-100 text-purple-600' :
                    'bg-emerald-100 text-emerald-600'
                  }`}>
                    {i === 0 ? <Lightbulb className="w-5 h-5" /> :
                     i === 1 ? <TrendingUp className="w-5 h-5" /> :
                     <Zap className="w-5 h-5" />}
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">{layer.layer}</div>
                    <div className="font-semibold text-gray-900">{layer.name}</div>
                  </div>
                </div>
                <div className="text-xs text-purple-600 font-medium mb-4 p-2 bg-purple-50 rounded-lg">
                  {layer.access}
                </div>
                <ul className="space-y-2">
                  {layer.features.map((feature, j) => (
                    <li key={j} className="flex items-start gap-2 text-sm text-gray-600">
                      <Check className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="mb-20">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Execution Reports</h2>
            <p className="text-gray-600">Transform opportunities into investor-ready documentation</p>
          </div>

          <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-2xl border border-purple-200 p-8 mb-8">
            <div className="flex flex-col md:flex-row md:items-center gap-6">
              <div className="w-16 h-16 bg-purple-100 rounded-xl flex items-center justify-center flex-shrink-0">
                <Target className="w-8 h-8 text-purple-600" />
              </div>
              <div className="flex-1">
                <div className="text-sm text-purple-600 font-medium">BEST VALUE - START HERE</div>
                <h3 className="text-2xl font-bold text-gray-900">Feasibility Study</h3>
                <p className="text-gray-600">Quick viability check - prove our quality before you invest in the full suite</p>
              </div>
              <div className="text-right">
                <div className="text-4xl font-bold text-purple-600">$25</div>
                <div className="text-sm text-gray-500 line-through">$1,500-$15,000 from consultants</div>
                <div className="text-xs text-purple-500 font-medium">Save 98%+</div>
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            {reports.filter(r => r.id !== 'feasibility').map((report) => (
              <div key={report.id} className="bg-white rounded-xl border border-gray-200 p-5 hover:border-purple-300 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                      <report.icon className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{report.name}</h4>
                      <p className="text-xs text-gray-500">{report.description}</p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-purple-600">{report.priceLabel}</span>
                  <span className="text-xs text-gray-400 line-through">{report.consultantPrice}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mb-20">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Save with Bundles</h2>
            <p className="text-gray-600">Get everything you need at a significant discount</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {bundles.map((bundle) => (
              <div key={bundle.id} className="bg-white rounded-xl border-2 border-gray-200 hover:border-purple-300 transition-colors overflow-hidden">
                <div className="p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-1">{bundle.name}</h3>
                  <p className="text-sm text-gray-500 mb-4">{bundle.description}</p>
                  <div className="flex items-baseline gap-2 mb-4">
                    <span className="text-3xl font-bold text-purple-600">
                      {bundle.priceLabel || `$${bundle.price}`}
                    </span>
                    {bundle.savings > 0 && (
                      <span className="text-sm text-green-600 font-medium">Save ${bundle.savings}</span>
                    )}
                  </div>
                  <div className="text-xs text-gray-400 mb-4">
                    <span className="line-through">{bundle.consultantValue}</span> from consultants
                  </div>
                  <ul className="space-y-2 mb-6">
                    {bundle.includes.map((item, i) => (
                      <li key={i} className="flex items-center gap-2 text-sm text-gray-600">
                        <Check className="w-4 h-4 text-green-500" />
                        {item}
                      </li>
                    ))}
                  </ul>
                  <Link
                    to="/build"
                    className="block w-full py-3 bg-purple-600 text-white rounded-lg text-center font-medium hover:bg-purple-700 transition-colors"
                  >
                    Get {bundle.name}
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mb-20">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Additional Services</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                  <Database className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900">API Access</h3>
                  <p className="text-sm text-gray-500">Integrate OppGrid into your systems</p>
                </div>
              </div>
              <ul className="space-y-2 mb-4">
                <li className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Opportunity data endpoint</span>
                  <span className="font-medium">$0.10/call</span>
                </li>
                <li className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Report generation API</span>
                  <span className="font-medium">$0.50/report</span>
                </li>
                <li className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Bulk data export</span>
                  <span className="font-medium">$99/month</span>
                </li>
              </ul>
              <Link to="/api" className="text-purple-600 hover:text-purple-700 text-sm font-medium">
                View API Documentation →
              </Link>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
                  <Users className="w-6 h-6 text-amber-600" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Leads Marketplace</h3>
                  <p className="text-sm text-gray-500">Connect with verified business leads</p>
                </div>
              </div>
              <ul className="space-y-2 mb-4">
                <li className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Verified business leads</span>
                  <span className="font-medium">$5-$25/lead</span>
                </li>
                <li className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Investor connections</span>
                  <span className="font-medium">$50-$100/intro</span>
                </li>
                <li className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Expert consultations</span>
                  <span className="font-medium">$150-$500/hour</span>
                </li>
              </ul>
              <Link to="/leads" className="text-purple-600 hover:text-purple-700 text-sm font-medium">
                Browse Leads →
              </Link>
            </div>
          </div>
        </div>

        <div className="mb-20">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Frequently Asked Questions</h2>
          </div>
          <div className="max-w-3xl mx-auto space-y-4">
            {faqs.map((faq, i) => (
              <div key={i} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <button
                  onClick={() => setExpandedFaq(expandedFaq === i ? null : i)}
                  className="w-full p-6 text-left flex items-center justify-between"
                >
                  <span className="font-medium text-gray-900">{faq.question}</span>
                  {expandedFaq === i ? (
                    <ChevronUp className="w-5 h-5 text-gray-500" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-500" />
                  )}
                </button>
                {expandedFaq === i && (
                  <div className="px-6 pb-6 text-gray-600">
                    {faq.answer}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl p-8 md:p-12 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
          <p className="text-white/80 mb-8 max-w-2xl mx-auto">
            Browse opportunities and get your first Feasibility Study for just $25. No subscription required.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/opportunities"
              className="px-8 py-3 bg-white text-purple-600 rounded-lg font-medium hover:bg-gray-100 transition-colors"
            >
              Browse Opportunities
            </Link>
            <Link
              to="/build"
              className="px-8 py-3 bg-purple-500 text-white rounded-lg font-medium hover:bg-purple-400 transition-colors border border-white/20"
            >
              See Sample Reports
            </Link>
          </div>
        </div>
      </div>

      {subOpen && subPublishableKey && subClientSecret && (
        <PayPerUnlockModal
          publishableKey={subPublishableKey}
          clientSecret={subClientSecret}
          amountLabel={subPlanLabel}
          contextLabel="Subscription"
          title={`Subscribe for ${subPlanLabel}`}
          confirmLabel="Subscribe"
          footnote="Your plan updates after confirmation (Stripe + webhooks may take a moment)."
          onClose={() => setSubOpen(false)}
          onConfirmed={confirmSubscriptionPayment}
        />
      )}

      {enterpriseModalOpen && (
        <EnterpriseContactModal
          source="pricing"
          onClose={() => setEnterpriseModalOpen(false)}
        />
      )}
    </div>
  )
}

function isExpectedTierActive(raw: unknown, expectedTier: string | null) {
  const obj = (raw && typeof raw === 'object' ? (raw as Record<string, unknown>) : {}) as Record<string, unknown>
  const tier = String(obj.tier ?? '').toLowerCase()
  const isActive = Boolean(obj.is_active)
  if (!expectedTier) return isActive
  return isActive && tier === expectedTier
}
