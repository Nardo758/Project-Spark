import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { 
  ArrowLeft, Briefcase, CheckCircle2, ChevronRight, FileText, 
  PenLine, Plus, 
  Send, Sparkles, Target, Trash2, Loader2,
  BarChart3, Search, Zap, Mic, ClipboardList, Crosshair, DollarSign, TrendingUp
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import EnhancedOverviewTab from '../components/workspace/EnhancedOverviewTab'
import ResearchHubTab from '../components/workspace/ResearchHubTab'
import WorkflowTab from '../components/workspace/WorkflowTab'
import InterviewTab from '../components/workspace/InterviewTab'
import SurveyTab from '../components/workspace/SurveyTab'
import CompetitorTab from '../components/workspace/CompetitorTab'
import FinancialTab from '../components/workspace/FinancialTab'
import AnalyticsTab from '../components/workspace/AnalyticsTab'

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

type WorkspaceDocument = {
  id: number
  name: string
  doc_type: string | null
  created_at: string
}

type Opportunity = {
  id: number
  title: string
  category: string
  description: string | null
  feasibility_score: number | null
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
  opportunity: Opportunity | null
  notes: WorkspaceNote[]
  tasks: WorkspaceTask[]
  documents: WorkspaceDocument[]
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

type TabId = 'overview' | 'research' | 'workflow' | 'interviews' | 'surveys' | 'competitors' | 'financial' | 'analytics' | 'tasks' | 'notes' | 'docs' | 'ai'

const enhancedTabs: { id: TabId; name: string; icon: typeof BarChart3 }[] = [
  { id: 'overview', name: 'Overview', icon: BarChart3 },
  { id: 'research', name: 'Research Hub', icon: Search },
  { id: 'workflow', name: 'Workflow', icon: Zap },
  { id: 'interviews', name: 'Interviews', icon: Mic },
  { id: 'surveys', name: 'Surveys', icon: ClipboardList },
  { id: 'competitors', name: 'Competitors', icon: Crosshair },
  { id: 'financial', name: 'Financial', icon: DollarSign },
  { id: 'analytics', name: 'Analytics', icon: TrendingUp },
]

const legacyTabs: { id: TabId; name: string; icon: typeof CheckCircle2 }[] = [
  { id: 'tasks', name: 'Tasks', icon: CheckCircle2 },
  { id: 'notes', name: 'Notes', icon: PenLine },
  { id: 'docs', name: 'Documents', icon: FileText },
  { id: 'ai', name: 'AI Assistant', icon: Sparkles },
]

const priorityColors: Record<TaskPriority, string> = {
  low: 'bg-stone-100 text-stone-600',
  medium: 'bg-blue-100 text-blue-700',
  high: 'bg-amber-100 text-amber-700',
  urgent: 'bg-red-100 text-red-700',
}

export default function WorkspacePage() {
  const { id } = useParams()
  const workspaceId = Number(id)
  const { token } = useAuthStore()
  const queryClient = useQueryClient()

  const [activeTab, setActiveTab] = useState<TabId>('overview')
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [newNoteContent, setNewNoteContent] = useState('')
  const [aiMessage, setAiMessage] = useState('')

  const workspaceQuery = useQuery({
    queryKey: ['workspace', workspaceId],
    enabled: Number.isFinite(workspaceId) && Boolean(token),
    queryFn: async (): Promise<Workspace> => {
      const res = await fetch(`/api/v1/workspaces/${workspaceId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to load workspace')
      return await res.json()
    },
  })

  const enhancedQuery = useQuery({
    queryKey: ['enhanced-workspace-by-opp', workspaceQuery.data?.opportunity_id],
    enabled: Boolean(token) && Boolean(workspaceQuery.data?.opportunity_id),
    queryFn: async () => {
      const res = await fetch(`/api/v1/enhanced-workspaces`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) return null
      const data = await res.json()
      return data.workspaces?.find((w: any) => w.opportunity_id === workspaceQuery.data?.opportunity_id) || null
    },
  })

  const createEnhancedMutation = useMutation({
    mutationFn: async (workflowType: string) => {
      const res = await fetch(`/api/v1/enhanced-workspaces`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          opportunity_id: workspaceQuery.data?.opportunity_id,
          workflow_type: workflowType,
        }),
      })
      if (!res.ok) throw new Error('Failed to create enhanced workspace')
      return await res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['enhanced-workspace-by-opp'] })
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

  const workspace = workspaceQuery.data
  const enhancedWs = enhancedQuery.data
  const currentStatus = statusOptions.find(s => s.value === workspace?.status) || statusOptions[0]

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['enhanced-workspace-by-opp'] })
    queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId] })
  }

  if (workspaceQuery.isLoading) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-violet-600" />
      </div>
    )
  }

  if (workspaceQuery.isError || !workspace) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="text-center">
          <Briefcase className="w-16 h-16 text-stone-300 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-stone-900 mb-2">Workspace not found</h2>
          <p className="text-stone-600 mb-4">This workspace may have been deleted or you don't have access.</p>
          <Link to="/workspaces" className="text-violet-600 font-medium hover:text-violet-700">
            View all workspaces
          </Link>
        </div>
      </div>
    )
  }

  const completedTasks = workspace.tasks.filter(t => t.is_completed).length
  const totalTasks = workspace.tasks.length

  const isEnhancedTab = enhancedTabs.some(t => t.id === activeTab)
  const allTabs = enhancedWs ? [...enhancedTabs, ...legacyTabs] : legacyTabs

  return (
    <div className="min-h-screen bg-stone-50">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex items-center gap-2 text-sm text-stone-500 mb-4">
          <Link to="/workspaces" className="hover:text-stone-700 flex items-center gap-1">
            <ArrowLeft className="w-4 h-4" />
            My Workspaces
          </Link>
          <ChevronRight className="w-4 h-4" />
          <span className="text-stone-900 font-medium">{workspace.custom_title || workspace.opportunity?.title}</span>
        </div>

        <div className="grid lg:grid-cols-5 gap-6">
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl border border-stone-200 p-5 sticky top-6">
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-3">
                  <Briefcase className="w-5 h-5 text-violet-600" />
                  <span className="font-bold text-stone-900">Workspace</span>
                </div>
                
                <select 
                  value={workspace.status}
                  onChange={(e) => updateStatusMutation.mutate(e.target.value as WorkspaceStatus)}
                  className={`w-full px-3 py-2 rounded-lg text-sm font-medium ${currentStatus.color} border-0 cursor-pointer`}
                >
                  {statusOptions.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>

              <div className="mb-4">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-stone-600">Progress</span>
                  <span className="font-medium text-stone-900">
                    {enhancedWs ? enhancedWs.progress_percent : workspace.progress_percent}%
                  </span>
                </div>
                <div className="h-2 bg-stone-100 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-violet-500 to-purple-500 transition-all duration-500"
                    style={{ width: `${enhancedWs ? enhancedWs.progress_percent : workspace.progress_percent}%` }}
                  />
                </div>
                <p className="text-xs text-stone-500 mt-1">
                  {completedTasks} of {totalTasks} tasks completed
                </p>
              </div>

              {!enhancedWs && (
                <div className="border-t border-stone-100 pt-4 mb-4">
                  <p className="text-xs text-stone-500 mb-2">Upgrade to Enhanced Workspace</p>
                  <button
                    onClick={() => createEnhancedMutation.mutate('lean_validation')}
                    disabled={createEnhancedMutation.isPending}
                    className="w-full px-3 py-2 bg-violet-600 text-white text-sm rounded-lg hover:bg-violet-700 disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {createEnhancedMutation.isPending ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Zap className="w-4 h-4" />
                    )}
                    Enable Enhanced Mode
                  </button>
                </div>
              )}

              <div className="border-t border-stone-100 pt-4 space-y-1">
                {allTabs.map(tab => {
                  const Icon = tab.icon
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                        activeTab === tab.id ? 'bg-violet-50 text-violet-700 font-medium' : 'text-stone-600 hover:bg-stone-50'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      {tab.name}
                    </button>
                  )
                })}
              </div>

              <div className="border-t border-stone-100 pt-4 mt-4">
                <Link
                  to={`/opportunity/${workspace.opportunity_id}`}
                  className="flex items-center gap-2 text-sm text-stone-600 hover:text-stone-900"
                >
                  <Target className="w-4 h-4" />
                  View Opportunity Details
                </Link>
              </div>
            </div>
          </div>

          <div className="lg:col-span-4">
            <div className="bg-white rounded-xl border border-stone-200 overflow-hidden">
              <div className="border-b border-stone-200 p-5">
                <h1 className="text-xl font-bold text-stone-900 mb-1">
                  {workspace.custom_title || workspace.opportunity?.title}
                </h1>
                <p className="text-stone-600 text-sm">{workspace.opportunity?.category}</p>
              </div>

              {isEnhancedTab && enhancedWs && token && (
                <div className="p-5">
                  {activeTab === 'overview' && (
                    <EnhancedOverviewTab workspaceId={enhancedWs.id} workspace={enhancedWs} token={token} onRefresh={handleRefresh} />
                  )}
                  {activeTab === 'research' && (
                    <ResearchHubTab workspaceId={enhancedWs.id} workspace={enhancedWs} token={token} onRefresh={handleRefresh} />
                  )}
                  {activeTab === 'workflow' && (
                    <WorkflowTab workspaceId={enhancedWs.id} workspace={enhancedWs} token={token} onRefresh={handleRefresh} />
                  )}
                  {activeTab === 'interviews' && (
                    <InterviewTab workspaceId={enhancedWs.id} workspace={enhancedWs} token={token} onRefresh={handleRefresh} />
                  )}
                  {activeTab === 'surveys' && (
                    <SurveyTab workspaceId={enhancedWs.id} workspace={enhancedWs} token={token} onRefresh={handleRefresh} />
                  )}
                  {activeTab === 'competitors' && (
                    <CompetitorTab workspaceId={enhancedWs.id} workspace={enhancedWs} token={token} onRefresh={handleRefresh} />
                  )}
                  {activeTab === 'financial' && (
                    <FinancialTab workspaceId={enhancedWs.id} workspace={enhancedWs} token={token} onRefresh={handleRefresh} />
                  )}
                  {activeTab === 'analytics' && (
                    <AnalyticsTab workspaceId={enhancedWs.id} workspace={enhancedWs} token={token} onRefresh={handleRefresh} />
                  )}
                </div>
              )}

              {isEnhancedTab && !enhancedWs && (
                <div className="p-5">
                  <div className="text-center py-12">
                    <Zap className="w-16 h-16 text-stone-300 mx-auto mb-4" />
                    <h3 className="font-medium text-stone-900 mb-2">Enhanced Workspace Not Active</h3>
                    <p className="text-sm text-stone-500 mb-4">Enable Enhanced Mode from the sidebar to access AI-powered research tools.</p>
                  </div>
                </div>
              )}

              {activeTab === 'tasks' && (
                <div className="p-5">
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
                          task.is_completed 
                            ? 'bg-stone-50 border-stone-100' 
                            : 'bg-white border-stone-200 hover:border-stone-300'
                        }`}
                      >
                        <button
                          onClick={() => toggleTaskMutation.mutate({ taskId: task.id, completed: !task.is_completed })}
                          className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors ${
                            task.is_completed 
                              ? 'bg-emerald-500 border-emerald-500 text-white' 
                              : 'border-stone-300 hover:border-violet-400'
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
                          className="p-1 text-stone-400 hover:text-red-500 transition-colors"
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

              {activeTab === 'notes' && (
                <div className="p-5">
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
                            className="p-1 text-stone-400 hover:text-red-500 transition-colors flex-shrink-0 ml-2"
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

              {activeTab === 'docs' && (
                <div className="p-5">
                  <div className="text-center py-12 text-stone-500">
                    <FileText className="w-16 h-16 mx-auto mb-4 text-stone-300" />
                    <h3 className="font-medium text-stone-900 mb-2">Documents coming soon</h3>
                    <p className="text-sm">You'll be able to upload and manage files here.</p>
                  </div>
                </div>
              )}

              {activeTab === 'ai' && (
                <div className="p-5">
                  <div className="bg-violet-50 rounded-lg p-4 mb-4">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-violet-600 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Sparkles className="w-4 h-4 text-white" />
                      </div>
                      <div>
                        <p className="text-sm text-stone-700 mb-2">
                          I'm your AI co-pilot for this opportunity. I can help you with market research, 
                          competitive analysis, business planning, and more. What would you like to explore?
                        </p>
                        <div className="flex flex-wrap gap-2">
                          <button className="text-xs px-3 py-1.5 bg-white border border-violet-200 rounded-full text-violet-700 hover:bg-violet-100">
                            Analyze competition
                          </button>
                          <button className="text-xs px-3 py-1.5 bg-white border border-violet-200 rounded-full text-violet-700 hover:bg-violet-100">
                            Suggest next steps
                          </button>
                          <button className="text-xs px-3 py-1.5 bg-white border border-violet-200 rounded-full text-violet-700 hover:bg-violet-100">
                            Create business plan outline
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={aiMessage}
                      onChange={(e) => setAiMessage(e.target.value)}
                      placeholder="Ask the AI assistant..."
                      className="flex-1 px-4 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:border-violet-400"
                    />
                    <button className="px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700">
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
