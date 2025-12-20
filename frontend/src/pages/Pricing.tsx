import { useEffect, useMemo, useState } from 'react'
import { Check, Loader2 } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import PayPerUnlockModal from '../components/PayPerUnlockModal'
import EnterpriseContactModal from '../components/EnterpriseContactModal'

const plans = [
  {
    name: 'Explorer',
    price: '$0',
    period: '/month',
    description: 'Start free and browse the archive',
    features: [
      'Browse 91+ day opportunities (Archive)',
      'Basic search & filters',
      'Save opportunities',
      'Pay‑per‑unlock ($15 / opportunity)',
    ],
    cta: 'Get Started',
    highlighted: false,
  },
  {
    name: 'Builder',
    price: '$99',
    period: '/month',
    description: 'Early access + AI co-founder basics',
    features: [
      'Unlimited access to 31+ day opportunities (Validated)',
      'Preview 8–30 day opportunities (Fresh)',
      'AI Co‑founder (Basic)',
      'Deep Dive add‑on ($49 / opportunity)',
      'CSV export + advanced filters',
    ],
    cta: 'Start Free Trial',
    highlighted: true,
    badge: 'Most Popular',
  },
  {
    name: 'Scaler',
    price: '$499',
    period: '/month',
    description: 'Full access to Fresh + deeper intelligence',
    features: [
      'Full access to 8+ day opportunities (Fresh)',
      'Full Layer 1 & 2 on all accessible opportunities',
      'Fast Pass ($99) for HOT 0–7 day opportunities',
      'Team-ready exports & reporting',
      'API access (coming soon)',
    ],
    cta: 'Get Scaler',
    highlighted: false,
  },
]

