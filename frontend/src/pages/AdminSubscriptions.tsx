import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  Users, 
  Search, 
  CreditCard,
  Loader2,
  AlertCircle,
  CheckCircle,
  RefreshCw,
  Edit2,
  X,
  Check,
  AlertTriangle
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import { Navigate } from 'react-router-dom'

type SubscriptionUser = {
  id: number
  user_id: number
  email: string
  name: string
  tier: string
  status: string
  stripe_subscription_id: string | null
  stripe_customer_id: string | null
  created_at: string | null
}

const TIERS = ['FREE', 'STARTER', 'GROWTH', 'PRO', 'TEAM', 'BUSINESS', 'ENTERPRISE']

export default function AdminSubscriptions() {
  const { token, user, isAuthenticated } = useAuthStore()
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [tierFilter, setTierFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editTier, setEditTier] = useState('')
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  if (!isAuthenticated || !user?.is_admin) {
    return <Navigate to="/" replace />
  }

  const subscriptionsQuery = useQuery({
    queryKey: ['admin-subscriptions', { search: searchQuery, tier: tierFilter, status: statusFilter }],
    queryFn: async (): Promise<{ subscriptions: SubscriptionUser[]; total: number }> => {
      const params = new URLSearchParams()
      params.set('limit', '100')
      if (tierFilter) params.set('tier_filter', tierFilter.toLowerCase())
      if (statusFilter) params.set('status_filter', statusFilter)
      
      const res = await fetch(`/api/v1/admin/subscriptions?${params.toString()}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to load subscriptions')
      return res.json()
    },
  })

  const updateTierMutation = useMutation({
    mutationFn: async ({ subscriptionId, tier }: { subscriptionId: number; tier: string }) => {
      const res = await fetch(`/api/v1/admin/subscriptions/${subscriptionId}/tier?tier=${tier.toLowerCase()}`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      if (!res.ok) {
        const error = await res.json()
        throw new Error(error.detail || 'Failed to update tier')
      }
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-subscriptions'] })
      setEditingId(null)
      setMessage({ type: 'success', text: 'Subscription tier updated successfully' })
      setTimeout(() => setMessage(null), 3000)
    },
    onError: (error: Error) => {
      setMessage({ type: 'error', text: error.message })
      setTimeout(() => setMessage(null), 5000)
    },
  })

  const bulkResetMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/v1/admin/subscriptions/bulk-reset-invalid', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      if (!res.ok) {
        const error = await res.json()
        throw new Error(error.detail || 'Failed to reset subscriptions')
      }
      return res.json()
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['admin-subscriptions'] })
      setMessage({ type: 'success', text: `Reset ${data.count} subscriptions to FREE` })
      setTimeout(() => setMessage(null), 5000)
    },
    onError: (error: Error) => {
      setMessage({ type: 'error', text: error.message })
      setTimeout(() => setMessage(null), 5000)
    },
  })

  const startEdit = (sub: SubscriptionUser) => {
    setEditingId(sub.id)
    setEditTier(sub.tier.toUpperCase())
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditTier('')
  }

  const saveEdit = (subscriptionId: number) => {
    updateTierMutation.mutate({ subscriptionId, tier: editTier })
  }

  const subscriptions = subscriptionsQuery.data?.subscriptions || []
  
  const filteredSubscriptions = subscriptions.filter(sub => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    return (
      sub.email?.toLowerCase().includes(query) ||
      sub.name?.toLowerCase().includes(query)
    )
  })

  const invalidSubscriptions = subscriptions.filter(
    sub => sub.tier !== 'FREE' && !sub.stripe_subscription_id
  )

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Subscription Management</h1>
          <p className="mt-2 text-gray-600">View and manage user subscriptions</p>
        </div>

        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${
            message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
          }`}>
            {message.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
            {message.text}
          </div>
        )}

        {invalidSubscriptions.length > 0 && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
              <div className="flex-1">
                <h3 className="font-semibold text-yellow-800">
                  {invalidSubscriptions.length} Invalid Subscription{invalidSubscriptions.length > 1 ? 's' : ''} Detected
                </h3>
                <p className="text-sm text-yellow-700 mt-1">
                  These users have paid tiers but no active Stripe subscription. This may be due to incomplete payments.
                </p>
                <button
                  onClick={() => bulkResetMutation.mutate()}
                  disabled={bulkResetMutation.isPending}
                  className="mt-3 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {bulkResetMutation.isPending ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <RefreshCw className="w-4 h-4" />
                  )}
                  Reset All to FREE
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-4 border-b border-gray-200">
            <div className="flex flex-wrap gap-4">
              <div className="flex-1 min-w-[200px]">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Filter by email or name (showing first 100)..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
              </div>
              <select
                value={tierFilter}
                onChange={(e) => setTierFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">All Tiers</option>
                {TIERS.map(tier => (
                  <option key={tier} value={tier}>{tier}</option>
                ))}
              </select>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">All Statuses</option>
                <option value="ACTIVE">Active</option>
                <option value="PAST_DUE">Past Due</option>
                <option value="CANCELED">Canceled</option>
              </select>
              <button
                onClick={() => subscriptionsQuery.refetch()}
                disabled={subscriptionsQuery.isFetching}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2"
              >
                <RefreshCw className={`w-4 h-4 ${subscriptionsQuery.isFetching ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>
          </div>

          {subscriptionsQuery.isLoading ? (
            <div className="p-12 text-center">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-600 mx-auto" />
              <p className="mt-2 text-gray-500">Loading subscriptions...</p>
            </div>
          ) : subscriptionsQuery.isError ? (
            <div className="p-12 text-center text-red-600">
              <AlertCircle className="w-8 h-8 mx-auto mb-2" />
              <p>Failed to load subscriptions</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tier</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stripe ID</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredSubscriptions.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                        No subscriptions found
                      </td>
                    </tr>
                  ) : (
                    filteredSubscriptions.map((sub) => (
                      <tr key={sub.id} className={`hover:bg-gray-50 ${
                        sub.tier !== 'FREE' && !sub.stripe_subscription_id ? 'bg-yellow-50' : ''
                      }`}>
                        <td className="px-4 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                              <Users className="w-4 h-4 text-indigo-600" />
                            </div>
                            <div>
                              <div className="font-medium text-gray-900">{sub.name || 'Unknown'}</div>
                              <div className="text-sm text-gray-500">{sub.email}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-4">
                          {editingId === sub.id ? (
                            <select
                              value={editTier}
                              onChange={(e) => setEditTier(e.target.value)}
                              className="px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500"
                            >
                              {TIERS.map(tier => (
                                <option key={tier} value={tier}>{tier}</option>
                              ))}
                            </select>
                          ) : (
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              sub.tier === 'FREE' ? 'bg-gray-100 text-gray-800' :
                              sub.tier === 'ENTERPRISE' ? 'bg-purple-100 text-purple-800' :
                              sub.tier === 'BUSINESS' ? 'bg-blue-100 text-blue-800' :
                              sub.tier === 'PRO' ? 'bg-indigo-100 text-indigo-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {sub.tier}
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-4">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            sub.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
                            sub.status === 'PAST_DUE' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {sub.status}
                          </span>
                        </td>
                        <td className="px-4 py-4">
                          {sub.stripe_subscription_id ? (
                            <div className="flex items-center gap-2">
                              <CreditCard className="w-4 h-4 text-gray-400" />
                              <span className="text-sm text-gray-600 font-mono">
                                {sub.stripe_subscription_id.slice(0, 20)}...
                              </span>
                            </div>
                          ) : (
                            <span className="text-sm text-gray-400 italic">No Stripe link</span>
                          )}
                        </td>
                        <td className="px-4 py-4">
                          {editingId === sub.id ? (
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => saveEdit(sub.id)}
                                disabled={updateTierMutation.isPending}
                                className="p-1 text-green-600 hover:bg-green-50 rounded"
                              >
                                {updateTierMutation.isPending ? (
                                  <Loader2 className="w-4 h-4 animate-spin" />
                                ) : (
                                  <Check className="w-4 h-4" />
                                )}
                              </button>
                              <button
                                onClick={cancelEdit}
                                className="p-1 text-gray-600 hover:bg-gray-100 rounded"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </div>
                          ) : (
                            <button
                              onClick={() => startEdit(sub)}
                              className="p-1 text-gray-600 hover:bg-gray-100 rounded"
                              title="Edit tier"
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
