import { useMemo, useState, useEffect } from 'react'
import { Elements, CardElement, useElements, useStripe } from '@stripe/react-stripe-js'
import { loadStripe } from '@stripe/stripe-js'
import { Loader2, Package, Check } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

type ReportProduct = {
  id: string
  name: string
  description: string
  price: number
  is_included: boolean
  user_price: number
}

type Bundle = {
  id: string
  name: string
  description: string
  price: number
  reports: string[]
  savings: number
}

type Props = {
  opportunityId: number
  opportunityTitle?: string
  onClose: () => void
  onPurchased: () => void
}

function formatPrice(cents: number): string {
  return `$${(cents / 100).toFixed(0)}`
}

function ReportPurchaseInner({
  opportunityId,
  opportunityTitle,
  onClose,
  onPurchased,
}: Props) {
  const stripe = useStripe()
  const elements = useElements()
  const { token } = useAuthStore()
  
  const [pricing, setPricing] = useState<{ reports: ReportProduct[]; bundles: Bundle[]; user_tier: string } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedReport, setSelectedReport] = useState<string | null>(null)
  const [selectedBundle, setSelectedBundle] = useState<string | null>(null)
  const [paymentMode, setPaymentMode] = useState(false)
  const [clientSecret, setClientSecret] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [paymentError, setPaymentError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchPricing() {
      try {
        const res = await fetch(`/api/v1/report-pricing/?opportunity_id=${opportunityId}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (!res.ok) throw new Error('Failed to fetch pricing')
        const data = await res.json()
        setPricing(data)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to load pricing')
      } finally {
        setLoading(false)
      }
    }
    fetchPricing()
  }, [opportunityId, token])

  async function startPurchase() {
    setPaymentError(null)
    setSubmitting(true)
    
    try {
      let res
      if (selectedBundle) {
        res = await fetch('/api/v1/report-pricing/purchase-bundle', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
          body: JSON.stringify({ opportunity_id: opportunityId, bundle_type: selectedBundle })
        })
      } else if (selectedReport) {
        res = await fetch('/api/v1/report-pricing/purchase-report', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
          body: JSON.stringify({ opportunity_id: opportunityId, report_type: selectedReport })
        })
      }
      
      if (!res || !res.ok) {
        const data = await res?.json().catch(() => ({}))
        throw new Error(data?.detail || 'Failed to create payment')
      }
      
      const data = await res.json()
      setClientSecret(data.client_secret)
      setPaymentMode(true)
    } catch (e) {
      setPaymentError(e instanceof Error ? e.message : 'Payment failed')
    } finally {
      setSubmitting(false)
    }
  }

  async function confirmPayment() {
    setPaymentError(null)
    if (!stripe || !elements || !clientSecret) return
    
    const card = elements.getElement(CardElement)
    if (!card) return
    
    try {
      setSubmitting(true)
      const result = await stripe.confirmCardPayment(clientSecret, {
        payment_method: { card }
      })
      
      if (result.error) {
        setPaymentError(result.error.message || 'Payment failed')
        return
      }
      
      const pi = result.paymentIntent
      if (!pi || (pi.status !== 'succeeded' && pi.status !== 'processing')) {
        setPaymentError(`Payment not completed (status: ${pi?.status || 'unknown'})`)
        return
      }
      
      const confirmRes = await fetch('/api/v1/report-pricing/confirm-report-purchase', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ payment_intent_id: pi.id })
      })
      
      if (!confirmRes.ok) {
        const data = await confirmRes.json().catch(() => ({}))
        throw new Error(data?.detail || 'Failed to confirm purchase')
      }
      
      onPurchased()
      onClose()
    } catch (e) {
      setPaymentError(e instanceof Error ? e.message : 'Payment confirmation failed')
    } finally {
      setSubmitting(false)
    }
  }

  const selectedPrice = useMemo(() => {
    if (selectedBundle && pricing) {
      const bundle = pricing.bundles.find(b => b.id === selectedBundle)
      return bundle?.price || 0
    }
    if (selectedReport && pricing) {
      const report = pricing.reports.find(r => r.id === selectedReport)
      return report?.user_price || 0
    }
    return 0
  }, [selectedBundle, selectedReport, pricing])

  if (loading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
        <div className="w-full max-w-2xl rounded-2xl bg-white p-8 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-gray-400" />
          <p className="mt-4 text-gray-600">Loading pricing...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
        <div className="w-full max-w-md rounded-2xl bg-white p-6">
          <p className="text-red-600">{error}</p>
          <button onClick={onClose} className="mt-4 px-4 py-2 bg-gray-100 rounded-lg">Close</button>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 overflow-y-auto py-8">
      <div className="w-full max-w-2xl rounded-2xl bg-white border border-gray-200 shadow-xl">
        <div className="p-5 border-b border-gray-200 flex items-center justify-between">
          <div>
            <div className="text-sm text-gray-500">Execution Reports</div>
            <div className="text-lg font-semibold text-gray-900">
              {opportunityTitle ? `Reports for: ${opportunityTitle}` : 'Purchase Reports'}
            </div>
          </div>
          <button onClick={onClose} className="px-3 py-2 text-gray-600 hover:text-gray-900">
            ✕
          </button>
        </div>

        <div className="p-5">
          {!paymentMode ? (
            <>
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Individual Reports</h3>
                <div className="grid gap-2">
                  {pricing?.reports.map((report) => (
                    <button
                      key={report.id}
                      onClick={() => { setSelectedReport(report.id); setSelectedBundle(null); }}
                      disabled={report.is_included}
                      className={`p-3 rounded-lg border text-left flex items-center justify-between transition-all ${
                        selectedReport === report.id
                          ? 'border-black bg-gray-50'
                          : report.is_included
                          ? 'border-green-200 bg-green-50 opacity-75'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div>
                        <div className="font-medium text-gray-900">{report.name}</div>
                        <div className="text-sm text-gray-500">{report.description}</div>
                      </div>
                      <div className="text-right">
                        {report.is_included ? (
                          <span className="flex items-center gap-1 text-green-600 text-sm">
                            <Check className="w-4 h-4" /> Included
                          </span>
                        ) : (
                          <span className="font-semibold text-gray-900">{formatPrice(report.price)}</span>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                  <Package className="w-4 h-4" /> Bundles (Save More)
                </h3>
                <div className="grid gap-2">
                  {pricing?.bundles.filter(b => b.id !== 'consultant_license').map((bundle) => (
                    <button
                      key={bundle.id}
                      onClick={() => { setSelectedBundle(bundle.id); setSelectedReport(null); }}
                      className={`p-4 rounded-lg border text-left transition-all ${
                        selectedBundle === bundle.id
                          ? 'border-black bg-gray-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-semibold text-gray-900">{bundle.name}</div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-green-600">Save {formatPrice(bundle.savings)}</span>
                          <span className="font-bold text-gray-900">{formatPrice(bundle.price)}</span>
                        </div>
                      </div>
                      <div className="text-sm text-gray-500">{bundle.description}</div>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {bundle.reports.map((r) => (
                          <span key={r} className="text-xs bg-gray-100 px-2 py-0.5 rounded">
                            {pricing?.reports.find(rep => rep.id === r)?.name || r}
                          </span>
                        ))}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {paymentError && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                  {paymentError}
                </div>
              )}

              <div className="flex gap-2 justify-end">
                <button
                  onClick={onClose}
                  className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={startPurchase}
                  disabled={(!selectedReport && !selectedBundle) || submitting}
                  className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium disabled:opacity-50"
                >
                  {submitting ? (
                    <span className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" /> Processing...
                    </span>
                  ) : selectedPrice > 0 ? (
                    `Continue to Payment (${formatPrice(selectedPrice)})`
                  ) : (
                    'Select a Report'
                  )}
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500 mb-1">You're purchasing:</div>
                <div className="font-semibold text-gray-900">
                  {selectedBundle 
                    ? pricing?.bundles.find(b => b.id === selectedBundle)?.name 
                    : pricing?.reports.find(r => r.id === selectedReport)?.name}
                </div>
                <div className="text-lg font-bold mt-1">{formatPrice(selectedPrice)}</div>
              </div>

              <div className="mb-4">
                <div className="text-sm text-gray-600 mb-2">Enter your card details:</div>
                <div className="border border-gray-200 rounded-lg p-3">
                  <CardElement options={{ hidePostalCode: true }} />
                </div>
              </div>

              {paymentError && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                  {paymentError}
                </div>
              )}

              <div className="flex gap-2 justify-end">
                <button
                  onClick={() => { setPaymentMode(false); setClientSecret(null); }}
                  className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium"
                  disabled={submitting}
                >
                  Back
                </button>
                <button
                  onClick={confirmPayment}
                  disabled={submitting || !stripe || !elements}
                  className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium disabled:opacity-50"
                >
                  {submitting ? (
                    <span className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" /> Processing...
                    </span>
                  ) : (
                    `Pay ${formatPrice(selectedPrice)}`
                  )}
                </button>
              </div>

              <div className="mt-4 text-xs text-gray-500">
                Your report will be available immediately after payment.
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default function ReportPurchaseModal(props: Props) {
  const { token } = useAuthStore()
  const [publishableKey, setPublishableKey] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    async function fetchKey() {
      try {
        const res = await fetch('/api/v1/subscriptions/stripe-key')
        const data = await res.json()
        setPublishableKey(data.publishable_key)
      } catch (e) {
        console.error('Failed to fetch Stripe key:', e)
      } finally {
        setLoading(false)
      }
    }
    fetchKey()
  }, [])

  if (loading || !publishableKey) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
        <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-gray-400" />
          <p className="mt-4 text-gray-600">Loading payment system...</p>
        </div>
      </div>
    )
  }

  const stripePromise = loadStripe(publishableKey)

  return (
    <Elements stripe={stripePromise}>
      <ReportPurchaseInner {...props} />
    </Elements>
  )
}
