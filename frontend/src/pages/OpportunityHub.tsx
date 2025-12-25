import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { 
  ArrowLeft, BarChart3, Briefcase, CheckCircle, CheckCircle2, ChevronDown, ChevronRight, 
  Lightbulb, Loader2, MapPin, MessageSquare, PanelLeftClose, PanelLeftOpen,
  PenLine, Plus, Rocket, Search, Send, Sparkles, 
  Target, Trash2, TrendingUp, Users, X, Zap
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

// Workflow stages with icons for circular navigation
const workflowStages = [
  { key: 'researching' as WorkspaceStatus, label: 'Validate', icon: CheckCircle },
  { key: 'validating' as WorkspaceStatus, label: 'Research', icon: Search },
  { key: 'planning' as WorkspaceStatus, label: 'Plan', icon: Target },
  { key: 'building' as WorkspaceStatus, label: 'Execute', icon: Zap },
]

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

  const [activeTab, setActiveTab] = useState<WorkspaceStatus>('researching')
  const [workspaceSubTab, setWorkspaceSubTab] = useState<'tasks' | 'notes' | 'ai'>('tasks')
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [newNoteContent, setNewNoteContent] = useState('')
  const [aiMessage, setAiMessage] = useState('')
  const [validationPath, setValidationPath] = useState<'platform' | 'new_idea' | 'locations' | null>(null)
  const [workspacePanelOpen, setWorkspacePanelOpen] = useState(false)

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
      setWorkspacePanelOpen(true)
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

          {/* Consultant Studio Workflow - Circular Icon Navigation */}
          <div className="px-5 py-4 bg-stone-50 border-b border-stone-100">
            <div className="flex items-center justify-between max-w-2xl mx-auto">
              {workflowStages.map((stage, idx) => {
                const Icon = stage.icon
                const currentIdx = hasWorkspace ? workflowStages.findIndex(s => s.key === workspace?.status) : -1
                const isCompleted = hasWorkspace && idx < currentIdx
                const isCurrent = activeTab === stage.key
                
                return (
                  <div key={stage.key} className="flex items-center">
                    <button
                      onClick={() => {
                        setActiveTab(stage.key)
                      }}
                      className={`flex flex-col items-center ${idx > 0 ? 'ml-4' : ''} cursor-pointer group`}
                    >
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                        isCurrent 
                          ? 'bg-violet-600 text-white ring-4 ring-violet-100' 
                          : isCompleted 
                            ? 'bg-emerald-100 text-emerald-600' 
                            : 'bg-stone-100 text-stone-400'
                      } group-hover:ring-2 group-hover:ring-violet-300 group-hover:ring-offset-2`}>
                        {isCompleted ? (
                          <CheckCircle2 className="w-5 h-5" />
                        ) : (
                          <Icon className="w-5 h-5" />
                        )}
                      </div>
                      <span className={`text-xs mt-1 font-medium ${
                        isCurrent ? 'text-violet-600' : isCompleted ? 'text-emerald-600' : 'text-stone-400'
                      }`}>
                        {stage.label}
                      </span>
                    </button>
                    {idx < workflowStages.length - 1 && (
                      <div className={`w-12 h-0.5 ml-4 ${isCompleted || isCurrent ? 'bg-emerald-300' : 'bg-stone-200'}`} />
                    )}
                  </div>
                )
              })}
            </div>
            
            {/* Progress Bar */}
            <div className="mt-4 max-w-2xl mx-auto">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-stone-600">Overall Progress</span>
                <span className="font-medium text-stone-900">{hasWorkspace && workspace ? workspace.progress_percent : 0}%</span>
              </div>
              <div className="h-2 bg-stone-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-violet-500 to-purple-500 transition-all duration-500"
                  style={{ width: `${hasWorkspace && workspace ? workspace.progress_percent : 0}%` }}
                />
              </div>
            </div>
          </div>

          <div className="flex border-b border-stone-200">
            <button
              onClick={() => {
                if (!hasWorkspace) {
                  createWorkspaceMutation.mutate()
                } else {
                  setWorkspacePanelOpen(!workspacePanelOpen)
                }
              }}
              disabled={createWorkspaceMutation.isPending}
              className={`px-4 py-3 text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
                workspacePanelOpen 
                  ? 'text-violet-600 bg-violet-50' 
                  : 'text-stone-600 hover:text-stone-900 hover:bg-stone-50'
              }`}
              title={workspacePanelOpen ? 'Hide Workspace' : 'Show Workspace'}
            >
              <Briefcase className="w-4 h-4" />
              {hasWorkspace ? (
                <>
                  <span>Workspace</span>
                  {workspacePanelOpen ? <PanelLeftClose className="w-4 h-4" /> : <PanelLeftOpen className="w-4 h-4" />}
                </>
              ) : (
                <span>{createWorkspaceMutation.isPending ? 'Creating...' : 'Workspace'}</span>
              )}
            </button>
          </div>

          <div className="flex">
            {workspacePanelOpen && hasWorkspace && (
              <div className="w-[380px] flex-shrink-0 border-r border-stone-200 bg-white">
                <div className="sticky top-0 bg-white border-b border-stone-200 p-4 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Briefcase className="w-5 h-5 text-violet-600" />
                    <span className="font-semibold text-stone-900">Workspace</span>
                  </div>
                  <button 
                    onClick={() => setWorkspacePanelOpen(false)}
                    className="p-2 hover:bg-stone-100 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-stone-500" />
                  </button>
                </div>
                
                {!workspace && (
                  <div className="p-8 flex items-center justify-center">
                    <Loader2 className="w-6 h-6 animate-spin text-violet-600" />
                  </div>
                )}
                
                {workspace && (
                
                <div className="p-4 space-y-4 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 300px)' }}>
                  <div className="bg-stone-50 rounded-lg p-4">
                    <div className="mb-2">
                      <span className="text-sm text-stone-600">Status:</span>
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
                      {workspace.status === 'researching' && 'Step 1: Validate'}
                      {workspace.status === 'validating' && 'Step 2: Research'}
                      {workspace.status === 'planning' && 'Step 3: Plan'}
                      {workspace.status === 'building' && 'Step 4: Execute'}
                      {workspace.status === 'launched' && 'Launched'}
                      {(workspace.status === 'paused' || workspace.status === 'archived') && 'Paused'}
                    </h4>
                    <p className="text-xs text-stone-600 mb-3">
                      {workspace.status === 'researching' && 'Validate the opportunity with platform data or research your own idea.'}
                      {workspace.status === 'validating' && 'Deep market research: TAM/SAM/SOM analysis, competitive landscape.'}
                      {workspace.status === 'planning' && 'Generate your business plan: executive summary, go-to-market strategy.'}
                      {workspace.status === 'building' && 'Execute your roadmap: validate with customers, build MVP, secure funding.'}
                      {workspace.status === 'launched' && 'Track progress, measure results, iterate on feedback.'}
                      {(workspace.status === 'paused' || workspace.status === 'archived') && 'Resume to continue your journey.'}
                    </p>
                    <button
                      onClick={() => setWorkspaceSubTab('ai')}
                      className="w-full py-2 text-xs bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700"
                    >
                      Ask AI Co-Founder
                    </button>
                  </div>

                  {workspace.status === 'researching' && !validationPath && (
                    <div className="bg-white rounded-lg border border-stone-200 p-4">
                      <h4 className="font-medium text-stone-900 mb-3">Choose your validation path:</h4>
                      <div className="space-y-2">
                        <button
                          onClick={() => setValidationPath('platform')}
                          className="w-full flex items-center gap-3 p-3 rounded-lg border border-stone-200 hover:border-violet-400 hover:bg-violet-50 text-left"
                        >
                          <CheckCircle className="w-5 h-5 text-violet-600" />
                          <div>
                            <p className="text-sm font-medium text-stone-900">Validate platform opportunity</p>
                            <span className="text-xs text-emerald-600">Recommended</span>
                          </div>
                        </button>
                        <button
                          onClick={() => setValidationPath('new_idea')}
                          className="w-full flex items-center gap-3 p-3 rounded-lg border border-stone-200 hover:border-violet-400 hover:bg-violet-50 text-left"
                        >
                          <Lightbulb className="w-5 h-5 text-blue-600" />
                          <p className="text-sm font-medium text-stone-900">Research a new idea</p>
                        </button>
                        <button
                          onClick={() => setValidationPath('locations')}
                          className="w-full flex items-center gap-3 p-3 rounded-lg border border-stone-200 hover:border-violet-400 hover:bg-violet-50 text-left"
                        >
                          <MapPin className="w-5 h-5 text-amber-600" />
                          <p className="text-sm font-medium text-stone-900">Find optimal locations</p>
                        </button>
                      </div>
                    </div>
                  )}

                  {workspace.status === 'researching' && validationPath && (
                    <div className="bg-white rounded-lg border border-stone-200 p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          {validationPath === 'platform' && <CheckCircle className="w-5 h-5 text-violet-600" />}
                          {validationPath === 'new_idea' && <Lightbulb className="w-5 h-5 text-blue-600" />}
                          {validationPath === 'locations' && <MapPin className="w-5 h-5 text-amber-600" />}
                          <span className="text-sm font-medium text-stone-900">
                            {validationPath === 'platform' && 'Validating Platform Opportunity'}
                            {validationPath === 'new_idea' && 'Researching New Idea'}
                            {validationPath === 'locations' && 'Finding Locations'}
                          </span>
                        </div>
                        <button onClick={() => setValidationPath(null)} className="text-xs text-stone-500 hover:text-stone-700">
                          Change
                        </button>
                      </div>
                      <button
                        onClick={() => {
                          updateStatusMutation.mutate('validating')
                          setValidationPath(null)
                        }}
                        className="w-full py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 flex items-center justify-center gap-2"
                      >
                        <Rocket className="w-4 h-4" />
                        Continue to Research
                      </button>
                    </div>
                  )}

                  {workspaceSubTab === 'tasks' && (
                    <div className="bg-white rounded-lg border border-stone-200 p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <input
                          type="text"
                          value={newTaskTitle}
                          onChange={(e) => setNewTaskTitle(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && newTaskTitle.trim() && createTaskMutation.mutate(newTaskTitle.trim())}
                          placeholder="Add a task..."
                          className="flex-1 px-3 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:border-violet-400"
                        />
                        <button
                          onClick={() => newTaskTitle.trim() && createTaskMutation.mutate(newTaskTitle.trim())}
                          disabled={!newTaskTitle.trim() || createTaskMutation.isPending}
                          className="px-3 py-2 bg-violet-600 text-white rounded-lg text-sm hover:bg-violet-700 disabled:opacity-50"
                        >
                          <Plus className="w-4 h-4" />
                        </button>
                      </div>
                      <div className="space-y-2 max-h-[300px] overflow-y-auto">
                        {workspace.tasks.sort((a, b) => a.sort_order - b.sort_order).map((task) => (
                          <div 
                            key={task.id}
                            className={`flex items-center gap-2 p-2 rounded-lg border text-sm ${
                              task.is_completed ? 'bg-stone-50 border-stone-100' : 'bg-white border-stone-200'
                            }`}
                          >
                            <button
                              onClick={() => toggleTaskMutation.mutate({ taskId: task.id, completed: !task.is_completed })}
                              className={`w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                                task.is_completed ? 'bg-emerald-500 border-emerald-500 text-white' : 'border-stone-300'
                              }`}
                            >
                              {task.is_completed && <CheckCircle2 className="w-3 h-3" />}
                            </button>
                            <span className={`flex-1 ${task.is_completed ? 'text-stone-400 line-through' : 'text-stone-900'}`}>
                              {task.title}
                            </span>
                            <span className={`text-xs px-1.5 py-0.5 rounded ${priorityColors[task.priority]}`}>
                              {task.priority}
                            </span>
                            <button onClick={() => deleteTaskMutation.mutate(task.id)} className="p-1 text-stone-400 hover:text-red-500">
                              <Trash2 className="w-3 h-3" />
                            </button>
                          </div>
                        ))}
                        {workspace.tasks.length === 0 && (
                          <p className="text-center py-4 text-stone-400 text-sm">No tasks yet</p>
                        )}
                      </div>
                    </div>
                  )}

                  {workspaceSubTab === 'notes' && (
                    <div className="bg-white rounded-lg border border-stone-200 p-4">
                      <textarea
                        value={newNoteContent}
                        onChange={(e) => setNewNoteContent(e.target.value)}
                        placeholder="Write a note..."
                        rows={3}
                        className="w-full px-3 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:border-violet-400 resize-none mb-2"
                      />
                      <button
                        onClick={() => newNoteContent.trim() && createNoteMutation.mutate(newNoteContent.trim())}
                        disabled={!newNoteContent.trim() || createNoteMutation.isPending}
                        className="px-3 py-2 bg-violet-600 text-white rounded-lg text-sm hover:bg-violet-700 disabled:opacity-50 mb-3"
                      >
                        Add Note
                      </button>
                      <div className="space-y-2 max-h-[250px] overflow-y-auto">
                        {workspace.notes.map((note) => (
                          <div key={note.id} className="bg-stone-50 rounded-lg p-3 border border-stone-100">
                            <div className="flex items-start justify-between">
                              <p className="text-sm text-stone-700 whitespace-pre-wrap">{note.content}</p>
                              <button onClick={() => deleteNoteMutation.mutate(note.id)} className="p-1 text-stone-400 hover:text-red-500">
                                <Trash2 className="w-3 h-3" />
                              </button>
                            </div>
                            <p className="text-xs text-stone-400 mt-1">{new Date(note.created_at).toLocaleDateString()}</p>
                          </div>
                        ))}
                        {workspace.notes.length === 0 && (
                          <p className="text-center py-4 text-stone-400 text-sm">No notes yet</p>
                        )}
                      </div>
                    </div>
                  )}

                  {workspaceSubTab === 'ai' && (
                    <div className="bg-white rounded-lg border border-stone-200 p-4 flex flex-col" style={{ height: '400px' }}>
                      <div className="flex-1 overflow-y-auto space-y-3 mb-3">
                        {chatMessages.map((msg) => (
                          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[85%] rounded-lg p-3 text-sm ${
                              msg.role === 'user' ? 'bg-violet-600 text-white' : 'bg-stone-100 text-stone-800'
                            }`}>
                              {msg.content}
                            </div>
                          </div>
                        ))}
                        {chatMessages.length === 0 && (
                          <div className="text-center py-8">
                            <MessageSquare className="w-8 h-8 mx-auto mb-2 text-stone-300" />
                            <p className="text-sm text-stone-400">Ask AI about this opportunity</p>
                          </div>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          value={aiMessage}
                          onChange={(e) => setAiMessage(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && aiMessage.trim() && sendMessageMutation.mutate(aiMessage.trim())}
                          placeholder="Ask a question..."
                          className="flex-1 px-3 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:border-violet-400"
                        />
                        <button
                          onClick={() => aiMessage.trim() && sendMessageMutation.mutate(aiMessage.trim())}
                          disabled={!aiMessage.trim() || sendMessageMutation.isPending}
                          className="p-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 disabled:opacity-50"
                        >
                          <Send className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
                )}
              </div>
            )}

            <div className="flex-1 p-6">
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
                      Open the workspace panel to track your progress, take notes, and work with the AI assistant.
                    </p>
                    <button
                      onClick={() => {
                        if (!hasWorkspace) {
                          createWorkspaceMutation.mutate()
                        } else {
                          setWorkspacePanelOpen(true)
                        }
                      }}
                      disabled={createWorkspaceMutation.isPending}
                      className="w-full py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 disabled:opacity-50"
                    >
                      {hasWorkspace ? 'Open Workspace' : 'Start Working on This'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
