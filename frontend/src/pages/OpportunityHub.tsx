import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { 
  ArrowLeft, BarChart3, Briefcase, CheckCircle2, ChevronDown, ChevronRight, Clock, 
  Lightbulb, Loader2, MessageSquare, 
  PenLine, Plus, Rocket, Search, Send, Sparkles, 
  Target, Trash2, TrendingUp, Users
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

type WorkspaceStatus = 'researching' | 'validating' | 'planning' | 'building' | 'launched' | 'paused' | 'archived'
type TaskPriority = 'low' | 'medium' | 'high' | 'urgent'

type WorkspaceNote = {
  id: number
  title: string | null
  content: string
  is_pinned: boolean
  created_at: string
}

type WorkspaceTask = {
  id: number
  title: string
  description: string | null
  is_completed: boolean
  priority: TaskPriority
  due_date: string | null
  sort_order: number
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

type Workspace = {
  id: number
  user_id: number
  opportunity_id: number
  status: WorkspaceStatus
  progress_percent: number
  custom_title: string | null
  description: string | null
  ai_context: string | null
  created_at: string
  last_activity_at: string | null
  opportunity: { id: number; title: string; category: string } | null
  notes: WorkspaceNote[]
  tasks: WorkspaceTask[]
  documents: { id: number; name: string; doc_type: string | null }[]
}

type RecommendedExpert = {
  id: number
  name: string
  headline: string | null
  avatar_url: string | null
  skills: string[]
  specialization: string[]
  avg_rating: number | null
  total_reviews: number
  is_available: boolean
  hourly_rate_cents: number | null
  match_score: number
  match_reason: string
}

type ChatMessage = {
  id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

const statusOptions: { value: WorkspaceStatus; label: string; color: string }[] = [
  { value: 'researching', label: 'Researching', color: 'bg-blue-100 text-blue-700' },
  { value: 'validating', label: 'Validating', color: 'bg-amber-100 text-amber-700' },
  { value: 'planning', label: 'Planning', color: 'bg-purple-100 text-purple-700' },
  { value: 'building', label: 'Building', color: 'bg-emerald-100 text-emerald-700' },
  { value: 'launched', label: 'Launched', color: 'bg-green-100 text-green-700' },
  { value: 'paused', label: 'Paused', color: 'bg-stone-100 text-stone-700' },
  { value: 'archived', label: 'Archived', color: 'bg-stone-100 text-stone-500' },
]

const priorityColors: Record<TaskPriority, string> = {
  low: 'bg-stone-100 text-stone-600',
  medium: 'bg-blue-100 text-blue-700',
  high: 'bg-amber-100 text-amber-700',
  urgent: 'bg-red-100 text-red-700',
}

export default function OpportunityHub() {
  const { id } = useParams()
  const opportunityId = Number(id)
  const { token, isAuthenticated } = useAuthStore()
  const queryClient = useQueryClient()

  const [activeTab, setActiveTab] = useState<'research' | 'workspace'>('research')
  const [workspaceSubTab, setWorkspaceSubTab] = useState<'tasks' | 'notes' | 'ai'>('tasks')
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [newNoteContent, setNewNoteContent] = useState('')
  const [aiMessage, setAiMessage] = useState('')

  const opportunityQuery = useQuery({
    queryKey: ['opportunity', opportunityId, isAuthenticated, token?.slice(-8)],
    enabled: Number.isFinite(opportunityId),
    queryFn: async (): Promise<Opportunity> => {
      const headers: Record<string, string> = {}
      if (token) headers.Authorization = `Bearer ${token}`
      const res = await fetch(`/api/v1/opportunities/${opportunityId}`, { headers })
      if (!res.ok) throw new Error('Failed to load opportunity')
      return await res.json()
    },
  })

  const expertsQuery = useQuery({
    queryKey: ['opportunity-experts', opportunityId, isAuthenticated],
    enabled: Number.isFinite(opportunityId),
    queryFn: async (): Promise<{ experts: RecommendedExpert[]; total: number }> => {
      const headers: Record<string, string> = {}
      if (token) headers.Authorization = `Bearer ${token}`
      const res = await fetch(`/api/v1/opportunities/${opportunityId}/experts?limit=3`, { headers })
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
      return await res.json()
    },
  })

  const workspaceId = workspaceCheckQuery.data?.workspace_id
  const workspaceQuery = useQuery({
    queryKey: ['workspace', workspaceId],
    enabled: Boolean(workspaceId) && Boolean(token),
    queryFn: async (): Promise<Workspace> => {
      const res = await fetch(`/api/v1/workspaces/${workspaceId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to load workspace')
      return await res.json()
    },
  })

  const createWorkspaceMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/v1/workspaces/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ opportunity_id: opportunityId }),
      })
      if (!res.ok) throw new Error('Failed to create workspace')
      return await res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-check', opportunityId] })
      setActiveTab('workspace')
    },
  })

  const updateStatusMutation = useMutation({
    mutationFn: async (status: WorkspaceStatus) => {
      const res = await fetch(`/api/v1/workspaces/${workspaceId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ status }),
      })
      if (!res.ok) throw new Error('Failed to update status')
      return await res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId] })
    },
  })

  const createTaskMutation = useMutation({
    mutationFn: async (title: string) => {
      const res = await fetch(`/api/v1/workspaces/${workspaceId}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ title }),
      })
      if (!res.ok) throw new Error('Failed to create task')
      return await res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId] })
      setNewTaskTitle('')
    },
  })

  const toggleTaskMutation = useMutation({
    mutationFn: async ({ taskId, completed }: { taskId: number; completed: boolean }) => {
      const res = await fetch(`/api/v1/workspaces/${workspaceId}/tasks/${taskId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ is_completed: completed }),
      })
      if (!res.ok) throw new Error('Failed to update task')
      return await res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId] })
    },
  })

  const deleteTaskMutation = useMutation({
    mutationFn: async (taskId: number) => {
      const res = await fetch(`/api/v1/workspaces/${workspaceId}/tasks/${taskId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to delete task')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId] })
    },
  })

  const createNoteMutation = useMutation({
    mutationFn: async (content: string) => {
      const res = await fetch(`/api/v1/workspaces/${workspaceId}/notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ content }),
      })
      if (!res.ok) throw new Error('Failed to create note')
      return await res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId] })
      setNewNoteContent('')
    },
  })

  const deleteNoteMutation = useMutation({
    mutationFn: async (noteId: number) => {
      const res = await fetch(`/api/v1/workspaces/${workspaceId}/notes/${noteId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to delete note')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId] })
    },
  })

  const chatHistoryQuery = useQuery({
    queryKey: ['chat-history', workspaceId],
    enabled: Boolean(workspaceId) && workspaceId > 0 && Boolean(token),
    queryFn: async (): Promise<ChatMessage[]> => {
      if (!workspaceId) return []
      const res = await fetch(`/api/v1/ai-cofounder/workspace/${workspaceId}/chat-history`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) return []
      return await res.json()
    },
  })

  const sendMessageMutation = useMutation({
    mutationFn: async (message: string): Promise<{ response: string; chat_history: ChatMessage[] }> => {
      if (!workspaceId) throw new Error('No workspace')
      const res = await fetch(`/api/v1/ai-cofounder/workspace/${workspaceId}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ message: message.trim().slice(0, 4000) }),
      })
      if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: 'Failed to send message' }))
        throw new Error(error.detail || 'Failed to send message')
      }
      return await res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat-history', workspaceId] })
      setAiMessage('')
    },
  })

  const chatMessages = chatHistoryQuery.data || []

  const opp = opportunityQuery.data
  const workspace = workspaceQuery.data
  const hasWorkspace = workspaceCheckQuery.data?.has_workspace
  const experts = expertsQuery.data?.experts || []

  if (opportunityQuery.isLoading) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-violet-600" />
      </div>
    )
  }

  if (!opp) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="text-center">
          <Target className="w-16 h-16 text-stone-300 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-stone-900 mb-2">Opportunity not found</h2>
          <Link to="/discover" className="text-violet-600 font-medium hover:text-violet-700">
            Browse opportunities
          </Link>
        </div>
      </div>
    )
  }

  const completedTasks = workspace?.tasks.filter(t => t.is_completed).length || 0
  const totalTasks = workspace?.tasks.length || 0

  return (
    <div className="min-h-screen bg-stone-50">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex items-center gap-2 text-sm text-stone-500 mb-4">
          <Link to="/projects" className="hover:text-stone-700 flex items-center gap-1">
            <ArrowLeft className="w-4 h-4" />
            My Projects
          </Link>
          <ChevronRight className="w-4 h-4" />
          <span className="text-stone-900 font-medium truncate max-w-xs">{opp.title}</span>
        </div>

        <div className="bg-white rounded-xl border border-stone-200 mb-6 overflow-hidden">
          <div className="p-5 border-b border-stone-100">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-medium text-stone-500 uppercase">{opp.category}</span>
                  {opp.feasibility_score && (
                    <span className="flex items-center gap-1 text-emerald-600 text-sm font-semibold">
                      <TrendingUp className="w-4 h-4" />
                      {Math.round(opp.feasibility_score)}% Match
                    </span>
                  )}
                </div>
                <h1 className="text-xl font-bold text-stone-900 mb-2">{opp.title}</h1>
                <p className="text-stone-600 text-sm">{opp.description}</p>
              </div>
            </div>
          </div>

          {/* Consultant Studio Workflow - Main Navigation */}
          <div className="border-b border-stone-200 bg-stone-50 px-5 py-3">
            <h3 className="font-semibold text-stone-900 flex items-center gap-2">
              <Target className="w-5 h-5 text-violet-600" />
              Consultant Studio Workflow
            </h3>
          </div>
          
          <div className="flex border-b border-stone-200">
            <button 
              onClick={() => {
                if (!hasWorkspace) {
                  createWorkspaceMutation.mutate()
                } else {
                  updateStatusMutation.mutate('researching')
                  setActiveTab('workspace')
                }
              }}
              disabled={createWorkspaceMutation.isPending}
              className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 border-b-2 transition-colors ${
                hasWorkspace && workspace?.status === 'researching' ? 'border-violet-600 text-violet-700 bg-violet-50' : 'border-transparent text-stone-500 hover:text-stone-700'
              }`}
            >
              <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                hasWorkspace && workspace?.status === 'researching' ? 'bg-violet-600 text-white' : 
                hasWorkspace && ['validating', 'planning', 'building', 'launched'].includes(workspace?.status || '') ? 'bg-emerald-500 text-white' : 'bg-stone-300 text-white'
              }`}>{hasWorkspace && ['validating', 'planning', 'building', 'launched'].includes(workspace?.status || '') ? '✓' : '1'}</span>
              Validate
            </button>
            <button 
              onClick={() => {
                if (!hasWorkspace) {
                  createWorkspaceMutation.mutate()
                } else {
                  updateStatusMutation.mutate('validating')
                  setActiveTab('workspace')
                }
              }}
              disabled={createWorkspaceMutation.isPending}
              className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 border-b-2 transition-colors ${
                hasWorkspace && workspace?.status === 'validating' ? 'border-violet-600 text-violet-700 bg-violet-50' : 'border-transparent text-stone-500 hover:text-stone-700'
              }`}
            >
              <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                hasWorkspace && workspace?.status === 'validating' ? 'bg-violet-600 text-white' : 
                hasWorkspace && ['planning', 'building', 'launched'].includes(workspace?.status || '') ? 'bg-emerald-500 text-white' : 'bg-stone-300 text-white'
              }`}>{hasWorkspace && ['planning', 'building', 'launched'].includes(workspace?.status || '') ? '✓' : '2'}</span>
              Research
            </button>
            <button 
              onClick={() => {
                if (!hasWorkspace) {
                  createWorkspaceMutation.mutate()
                } else {
                  updateStatusMutation.mutate('planning')
                  setActiveTab('workspace')
                }
              }}
              disabled={createWorkspaceMutation.isPending}
              className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 border-b-2 transition-colors ${
                hasWorkspace && workspace?.status === 'planning' ? 'border-violet-600 text-violet-700 bg-violet-50' : 'border-transparent text-stone-500 hover:text-stone-700'
              }`}
            >
              <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                hasWorkspace && workspace?.status === 'planning' ? 'bg-violet-600 text-white' : 
                hasWorkspace && ['building', 'launched'].includes(workspace?.status || '') ? 'bg-emerald-500 text-white' : 'bg-stone-300 text-white'
              }`}>{hasWorkspace && ['building', 'launched'].includes(workspace?.status || '') ? '✓' : '3'}</span>
              Plan
            </button>
            <button 
              onClick={() => {
                if (!hasWorkspace) {
                  createWorkspaceMutation.mutate()
                } else {
                  updateStatusMutation.mutate('building')
                  setActiveTab('workspace')
                }
              }}
              disabled={createWorkspaceMutation.isPending}
              className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 border-b-2 transition-colors ${
                hasWorkspace && ['building', 'launched'].includes(workspace?.status || '') ? 'border-violet-600 text-violet-700 bg-violet-50' : 'border-transparent text-stone-500 hover:text-stone-700'
              }`}
            >
              <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                hasWorkspace && ['building', 'launched'].includes(workspace?.status || '') ? 'bg-violet-600 text-white' : 'bg-stone-300 text-white'
              }`}>{hasWorkspace && workspace?.status === 'launched' ? '✓' : '4'}</span>
              Execute
            </button>
          </div>

          {hasWorkspace && workspace && (
            <div className="px-5 py-3 bg-stone-50 border-b border-stone-100">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-stone-600">Overall Progress</span>
                <span className="font-medium text-stone-900">{workspace.progress_percent}%</span>
              </div>
              <div className="h-2 bg-stone-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-violet-500 to-purple-500 transition-all duration-500"
                  style={{ width: `${workspace.progress_percent}%` }}
                />
              </div>
            </div>
          )}

          <div className="flex border-b border-stone-200">
            <button
              onClick={() => setActiveTab('research')}
              className={`flex-1 px-6 py-3 text-sm font-medium transition-colors ${
                activeTab === 'research' 
                  ? 'text-violet-600 border-b-2 border-violet-600 bg-violet-50' 
                  : 'text-stone-600 hover:text-stone-900 hover:bg-stone-50'
              }`}
            >
              <Search className="w-4 h-4 inline mr-2" />
              Research
            </button>
            <button
              onClick={() => {
                if (!hasWorkspace) {
                  createWorkspaceMutation.mutate()
                } else {
                  setActiveTab('workspace')
                }
              }}
              disabled={createWorkspaceMutation.isPending}
              className={`flex-1 px-6 py-3 text-sm font-medium transition-colors ${
                activeTab === 'workspace' 
                  ? 'text-violet-600 border-b-2 border-violet-600 bg-violet-50' 
                  : 'text-stone-600 hover:text-stone-900 hover:bg-stone-50'
              }`}
            >
              <Briefcase className="w-4 h-4 inline mr-2" />
              {hasWorkspace ? 'Workspace' : (createWorkspaceMutation.isPending ? 'Creating...' : 'Start Working')}
            </button>
          </div>

          {activeTab === 'research' && (
            <div className="p-6">
              <div className="grid lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                  <div className="bg-stone-50 rounded-lg p-5">
                    <h3 className="font-semibold text-stone-900 mb-3 flex items-center gap-2">
                      <Lightbulb className="w-5 h-5 text-amber-500" />
                      AI Analysis
                    </h3>
                    {opp.ai_analyzed ? (
                      <div className="space-y-4">
                        {opp.ai_problem_statement && (
                          <div>
                            <h4 className="text-sm font-medium text-stone-700 mb-1">Problem Statement</h4>
                            <p className="text-sm text-stone-600">{opp.ai_problem_statement}</p>
                          </div>
                        )}
                        <div className="grid grid-cols-2 gap-4">
                          {opp.ai_market_size_estimate && (
                            <div className="bg-white rounded-lg p-3 border border-stone-200">
                              <p className="text-xs text-stone-500 mb-1">Market Size</p>
                              <p className="font-semibold text-stone-900">{opp.ai_market_size_estimate}</p>
                            </div>
                          )}
                          {opp.ai_competition_level && (
                            <div className="bg-white rounded-lg p-3 border border-stone-200">
                              <p className="text-xs text-stone-500 mb-1">Competition</p>
                              <p className="font-semibold text-stone-900">{opp.ai_competition_level}</p>
                            </div>
                          )}
                          {opp.ai_target_audience && (
                            <div className="bg-white rounded-lg p-3 border border-stone-200">
                              <p className="text-xs text-stone-500 mb-1">Target Audience</p>
                              <p className="font-semibold text-stone-900">{opp.ai_target_audience}</p>
                            </div>
                          )}
                          {opp.ai_urgency_level && (
                            <div className="bg-white rounded-lg p-3 border border-stone-200">
                              <p className="text-xs text-stone-500 mb-1">Urgency</p>
                              <p className="font-semibold text-stone-900">{opp.ai_urgency_level}</p>
                            </div>
                          )}
                        </div>
                        {opp.ai_business_model_suggestions && opp.ai_business_model_suggestions.length > 0 && (
                          <div>
                            <h4 className="text-sm font-medium text-stone-700 mb-2">Business Model Ideas</h4>
                            <div className="flex flex-wrap gap-2">
                              {opp.ai_business_model_suggestions.map((model, i) => (
                                <span key={i} className="text-xs px-3 py-1.5 bg-violet-100 text-violet-700 rounded-full">
                                  {model}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {opp.ai_next_steps && opp.ai_next_steps.length > 0 && (
                          <div>
                            <h4 className="text-sm font-medium text-stone-700 mb-2">Suggested Next Steps</h4>
                            <ul className="space-y-1">
                              {opp.ai_next_steps.map((step, i) => (
                                <li key={i} className="flex items-start gap-2 text-sm text-stone-600">
                                  <ChevronRight className="w-4 h-4 text-violet-500 flex-shrink-0 mt-0.5" />
                                  {step}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ) : (
                      <p className="text-sm text-stone-500">AI analysis not yet available for this opportunity.</p>
                    )}
                  </div>

                  <div className="bg-stone-50 rounded-lg p-5">
                    <h3 className="font-semibold text-stone-900 mb-3 flex items-center gap-2">
                      <BarChart3 className="w-5 h-5 text-blue-500" />
                      Market Signals
                    </h3>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="text-center p-3 bg-white rounded-lg border border-stone-200">
                        <p className="text-2xl font-bold text-stone-900">{opp.validation_count}</p>
                        <p className="text-xs text-stone-500">Validations</p>
                      </div>
                      <div className="text-center p-3 bg-white rounded-lg border border-stone-200">
                        <p className="text-2xl font-bold text-stone-900">{opp.market_size || 'TBD'}</p>
                        <p className="text-xs text-stone-500">Market Size</p>
                      </div>
                      <div className="text-center p-3 bg-white rounded-lg border border-stone-200">
                        <p className="text-2xl font-bold text-emerald-600">
                          {opp.growth_rate ? `+${opp.growth_rate}%` : 'TBD'}
                        </p>
                        <p className="text-xs text-stone-500">Growth Rate</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="bg-stone-50 rounded-lg p-5">
                    <h3 className="font-semibold text-stone-900 mb-3 flex items-center gap-2">
                      <Users className="w-5 h-5 text-violet-500" />
                      Top Experts
                    </h3>
                    {experts.length > 0 ? (
                      <div className="space-y-3">
                        {experts.map((expert) => (
                          <div key={expert.id} className="flex items-center gap-3 p-3 bg-white rounded-lg border border-stone-200">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-400 to-purple-500 flex items-center justify-center text-white font-medium">
                              {expert.name.charAt(0)}
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-stone-900 truncate">{expert.name}</p>
                              <p className="text-xs text-stone-500 truncate">{expert.headline}</p>
                            </div>
                            <span className="text-xs font-medium text-emerald-600">{expert.match_score}%</span>
                          </div>
                        ))}
                        <Link to="/network/experts" className="block text-center text-sm text-violet-600 font-medium hover:text-violet-700">
                          View all experts
                        </Link>
                      </div>
                    ) : (
                      <p className="text-sm text-stone-500">No expert matches found yet.</p>
                    )}
                  </div>

                  <div className="bg-gradient-to-br from-violet-50 to-purple-50 rounded-lg p-5 border border-violet-100">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="w-5 h-5 text-violet-600" />
                      <h3 className="font-semibold text-stone-900">Ready to start?</h3>
                    </div>
                    <p className="text-sm text-stone-600 mb-4">
                      Switch to the Workspace tab to track your progress, take notes, and work with the AI assistant.
                    </p>
                    <button
                      onClick={() => {
                        if (!hasWorkspace) {
                          createWorkspaceMutation.mutate()
                        } else {
                          setActiveTab('workspace')
                        }
                      }}
                      disabled={createWorkspaceMutation.isPending}
                      className="w-full py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 disabled:opacity-50"
                    >
                      {hasWorkspace ? 'Go to Workspace' : 'Start Working on This'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'workspace' && workspace && (
            <div className="p-6">
              <div className="grid lg:grid-cols-4 gap-6">
                <div className="lg:col-span-1 space-y-4">
                  <div className="bg-white rounded-lg border border-stone-200 p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <Briefcase className="w-5 h-5 text-violet-600" />
                      <span className="font-semibold text-stone-900">Workspace</span>
                    </div>
                    <div className="relative">
                      <select 
                        value={workspace.status}
                        onChange={(e) => updateStatusMutation.mutate(e.target.value as WorkspaceStatus)}
                        className={`w-full px-3 py-2 pr-8 rounded-lg text-sm font-medium border-0 cursor-pointer appearance-none ${
                          statusOptions.find(s => s.value === workspace.status)?.color || 'bg-stone-100'
                        }`}
                      >
                        {statusOptions.map(opt => (
                          <option key={opt.value} value={opt.value}>{opt.label}</option>
                        ))}
                      </select>
                      <ChevronDown className="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-current opacity-60" />
                    </div>
                  </div>

                  <div className="bg-stone-50 rounded-lg p-4 space-y-2">
                    <button
                      onClick={() => setWorkspaceSubTab('tasks')}
                      className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                        workspaceSubTab === 'tasks' ? 'bg-white text-violet-700 shadow-sm' : 'text-stone-600 hover:bg-white/50'
                      }`}
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      Tasks ({totalTasks})
                    </button>
                    <button
                      onClick={() => setWorkspaceSubTab('notes')}
                      className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                        workspaceSubTab === 'notes' ? 'bg-white text-violet-700 shadow-sm' : 'text-stone-600 hover:bg-white/50'
                      }`}
                    >
                      <PenLine className="w-4 h-4" />
                      Notes ({workspace.notes.length})
                    </button>
                    <button
                      onClick={() => setWorkspaceSubTab('ai')}
                      className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                        workspaceSubTab === 'ai' ? 'bg-white text-violet-700 shadow-sm' : 'text-stone-600 hover:bg-white/50'
                      }`}
                    >
                      <Sparkles className="w-4 h-4" />
                      AI Assistant
                    </button>
                  </div>

                  <div className="p-4 bg-stone-50 rounded-lg">
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span className="text-stone-600">Task Progress</span>
                      <span className="font-medium">{completedTasks}/{totalTasks}</span>
                    </div>
                    <div className="h-2 bg-stone-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-emerald-500 transition-all"
                        style={{ width: totalTasks > 0 ? `${(completedTasks / totalTasks) * 100}%` : '0%' }}
                      />
                    </div>
                  </div>

                  <div className="p-4 bg-gradient-to-br from-violet-50 to-purple-50 rounded-lg border border-violet-100">
                    <h4 className="text-sm font-semibold text-stone-900 mb-2 flex items-center gap-2">
                      <Lightbulb className="w-4 h-4 text-violet-600" />
                      {workspace.status === 'researching' && 'Empathize Phase'}
                      {workspace.status === 'validating' && 'Define Phase'}
                      {workspace.status === 'planning' && 'Ideate Phase'}
                      {workspace.status === 'building' && 'Prototype Phase'}
                      {workspace.status === 'launched' && 'Test Phase'}
                      {(workspace.status === 'paused' || workspace.status === 'archived') && 'Paused'}
                    </h4>
                    <p className="text-xs text-stone-600 mb-3">
                      {workspace.status === 'researching' && 'Understand your users. Conduct interviews, observe behaviors, gather insights.'}
                      {workspace.status === 'validating' && 'Define the problem. Synthesize findings into a clear problem statement.'}
                      {workspace.status === 'planning' && 'Generate ideas. Brainstorm solutions, explore business models.'}
                      {workspace.status === 'building' && 'Build prototypes. Create MVPs, test with real users.'}
                      {workspace.status === 'launched' && 'Test and iterate. Gather feedback, measure results, scale.'}
                      {(workspace.status === 'paused' || workspace.status === 'archived') && 'Resume to continue your Design Thinking journey.'}
                    </p>
                    <button
                      onClick={() => setWorkspaceSubTab('ai')}
                      className="w-full py-2 text-xs bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700"
                    >
                      Ask AI Co-Founder
                    </button>
                  </div>
                </div>

                <div className="lg:col-span-3">
                  {workspaceSubTab === 'tasks' && (
                    <div>
                      <div className="flex items-center gap-2 mb-4">
                        <input
                          type="text"
                          value={newTaskTitle}
                          onChange={(e) => setNewTaskTitle(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && newTaskTitle.trim() && createTaskMutation.mutate(newTaskTitle.trim())}
                          placeholder="Add a new task..."
                          className="flex-1 px-4 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:border-violet-400"
                        />
                        <button
                          onClick={() => newTaskTitle.trim() && createTaskMutation.mutate(newTaskTitle.trim())}
                          disabled={!newTaskTitle.trim() || createTaskMutation.isPending}
                          className="px-4 py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 disabled:opacity-50"
                        >
                          <Plus className="w-4 h-4" />
                        </button>
                      </div>
                      <div className="space-y-2">
                        {workspace.tasks.sort((a, b) => a.sort_order - b.sort_order).map((task) => (
                          <div 
                            key={task.id}
                            className={`flex items-center gap-3 p-3 rounded-lg border transition-colors ${
                              task.is_completed ? 'bg-stone-50 border-stone-100' : 'bg-white border-stone-200 hover:border-stone-300'
                            }`}
                          >
                            <button
                              onClick={() => toggleTaskMutation.mutate({ taskId: task.id, completed: !task.is_completed })}
                              className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                                task.is_completed ? 'bg-emerald-500 border-emerald-500 text-white' : 'border-stone-300 hover:border-violet-400'
                              }`}
                            >
                              {task.is_completed && <CheckCircle2 className="w-3 h-3" />}
                            </button>
                            <span className={`flex-1 text-sm ${task.is_completed ? 'text-stone-400 line-through' : 'text-stone-900'}`}>
                              {task.title}
                            </span>
                            <span className={`text-xs px-2 py-0.5 rounded ${priorityColors[task.priority]}`}>
                              {task.priority}
                            </span>
                            <button
                              onClick={() => deleteTaskMutation.mutate(task.id)}
                              className="p-1 text-stone-400 hover:text-red-500"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                        {workspace.tasks.length === 0 && (
                          <div className="text-center py-8 text-stone-500">
                            <CheckCircle2 className="w-12 h-12 mx-auto mb-3 text-stone-300" />
                            <p>No tasks yet. Add your first task above!</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {workspaceSubTab === 'notes' && (
                    <div>
                      <div className="mb-4">
                        <textarea
                          value={newNoteContent}
                          onChange={(e) => setNewNoteContent(e.target.value)}
                          placeholder="Write a note..."
                          rows={3}
                          className="w-full px-4 py-3 border border-stone-200 rounded-lg text-sm focus:outline-none focus:border-violet-400 resize-none"
                        />
                        <button
                          onClick={() => newNoteContent.trim() && createNoteMutation.mutate(newNoteContent.trim())}
                          disabled={!newNoteContent.trim() || createNoteMutation.isPending}
                          className="mt-2 px-4 py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 disabled:opacity-50"
                        >
                          Add Note
                        </button>
                      </div>
                      <div className="space-y-3">
                        {workspace.notes.map((note) => (
                          <div key={note.id} className="bg-stone-50 rounded-lg p-4 border border-stone-100">
                            <div className="flex items-start justify-between">
                              <p className="text-sm text-stone-700 whitespace-pre-wrap">{note.content}</p>
                              <button
                                onClick={() => deleteNoteMutation.mutate(note.id)}
                                className="p-1 text-stone-400 hover:text-red-500 flex-shrink-0 ml-2"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                            <p className="text-xs text-stone-400 mt-2">
                              {new Date(note.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        ))}
                        {workspace.notes.length === 0 && (
                          <div className="text-center py-8 text-stone-500">
                            <PenLine className="w-12 h-12 mx-auto mb-3 text-stone-300" />
                            <p>No notes yet. Start capturing your ideas!</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {workspaceSubTab === 'ai' && (
                    <div className="flex flex-col h-[500px]">
                      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
                        {chatMessages.length === 0 && (
                          <div className="bg-violet-50 rounded-lg p-4">
                            <div className="flex items-start gap-3">
                              <div className="w-8 h-8 bg-violet-600 rounded-lg flex items-center justify-center flex-shrink-0">
                                <Sparkles className="w-4 h-4 text-white" />
                              </div>
                              <div>
                                <p className="text-sm text-stone-700 mb-2">
                                  <strong>AI Co-Founder</strong> - I'm here to guide you through your opportunity journey. 
                                  Based on your current stage (<span className="font-medium text-violet-700">{workspace?.status || 'researching'}</span>), 
                                  I can help with:
                                </p>
                                <div className="flex flex-wrap gap-2 mt-3">
                                  <button 
                                    onClick={() => setAiMessage("What should I focus on in this stage?")}
                                    className="text-xs px-3 py-1.5 bg-white border border-violet-200 rounded-full text-violet-700 hover:bg-violet-100"
                                  >
                                    What should I focus on?
                                  </button>
                                  <button 
                                    onClick={() => setAiMessage("Analyze the competition for this opportunity")}
                                    className="text-xs px-3 py-1.5 bg-white border border-violet-200 rounded-full text-violet-700 hover:bg-violet-100"
                                  >
                                    Analyze competition
                                  </button>
                                  <button 
                                    onClick={() => setAiMessage("What tools do you recommend for execution?")}
                                    className="text-xs px-3 py-1.5 bg-white border border-violet-200 rounded-full text-violet-700 hover:bg-violet-100"
                                  >
                                    Recommend tools
                                  </button>
                                  <button 
                                    onClick={() => setAiMessage("Help me create a business plan outline")}
                                    className="text-xs px-3 py-1.5 bg-white border border-violet-200 rounded-full text-violet-700 hover:bg-violet-100"
                                  >
                                    Business plan outline
                                  </button>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                        {chatMessages.map((msg) => (
                          <div 
                            key={msg.id}
                            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                          >
                            {msg.role === 'assistant' && (
                              <div className="w-8 h-8 bg-violet-600 rounded-lg flex items-center justify-center flex-shrink-0">
                                <Sparkles className="w-4 h-4 text-white" />
                              </div>
                            )}
                            <div className={`max-w-[80%] rounded-lg p-3 ${
                              msg.role === 'user' 
                                ? 'bg-stone-900 text-white' 
                                : 'bg-stone-100 text-stone-800'
                            }`}>
                              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                              <p className={`text-xs mt-1 ${msg.role === 'user' ? 'text-stone-400' : 'text-stone-500'}`}>
                                {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </p>
                            </div>
                            {msg.role === 'user' && (
                              <div className="w-8 h-8 bg-stone-900 rounded-lg flex items-center justify-center flex-shrink-0">
                                <MessageSquare className="w-4 h-4 text-white" />
                              </div>
                            )}
                          </div>
                        ))}
                        {sendMessageMutation.isPending && (
                          <div className="flex gap-3">
                            <div className="w-8 h-8 bg-violet-600 rounded-lg flex items-center justify-center flex-shrink-0">
                              <Sparkles className="w-4 h-4 text-white" />
                            </div>
                            <div className="bg-stone-100 rounded-lg p-3">
                              <Loader2 className="w-4 h-4 animate-spin text-violet-600" />
                            </div>
                          </div>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={aiMessage}
                          onChange={(e) => setAiMessage(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && aiMessage.trim() && !sendMessageMutation.isPending && sendMessageMutation.mutate(aiMessage.trim())}
                          placeholder="Ask your AI Co-Founder..."
                          disabled={sendMessageMutation.isPending}
                          className="flex-1 px-4 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:border-violet-400 disabled:opacity-50"
                        />
                        <button 
                          onClick={() => aiMessage.trim() && sendMessageMutation.mutate(aiMessage.trim())}
                          disabled={!aiMessage.trim() || sendMessageMutation.isPending}
                          className="px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 disabled:opacity-50"
                        >
                          <Send className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Step Content - shows based on current workflow status */}
              <div className="mt-6 bg-white rounded-xl border border-stone-200 overflow-hidden">
                <div className="p-5">
                  {workspace.status === 'researching' && (
                    <div>
                      <h4 className="font-medium text-stone-900 mb-4">Step 1: Validate Opportunity</h4>
                      <p className="text-sm text-stone-600 mb-4">Choose how you want to validate this opportunity:</p>
                      <div className="space-y-3">
                        <div className="p-4 border border-violet-200 bg-violet-50 rounded-lg cursor-pointer hover:border-violet-400 transition-colors">
                          <div className="flex items-start gap-3">
                            <div className="w-5 h-5 rounded-full border-2 border-violet-600 flex items-center justify-center mt-0.5">
                              <div className="w-2.5 h-2.5 rounded-full bg-violet-600"></div>
                            </div>
                            <div>
                              <h5 className="font-medium text-violet-900">Validate this platform opportunity</h5>
                              <p className="text-xs text-violet-700 mt-1">Use OppGrid's validated data as foundation (Recommended)</p>
                            </div>
                          </div>
                        </div>
                        <div className="p-4 border border-stone-200 rounded-lg cursor-pointer hover:border-stone-400 transition-colors">
                          <div className="flex items-start gap-3">
                            <div className="w-5 h-5 rounded-full border-2 border-stone-300 mt-0.5"></div>
                            <div>
                              <h5 className="font-medium text-stone-700">Research a new idea</h5>
                              <p className="text-xs text-stone-500 mt-1">Start from scratch with your own concept</p>
                            </div>
                          </div>
                        </div>
                        <div className="p-4 border border-stone-200 rounded-lg cursor-pointer hover:border-stone-400 transition-colors">
                          <div className="flex items-start gap-3">
                            <div className="w-5 h-5 rounded-full border-2 border-stone-300 mt-0.5"></div>
                            <div>
                              <h5 className="font-medium text-stone-700">Find optimal locations</h5>
                              <p className="text-xs text-stone-500 mt-1">Geographic analysis and market sizing</p>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="mt-4 p-4 bg-stone-50 rounded-lg">
                        <h5 className="text-sm font-medium text-stone-700 mb-2">Platform Intelligence</h5>
                        <div className="grid grid-cols-2 gap-3 text-xs">
                          <div className="flex items-center gap-2 text-stone-600">
                            <BarChart3 className="w-4 h-4 text-violet-500" />
                            <span>{String((opp as Record<string, unknown>)?.validations || 0)} validated signals</span>
                          </div>
                          <div className="flex items-center gap-2 text-stone-600">
                            <TrendingUp className="w-4 h-4 text-emerald-500" />
                            <span>{opp?.market_size || 'Unknown'} market</span>
                          </div>
                        </div>
                      </div>
                      <button 
                        onClick={() => updateStatusMutation.mutate('validating')}
                        className="mt-4 w-full py-3 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700 flex items-center justify-center gap-2"
                      >
                        Continue to Validation
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  )}

                  {workspace.status === 'validating' && (
                    <div>
                      <h4 className="font-medium text-stone-900 mb-4">Step 2: Market Research</h4>
                      <p className="text-sm text-stone-600 mb-4">AI is analyzing market conditions for this opportunity:</p>
                      <div className="grid md:grid-cols-2 gap-4 mb-4">
                        <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                          <h5 className="font-medium text-blue-900 mb-2 flex items-center gap-2">
                            <BarChart3 className="w-4 h-4" />
                            Market Overview
                          </h5>
                          <div className="space-y-2 text-xs text-blue-800">
                            <div className="flex justify-between">
                              <span>Total Addressable Market (TAM)</span>
                              <span className="font-medium">{opp?.market_size || 'Analyzing...'}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Growth Rate</span>
                              <span className="font-medium text-emerald-600">+15.3% YoY</span>
                            </div>
                          </div>
                        </div>
                        <div className="p-4 bg-amber-50 rounded-lg border border-amber-100">
                          <h5 className="font-medium text-amber-900 mb-2 flex items-center gap-2">
                            <Users className="w-4 h-4" />
                            Competitive Landscape
                          </h5>
                          <div className="space-y-2 text-xs text-amber-800">
                            <div className="flex justify-between">
                              <span>Competition Level</span>
                              <span className="font-medium">{String((opp as Record<string, unknown>)?.competition || 'Medium')}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Market Gaps</span>
                              <span className="font-medium text-emerald-600">3 identified</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <button 
                        onClick={() => setWorkspaceSubTab('ai')}
                        className="w-full py-2 text-sm bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 mb-3"
                      >
                        Generate Full Research Report with AI
                      </button>
                      <button 
                        onClick={() => updateStatusMutation.mutate('planning')}
                        className="w-full py-3 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700 flex items-center justify-center gap-2"
                      >
                        Continue to Business Plan
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  )}

                  {workspace.status === 'planning' && (
                    <div>
                      <h4 className="font-medium text-stone-900 mb-4">Step 3: Generate Business Plan</h4>
                      <p className="text-sm text-stone-600 mb-4">Select sections to include in your business plan:</p>
                      <div className="grid grid-cols-2 gap-2 mb-4">
                        {['Executive Summary', 'Market Analysis', 'Competitive Positioning', 'Product Strategy', 'Go-to-Market Plan', 'Financial Projections', 'Risk Analysis'].map((section) => (
                          <label key={section} className="flex items-center gap-2 p-2 bg-stone-50 rounded text-sm cursor-pointer hover:bg-stone-100">
                            <input type="checkbox" defaultChecked className="rounded border-stone-300 text-violet-600 focus:ring-violet-500" />
                            <span>{section}</span>
                          </label>
                        ))}
                      </div>
                      <div className="flex gap-2 mb-4">
                        <span className="text-sm text-stone-600">Detail Level:</span>
                        <label className="flex items-center gap-1 text-sm">
                          <input type="radio" name="detail" className="text-violet-600" />
                          Brief
                        </label>
                        <label className="flex items-center gap-1 text-sm">
                          <input type="radio" name="detail" defaultChecked className="text-violet-600" />
                          Standard
                        </label>
                        <label className="flex items-center gap-1 text-sm">
                          <input type="radio" name="detail" className="text-violet-600" />
                          Comprehensive
                        </label>
                      </div>
                      <button 
                        onClick={() => setWorkspaceSubTab('ai')}
                        className="w-full py-2 text-sm bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 mb-3"
                      >
                        Generate Business Plan with AI
                      </button>
                      <button 
                        onClick={() => updateStatusMutation.mutate('building')}
                        className="w-full py-3 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700 flex items-center justify-center gap-2"
                      >
                        Continue to Execution
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  )}

                  {(workspace.status === 'building' || workspace.status === 'launched') && (
                    <div>
                      <h4 className="font-medium text-stone-900 mb-4">Step 4: Execution Roadmap</h4>
                      <p className="text-sm text-stone-600 mb-4">Connect with resources to launch your business:</p>
                      <div className="grid md:grid-cols-3 gap-4">
                        <div className="p-4 bg-violet-50 rounded-lg border border-violet-100">
                          <h5 className="font-medium text-violet-900 mb-2 flex items-center gap-2">
                            <Users className="w-4 h-4" />
                            Team
                          </h5>
                          <p className="text-xs text-violet-700 mb-3">Find co-founders, advisors, and contractors</p>
                          <Link to="/network" className="block w-full py-2 text-xs bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700 text-center">
                            Find Team Members
                          </Link>
                        </div>
                        <div className="p-4 bg-emerald-50 rounded-lg border border-emerald-100">
                          <h5 className="font-medium text-emerald-900 mb-2 flex items-center gap-2">
                            <TrendingUp className="w-4 h-4" />
                            Funding
                          </h5>
                          <p className="text-xs text-emerald-700 mb-3">Connect with investors, grants, and loans</p>
                          <Link to="/network" className="block w-full py-2 text-xs bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 text-center">
                            Browse Investors
                          </Link>
                        </div>
                        <div className="p-4 bg-amber-50 rounded-lg border border-amber-100">
                          <h5 className="font-medium text-amber-900 mb-2 flex items-center gap-2">
                            <Target className="w-4 h-4" />
                            Customers
                          </h5>
                          <p className="text-xs text-amber-700 mb-3">Get validated leads for beta users</p>
                          <Link to="/leads" className="block w-full py-2 text-xs bg-amber-600 text-white rounded-lg font-medium hover:bg-amber-700 text-center">
                            Purchase Leads
                          </Link>
                        </div>
                      </div>
                      {workspace.status === 'building' && (
                        <button 
                          onClick={() => updateStatusMutation.mutate('launched')}
                          className="mt-4 w-full py-3 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 flex items-center justify-center gap-2"
                        >
                          <Rocket className="w-4 h-4" />
                          Mark as Launched
                        </button>
                      )}
                      {workspace.status === 'launched' && (
                        <div className="mt-4 p-4 bg-emerald-50 border border-emerald-200 rounded-lg text-center">
                          <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
                          <p className="font-medium text-emerald-800">Congratulations! Your project is launched.</p>
                          <p className="text-xs text-emerald-600 mt-1">Track progress in the Active Projects dashboard.</p>
                        </div>
                      )}
                    </div>
                  )}

                  {(workspace.status === 'paused' || workspace.status === 'archived') && (
                    <div className="text-center py-8">
                      <div className="w-16 h-16 bg-stone-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Clock className="w-8 h-8 text-stone-400" />
                      </div>
                      <h4 className="font-medium text-stone-700 mb-2">This project is {workspace.status}</h4>
                      <p className="text-sm text-stone-500 mb-4">Change the status above to resume your journey.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'workspace' && !workspace && workspaceCheckQuery.isLoading && (
            <div className="p-12 text-center">
              <Loader2 className="w-8 h-8 animate-spin text-violet-600 mx-auto" />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