export default function Pricing() {
  const { token, isAuthenticated } = useAuthStore()
  const navigate = useNavigate()

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

  async function startSubscription(tier: 'pro' | 'business') {
    if (!token) {
      navigate(`/login?next=${encodeURIComponent('/pricing')}`)
      return
    }
    setBillingError(null)
    setBillingSuccess(null)
    setBillingLoading(tier)
    try {
      // 1) Stripe publishable key (public endpoint)
      const keyRes = await fetch('/api/v1/subscriptions/stripe-key')
      const keyData = await keyRes.json().catch(() => ({}))
      if (!keyRes.ok) throw new Error(keyData?.detail || 'Stripe not configured')

      // 2) Create subscription PaymentIntent (in-app Elements modal)
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
    return data as any
  }

  async function confirmSubscriptionPayment(_paymentIntentId: string) {
    // Start polling for webhook reconciliation
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
    // Keep a snapshot of current subscription for signed-in users.
    if (!isAuthenticated || !token) return
    fetchMySubscription().catch(() => {
      // ignore initial load errors; user might not have billing set up yet
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, token])

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
        // Keep polling; intermittent failures happen during deploys.
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

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Simple, Transparent Pricing</h1>
        <p className="text-xl text-gray-600">Start for free, upgrade as you grow. Cancel anytime.</p>
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
              {subscriptionInfo.period_end ? (
                <span className="text-gray-500"> • Renews/ends {new Date(subscriptionInfo.period_end).toLocaleDateString()}</span>
              ) : null}
            </div>
            {isAuthenticated && (
              <button
                type="button"
                onClick={() => fetchMySubscription().catch((e) => setBillingError(e instanceof Error ? e.message : 'Failed to refresh'))}
                className="px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 font-medium"
                disabled={billingSyncing}
              >
                Refresh
              </button>
            )}
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-3 gap-8 mb-16">
        {plans.map((plan) => (
          <div
            key={plan.name}
            className={`relative rounded-2xl p-8 ${
              plan.highlighted
                ? 'bg-gray-900 text-white ring-4 ring-gray-900'
                : 'bg-white border border-gray-200'
            }`}
          >
            {plan.badge && (
              <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                <span className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                  {plan.badge}
                </span>
              </div>
            )}
            <div className="mb-6">
              <h2 className={`text-2xl font-bold ${plan.highlighted ? 'text-white' : 'text-gray-900'}`}>
                {plan.name}
              </h2>
              <div className="mt-4 flex items-baseline">
                <span className={`text-4xl font-bold ${plan.highlighted ? 'text-white' : 'text-gray-900'}`}>
                  {plan.price}
                </span>
                {plan.period && (
                  <span className={`ml-1 ${plan.highlighted ? 'text-gray-300' : 'text-gray-500'}`}>
                    {plan.period}
                  </span>
                )}
              </div>
              <p className={`mt-2 ${plan.highlighted ? 'text-gray-300' : 'text-gray-600'}`}>
                {plan.description}
              </p>
            </div>
            <ul className="space-y-4 mb-8">
              {plan.features.map((feature) => (
                <li key={feature} className="flex items-start gap-3">
                  <Check className={`w-5 h-5 flex-shrink-0 ${plan.highlighted ? 'text-green-400' : 'text-green-500'}`} />
                  <span className={plan.highlighted ? 'text-gray-300' : 'text-gray-600'}>
                    {feature}
                  </span>
                </li>
              ))}
            </ul>
            {plan.name === 'Explorer' ? (
              <Link
                to={isAuthenticated ? '/discover' : '/signup'}
                className={`block w-full text-center py-3 rounded-lg font-medium ${
                  plan.highlighted
                    ? 'bg-white text-gray-900 hover:bg-gray-100'
                    : 'bg-gray-900 text-white hover:bg-gray-800'
                }`}
              >
                {isAuthenticated ? 'Browse opportunities' : plan.cta}
              </Link>
            ) : plan.name === 'Builder' ? (
              <button
                type="button"
                onClick={() => {
                  if (!isAuthenticated) {
                    navigate(`/login?next=${encodeURIComponent('/pricing?plan=builder')}`)
                  } else {
                    startSubscription('pro')
                  }
                }}
                disabled={billingLoading !== null}
                className={`block w-full text-center py-3 rounded-lg font-medium disabled:opacity-50 ${
                  plan.highlighted
                    ? 'bg-white text-gray-900 hover:bg-gray-100'
                    : 'bg-gray-900 text-white hover:bg-gray-800'
                }`}
              >
                {billingLoading === 'pro' ? (
                  <span className="inline-flex items-center justify-center gap-2">
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Starting payment…
                  </span>
                ) : (
                  plan.cta
                )}
              </button>
            ) : (
              <button
                type="button"
                onClick={() => {
                  if (!isAuthenticated) {
                    navigate(`/login?next=${encodeURIComponent('/pricing?plan=scaler')}`)
                  } else {
                    startSubscription('business')
                  }
                }}
                disabled={billingLoading !== null}
                className={`block w-full text-center py-3 rounded-lg font-medium disabled:opacity-50 ${
                  plan.highlighted
                    ? 'bg-white text-gray-900 hover:bg-gray-100'
                    : 'bg-gray-900 text-white hover:bg-gray-800'
                }`}
              >
                {billingLoading === 'business' ? (
                  <span className="inline-flex items-center justify-center gap-2">
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Starting payment…
                  </span>
                ) : (
                  plan.cta
                )}
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="mt-16 text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">One‑time unlock options</h3>
        <div className="inline-flex gap-4 flex-wrap justify-center">
          <div className="bg-white border border-gray-200 rounded-lg px-6 py-3">
            <span className="text-gray-600">Archive:</span>
            <span className="ml-2 font-bold text-gray-900">$15</span>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg px-6 py-3">
            <span className="text-gray-600">Deep Dive add‑on:</span>
            <span className="ml-2 font-bold text-gray-900">$49</span>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg px-6 py-3">
            <span className="text-gray-600">Fast Pass:</span>
            <span className="ml-2 font-bold text-gray-900">$99</span>
          </div>
        </div>
        <div className="mt-6 text-sm text-gray-600">
          Need earliest access (HOT 0–7 days)?{' '}
          <button
            type="button"
            onClick={() => setEnterpriseModalOpen(true)}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Contact sales for Enterprise
          </button>
          .
        </div>
        {isAuthenticated && (
          <div className="mt-4">
            <button
              type="button"
              onClick={openBillingPortal}
              disabled={billingLoading !== null}
              className="px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 font-medium disabled:opacity-50"
            >
              {billingLoading === 'portal' ? (
                <span className="inline-flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Opening billing portal…
                </span>
              ) : (
                'Manage billing'
              )}
            </button>
          </div>
        )}
        {!isAuthenticated && (
          <div className="mt-4 text-sm text-gray-600">
            To subscribe,{' '}
            <Link className="text-blue-600 hover:text-blue-700 font-medium" to={`/login?next=${encodeURIComponent('/pricing')}`}>
              sign in
            </Link>
            .
          </div>
        )}
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

function isExpectedTierActive(raw: any, expectedTier: string | null) {
  const tier = String(raw?.tier || '').toLowerCase()
  const isActive = Boolean(raw?.is_active)
  if (!expectedTier) return isActive
  return isActive && tier === expectedTier
}

