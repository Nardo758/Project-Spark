import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import SimplePage from '../../components/SimplePage'
import { useAuthStore } from '../../stores/authStore'

type Purchase = {
  id: number
  lead_id: number
  buyer_id: number
  payment_status: string
  amount_paid_cents: number
  purchased_at?: string | null
}

function fmtCents(cents: number) {
  return `$${(cents / 100).toFixed(0)}`
}

export default function MarketplaceDashboard() {
  const token = useAuthStore((s) => s.token)

  const purchasesQuery = useQuery({
    queryKey: ['marketplace-me-purchases'],
    enabled: Boolean(token),
    queryFn: async () => {
      const res = await fetch('/api/v1/marketplace/me/purchases', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to load purchases')
      const data = (await res.json()) as { purchases: Purchase[] }
      return data.purchases
    },
  })

  return (
    <SimplePage title="Lead dashboard" subtitle="Manage purchased leads and saved searches (MVP placeholder).">
      {purchasesQuery.isLoading ? (
        <div className="bg-white border border-gray-200 rounded-2xl p-6 text-gray-700">Loading…</div>
      ) : null}
      {purchasesQuery.isError ? (
        <div className="bg-white border border-gray-200 rounded-2xl p-6 text-red-700">Failed to load purchases.</div>
      ) : null}

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 bg-white border border-gray-200 rounded-2xl p-6">
          <div className="text-sm font-semibold text-gray-900">Recent purchases</div>
          <div className="mt-4 space-y-3">
            {(purchasesQuery.data ?? []).slice(0, 8).map((p) => (
              <div key={p.id} className="flex items-center justify-between gap-4 border border-gray-200 rounded-xl p-4">
                <div>
                  <div className="text-sm font-medium text-gray-900">Lead #{p.lead_id}</div>
                  <div className="text-xs text-gray-500">Status: {p.payment_status}</div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="text-sm font-semibold text-gray-900">{fmtCents(p.amount_paid_cents)}</div>
                  <Link to={`/marketplace/lead/${p.lead_id}`} className="px-3 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium text-sm">
                    View
                  </Link>
                </div>
              </div>
            ))}
            {purchasesQuery.data && purchasesQuery.data.length === 0 ? (
              <div className="text-sm text-gray-600">No purchases yet.</div>
            ) : null}
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-2xl p-6">
          <div className="text-sm font-semibold text-gray-900">Quick actions</div>
          <div className="mt-4 flex flex-col gap-2">
            <Link to="/marketplace" className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium text-sm text-center">
              Browse marketplace
            </Link>
            <Link to="/pricing" className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium text-sm text-center">
              Upgrade
            </Link>
          </div>
        </div>
      </div>
    </SimplePage>
  )
}

