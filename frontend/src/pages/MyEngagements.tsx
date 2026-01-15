import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  MessageSquare, Clock, CheckCircle, XCircle, Loader2,
  User, Calendar, DollarSign, ChevronRight, ArrowLeft, Send,
  FileText, Star, Briefcase
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import ReviewModal from '../components/ReviewModal'

type EngagementStatus = 'request_sent' | 'proposal_sent' | 'negotiating' | 'accepted' | 'in_progress' | 'paused' | 'completed' | 'declined' | 'cancelled'

type Engagement = {
  id: number
  user_id: number
  expert_profile_id: number
  engagement_type: string
  status: EngagementStatus
  title: string
  description: string | null
  request_message: string | null
  proposal_message: string | null
  proposed_amount_cents: number | null
  final_amount_cents: number | null
  created_at: string
  expert_name: string | null
  expert_title: string | null
  expert_avatar: string | null
  is_reviewed: boolean
}

type EngagementDetail = Engagement & {
  scope_of_work: string | null
  shared_materials: string[]
  proposed_scope: string | null
  proposed_duration_days: number | null
  platform_fee_cents: number | null
  preferred_start_date: string | null
  actual_start_date: string | null
  expected_end_date: string | null
  permission_level: string
}

type Message = {
  id: number
  engagement_id: number
  sender_id: number
  content: string
  attachments: string[]
  is_read: boolean
  is_ai_suggestion: boolean
  created_at: string
  sender_name: string | null
}

function formatCents(cents: number | null): string {
  if (!cents) return '--'
  return `$${(cents / 100).toLocaleString()}`
}

