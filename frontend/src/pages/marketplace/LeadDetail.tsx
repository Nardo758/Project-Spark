import { useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import SimplePage from '../../components/SimplePage'
import { fetchMarketplaceLead } from '../../services/marketplaceApi'
import { useAuthStore } from '../../stores/authStore'

function fmtCents(cents: number) {
  return `$${(cents / 100).toFixed(0)}`
}

export default function LeadDetail() {
  const params = useParams()
  const leadId = Number(params.id)
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

  const query = useQuery({
    queryKey: ['marketplace-lead', leadId],
    enabled: Number.isFinite(leadId),
    queryFn: () => fetchMarketplaceLead(leadId),
  })

  useEffect(() => {
    if (!Number.isFinite(leadId)) return
    // best-effort view tracking; ignore failures
    fetch(`/api/v1/marketplace/leads/${leadId}/view`, { method: 'POST' }).catch(() => {})
  }, [leadId])

  const lead = query.data

  return (
    <SimplePage
      title="Lead details"
      subtitle="Evaluate the anonymized summary and purchase when ready."
      actions={
        <>
          <Link to="/marketplace" className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium">
            Back to marketplace
          </Link>
          <Link to="/cart" className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium">
            Cart
          </Link>
        </>
      }
    >
      {query.isLoading ? (
        <div className="bg-white border border-gray-200 rounded-2xl p-6 text-gray-700">Loading lead…</div>
      ) : null}
      {query.isError ? (
        <div className="bg-white border border-gray-200 rounded-2xl p-6 text-red-700">Failed to load lead.</div>
      ) : null}

      {lead ? (
        <div className="bg-white border border-gray-200 rounded-2xl p-6">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div>
              <div className="text-xs text-gray-500">{lead.public_id}</div>
              <div className="mt-1 text-2xl font-semibold text-gray-900">{lead.public_title}</div>
              <div className="mt-2 text-sm text-gray-700">{lead.anonymized_summary}</div>
              <div className="mt-4 text-sm text-gray-700">
                <span className="font-medium">Price:</span> {fmtCents(lead.lead_price_cents)}
              </div>
            </div>

            <div className="w-full md:w-80 border border-gray-200 rounded-xl p-4 bg-gray-50">
              <div className="text-sm font-semibold text-gray-900">What’s included</div>
              <ul className="mt-2 text-sm text-gray-700 space-y-1">
                <li>• Full contact information</li>
                <li>• Detailed context + notes</li>
                <li>• Any attached docs (when available)</li>
              </ul>

              <div className="mt-4 flex flex-col gap-2">
                <Link to="/cart" className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium text-sm text-center">
                  Add to cart
                </Link>
                {!isAuthenticated ? (
                  <Link to="/signup" className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-white font-medium text-sm text-center">
                    Sign in to purchase
                  </Link>
                ) : null}
                {lead.has_purchased ? (
                  <Link to="/network/inbox" className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-white font-medium text-sm text-center">
                    Message seller (via Network Hub)
                  </Link>
                ) : null}
              </div>
            </div>
          </div>

          {lead.has_purchased && lead.full_data_json ? (
            <div className="mt-6 border-t border-gray-100 pt-6">
              <div className="text-sm font-semibold text-gray-900">Purchased lead data</div>
              <pre className="mt-2 text-xs bg-gray-50 border border-gray-200 rounded-xl p-4 overflow-auto">{lead.full_data_json}</pre>
            </div>
          ) : null}
        </div>
      ) : null}
    </SimplePage>
  )
}

