import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { 
  Users, 
  Mail, 
  Download, 
  Search, 
  Send,
  TrendingUp,
  UserCheck,
  Calendar,
  Loader2,
  AlertCircle,
  CheckCircle,
  Target,
  Globe,
  FileText,
  DollarSign
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import { Navigate } from 'react-router-dom'

type MarketingUser = {
  id: number
  email: string
  name: string
  tier: string
  is_verified: boolean
  is_active: boolean
  created_at: string | null
  oauth_provider: string | null
}

type MarketingStats = {
  total_users: number
  verified_users: number
  new_users_7d: number
  new_users_30d: number
  tier_distribution: Record<string, number>
  oauth_breakdown: Record<string, number>
  verification_rate: number
}

type PlatformStats = {
  validated_ideas: number
  total_market_opportunity: string
  global_markets: number
  reports_generated: number
}

export default function AdminMarketing() {
  const { token, user, isAuthenticated } = useAuthStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [tierFilter, setTierFilter] = useState('')
  const [verifiedOnly, setVerifiedOnly] = useState(false)
  const [selectedUsers, setSelectedUsers] = useState<number[]>([])
  const [showEmailComposer, setShowEmailComposer] = useState(false)
  const [emailSubject, setEmailSubject] = useState('')
  const [emailContent, setEmailContent] = useState('')
  const [campaignStatus, setCampaignStatus] = useState<{ sent?: number; failed?: number; message?: string } | null>(null)

  if (!isAuthenticated || !user?.is_admin) {
    return <Navigate to="/" replace />
  }

  const statsQuery = useQuery({
    queryKey: ['admin-marketing-stats'],
    queryFn: async (): Promise<MarketingStats> => {
      const res = await fetch('/api/v1/admin/marketing/stats', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to load stats')
      return res.json()
    },
  })

  const platformStatsQuery = useQuery({
    queryKey: ['platform-stats'],
    queryFn: async (): Promise<PlatformStats> => {
      const res = await fetch('/api/v1/opportunities/stats/platform')
      if (!res.ok) throw new Error('Failed to load platform stats')
      return res.json()
    },
  })

  const usersQuery = useQuery({
    queryKey: ['admin-marketing-users', { search: searchQuery, tier: tierFilter, verified: verifiedOnly }],
    queryFn: async (): Promise<{ users: MarketingUser[]; total: number }> => {
      const params = new URLSearchParams()
      params.set('limit', '100')
      if (searchQuery) params.set('search', searchQuery)
      if (tierFilter) params.set('tier_filter', tierFilter)
      if (verifiedOnly) params.set('verified_only', 'true')
      
      const res = await fetch(`/api/v1/admin/marketing/users?${params.toString()}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to load users')
      return res.json()
    },
  })

  const sendCampaignMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/v1/admin/marketing/send-campaign', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_ids: selectedUsers,
          subject: emailSubject,
          html_content: emailContent,
        }),
      })
      if (!res.ok) throw new Error('Failed to send campaign')
      return res.json()
    },
    onSuccess: (data) => {
      setCampaignStatus(data)
      setSelectedUsers([])
      setEmailSubject('')
      setEmailContent('')
      setShowEmailComposer(false)
    },
  })

  const handleExportCSV = async () => {
    const params = new URLSearchParams()
    params.set('format', 'csv')
    if (tierFilter) params.set('tier_filter', tierFilter)
    if (verifiedOnly) params.set('verified_only', 'true')
    
    const res = await fetch(`/api/v1/admin/marketing/users/export?${params.toString()}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.ok) {
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'oppgrid_users.csv'
      a.click()
      URL.revokeObjectURL(url)
    }
  }

  const toggleSelectAll = () => {
    if (selectedUsers.length === (usersQuery.data?.users.length || 0)) {
      setSelectedUsers([])
    } else {
      setSelectedUsers(usersQuery.data?.users.map(u => u.id) || [])
    }
  }

  const toggleUser = (id: number) => {
    setSelectedUsers(prev => 
      prev.includes(id) ? prev.filter(uid => uid !== id) : [...prev, id]
    )
  }

  const stats = statsQuery.data
  const platformStats = platformStatsQuery.data
  const users = usersQuery.data?.users || []

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Marketing Dashboard</h1>
          <p className="mt-2 text-gray-600">Manage users and email campaigns</p>
        </div>

        {campaignStatus && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <p className="text-green-800">{campaignStatus.message}</p>
            <button onClick={() => setCampaignStatus(null)} className="ml-auto text-green-600 hover:text-green-800">
              Dismiss
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Users</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.total_users || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-100 rounded-lg">
                <UserCheck className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Verified Users</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.verified_users || 0}</p>
                <p className="text-xs text-gray-400">{stats?.verification_rate || 0}% rate</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">New (7 days)</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.new_users_7d || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-amber-100 rounded-lg">
                <Calendar className="w-6 h-6 text-amber-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">New (30 days)</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.new_users_30d || 0}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Platform Stats Section */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Platform Stats</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-emerald-100 rounded-lg">
                  <Target className="w-6 h-6 text-emerald-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Validated Opportunities</p>
                  <p className="text-2xl font-bold text-gray-900">{platformStats?.validated_ideas ?? 0}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-indigo-100 rounded-lg">
                  <DollarSign className="w-6 h-6 text-indigo-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Market Opportunity</p>
                  <p className="text-2xl font-bold text-gray-900">{platformStats?.total_market_opportunity ?? '$0'}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-cyan-100 rounded-lg">
                  <Globe className="w-6 h-6 text-cyan-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Global Markets</p>
                  <p className="text-2xl font-bold text-gray-900">{platformStats?.global_markets ?? 0}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-rose-100 rounded-lg">
                  <FileText className="w-6 h-6 text-rose-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Reports Generated</p>
                  <p className="text-2xl font-bold text-gray-900">{platformStats?.reports_generated ?? 0}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-4">Tier Distribution</h3>
              <div className="space-y-3">
                {Object.entries(stats.tier_distribution).map(([tier, count]) => (
                  <div key={tier} className="flex items-center justify-between">
                    <span className="capitalize text-gray-700">{tier}</span>
                    <div className="flex items-center gap-3">
                      <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-purple-600 rounded-full"
                          style={{ width: `${(count / stats.total_users) * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-900 w-10 text-right">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-4">Sign-up Method</h3>
              <div className="space-y-3">
                {Object.entries(stats.oauth_breakdown).map(([provider, count]) => (
                  <div key={provider} className="flex items-center justify-between">
                    <span className="capitalize text-gray-700">{provider}</span>
                    <div className="flex items-center gap-3">
                      <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-blue-600 rounded-full"
                          style={{ width: `${(count / stats.total_users) * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-900 w-10 text-right">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <h2 className="text-xl font-semibold text-gray-900">User List</h2>
              
              <div className="flex flex-wrap items-center gap-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search name or email..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                
                <select
                  value={tierFilter}
                  onChange={(e) => setTierFilter(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                >
                  <option value="">All Tiers</option>
                  <option value="free">Free</option>
                  <option value="pro">Pro</option>
                  <option value="business">Business</option>
                  <option value="enterprise">Enterprise</option>
                </select>
                
                <label className="flex items-center gap-2 text-sm text-gray-600">
                  <input
                    type="checkbox"
                    checked={verifiedOnly}
                    onChange={(e) => setVerifiedOnly(e.target.checked)}
                    className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                  />
                  Verified only
                </label>
                
                <button
                  onClick={handleExportCSV}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium"
                >
                  <Download className="w-4 h-4" />
                  Export CSV
                </button>
                
                <button
                  onClick={() => setShowEmailComposer(!showEmailComposer)}
                  disabled={selectedUsers.length === 0}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Mail className="w-4 h-4" />
                  Email Selected ({selectedUsers.length})
                </button>
              </div>
            </div>
          </div>

          {showEmailComposer && selectedUsers.length > 0 && (
            <div className="p-6 bg-purple-50 border-b border-purple-200">
              <h3 className="font-semibold text-purple-900 mb-4">Compose Email Campaign</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                  <input
                    type="text"
                    value={emailSubject}
                    onChange={(e) => setEmailSubject(e.target.value)}
                    placeholder="Email subject line..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Content (HTML supported, use {"{{name}}"} for personalization)
                  </label>
                  <textarea
                    value={emailContent}
                    onChange={(e) => setEmailContent(e.target.value)}
                    placeholder="<p>Hi {{name}},</p><p>Your email content here...</p>"
                    rows={6}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 font-mono text-sm"
                  />
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => sendCampaignMutation.mutate()}
                    disabled={!emailSubject || !emailContent || sendCampaignMutation.isPending}
                    className="flex items-center gap-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium disabled:opacity-50"
                  >
                    {sendCampaignMutation.isPending ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                    Send to {selectedUsers.length} users
                  </button>
                  <button
                    onClick={() => setShowEmailComposer(false)}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left">
                    <input
                      type="checkbox"
                      checked={selectedUsers.length === users.length && users.length > 0}
                      onChange={toggleSelectAll}
                      className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                    />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tier</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sign-up</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {usersQuery.isLoading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <Loader2 className="w-8 h-8 animate-spin mx-auto text-purple-600" />
                    </td>
                  </tr>
                ) : users.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                      No users found
                    </td>
                  </tr>
                ) : (
                  users.map((u) => (
                    <tr key={u.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <input
                          type="checkbox"
                          checked={selectedUsers.includes(u.id)}
                          onChange={() => toggleUser(u.id)}
                          className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                        />
                      </td>
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium text-gray-900">{u.name}</p>
                          <p className="text-sm text-gray-500">{u.email}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          u.tier === 'enterprise' ? 'bg-amber-100 text-amber-800' :
                          u.tier === 'business' ? 'bg-emerald-100 text-emerald-800' :
                          u.tier === 'pro' ? 'bg-purple-100 text-purple-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {u.tier}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          {u.is_verified ? (
                            <span className="flex items-center gap-1 text-green-600 text-sm">
                              <CheckCircle className="w-4 h-4" />
                              Verified
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 text-gray-400 text-sm">
                              <AlertCircle className="w-4 h-4" />
                              Unverified
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 capitalize">
                        {u.oauth_provider || 'email'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {u.created_at ? new Date(u.created_at).toLocaleDateString() : '-'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          
          {usersQuery.data && (
            <div className="px-6 py-4 border-t border-gray-200 text-sm text-gray-500">
              Showing {users.length} of {usersQuery.data.total} users
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