function formatDate(date: string | null): string {
  if (!date) return '--'
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

function getStatusBadge(status: EngagementStatus) {
  const statusStyles: Record<EngagementStatus, { bg: string; text: string; icon: React.ReactNode; label: string }> = {
    request_sent: { bg: 'bg-amber-50', text: 'text-amber-700', icon: <Clock className="w-3 h-3" />, label: 'Request Sent' },
    proposal_sent: { bg: 'bg-blue-50', text: 'text-blue-700', icon: <FileText className="w-3 h-3" />, label: 'Proposal Received' },
    negotiating: { bg: 'bg-indigo-50', text: 'text-indigo-700', icon: <MessageSquare className="w-3 h-3" />, label: 'Negotiating' },
    accepted: { bg: 'bg-emerald-50', text: 'text-emerald-700', icon: <CheckCircle className="w-3 h-3" />, label: 'Accepted' },
    in_progress: { bg: 'bg-purple-50', text: 'text-purple-700', icon: <Briefcase className="w-3 h-3" />, label: 'In Progress' },
    paused: { bg: 'bg-yellow-50', text: 'text-yellow-700', icon: <Clock className="w-3 h-3" />, label: 'Paused' },
    completed: { bg: 'bg-green-50', text: 'text-green-700', icon: <CheckCircle className="w-3 h-3" />, label: 'Completed' },
    declined: { bg: 'bg-red-50', text: 'text-red-700', icon: <XCircle className="w-3 h-3" />, label: 'Declined' },
    cancelled: { bg: 'bg-stone-50', text: 'text-stone-500', icon: <XCircle className="w-3 h-3" />, label: 'Cancelled' }
  }
  const style = statusStyles[status] || statusStyles.request_sent
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${style.bg} ${style.text}`}>
      {style.icon}
      {style.label}
    </span>
  )
}

function getEngagementTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    consultation: 'Consultation',
    project: 'Project',
    retainer: 'Retainer',
    hourly: 'Hourly',
    equity_partnership: 'Equity Partnership'
  }
  return labels[type] || type
}

export default function MyEngagements() {
  const { token, isAuthenticated } = useAuthStore()
  const queryClient = useQueryClient()
  const [selectedEngagement, setSelectedEngagement] = useState<number | null>(null)
  const [messageInput, setMessageInput] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [showReviewModal, setShowReviewModal] = useState(false)

  const { data: engagements, isLoading } = useQuery({
    queryKey: ['my-engagements', filterStatus],
    enabled: isAuthenticated,
    queryFn: async (): Promise<Engagement[]> => {
      const params = new URLSearchParams()
      if (filterStatus !== 'all') params.append('status', filterStatus)
      const res = await fetch(`/api/v1/expert-network/engagements${params.toString() ? '?' + params : ''}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) throw new Error('Failed to load engagements')
      return res.json()
    }
  })

  const { data: engagementDetail } = useQuery({
    queryKey: ['engagement-detail', selectedEngagement],
    enabled: !!selectedEngagement,
    queryFn: async (): Promise<EngagementDetail> => {
      const res = await fetch(`/api/v1/expert-network/engagements/${selectedEngagement}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) throw new Error('Failed to load engagement')
      return res.json()
    }
  })

  const { data: messages, refetch: refetchMessages } = useQuery({
    queryKey: ['engagement-messages', selectedEngagement],
    enabled: !!selectedEngagement,
    queryFn: async (): Promise<Message[]> => {
      const res = await fetch(`/api/v1/expert-network/engagements/${selectedEngagement}/messages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) return []
      return res.json()
    }
  })

  const sendMessageMutation = useMutation({
    mutationFn: async (content: string) => {
      const res = await fetch(`/api/v1/expert-network/engagements/${selectedEngagement}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ content })
      })
      if (!res.ok) throw new Error('Failed to send message')
      return res.json()
    },
    onSuccess: () => {
      setMessageInput('')
      refetchMessages()
    }
  })

  const acceptProposalMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch(`/api/v1/expert-network/engagements/${selectedEngagement}/accept`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) throw new Error('Failed to accept proposal')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['engagement-detail', selectedEngagement] })
      queryClient.invalidateQueries({ queryKey: ['my-engagements'] })
    }
  })

  const declineEngagementMutation = useMutation({
    mutationFn: async (reason: string) => {
      const params = new URLSearchParams()
      if (reason) params.append('reason', reason)
      const url = `/api/v1/expert-network/engagements/${selectedEngagement}/decline${params.toString() ? '?' + params : ''}`
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) throw new Error('Failed to decline')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-engagements'] })
      setSelectedEngagement(null)
    }
  })

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="text-center">
          <User className="w-16 h-16 text-stone-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-stone-900 mb-2">Sign in to view your engagements</h2>
          <Link to="/login" className="text-purple-600 font-medium hover:text-purple-700">
            Sign in
          </Link>
        </div>
      </div>
    )
  }

  if (selectedEngagement && engagementDetail) {
    return (
      <div className="min-h-screen bg-stone-50">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <button
            onClick={() => setSelectedEngagement(null)}
            className="flex items-center gap-2 text-stone-600 hover:text-stone-900 mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to engagements
          </button>

          <div className="bg-white rounded-2xl border border-stone-200 overflow-hidden">
            <div className="p-6 border-b border-stone-100">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                  {engagementDetail.expert_avatar ? (
                    <img src={engagementDetail.expert_avatar} alt="" className="w-14 h-14 rounded-full object-cover" />
                  ) : (
                    <div className="w-14 h-14 rounded-full bg-gradient-to-br from-purple-400 to-indigo-500 flex items-center justify-center text-white font-bold text-lg">
                      {(engagementDetail.expert_name || 'E').charAt(0)}
                    </div>
                  )}
                  <div>
                    <h1 className="text-xl font-bold text-stone-900">{engagementDetail.title}</h1>
                    <p className="text-stone-600">{engagementDetail.expert_name || 'Expert'}</p>
                    <p className="text-sm text-purple-600">{engagementDetail.expert_title}</p>
                  </div>
                </div>
                {getStatusBadge(engagementDetail.status)}
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
                <div className="bg-stone-50 rounded-lg p-3">
                  <p className="text-xs text-stone-500 mb-1">Type</p>
                  <p className="font-medium text-stone-900">{getEngagementTypeLabel(engagementDetail.engagement_type)}</p>
                </div>
                <div className="bg-stone-50 rounded-lg p-3">
                  <p className="text-xs text-stone-500 mb-1">Started</p>
                  <p className="font-medium text-stone-900">{formatDate(engagementDetail.created_at)}</p>
                </div>
                <div className="bg-stone-50 rounded-lg p-3">
                  <p className="text-xs text-stone-500 mb-1">Amount</p>
                  <p className="font-medium text-emerald-600">{formatCents(engagementDetail.final_amount_cents || engagementDetail.proposed_amount_cents)}</p>
                </div>
                <div className="bg-stone-50 rounded-lg p-3">
                  <p className="text-xs text-stone-500 mb-1">Access Level</p>
                  <p className="font-medium text-stone-900 capitalize">{engagementDetail.permission_level}</p>
                </div>
              </div>
            </div>

            {engagementDetail.status === 'proposal_sent' && (
              <div className="p-6 bg-blue-50 border-b border-blue-100">
                <div className="flex items-start gap-4">
                  <FileText className="w-6 h-6 text-blue-600 flex-shrink-0" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-blue-900 mb-2">Expert Proposal</h3>
                    <p className="text-blue-800 text-sm mb-3">{engagementDetail.proposal_message}</p>
                    {engagementDetail.proposed_scope && (
                      <p className="text-blue-700 text-sm mb-3"><strong>Scope:</strong> {engagementDetail.proposed_scope}</p>
                    )}
                    <div className="flex items-center gap-4 mt-4">
                      <div className="bg-white px-4 py-2 rounded-lg">
                        <p className="text-xs text-stone-500">Proposed Amount</p>
                        <p className="text-lg font-bold text-emerald-600">{formatCents(engagementDetail.proposed_amount_cents)}</p>
                      </div>
                      {engagementDetail.proposed_duration_days && (
                        <div className="bg-white px-4 py-2 rounded-lg">
                          <p className="text-xs text-stone-500">Duration</p>
                          <p className="text-lg font-bold text-stone-900">{engagementDetail.proposed_duration_days} days</p>
                        </div>
                      )}
                    </div>
                    <div className="flex gap-3 mt-4">
                      <button
                        onClick={() => acceptProposalMutation.mutate()}
                        disabled={acceptProposalMutation.isPending}
                        className="flex items-center gap-2 px-6 py-2 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 disabled:opacity-50"
                      >
                        {acceptProposalMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
                        Accept Proposal
                      </button>
                      <button
                        onClick={() => {
                          const reason = prompt('Reason for declining (optional):')
                          if (reason !== null) declineEngagementMutation.mutate(reason)
                        }}
                        className="flex items-center gap-2 px-6 py-2 border border-stone-300 text-stone-700 rounded-lg font-medium hover:bg-stone-50"
                      >
                        <XCircle className="w-4 h-4" />
                        Decline
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {engagementDetail.description && (
              <div className="p-6 border-b border-stone-100">
                <h3 className="font-semibold text-stone-900 mb-2">Description</h3>
                <p className="text-stone-600">{engagementDetail.description}</p>
              </div>
            )}

            {engagementDetail.request_message && (
              <div className="p-6 border-b border-stone-100">
                <h3 className="font-semibold text-stone-900 mb-2">Your Request</h3>
                <p className="text-stone-600">{engagementDetail.request_message}</p>
              </div>
            )}

            {engagementDetail.status === 'completed' && !engagementDetail.is_reviewed && (
              <div className="p-6 bg-amber-50 border-b border-amber-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Star className="w-6 h-6 text-amber-600" />
                    <div>
                      <h3 className="font-semibold text-amber-900">Rate your experience</h3>
                      <p className="text-sm text-amber-700">Share feedback to help others find great experts</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setShowReviewModal(true)}
                    className="px-4 py-2 bg-amber-600 text-white rounded-lg font-medium hover:bg-amber-700"
                  >
                    Leave Review
                  </button>
                </div>
              </div>
            )}

            <div className="p-6">
              <h3 className="font-semibold text-stone-900 mb-4 flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-purple-600" />
                Messages
              </h3>

              <div className="space-y-3 max-h-80 overflow-y-auto mb-4">
                {(!messages || messages.length === 0) && (
                  <p className="text-center text-stone-400 py-8">No messages yet. Start the conversation!</p>
                )}
                {messages?.map((msg) => (
                  <div key={msg.id} className={`p-3 rounded-lg ${msg.sender_id === engagementDetail.user_id ? 'bg-purple-50 ml-8' : 'bg-stone-50 mr-8'}`}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-medium text-stone-700">{msg.sender_name || 'User'}</span>
                      <span className="text-xs text-stone-400">{formatDate(msg.created_at)}</span>
                    </div>
                    <p className="text-sm text-stone-700">{msg.content}</p>
                  </div>
                ))}
              </div>

              {['request_sent', 'proposal_sent', 'negotiating', 'accepted', 'in_progress'].includes(engagementDetail.status) && (
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                    placeholder="Type a message..."
                    className="flex-1 px-4 py-2 border border-stone-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && messageInput.trim()) {
                        sendMessageMutation.mutate(messageInput.trim())
                      }
                    }}
                  />
                  <button
                    onClick={() => messageInput.trim() && sendMessageMutation.mutate(messageInput.trim())}
                    disabled={!messageInput.trim() || sendMessageMutation.isPending}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
                  >
                    {sendMessageMutation.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-stone-50">
      <div className="bg-gradient-to-br from-purple-900 via-indigo-900 to-violet-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-3xl font-bold mb-2">My Engagements</h1>
          <p className="text-purple-200">Track your expert collaborations and project progress</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex flex-wrap items-center gap-3 mb-6">
          {[
            { value: 'all', label: 'All' },
            { value: 'request_sent', label: 'Pending' },
            { value: 'proposal_sent', label: 'Proposals' },
            { value: 'in_progress', label: 'Active' },
            { value: 'completed', label: 'Completed' }
          ].map((filter) => (
            <button
              key={filter.value}
              onClick={() => setFilterStatus(filter.value)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filterStatus === filter.value
                  ? 'bg-purple-600 text-white'
                  : 'bg-white text-stone-600 border border-stone-200 hover:border-purple-300'
              }`}
            >
              {filter.label}
            </button>
          ))}
        </div>

        {isLoading && (
          <div className="bg-white rounded-2xl border border-stone-200 p-12 text-center">
            <Loader2 className="w-10 h-10 animate-spin text-purple-600 mx-auto mb-4" />
            <p className="text-stone-500">Loading your engagements...</p>
          </div>
        )}

        {!isLoading && (!engagements || engagements.length === 0) && (
          <div className="bg-white rounded-2xl border border-stone-200 p-12 text-center">
            <Briefcase className="w-16 h-16 text-stone-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-stone-900 mb-2">No Engagements Yet</h3>
            <p className="text-stone-500 mb-6">Connect with experts to start your first engagement</p>
            <Link
              to="/build/experts"
              className="inline-flex items-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-xl font-medium hover:bg-purple-700 transition-colors"
            >
              <User className="w-5 h-5" />
              Browse Experts
            </Link>
          </div>
        )}

        <div className="space-y-4">
          {engagements?.map((eng) => (
            <div
              key={eng.id}
              onClick={() => setSelectedEngagement(eng.id)}
              className="bg-white rounded-xl border border-stone-200 p-5 hover:border-purple-300 hover:shadow-md transition-all cursor-pointer group"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  {eng.expert_avatar ? (
                    <img src={eng.expert_avatar} alt="" className="w-12 h-12 rounded-full object-cover" />
                  ) : (
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-indigo-500 flex items-center justify-center text-white font-bold">
                      {(eng.expert_name || 'E').charAt(0)}
                    </div>
                  )}
                  <div>
                    <h3 className="font-semibold text-stone-900 group-hover:text-purple-700 transition-colors">
                      {eng.title}
                    </h3>
                    <p className="text-sm text-stone-600">with {eng.expert_name || 'Expert'}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-stone-500">
                      <span className="flex items-center gap-1">
                        <Briefcase className="w-3 h-3" />
                        {getEngagementTypeLabel(eng.engagement_type)}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatDate(eng.created_at)}
                      </span>
                      {(eng.final_amount_cents || eng.proposed_amount_cents) && (
                        <span className="flex items-center gap-1 text-emerald-600">
                          <DollarSign className="w-3 h-3" />
                          {formatCents(eng.final_amount_cents || eng.proposed_amount_cents)}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {getStatusBadge(eng.status)}
                  <ChevronRight className="w-5 h-5 text-stone-300 group-hover:text-purple-500 transition-colors" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {showReviewModal && engagementDetail && (
        <ReviewModal
          engagementId={engagementDetail.id}
          expertName={engagementDetail.expert_name || 'Expert'}
          onClose={() => setShowReviewModal(false)}
        />
      )}
    </div>
  )
}
