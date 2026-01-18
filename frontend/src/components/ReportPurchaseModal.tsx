import { useState, useEffect } from 'react'
import { Loader2, Package, Check, X, Mail } from 'lucide-react'
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

function isValidEmail(email: string): boolean {
  return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)
}

export default function ReportPurchaseModal({
  opportunityId,
  opportunityTitle,
  onClose,
  onPurchased: _onPurchased,
}: Props) {
  void _onPurchased;
  const { token } = useAuthStore()
  const isGuest = !token
  
  const [pricing, setPricing] = useState<{ reports: ReportProduct[]; bundles: Bundle[]; user_tier: string } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedReport, setSelectedReport] = useState<string | null>(null)
  const [selectedBundle, setSelectedBundle] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [paymentError, setPaymentError] = useState<string | null>(null)
  const [guestEmail, setGuestEmail] = useState('')

  useEffect(() => {
    async function fetchPricing() {
      try {
        const headers: Record<string, string> = {}
        if (token) {
          headers.Authorization = `Bearer ${token}`
        }
        const endpoint = token 
          ? `/api/v1/report-pricing/?opportunity_id=${opportunityId}`
          : `/api/v1/report-pricing/public`
        const res = await fetch(endpoint, { headers })
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

  async function handleCheckout() {
    if (isGuest && !isValidEmail(guestEmail)) {
      setPaymentError('Please enter a valid email address')
      return
    }

    setPaymentError(null)
    setSubmitting(true)
    
    try {
      const baseUrl = window.location.origin
      const successUrl = `${baseUrl}/build/reports?purchase=success&opportunity_id=${opportunityId}`
      const cancelUrl = `${baseUrl}/build/reports?purchase=canceled`

      let res
      if (isGuest) {
        if (selectedBundle) {
          res = await fetch('/api/v1/report-pricing/guest-checkout-bundle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              opportunity_id: opportunityId, 
              bundle_type: selectedBundle,
              email: guestEmail,
              success_url: successUrl,
              cancel_url: cancelUrl,
            })
          })
        } else if (selectedReport) {
          res = await fetch('/api/v1/report-pricing/guest-checkout-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              opportunity_id: opportunityId, 
              report_type: selectedReport,
              email: guestEmail,
              success_url: successUrl,
              cancel_url: cancelUrl,
            })
          })
        } else {
          throw new Error('Please select a report or bundle')
        }
      } else {
        if (selectedBundle) {
          res = await fetch('/api/v1/report-pricing/checkout-bundle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
            body: JSON.stringify({ 
              opportunity_id: opportunityId, 
              bundle_type: selectedBundle,
              success_url: successUrl,
              cancel_url: cancelUrl,
            })
          })
        } else if (selectedReport) {
          res = await fetch('/api/v1/report-pricing/checkout-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
            body: JSON.stringify({ 
              opportunity_id: opportunityId, 
              report_type: selectedReport,
              success_url: successUrl,
              cancel_url: cancelUrl,
            })
          })
        } else {
          throw new Error('Please select a report or bundle')
        }
      }
      
      const data = await res?.json().catch(() => ({}))

      if (!res || !res.ok) {
        const errorMessage = data?.detail || data?.message || `Error ${res?.status}: Unable to start checkout`
        throw new Error(errorMessage)
      }
      
      if (data?.url) {
        window.location.href = data.url
      } else {
        throw new Error('No checkout URL returned')
      }
    } catch (e) {
      console.error('Report checkout error:', e)
      setPaymentError(e instanceof Error ? e.message : 'Unable to start checkout')
      setSubmitting(false)
    }
  }

  const selectedPrice = selectedBundle
    ? pricing?.bundles.find(b => b.id === selectedBundle)?.price || 0
    : selectedReport
    ? pricing?.reports.find(r => r.id === selectedReport)?.user_price || 0
    : 0

  if (loading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
        <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-gray-400" />
          <p className="mt-4 text-gray-600">Loading pricing...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
        <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center">
          <p className="text-red-600">{error}</p>
          <button onClick={onClose} className="mt-4 px-4 py-2 bg-gray-100 rounded-lg">
            Close
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="w-full max-w-md rounded-2xl bg-white shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b">
          <div>
            <h2 className="font-semibold text-lg">Purchase Reports</h2>
            {opportunityTitle && (
              <p className="text-sm text-gray-500 truncate max-w-[250px]">{opportunityTitle}</p>
            )}
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-full">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-5 max-h-[60vh] overflow-y-auto">
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Individual Reports</h3>
            <div className="grid gap-2">
              {pricing?.reports.map((report) => (
                <button
                  key={report.id}
                  onClick={() => {
                    if (!report.is_included) {
                      setSelectedReport(report.id)
                      setSelectedBundle(null)
                      setPaymentError(null)
                    }
                  }}
                  disabled={report.is_included || submitting}
                  className={`p-3 text-left rounded-lg border-2 transition-all ${
                    report.is_included
                      ? 'bg-green-50 border-green-200 cursor-default'
                      : selectedReport === report.id
                      ? 'border-purple-500 bg-purple-50'
                      : 'border-gray-200 hover:border-gray-300'
                  } disabled:opacity-60`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="font-medium">{report.name}</span>
                      <p className="text-xs text-gray-500 mt-0.5">{report.description}</p>
                    </div>
                    {report.is_included ? (
                      <span className="flex items-center gap-1 text-green-600 text-sm">
                        <Check className="w-4 h-4" />
                        Included
                      </span>
                    ) : (
                      <span className="font-semibold text-gray-900">{formatPrice(report.user_price)}</span>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Report Bundles</h3>
            <div className="grid gap-2">
              {pricing?.bundles.map((bundle) => (
                <button
                  key={bundle.id}
                  onClick={() => {
                    setSelectedBundle(bundle.id)
                    setSelectedReport(null)
                    setPaymentError(null)
                  }}
                  disabled={submitting}
                  className={`p-3 text-left rounded-lg border-2 transition-all ${
                    selectedBundle === bundle.id
                      ? 'border-purple-500 bg-purple-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="font-medium flex items-center gap-1">
                        <Package className="w-4 h-4" />
                        {bundle.name}
                      </span>
                      <p className="text-xs text-gray-500 mt-0.5">{bundle.description}</p>
                      <p className="text-xs text-green-600 mt-1">Save {bundle.savings}%</p>
                    </div>
                    <span className="font-semibold text-gray-900">{formatPrice(bundle.price)}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {isGuest && (selectedReport || selectedBundle) && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                <Mail className="w-4 h-4 inline-block mr-1" />
                Email Address
              </label>
              <input
                type="email"
                value={guestEmail}
                onChange={(e) => {
                  setGuestEmail(e.target.value)
                  setPaymentError(null)
                }}
                placeholder="Enter your email to receive the report"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-sm"
              />
              <p className="text-xs text-gray-500 mt-1">
                Your report will be delivered to this email after purchase.
              </p>
            </div>
          )}

          {paymentError && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {paymentError}
            </div>
          )}

          <div className="flex gap-2 justify-end">
            <button
              onClick={onClose}
              disabled={submitting}
              className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg"
            >
              Cancel
            </button>
            <button
              onClick={handleCheckout}
              disabled={(!selectedReport && !selectedBundle) || submitting || (isGuest && !isValidEmail(guestEmail))}
              className="px-4 py-2 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Processing...
                </>
              ) : (
                <>Checkout {selectedPrice > 0 && formatPrice(selectedPrice)}</>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
