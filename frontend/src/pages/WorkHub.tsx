import { useState, useEffect, useRef } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { 
  ArrowLeft, BarChart3, BookOpen, Briefcase, CheckCircle, CheckCircle2,
  ChevronRight, DollarSign, ExternalLink, FileText, 
  Loader2, PanelLeftClose, PanelLeftOpen,
  Rocket, Search, Send, Settings, Sparkles, Target, 
  TrendingUp, Users, Wrench, X, Zap
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

type WorkspaceStatus = 'researching' | 'validating' | 'planning' | 'building' | 'launched' | 'paused' | 'archived'

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
  ai_analyzed?: boolean
  ai_summary?: string | null
  ai_market_size_estimate?: string | null
  ai_competition_level?: string | null
  ai_target_audience?: string | null
  ai_problem_statement?: string | null
  ai_business_model_suggestions?: string[] | null
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
  notes: { id: number; title: string | null; content: string; is_pinned: boolean; created_at: string }[]
  tasks: { id: number; title: string; is_completed: boolean; priority: string }[]
  documents: { id: number; name: string; doc_type: string | null; content: string | null; created_at: string }[]
}

type ChatMessage = {
  id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

type RecommendedExpert = {
  id: number
  user_id: number
  name: string | null
  avatar_url: string | null
  primary_category: string | null
  match_score: number
  match_reason: string
}

const workflowStages = [
  { key: 'researching' as WorkspaceStatus, label: 'Validate', icon: CheckCircle, color: 'emerald', description: 'Confirm demand with real data' },
  { key: 'validating' as WorkspaceStatus, label: 'Research', icon: Search, color: 'blue', description: 'Analyze market and competition' },
  { key: 'planning' as WorkspaceStatus, label: 'Plan', icon: Target, color: 'purple', description: 'Build your business model' },
  { key: 'building' as WorkspaceStatus, label: 'Execute', icon: Zap, color: 'amber', description: 'Launch and scale' },
]

type ParsedBlock = 
  | { type: 'text'; content: string }
  | { type: 'checklist'; items: { text: string; checked: boolean }[] }
  | { type: 'data_card'; title: string; items: { label: string; value: string }[] }
  | { type: 'action_card'; title: string; description: string; action?: string; link?: string }

function parseMessageContent(content: string): ParsedBlock[] {
  const blocks: ParsedBlock[] = []
  
  const checklistMatch = content.match(/(?:^|\n)(?:[\-\*\u2610\u2611\u2612]|\d+\.)\s+.+(?:\n(?:[\-\*\u2610\u2611\u2612]|\d+\.)\s+.+)*/gm)
  
  if (checklistMatch) {
    let remaining = content
    for (const match of checklistMatch) {
      const idx = remaining.indexOf(match)
      if (idx > 0) {
        blocks.push({ type: 'text', content: remaining.slice(0, idx).trim() })
      }
      
      const items = match.split('\n').filter(l => l.trim()).map(line => {
        const checked = line.includes('\u2611') || line.includes('[x]') || line.includes('[X]')
        const text = line.replace(/^[\-\*\u2610\u2611\u2612\[\]xX]|\d+\.\s*/, '').trim()
        return { text, checked }
      })
      
      if (items.length >= 2) {
        blocks.push({ type: 'checklist', items })
      } else {
        blocks.push({ type: 'text', content: match })
      }
      
      remaining = remaining.slice(idx + match.length)
    }
    if (remaining.trim()) {
      blocks.push({ type: 'text', content: remaining.trim() })
    }
  } else {
    blocks.push({ type: 'text', content })
  }
  
  return blocks
}

function PaidReportCard({ opportunityId }: { opportunityId: number }) {
  return (
    <div className="bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-50 rounded-xl border border-violet-200 p-4 mt-3">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center flex-shrink-0">
          <FileText className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-semibold text-stone-900 mb-1">Deep Dive Report Available</h4>
          <p className="text-xs text-stone-600 mb-3">
            Get a comprehensive analysis including market research, competitor breakdown, financial projections, and actionable roadmap.
          </p>
          <div className="flex flex-wrap gap-2">
            <Link 
              to={`/opportunity/${opportunityId}?tab=research`}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-violet-600 text-white text-xs font-medium rounded-lg hover:bg-violet-700 transition-colors"
            >
              <Sparkles className="w-3 h-3" />
              View Full Report
            </Link>
            <span className="inline-flex items-center px-2 py-1.5 text-xs text-violet-600 font-medium">
              Included in Pro
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

function MessageContent({ content, isUser, opportunityId }: { content: string; isUser: boolean; opportunityId?: number }) {
  if (isUser) {
    return <p className="text-sm whitespace-pre-wrap">{content}</p>
  }
  
  const blocks = parseMessageContent(content)
  
  const reportKeywords = ['detailed analysis', 'full report', 'deep dive', 'comprehensive research', 'market research report', 'competitor analysis report', 'financial projections']
  const showReportCTA = opportunityId && reportKeywords.some(kw => content.toLowerCase().includes(kw))
  
  return (
    <div className="space-y-3">
      {blocks.map((block, idx) => {
        if (block.type === 'text') {
          return <p key={idx} className="text-sm whitespace-pre-wrap">{block.content}</p>
        }
        
        if (block.type === 'checklist') {
          return (
            <div key={idx} className="bg-stone-50 rounded-lg p-3 border border-stone-100">
              <div className="space-y-2">
                {block.items.map((item, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <div className={`w-4 h-4 mt-0.5 rounded border flex items-center justify-center flex-shrink-0 ${
                      item.checked ? 'bg-emerald-500 border-emerald-500 text-white' : 'border-stone-300 bg-white'
                    }`}>
                      {item.checked && <CheckCircle className="w-3 h-3" />}
                    </div>
                    <span className={`text-sm ${item.checked ? 'text-stone-400 line-through' : 'text-stone-700'}`}>
                      {item.text}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )
        }
        
        if (block.type === 'data_card') {
          return (
            <div key={idx} className="bg-gradient-to-br from-violet-50 to-purple-50 rounded-lg p-3 border border-violet-100">
              <h4 className="text-sm font-semibold text-violet-900 mb-2">{block.title}</h4>
              <div className="grid grid-cols-2 gap-2">
                {block.items.map((item, i) => (
                  <div key={i}>
                    <p className="text-xs text-violet-600">{item.label}</p>
                    <p className="text-sm font-medium text-stone-900">{item.value}</p>
                  </div>
                ))}
              </div>
            </div>
          )
        }
        
        return null
      })}
      {showReportCTA && <PaidReportCard opportunityId={opportunityId} />}
    </div>
  )
}

const stageQuickActions: Record<WorkspaceStatus, { label: string; icon: typeof CheckCircle; action: string }[]> = {
  researching: [
    { label: 'View Signals', icon: TrendingUp, action: 'view_signals' },
    { label: 'Check Competition', icon: Users, action: 'check_competition' },
    { label: 'Search Web', icon: Search, action: 'web_search' },
  ],
  validating: [
    { label: 'Market Analysis', icon: BarChart3, action: 'market_analysis' },
    { label: 'Customer Segments', icon: Users, action: 'customer_segments' },
    { label: 'Search Trends', icon: TrendingUp, action: 'search_trends' },
  ],
  planning: [
    { label: 'Business Canvas', icon: Briefcase, action: 'business_canvas' },
    { label: 'Pricing Model', icon: DollarSign, action: 'pricing_model' },
    { label: 'Risk Analysis', icon: Target, action: 'risk_analysis' },
  ],
  building: [
    { label: 'Formation Guide', icon: BookOpen, action: 'formation_guide' },
    { label: 'Tool Stack', icon: Wrench, action: 'tool_stack' },
    { label: 'Find Funding', icon: DollarSign, action: 'find_funding' },
    { label: 'Find Expert', icon: Users, action: 'find_expert' },
  ],
  launched: [],
  paused: [],
  archived: [],
}

export default function WorkHub() {
  const { id } = useParams()
  const opportunityId = Number(id)
  const { token, isAuthenticated } = useAuthStore()
  const queryClient = useQueryClient()
  const chatContainerRef = useRef<HTMLDivElement>(null)

  const [activeStage, setActiveStage] = useState<WorkspaceStatus>('researching')
  const [leftPanelOpen, setLeftPanelOpen] = useState(true)
  const [chatMessage, setChatMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [agentName, setAgentName] = useState(() => {
    try {
      return localStorage.getItem('agent-name') || 'Atlas'
    } catch {
      return 'Atlas'
    }
  })
  const [claudeApiKey, setClaudeApiKey] = useState('')
  const [keyStatus, setKeyStatus] = useState<{has_key: boolean, is_valid: boolean} | null>(null)
  const [savingKey, setSavingKey] = useState(false)
  const [keyError, setKeyError] = useState('')

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

  const workspaceQuery = useQuery({
    queryKey: ['workspace-auto', opportunityId],
    enabled: isAuthenticated && Boolean(token) && Number.isFinite(opportunityId),
    queryFn: async (): Promise<Workspace> => {
      const res = await fetch(`/api/v1/workspaces/get-or-create/${opportunityId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to load/create workspace')
      return await res.json()
    },
  })

  const workspaceId = workspaceQuery.data?.id

  const chatHistoryQuery = useQuery({
    queryKey: ['chat-history', workspaceId],
    enabled: Boolean(workspaceId) && Boolean(token),
    queryFn: async (): Promise<ChatMessage[]> => {
      if (!workspaceId) return []
      const res = await fetch(`/api/v1/ai-cofounder/workspace/${workspaceId}/chat-history`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) return []
      return await res.json()
    },
  })

  const expertsQuery = useQuery({
    queryKey: ['opportunity-experts', opportunityId],
    enabled: Number.isFinite(opportunityId),
    queryFn: async (): Promise<{ experts: RecommendedExpert[]; total: number }> => {
      const res = await fetch(`/api/v1/opportunities/${opportunityId}/experts?limit=3`)
      if (!res.ok) return { experts: [], total: 0 }
      return await res.json()
    },
  })

  const updateStatusMutation = useMutation({
    mutationFn: async (newStatus: WorkspaceStatus) => {
      const res = await fetch(`/api/v1/workspaces/${workspaceId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ status: newStatus }),
      })
      if (!res.ok) throw new Error('Failed to update status')
      return await res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId] })
    },
  })

  const sendMessageMutation = useMutation({
    mutationFn: async (message: string): Promise<{ response: string; chat_history: ChatMessage[] }> => {
      if (!workspaceId) throw new Error('No workspace')
      const res = await fetch(`/api/v1/ai-cofounder/workspace/${workspaceId}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ message, stage: activeStage }),
      })
      if (!res.ok) throw new Error('Failed to send message')
      return await res.json()
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['chat-history', workspaceId], data.chat_history)
      setIsTyping(false)
    },
    onError: () => {
      setIsTyping(false)
    },
  })

  const createTaskMutation = useMutation({
    mutationFn: async (title: string) => {
      const res = await fetch(`/api/v1/workspaces/${workspaceId}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ title, priority: 'medium' }),
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

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }, [chatHistoryQuery.data, isTyping])

  useEffect(() => {
    if (workspaceQuery.data?.status) {
      setActiveStage(workspaceQuery.data.status)
    }
  }, [workspaceQuery.data?.status])

  const handleSendMessage = () => {
    if (!chatMessage.trim() || sendMessageMutation.isPending) return
    setIsTyping(true)
    sendMessageMutation.mutate(chatMessage.trim())
    setChatMessage('')
  }

  const handleQuickAction = (action: string) => {
    const actionMessages: Record<string, string> = {
      view_signals: 'Show me the demand signals for this opportunity.',
      check_competition: 'Who are the main competitors in this space?',
      web_search: 'Search the web for recent news about this market.',
      market_analysis: 'Give me a market analysis with TAM, SAM, and SOM.',
      customer_segments: 'Who are the target customer segments?',
      search_trends: 'What are the search trends for this category?',
      business_canvas: 'Help me fill out the business model canvas.',
      pricing_model: 'What pricing models would work for this business?',
      risk_analysis: 'What are the key risks I should be aware of?',
      formation_guide: 'Guide me through business formation steps.',
      tool_stack: 'What tools do I need to launch this business?',
      find_funding: 'What funding options are available for this type of business?',
      find_expert: 'Help me find an expert to work with.',
    }
    const message = actionMessages[action] || `Help me with ${action}`
    setChatMessage(message)
    setTimeout(() => handleSendMessage(), 100)
  }

  const handleStageChange = (newStage: WorkspaceStatus) => {
    setActiveStage(newStage)
    if (workspaceId && newStage !== workspaceQuery.data?.status) {
      updateStatusMutation.mutate(newStage)
    }
  }

  const saveAgentName = (name: string) => {
    setAgentName(name)
    try {
      localStorage.setItem('agent-name', name)
    } catch {}
    setShowSettings(false)
  }

  const fetchKeyStatus = async () => {
    if (!token) return
    try {
      const res = await fetch('/api/byok/status', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        const data = await res.json()
        setKeyStatus(data.keys?.claude || null)
      }
    } catch {}
  }

  const saveClaudeKey = async () => {
    if (!claudeApiKey.trim()) return
    setSavingKey(true)
    setKeyError('')
    try {
      const res = await fetch('/api/byok/set', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ provider: 'claude', api_key: claudeApiKey.trim() }),
      })
      if (res.ok) {
        setClaudeApiKey('')
        fetchKeyStatus()
      } else {
        const data = await res.json()
        setKeyError(data.detail || 'Failed to save key')
      }
    } catch (e) {
      setKeyError('Failed to connect')
    } finally {
      setSavingKey(false)
    }
  }

  const removeClaudeKey = async () => {
    try {
      const res = await fetch('/api/byok/claude', {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        setKeyStatus(null)
      }
    } catch {}
  }

  useEffect(() => {
    if (showSettings && token) {
      fetchKeyStatus()
    }
  }, [showSettings, token])

  const opp = opportunityQuery.data
  const workspace = workspaceQuery.data
  const chatMessages = chatHistoryQuery.data || []
  const experts = expertsQuery.data?.experts || []
  const currentStageIndex = workflowStages.findIndex(s => s.key === activeStage)

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

  if (workspaceQuery.isLoading) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-violet-600 mx-auto mb-4" />
          <p className="text-stone-600">Setting up your workspace...</p>
        </div>
      </div>
    )
  }

  if (workspaceQuery.isError || !workspace) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="max-w-md text-center bg-white rounded-xl border border-stone-200 p-8">
          <Rocket className="w-16 h-16 text-stone-300 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-stone-900 mb-2">Unable to create workspace</h2>
          <p className="text-stone-600 mb-6">Please sign in to start working on this opportunity.</p>
          <Link 
            to="/login"
            className="w-full py-3 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700 flex items-center justify-center gap-2"
          >
            <Sparkles className="w-5 h-5" />
            Sign In
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen bg-stone-50 flex flex-col">
      {/* Top Bar */}
      <div className="bg-white border-b border-stone-200 px-4 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-2">
          <button 
            onClick={() => setLeftPanelOpen(!leftPanelOpen)}
            className="text-stone-500 hover:text-stone-700 p-1.5 hover:bg-stone-100 rounded-lg lg:hidden"
          >
            <PanelLeftOpen className="w-5 h-5" />
          </button>
          <Link to="/projects" className="text-stone-500 hover:text-stone-700">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="font-semibold text-stone-900 text-sm truncate max-w-[150px] sm:max-w-xs">{opp.title}</h1>
            <p className="text-xs text-stone-500">{opp.category}</p>
          </div>
        </div>
        
        {/* Stage Navigation */}
        <div className="flex items-center gap-0.5 sm:gap-1 bg-stone-100 rounded-lg p-0.5 sm:p-1 overflow-x-auto">
          {workflowStages.map((stage, idx) => {
            const Icon = stage.icon
            const isActive = stage.key === activeStage
            const isPast = idx < currentStageIndex
            return (
              <button
                key={stage.key}
                onClick={() => handleStageChange(stage.key)}
                className={`flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-1.5 rounded-md text-xs sm:text-sm font-medium transition-all whitespace-nowrap ${
                  isActive 
                    ? 'bg-white shadow text-violet-700' 
                    : isPast 
                      ? 'text-stone-600 hover:bg-stone-200' 
                      : 'text-stone-400 hover:bg-stone-200'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 sm:w-4 sm:h-4 ${isActive ? 'text-violet-600' : isPast ? 'text-emerald-500' : ''}`} />
                <span className="hidden sm:inline">{stage.label}</span>
              </button>
            )
          })}
        </div>

        <button 
          onClick={() => setShowSettings(true)}
          className="text-stone-500 hover:text-stone-700 p-2 hover:bg-stone-100 rounded-lg"
        >
          <Settings className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 flex overflow-hidden relative">
        {/* Mobile Overlay */}
        {leftPanelOpen && (
          <div 
            className="fixed inset-0 bg-black/30 z-20 lg:hidden"
            onClick={() => setLeftPanelOpen(false)}
          />
        )}
        
        {/* Left Context Panel - Drawer on mobile */}
        <div className={`
          fixed lg:relative inset-y-0 left-0 z-30 lg:z-auto
          ${leftPanelOpen ? 'translate-x-0 w-72' : '-translate-x-full lg:translate-x-0 lg:w-0'} 
          bg-white border-r border-stone-200 flex-shrink-0 overflow-hidden 
          transition-all duration-300 lg:transition-none
        `}>
          <div className="h-full overflow-y-auto p-4 w-72">
            {/* Opportunity Summary */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-semibold text-stone-500 uppercase tracking-wide">This Opportunity</h3>
                <button onClick={() => setLeftPanelOpen(false)} className="text-stone-400 hover:text-stone-600">
                  <PanelLeftClose className="w-4 h-4" />
                </button>
              </div>
              <div className="space-y-3">
                <div className="bg-gradient-to-br from-violet-50 to-purple-50 rounded-lg p-3 border border-violet-100">
                  <p className="text-xs text-violet-600 font-medium mb-1">Market Size</p>
                  <p className="text-lg font-bold text-stone-900">{opp.ai_market_size_estimate || opp.market_size || 'TBD'}</p>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-stone-50 rounded-lg p-2 border border-stone-100">
                    <p className="text-xs text-stone-500">Signals</p>
                    <p className="text-sm font-semibold text-stone-900">{opp.validation_count}</p>
                  </div>
                  <div className="bg-stone-50 rounded-lg p-2 border border-stone-100">
                    <p className="text-xs text-stone-500">Competition</p>
                    <p className="text-sm font-semibold text-stone-900">{opp.ai_competition_level || 'N/A'}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Tasks - Interactive */}
            {workspace && (
              <div className="mb-6">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-xs font-semibold text-stone-500 uppercase tracking-wide">Tasks</h3>
                  <span className="text-xs text-stone-400">
                    {workspace.tasks.filter(t => t.is_completed).length}/{workspace.tasks.length}
                  </span>
                </div>
                <div className="flex gap-1 mb-2">
                  <input
                    type="text"
                    value={newTaskTitle}
                    onChange={(e) => setNewTaskTitle(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && newTaskTitle.trim() && createTaskMutation.mutate(newTaskTitle.trim())}
                    placeholder="Add task..."
                    className="flex-1 px-2 py-1.5 text-xs border border-stone-200 rounded-lg focus:outline-none focus:border-violet-400"
                  />
                  <button
                    onClick={() => newTaskTitle.trim() && createTaskMutation.mutate(newTaskTitle.trim())}
                    disabled={!newTaskTitle.trim() || createTaskMutation.isPending}
                    className="p-1.5 bg-violet-600 text-white rounded-lg disabled:opacity-50"
                  >
                    <Zap className="w-3 h-3" />
                  </button>
                </div>
                <div className="space-y-1.5 max-h-40 overflow-y-auto">
                  {workspace.tasks.map(task => (
                    <button
                      key={task.id}
                      onClick={() => toggleTaskMutation.mutate({ taskId: task.id, completed: !task.is_completed })}
                      className="w-full flex items-center gap-2 text-sm text-left hover:bg-stone-50 rounded p-1 -ml-1"
                    >
                      <div className={`w-4 h-4 rounded border flex items-center justify-center flex-shrink-0 ${
                        task.is_completed ? 'bg-emerald-500 border-emerald-500 text-white' : 'border-stone-300'
                      }`}>
                        {task.is_completed && <CheckCircle className="w-3 h-3" />}
                      </div>
                      <span className={`truncate ${task.is_completed ? 'text-stone-400 line-through' : 'text-stone-700'}`}>
                        {task.title}
                      </span>
                    </button>
                  ))}
                  {workspace.tasks.length === 0 && (
                    <p className="text-xs text-stone-400 py-2">No tasks yet</p>
                  )}
                </div>
              </div>
            )}

            {/* Recommended Experts */}
            {experts.length > 0 && (
              <div className="mb-6">
                <h3 className="text-xs font-semibold text-stone-500 uppercase tracking-wide mb-3">Experts</h3>
                <div className="space-y-2">
                  {experts.map(expert => (
                    <div key={expert.id} className="flex items-center gap-2 p-2 bg-stone-50 rounded-lg border border-stone-100">
                      <div className="w-8 h-8 rounded-full bg-violet-100 flex items-center justify-center text-violet-600 font-semibold text-xs">
                        {expert.name?.charAt(0) || 'E'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-stone-900 truncate">{expert.name}</p>
                        <p className="text-xs text-stone-500 truncate">{expert.primary_category}</p>
                      </div>
                      <span className="text-xs text-violet-600 font-medium">{expert.match_score}%</span>
                    </div>
                  ))}
                  <Link to="/network" className="text-xs text-violet-600 hover:text-violet-700 font-medium flex items-center gap-1">
                    View all experts <ChevronRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            )}

            {/* Saved Documents */}
            {workspace && workspace.documents.length > 0 && (
              <div className="mb-6">
                <h3 className="text-xs font-semibold text-stone-500 uppercase tracking-wide mb-3">Documents</h3>
                <div className="space-y-2">
                  {workspace.documents.slice(0, 3).map(doc => (
                    <div key={doc.id} className="flex items-center gap-2 p-2 bg-stone-50 rounded-lg border border-stone-100">
                      <FileText className="w-4 h-4 text-stone-400" />
                      <span className="text-sm text-stone-700 truncate">{doc.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Quick Links */}
            <div>
              <h3 className="text-xs font-semibold text-stone-500 uppercase tracking-wide mb-3">Quick Links</h3>
              <div className="space-y-1">
                <Link to={`/opportunity/${opportunityId}`} className="flex items-center gap-2 p-2 text-sm text-stone-600 hover:bg-stone-50 rounded-lg">
                  <ExternalLink className="w-4 h-4" />
                  Opportunity Details
                </Link>
                <Link to="/funding" className="flex items-center gap-2 p-2 text-sm text-stone-600 hover:bg-stone-50 rounded-lg">
                  <DollarSign className="w-4 h-4" />
                  Funding Discovery
                </Link>
                <Link to="/network" className="flex items-center gap-2 p-2 text-sm text-stone-600 hover:bg-stone-50 rounded-lg">
                  <Users className="w-4 h-4" />
                  Expert Network
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Panel Toggle (when closed) - desktop only */}
        {!leftPanelOpen && (
          <button
            onClick={() => setLeftPanelOpen(true)}
            className="hidden lg:block absolute left-0 top-1/2 -translate-y-1/2 bg-white border border-stone-200 rounded-r-lg p-2 shadow-sm hover:bg-stone-50 z-10"
          >
            <PanelLeftOpen className="w-4 h-4 text-stone-600" />
          </button>
        )}

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col bg-stone-50 relative">
          {/* Stage Banner */}
          <div className={`px-6 py-3 border-b border-stone-200 bg-gradient-to-r ${
            activeStage === 'researching' ? 'from-emerald-50 to-green-50' :
            activeStage === 'validating' ? 'from-blue-50 to-cyan-50' :
            activeStage === 'planning' ? 'from-purple-50 to-violet-50' :
            'from-amber-50 to-orange-50'
          }`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {(() => {
                  const stage = workflowStages.find(s => s.key === activeStage)
                  const Icon = stage?.icon || CheckCircle
                  return <Icon className={`w-5 h-5 ${
                    activeStage === 'researching' ? 'text-emerald-600' :
                    activeStage === 'validating' ? 'text-blue-600' :
                    activeStage === 'planning' ? 'text-purple-600' :
                    'text-amber-600'
                  }`} />
                })()}
                <div>
                  <h2 className="font-semibold text-stone-900">
                    {workflowStages.find(s => s.key === activeStage)?.label} Stage
                  </h2>
                  <p className="text-xs text-stone-600">
                    {workflowStages.find(s => s.key === activeStage)?.description}
                  </p>
                </div>
              </div>
              {currentStageIndex < workflowStages.length - 1 && (
                <button
                  onClick={() => handleStageChange(workflowStages[currentStageIndex + 1].key)}
                  className="text-xs font-medium text-violet-600 hover:text-violet-700 flex items-center gap-1"
                >
                  Next: {workflowStages[currentStageIndex + 1].label}
                  <ChevronRight className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          {/* Execute Stage Toolkit */}
          {activeStage === 'building' && (
            <div className="px-6 py-4 bg-gradient-to-r from-amber-50 to-orange-50 border-b border-amber-100">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-amber-800">Launch Toolkit</h3>
                <span className="text-xs text-amber-600">Everything you need to go live</span>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <button
                  onClick={() => handleQuickAction('formation_guide')}
                  className="flex flex-col items-center gap-2 p-3 bg-white rounded-xl border border-amber-200 hover:border-amber-300 hover:shadow-sm transition-all group"
                >
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-100 to-orange-100 flex items-center justify-center group-hover:from-amber-200 group-hover:to-orange-200">
                    <BookOpen className="w-5 h-5 text-amber-600" />
                  </div>
                  <div className="text-center">
                    <p className="text-xs font-medium text-stone-900">Formation Guide</p>
                    <p className="text-xs text-stone-500">LLC, Corp, etc.</p>
                  </div>
                </button>
                
                <button
                  onClick={() => handleQuickAction('tool_stack')}
                  className="flex flex-col items-center gap-2 p-3 bg-white rounded-xl border border-amber-200 hover:border-amber-300 hover:shadow-sm transition-all group"
                >
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-violet-100 to-purple-100 flex items-center justify-center group-hover:from-violet-200 group-hover:to-purple-200">
                    <Wrench className="w-5 h-5 text-violet-600" />
                  </div>
                  <div className="text-center">
                    <p className="text-xs font-medium text-stone-900">Tool Stack</p>
                    <p className="text-xs text-stone-500">Recommended tools</p>
                  </div>
                </button>
                
                <Link
                  to="/funding"
                  className="flex flex-col items-center gap-2 p-3 bg-white rounded-xl border border-amber-200 hover:border-amber-300 hover:shadow-sm transition-all group"
                >
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-100 to-green-100 flex items-center justify-center group-hover:from-emerald-200 group-hover:to-green-200">
                    <DollarSign className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div className="text-center">
                    <p className="text-xs font-medium text-stone-900">Find Funding</p>
                    <p className="text-xs text-stone-500">SBA loans & more</p>
                  </div>
                </Link>
                
                <Link
                  to="/network"
                  className="flex flex-col items-center gap-2 p-3 bg-white rounded-xl border border-amber-200 hover:border-amber-300 hover:shadow-sm transition-all group"
                >
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-100 to-cyan-100 flex items-center justify-center group-hover:from-blue-200 group-hover:to-cyan-200">
                    <Users className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className="text-center">
                    <p className="text-xs font-medium text-stone-900">Find Expert</p>
                    <p className="text-xs text-stone-500">Get help launching</p>
                  </div>
                </Link>
              </div>
            </div>
          )}

          {/* Chat Messages */}
          <div ref={chatContainerRef} className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
            {chatMessages.length === 0 && !isTyping && (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gradient-to-br from-violet-100 to-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="w-8 h-8 text-violet-600" />
                </div>
                <h3 className="text-lg font-semibold text-stone-900 mb-2">Hi! I'm {agentName}, your AI co-founder</h3>
                <p className="text-stone-600 mb-6 max-w-md mx-auto">
                  You're in the <strong>{workflowStages.find(s => s.key === activeStage)?.label}</strong> stage. 
                  I can help you {workflowStages.find(s => s.key === activeStage)?.description.toLowerCase()}.
                </p>
                
                {/* Quick Actions */}
                <div className="flex flex-wrap justify-center gap-2 max-w-lg mx-auto">
                  {stageQuickActions[activeStage]?.map((action) => {
                    const Icon = action.icon
                    return (
                      <button
                        key={action.action}
                        onClick={() => handleQuickAction(action.action)}
                        className="flex items-center gap-2 px-4 py-2 bg-white border border-stone-200 rounded-lg text-sm font-medium text-stone-700 hover:bg-stone-50 hover:border-stone-300 transition-all"
                      >
                        <Icon className="w-4 h-4 text-violet-600" />
                        {action.label}
                      </button>
                    )
                  })}
                </div>
              </div>
            )}

            {chatMessages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-2xl rounded-2xl px-4 py-3 ${
                  msg.role === 'user' 
                    ? 'bg-violet-600 text-white' 
                    : 'bg-white border border-stone-200 text-stone-900'
                }`}>
                  {msg.role === 'assistant' && (
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="w-3 h-3 text-violet-600" />
                      <span className="text-xs font-medium text-violet-600">{agentName}</span>
                    </div>
                  )}
                  <MessageContent content={msg.content} isUser={msg.role === 'user'} opportunityId={opportunityId} />
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-white border border-stone-200 rounded-2xl px-4 py-3">
                  <div className="flex items-center gap-2 mb-1">
                    <Sparkles className="w-3 h-3 text-violet-600" />
                    <span className="text-xs font-medium text-violet-600">{agentName}</span>
                  </div>
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-stone-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-stone-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-stone-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Quick Actions Bar (when chat has messages) */}
          {chatMessages.length > 0 && (
            <div className="px-6 py-2 border-t border-stone-200 bg-white/50">
              <div className="flex gap-2 overflow-x-auto pb-1">
                {stageQuickActions[activeStage]?.map((action) => {
                  const Icon = action.icon
                  return (
                    <button
                      key={action.action}
                      onClick={() => handleQuickAction(action.action)}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-stone-100 rounded-full text-xs font-medium text-stone-600 hover:bg-stone-200 whitespace-nowrap"
                    >
                      <Icon className="w-3 h-3" />
                      {action.label}
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {/* Chat Input */}
          <div className="p-4 border-t border-stone-200 bg-white">
            <div className="flex items-center gap-3 max-w-3xl mx-auto">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                  placeholder={`Ask ${agentName} anything...`}
                  className="w-full px-4 py-3 pr-12 bg-stone-50 border border-stone-200 rounded-xl text-sm focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!chatMessage.trim() || sendMessageMutation.isPending}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-stone-900">Agent Settings</h2>
              <button onClick={() => setShowSettings(false)} className="text-stone-400 hover:text-stone-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">Agent Name</label>
                <input
                  type="text"
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                  className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:outline-none focus:border-violet-400"
                  placeholder="Give your AI a name..."
                />
              </div>

              <div className="bg-gradient-to-br from-violet-50 to-purple-50 rounded-lg p-4 border border-violet-200">
                <h3 className="font-medium text-stone-900 mb-2 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-violet-600" />
                  Bring Your Own Claude Key
                </h3>
                <p className="text-sm text-stone-600 mb-3">
                  Use your own Anthropic API key for AI chats. Save on subscription costs and pay only for what you use.
                </p>
                
                {keyStatus?.has_key ? (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                      <span className="text-emerald-700 font-medium">Claude API key connected</span>
                    </div>
                    <p className="text-xs text-stone-500">Your API key is securely encrypted and stored.</p>
                    <button
                      onClick={removeClaudeKey}
                      className="text-sm text-red-600 hover:text-red-700 font-medium"
                    >
                      Remove Key
                    </button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="flex gap-2">
                      <input
                        type="password"
                        value={claudeApiKey}
                        onChange={(e) => setClaudeApiKey(e.target.value)}
                        placeholder="sk-ant-..."
                        className="flex-1 px-3 py-2 text-sm border border-stone-200 rounded-lg focus:outline-none focus:border-violet-400"
                      />
                      <button
                        onClick={saveClaudeKey}
                        disabled={!claudeApiKey.trim() || savingKey}
                        className="px-3 py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 disabled:opacity-50"
                      >
                        {savingKey ? 'Saving...' : 'Save'}
                      </button>
                    </div>
                    {keyError && (
                      <p className="text-xs text-red-600">{keyError}</p>
                    )}
                    <a
                      href="https://console.anthropic.com/settings/keys"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-violet-600 hover:text-violet-700 font-medium flex items-center gap-1"
                    >
                      Get API Key from Anthropic
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                )}
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowSettings(false)}
                className="px-4 py-2 text-stone-600 hover:bg-stone-100 rounded-lg text-sm font-medium"
              >
                Cancel
              </button>
              <button
                onClick={() => saveAgentName(agentName)}
                className="px-4 py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700"
              >
                Save Settings
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
