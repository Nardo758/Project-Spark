import { useState, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { 
  ArrowLeft, BarChart3, Briefcase, CheckCircle, CheckCircle2, ChevronDown, ChevronRight, 
  Download, FileText, Lightbulb, Loader2, MapPin, PanelLeftClose, PanelLeftOpen,
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
  documents: { id: number; name: string; doc_type: string | null; content: string | null; created_at: string }[]
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
  const [workspaceSubTab, setWorkspaceSubTab] = useState<'tasks' | 'notes' | 'docs' | 'plan'>('tasks')
  const [businessPlanContent, setBusinessPlanContent] = useState('')
  const [businessPlanDocId, setBusinessPlanDocId] = useState<number | null>(null)
  const [isEditingPlan, setIsEditingPlan] = useState(false)
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [newNoteContent, setNewNoteContent] = useState('')
  const [aiMessage, setAiMessage] = useState('')
  const [validationPath, setValidationPath] = useState<'platform' | 'new_idea' | 'locations' | null>(null)
  const [workspacePanelOpen, setWorkspacePanelOpen] = useState(false)
  const [showOnboarding, setShowOnboarding] = useState(() => {
    if (typeof window === 'undefined') return false
    try {
      return !localStorage.getItem('hub-onboarding-dismissed')
    } catch {
      return false
    }
  })
  
  const validationChecklistItems = [
    'Talked to 5+ potential customers',
    'Identified willingness to pay',
    'Confirmed problem urgency',
    'Validated solution approach',
    'Documented key insights',
  ]
  
  const launchChecklistItems = [
    'MVP feature complete',
    'Landing page live',
    'Payment integration',
    'Email list built',
    'Social media setup',
    'Launch announcement',
  ]
  
  const [validationChecked, setValidationChecked] = useState<Record<string, boolean>>({})
  const [launchChecked, setLaunchChecked] = useState<Record<string, boolean>>({})
  const [canvasData, setCanvasData] = useState<Record<string, string>>({})
  const [editingCanvas, setEditingCanvas] = useState<string | null>(null)
  const [canvasEditValue, setCanvasEditValue] = useState('')
  
  const canvasItemsBase = [
    { key: 'valueProp', title: 'Value Prop', placeholder: 'Core offering' },
    { key: 'customers', title: 'Customers', placeholder: 'Define segments' },
    { key: 'channels', title: 'Channels', placeholder: 'Distribution' },
    { key: 'revenue', title: 'Revenue', placeholder: 'Pricing model' },
    { key: 'resources', title: 'Resources', placeholder: 'Key assets' },
    { key: 'activities', title: 'Activities', placeholder: 'Core operations' },
    { key: 'partners', title: 'Partners', placeholder: 'Key alliances' },
    { key: 'costs', title: 'Costs', placeholder: 'Major expenses' },
    { key: 'advantage', title: 'Advantage', placeholder: 'Unique edge' },
  ]
  
  const [stateInitialized, setStateInitialized] = useState(false)
  
  useEffect(() => {
    setStateInitialized(false)
    try {
      const savedValidation = localStorage.getItem(`validation-checklist-${opportunityId}`)
      setValidationChecked(savedValidation ? JSON.parse(savedValidation) : {})
      
      const savedLaunch = localStorage.getItem(`launch-checklist-${opportunityId}`)
      setLaunchChecked(savedLaunch ? JSON.parse(savedLaunch) : {})
      
      const savedCanvas = localStorage.getItem(`canvas-${opportunityId}`)
      setCanvasData(savedCanvas ? JSON.parse(savedCanvas) : {})
      
      setEditingCanvas(null)
    } catch {
      setValidationChecked({})
      setLaunchChecked({})
      setCanvasData({})
    }
    setTimeout(() => setStateInitialized(true), 0)
  }, [opportunityId])
  
  useEffect(() => {
    if (stateInitialized) {
      localStorage.setItem(`validation-checklist-${opportunityId}`, JSON.stringify(validationChecked))
    }
  }, [validationChecked, opportunityId, stateInitialized])
  
  useEffect(() => {
    if (stateInitialized) {
      localStorage.setItem(`launch-checklist-${opportunityId}`, JSON.stringify(launchChecked))
    }
  }, [launchChecked, opportunityId, stateInitialized])
  
  useEffect(() => {
    if (stateInitialized) {
      localStorage.setItem(`canvas-${opportunityId}`, JSON.stringify(canvasData))
    }
  }, [canvasData, opportunityId, stateInitialized])

  const validateProgress = Math.round((Object.values(validationChecked).filter(Boolean).length / validationChecklistItems.length) * 100)
  const researchProgress = Math.round((Object.keys(canvasData).filter(k => canvasData[k]?.trim()).length / Math.ceil(canvasItemsBase.length / 2)) * 100)
  const planProgress = Math.round((Object.keys(canvasData).filter(k => canvasData[k]?.trim()).length / canvasItemsBase.length) * 100)
  const executeProgress = Math.round((Object.values(launchChecked).filter(Boolean).length / launchChecklistItems.length) * 100)
  
  const stageProgress: Record<WorkspaceStatus, number> = {
    researching: Math.min(validateProgress, 100),
    validating: Math.min(researchProgress, 100),
    planning: Math.min(planProgress, 100),
    building: Math.min(executeProgress, 100),
    launched: 100,
    paused: 0,
    archived: 0,
  }

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

  useEffect(() => {
    if (workspaceSubTab === 'plan' && workspaceQuery.data?.documents) {
      const businessPlanDocs = workspaceQuery.data.documents.filter(d => d.doc_type === 'business_plan')
      const latestPlan = businessPlanDocs.sort((a, b) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )[0]
      if (latestPlan?.content && latestPlan.id !== businessPlanDocId) {
        setBusinessPlanContent(latestPlan.content)
        setBusinessPlanDocId(latestPlan.id)
      }
    }
  }, [workspaceSubTab, workspaceQuery.data?.documents, businessPlanDocId])

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

  const saveReportMutation = useMutation({
    mutationFn: async (data: { name: string; doc_type: string; content: string }) => {
      if (!workspaceId) throw new Error('No workspace')
      const res = await fetch(`/api/v1/workspaces/${workspaceId}/documents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
      })
      if (!res.ok) throw new Error('Failed to save report')
      return await res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId] })
    },
  })

  const deleteDocMutation = useMutation({
    mutationFn: async (docId: number) => {
      const res = await fetch(`/api/v1/workspaces/${workspaceId}/documents/${docId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to delete document')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId] })
    },
  })

  const updateDocMutation = useMutation({
    mutationFn: async ({ docId, content }: { docId: number; content: string }) => {
      const res = await fetch(`/api/v1/workspaces/${workspaceId}/documents/${docId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ content }),
      })
      if (!res.ok) throw new Error('Failed to update document')
      return await res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId] })
    },
  })

  const chatMessages = chatHistoryQuery.data || []

  const generatePhaseReport = (phase: 'validate' | 'research' | 'plan' | 'execute') => {
    if (!opp) return
    const now = new Date().toLocaleDateString()
    let content = ''
    let title = ''
    
    if (phase === 'validate') {
      title = `Validation Report - ${now}`
      const checkedItems = validationChecklistItems.filter(item => validationChecked[item])
      content = `# Validation Report\n\n**Opportunity:** ${opp.title}\n**Date:** ${now}\n**Completion:** ${checkedItems.length}/${validationChecklistItems.length} items\n\n## Validation Checklist\n${validationChecklistItems.map(item => `- [${validationChecked[item] ? 'x' : ' '}] ${item}`).join('\n')}\n\n## Key Metrics\n- Community Interest: ${opp.validation_count} validations\n- Severity Score: ${opp.severity}/5\n- Feasibility: ${opp.feasibility_score ? Math.round(opp.feasibility_score) + '%' : 'N/A'}\n\n## AI Insights\n${opp.ai_summary || 'No AI analysis available'}`
    } else if (phase === 'research') {
      title = `Research Report - ${now}`
      content = `# Market Research Report\n\n**Opportunity:** ${opp.title}\n**Date:** ${now}\n\n## Market Size\n${opp.ai_market_size_estimate || opp.market_size || 'TBD'}\n\n## Target Audience\n${opp.ai_target_audience || 'TBD'}\n\n## Competition Level\n${opp.ai_competition_level || 'TBD'}\n\n## Problem Statement\n${opp.ai_problem_statement || opp.description}\n\n## Key Risks\n${opp.ai_key_risks?.map(r => `- ${r}`).join('\n') || 'Not analyzed'}`
    } else if (phase === 'plan') {
      title = `Business Plan - ${now}`
      const filledCanvas = canvasItemsBase.filter(c => canvasData[c.key]?.trim())
      content = `# Business Plan\n\n**Opportunity:** ${opp.title}\n**Date:** ${now}\n**Canvas Completion:** ${filledCanvas.length}/${canvasItemsBase.length} sections\n\n## Business Model Canvas\n${canvasItemsBase.map(c => `### ${c.title}\n${canvasData[c.key] || '_Not defined_'}`).join('\n\n')}\n\n## Suggested Business Models\n${opp.ai_business_model_suggestions?.map(s => `- ${s}`).join('\n') || 'Not available'}\n\n## Competitive Advantages\n${opp.ai_competitive_advantages?.map(a => `- ${a}`).join('\n') || 'Not available'}`
    } else {
      title = `Launch Report - ${now}`
      const checkedLaunch = launchChecklistItems.filter(item => launchChecked[item])
      content = `# Launch Execution Report\n\n**Opportunity:** ${opp.title}\n**Date:** ${now}\n**Launch Progress:** ${checkedLaunch.length}/${launchChecklistItems.length} items\n\n## Launch Checklist\n${launchChecklistItems.map(item => `- [${launchChecked[item] ? 'x' : ' '}] ${item}`).join('\n')}\n\n## Next Steps\n${opp.ai_next_steps?.map(s => `- ${s}`).join('\n') || 'Review your launch checklist and complete remaining items.'}`
    }
    
    saveReportMutation.mutate({ name: title, doc_type: phase, content })
  }

  const downloadAsPdf = (doc: { name: string; content: string | null }) => {
    if (!doc.content) return
    const printWindow = window.open('', '_blank')
    if (printWindow) {
      printWindow.document.write(`
        <html><head><title>${doc.name}</title>
        <style>body{font-family:system-ui,sans-serif;padding:40px;max-width:800px;margin:0 auto;line-height:1.6}h1,h2,h3{color:#1a1a1a}h1{border-bottom:2px solid #8b5cf6;padding-bottom:10px}h2{color:#6d28d9;margin-top:24px}h3{color:#7c3aed}ul{padding-left:20px}li{margin:4px 0}</style>
        </head><body>${doc.content.replace(/\n/g, '<br>').replace(/^# (.+)/gm, '<h1>$1</h1>').replace(/^## (.+)/gm, '<h2>$1</h2>').replace(/^### (.+)/gm, '<h3>$1</h3>').replace(/^- \[x\] (.+)/gm, '<li style="color:green">✓ $1</li>').replace(/^- \[ \] (.+)/gm, '<li style="color:gray">○ $1</li>').replace(/^- (.+)/gm, '<li>$1</li>')}</body></html>
      `)
      printWindow.document.close()
      printWindow.print()
    }
  }

  const generateFullBusinessPlan = () => {
    if (!opportunityQuery.data) return ''
    const o = opportunityQuery.data
    const now = new Date().toLocaleDateString()
    const checkedValidation = validationChecklistItems.filter(item => validationChecked[item])
    const checkedLaunch = launchChecklistItems.filter(item => launchChecked[item])
    const filledCanvas = canvasItemsBase.filter(c => canvasData[c.key]?.trim())
    
    return `# Business Plan
**${o.title}**
Generated: ${now}

---

## Executive Summary

${o.ai_summary || o.description || 'No summary available.'}

**Key Opportunity Metrics:**
- Severity Score: ${o.severity}/5
- Community Interest: ${o.validation_count} validations
- Feasibility: ${o.feasibility_score ? Math.round(o.feasibility_score) + '%' : 'N/A'}

---

## 1. Problem & Opportunity

### Problem Statement
${o.ai_problem_statement || o.description || 'Not defined'}

### Market Opportunity
${o.ai_summary || 'Market opportunity analysis pending.'}

---

## 2. Market Analysis

### Market Size
- **Total Addressable Market (TAM):** ${o.ai_market_size_estimate || o.market_size || 'TBD'}
- **Serviceable Addressable Market (SAM):** Est. 20-30% of TAM
- **Serviceable Obtainable Market (SOM):** Est. 5-10% of SAM

### Target Audience
${o.ai_target_audience || 'Target audience not yet defined.'}

### Competition Level
${o.ai_competition_level || 'Competition analysis pending.'}

### Key Risks
${o.ai_key_risks?.map(r => `- ${r}`).join('\n') || '- Risk analysis not yet completed'}

---

## 3. Validation Status

**Progress:** ${checkedValidation.length}/${validationChecklistItems.length} items completed

${validationChecklistItems.map(item => `- [${validationChecked[item] ? 'x' : ' '}] ${item}`).join('\n')}

---

## 4. Business Model

### Business Model Canvas
**Completion:** ${filledCanvas.length}/${canvasItemsBase.length} sections

${canvasItemsBase.map(c => `### ${c.title}
${canvasData[c.key] || '_Not yet defined_'}`).join('\n\n')}

### Suggested Business Models
${o.ai_business_model_suggestions?.map(s => `- ${s}`).join('\n') || '- Business model suggestions pending'}

### Competitive Advantages
${o.ai_competitive_advantages?.map(a => `- ${a}`).join('\n') || '- Competitive advantages not yet identified'}

---

## 5. Go-to-Market Strategy

### Launch Readiness
**Progress:** ${checkedLaunch.length}/${launchChecklistItems.length} items completed

${launchChecklistItems.map(item => `- [${launchChecked[item] ? 'x' : ' '}] ${item}`).join('\n')}

### Next Steps
${o.ai_next_steps?.map(s => `- ${s}`).join('\n') || '- Define immediate next steps for launch'}

---

## Appendix

**Category:** ${o.category || 'Uncategorized'}
**Created:** ${o.created_at ? new Date(o.created_at).toLocaleDateString() : 'N/A'}
`
  }

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

        {showOnboarding && (
          <div className="bg-gradient-to-r from-violet-50 to-purple-50 border border-violet-200 rounded-xl p-4 mb-6 relative">
            <button
              onClick={() => {
                localStorage.setItem('hub-onboarding-dismissed', 'true')
                setShowOnboarding(false)
              }}
              className="absolute top-3 right-3 text-violet-400 hover:text-violet-600"
            >
              <X className="w-4 h-4" />
            </button>
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-full bg-violet-100 flex items-center justify-center flex-shrink-0">
                <Lightbulb className="w-5 h-5 text-violet-600" />
              </div>
              <div>
                <h3 className="font-semibold text-stone-900 mb-1">Welcome to your Opportunity Hub!</h3>
                <p className="text-sm text-stone-600 mb-3">This is your command center for turning this opportunity into a real business. Here's how to get started:</p>
                <div className="grid sm:grid-cols-4 gap-3 text-xs">
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                    <span className="text-stone-700"><strong>Validate</strong> - Confirm demand with real data</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Search className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
                    <span className="text-stone-700"><strong>Research</strong> - Analyze market and competition</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Briefcase className="w-4 h-4 text-purple-500 flex-shrink-0 mt-0.5" />
                    <span className="text-stone-700"><strong>Plan</strong> - Build your business model</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Rocket className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
                    <span className="text-stone-700"><strong>Execute</strong> - Launch and scale</span>
                  </div>
                </div>
                <p className="text-xs text-violet-600 mt-3 flex items-center gap-1">
                  <Sparkles className="w-3 h-3" />
                  Tip: AI Co-Founder is available in each section to help guide you!
                </p>
              </div>
            </div>
          </div>
        )}

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
                      <div className="relative">
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
                        {stageProgress[stage.key] > 0 && stageProgress[stage.key] < 100 && !isCompleted && (
                          <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-white rounded-full flex items-center justify-center shadow-sm border border-stone-200">
                            <span className="text-[9px] font-bold text-violet-600">{stageProgress[stage.key]}</span>
                          </div>
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
                
                <div className="p-4 space-y-4 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 140px)' }}>
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
                      onClick={() => setWorkspaceSubTab('docs')}
                      className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                        workspaceSubTab === 'docs' ? 'bg-white text-violet-700 shadow-sm' : 'text-stone-600 hover:bg-white/50'
                      }`}
                    >
                      <FileText className="w-4 h-4" />
                      Reports ({workspace.documents.length})
                    </button>
                    <button
                      onClick={() => setWorkspaceSubTab('plan')}
                      className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                        workspaceSubTab === 'plan' ? 'bg-white text-violet-700 shadow-sm' : 'text-stone-600 hover:bg-white/50'
                      }`}
                    >
                      <Briefcase className="w-4 h-4" />
                      Business Plan
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
                    <p className="text-xs text-violet-600 italic">AI Co-Founder is available in each workflow stage below</p>
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

                  {workspaceSubTab === 'docs' && (
                    <div className="bg-white rounded-lg border border-stone-200 p-4">
                      <h4 className="font-medium text-stone-900 mb-3 flex items-center gap-2">
                        <FileText className="w-4 h-4 text-violet-600" />
                        Saved Reports
                      </h4>
                      <div className="space-y-2 max-h-[300px] overflow-y-auto">
                        {workspace.documents.map((doc) => (
                          <div key={doc.id} className="bg-stone-50 rounded-lg p-3 border border-stone-100">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <p className="text-sm font-medium text-stone-900">{doc.name}</p>
                                <p className="text-xs text-stone-500 mt-0.5">
                                  {doc.doc_type && <span className="capitalize">{doc.doc_type} Report</span>}
                                  {' • '}{new Date(doc.created_at).toLocaleDateString()}
                                </p>
                              </div>
                              <div className="flex items-center gap-1">
                                <button 
                                  onClick={() => downloadAsPdf(doc)}
                                  className="p-1.5 text-violet-600 hover:bg-violet-50 rounded"
                                  title="Download PDF"
                                >
                                  <Download className="w-3.5 h-3.5" />
                                </button>
                                <button 
                                  onClick={() => deleteDocMutation.mutate(doc.id)} 
                                  className="p-1.5 text-stone-400 hover:text-red-500 rounded"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                        {workspace.documents.length === 0 && (
                          <div className="text-center py-6">
                            <FileText className="w-8 h-8 mx-auto mb-2 text-stone-300" />
                            <p className="text-sm text-stone-400">No reports saved yet</p>
                            <p className="text-xs text-stone-400 mt-1">Generate reports from each workflow stage</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {workspaceSubTab === 'plan' && (
                    <div className="bg-white rounded-lg border border-stone-200 p-4">
                      <h4 className="font-medium text-stone-900 mb-3 flex items-center gap-2">
                        <Briefcase className="w-4 h-4 text-violet-600" />
                        Business Plan
                      </h4>
                      
                      {!businessPlanContent ? (
                        <div className="text-center py-6">
                          <Briefcase className="w-10 h-10 mx-auto mb-3 text-violet-300" />
                          <p className="text-sm text-stone-600 mb-2">Generate your complete business plan</p>
                          <p className="text-xs text-stone-400 mb-4">Compiles data from all 4 workflow stages into a structured document</p>
                          <button
                            onClick={() => {
                              const plan = generateFullBusinessPlan()
                              setBusinessPlanContent(plan)
                            }}
                            className="px-4 py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 flex items-center gap-2 mx-auto"
                          >
                            <Sparkles className="w-4 h-4" />
                            Generate from Journey
                          </button>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => setIsEditingPlan(!isEditingPlan)}
                                className={`px-3 py-1.5 rounded text-xs font-medium ${isEditingPlan ? 'bg-violet-100 text-violet-700' : 'bg-stone-100 text-stone-600 hover:bg-stone-200'}`}
                              >
                                {isEditingPlan ? 'Preview' : 'Edit'}
                              </button>
                              <button
                                onClick={() => {
                                  const plan = generateFullBusinessPlan()
                                  setBusinessPlanContent(plan)
                                }}
                                className="px-3 py-1.5 bg-stone-100 text-stone-600 rounded text-xs font-medium hover:bg-stone-200"
                              >
                                Regenerate
                              </button>
                            </div>
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => {
                                  const doc = { name: `Business Plan - ${opp.title}`, content: businessPlanContent }
                                  downloadAsPdf(doc as any)
                                }}
                                className="px-3 py-1.5 bg-emerald-100 text-emerald-700 rounded text-xs font-medium hover:bg-emerald-200 flex items-center gap-1"
                              >
                                <Download className="w-3 h-3" />
                                Export PDF
                              </button>
                              <button
                                onClick={() => {
                                  if (businessPlanDocId) {
                                    updateDocMutation.mutate({ docId: businessPlanDocId, content: businessPlanContent })
                                  } else {
                                    saveReportMutation.mutate({
                                      name: `Business Plan - ${new Date().toLocaleDateString()}`,
                                      content: businessPlanContent,
                                      doc_type: 'business_plan'
                                    })
                                  }
                                }}
                                disabled={saveReportMutation.isPending || updateDocMutation.isPending}
                                className="px-3 py-1.5 bg-violet-100 text-violet-700 rounded text-xs font-medium hover:bg-violet-200 flex items-center gap-1 disabled:opacity-50"
                              >
                                <FileText className="w-3 h-3" />
                                {(saveReportMutation.isPending || updateDocMutation.isPending) ? 'Saving...' : 'Save'}
                              </button>
                            </div>
                          </div>
                          
                          {isEditingPlan ? (
                            <textarea
                              value={businessPlanContent}
                              onChange={(e) => setBusinessPlanContent(e.target.value)}
                              className="w-full h-[300px] px-3 py-2 border border-stone-200 rounded-lg text-sm font-mono focus:outline-none focus:border-violet-400 resize-none"
                            />
                          ) : (
                            <div className="h-[300px] overflow-y-auto p-3 bg-stone-50 rounded-lg border border-stone-100">
                              <div className="prose prose-sm max-w-none">
                                {businessPlanContent.split('\n').map((line, i) => {
                                  if (line.startsWith('# ')) return <h1 key={i} className="text-lg font-bold text-stone-900 mt-4 mb-2">{line.slice(2)}</h1>
                                  if (line.startsWith('## ')) return <h2 key={i} className="text-base font-semibold text-stone-800 mt-3 mb-1">{line.slice(3)}</h2>
                                  if (line.startsWith('### ')) return <h3 key={i} className="text-sm font-medium text-stone-700 mt-2 mb-1">{line.slice(4)}</h3>
                                  if (line.startsWith('- ')) return <p key={i} className="text-sm text-stone-600 ml-4">• {line.slice(2)}</p>
                                  if (line.startsWith('**') && line.endsWith('**')) return <p key={i} className="text-sm font-semibold text-stone-700">{line.slice(2, -2)}</p>
                                  if (line.trim() === '') return <div key={i} className="h-2" />
                                  return <p key={i} className="text-sm text-stone-600">{line}</p>
                                })}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                </div>
                )}
              </div>
            )}

            <div className="flex-1 p-6">
              {/* VALIDATE STEP */}
              {activeTab === 'researching' && (
                <div className="space-y-6">
                  <div className="bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl p-6 border border-emerald-100">
                    <h2 className="text-xl font-bold text-stone-900 mb-2 flex items-center gap-2">
                      <CheckCircle className="w-6 h-6 text-emerald-600" />
                      Validate Your Opportunity
                    </h2>
                    <p className="text-stone-600 mb-6">Confirm this opportunity is worth pursuing with data-driven validation.</p>
                    
                    <div className="grid md:grid-cols-3 gap-4 mb-6">
                      <button 
                        onClick={() => setValidationPath('platform')}
                        className={`p-4 rounded-lg border-2 text-left transition-all ${validationPath === 'platform' ? 'border-emerald-500 bg-emerald-50' : 'border-stone-200 bg-white hover:border-emerald-300'}`}
                      >
                        <CheckCircle className="w-8 h-8 text-emerald-600 mb-2" />
                        <h3 className="font-semibold text-stone-900 mb-1">Platform Data</h3>
                        <p className="text-xs text-stone-500">Use existing platform signals and community validation</p>
                      </button>
                      <button 
                        onClick={() => setValidationPath('new_idea')}
                        className={`p-4 rounded-lg border-2 text-left transition-all ${validationPath === 'new_idea' ? 'border-blue-500 bg-blue-50' : 'border-stone-200 bg-white hover:border-blue-300'}`}
                      >
                        <Lightbulb className="w-8 h-8 text-blue-600 mb-2" />
                        <h3 className="font-semibold text-stone-900 mb-1">New Idea</h3>
                        <p className="text-xs text-stone-500">Research and validate your own unique concept</p>
                      </button>
                      <button 
                        onClick={() => setValidationPath('locations')}
                        className={`p-4 rounded-lg border-2 text-left transition-all ${validationPath === 'locations' ? 'border-amber-500 bg-amber-50' : 'border-stone-200 bg-white hover:border-amber-300'}`}
                      >
                        <MapPin className="w-8 h-8 text-amber-600 mb-2" />
                        <h3 className="font-semibold text-stone-900 mb-1">Location Analysis</h3>
                        <p className="text-xs text-stone-500">Find optimal geographic markets for this opportunity</p>
                      </button>
                    </div>
                  </div>

                  <div className="grid lg:grid-cols-2 gap-6">
                    <div className="bg-white rounded-xl border border-stone-200 p-5">
                      <h3 className="font-semibold text-stone-900 mb-4 flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-blue-500" />
                        Validation Metrics
                      </h3>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between p-3 bg-stone-50 rounded-lg">
                          <span className="text-sm text-stone-600">Community Interest</span>
                          <div className="flex items-center gap-2">
                            <div className="w-24 h-2 bg-stone-200 rounded-full overflow-hidden">
                              <div className="h-full bg-emerald-500" style={{ width: `${Math.min(opp.validation_count * 10, 100)}%` }} />
                            </div>
                            <span className="text-sm font-semibold text-stone-900">{opp.validation_count}</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-stone-50 rounded-lg">
                          <span className="text-sm text-stone-600">Problem Severity</span>
                          <div className="flex items-center gap-2">
                            <div className="w-24 h-2 bg-stone-200 rounded-full overflow-hidden">
                              <div className="h-full bg-amber-500" style={{ width: `${opp.severity * 10}%` }} />
                            </div>
                            <span className="text-sm font-semibold text-stone-900">{opp.severity}/10</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-stone-50 rounded-lg">
                          <span className="text-sm text-stone-600">Feasibility Score</span>
                          <div className="flex items-center gap-2">
                            <div className="w-24 h-2 bg-stone-200 rounded-full overflow-hidden">
                              <div className="h-full bg-violet-500" style={{ width: `${opp.feasibility_score || 0}%` }} />
                            </div>
                            <span className="text-sm font-semibold text-stone-900">{opp.feasibility_score || 'N/A'}%</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white rounded-xl border border-stone-200 p-5">
                      <h3 className="font-semibold text-stone-900 mb-4 flex items-center gap-2">
                        <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                        Quick Validation Checklist
                      </h3>
                      <p className="text-xs text-stone-500 mb-3">AI-verified items (auto-checked)</p>
                      <div className="space-y-2 mb-4">
                        {[
                          { label: 'Problem is clearly defined', done: !!opp.ai_problem_statement },
                          { label: 'Target audience identified', done: !!opp.ai_target_audience },
                          { label: 'Market size estimated', done: !!opp.ai_market_size_estimate },
                          { label: 'Competition level assessed', done: !!opp.ai_competition_level },
                          { label: 'AI analysis completed', done: !!opp.ai_analyzed },
                        ].map((item, i) => (
                          <div key={i} className={`flex items-center gap-3 p-2 rounded-lg ${item.done ? 'bg-emerald-50' : 'bg-stone-50'}`}>
                            <div className={`w-5 h-5 rounded-full flex items-center justify-center ${item.done ? 'bg-emerald-500 text-white' : 'border-2 border-stone-300'}`}>
                              {item.done && <CheckCircle2 className="w-3 h-3" />}
                            </div>
                            <span className={`text-sm ${item.done ? 'text-emerald-700' : 'text-stone-600'}`}>{item.label}</span>
                          </div>
                        ))}
                      </div>
                      <p className="text-xs text-stone-500 mb-3">Your validation progress (click to check)</p>
                      <div className="space-y-2">
                        {validationChecklistItems.map((item) => (
                          <button
                            key={item}
                            onClick={() => setValidationChecked(prev => ({ ...prev, [item]: !prev[item] }))}
                            className={`w-full flex items-center gap-3 p-2 rounded-lg transition-colors cursor-pointer ${validationChecked[item] ? 'bg-emerald-50 hover:bg-emerald-100' : 'bg-stone-50 hover:bg-stone-100'}`}
                          >
                            <div className={`w-5 h-5 rounded flex items-center justify-center flex-shrink-0 ${validationChecked[item] ? 'bg-emerald-500 text-white' : 'border-2 border-stone-300'}`}>
                              {validationChecked[item] && <CheckCircle2 className="w-3 h-3" />}
                            </div>
                            <span className={`text-sm text-left ${validationChecked[item] ? 'text-emerald-700 line-through' : 'text-stone-600'}`}>{item}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  {opp.ai_analyzed && (
                    <div className="bg-white rounded-xl border border-stone-200 p-5">
                      <h3 className="font-semibold text-stone-900 mb-4 flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-violet-500" />
                        AI Validation Summary
                      </h3>
                      {opp.ai_problem_statement && (
                        <p className="text-stone-600 mb-4">{opp.ai_problem_statement}</p>
                      )}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        <div className="p-3 bg-blue-50 rounded-lg text-center">
                          <p className="text-xs text-blue-600 mb-1">Market Size</p>
                          <p className="font-semibold text-stone-900 text-sm">{opp.ai_market_size_estimate || 'TBD'}</p>
                        </div>
                        <div className="p-3 bg-amber-50 rounded-lg text-center">
                          <p className="text-xs text-amber-600 mb-1">Competition</p>
                          <p className="font-semibold text-stone-900 text-sm">{opp.ai_competition_level || 'TBD'}</p>
                        </div>
                        <div className="p-3 bg-emerald-50 rounded-lg text-center">
                          <p className="text-xs text-emerald-600 mb-1">Target Audience</p>
                          <p className="font-semibold text-stone-900 text-sm">{opp.ai_target_audience || 'TBD'}</p>
                        </div>
                        <div className="p-3 bg-violet-50 rounded-lg text-center">
                          <p className="text-xs text-violet-600 mb-1">Urgency</p>
                          <p className="font-semibold text-stone-900 text-sm">{opp.ai_urgency_level || 'TBD'}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="bg-gradient-to-br from-violet-50 to-purple-50 rounded-xl border border-violet-200 p-5">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-stone-900 flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-violet-600" />
                        AI Co-Founder
                      </h3>
                      <span className="text-xs text-violet-600 bg-violet-100 px-2 py-1 rounded-full">Validate Stage</span>
                    </div>
                    <div className="grid md:grid-cols-3 gap-2 mb-4">
                      {[
                        'Is this problem worth solving?',
                        'Who are the ideal customers?',
                        'What makes this unique?',
                      ].map((prompt, i) => (
                        <button
                          key={i}
                          onClick={() => {
                            setAiMessage(prompt)
                            if (hasWorkspace) sendMessageMutation.mutate(prompt)
                          }}
                          className="p-2 text-xs text-left bg-white rounded-lg border border-violet-100 hover:border-violet-300 hover:bg-violet-50 transition-colors"
                        >
                          {prompt}
                        </button>
                      ))}
                    </div>
                    {chatMessages.length > 0 && (
                      <div className="mb-4 max-h-48 overflow-y-auto space-y-2 p-3 bg-white rounded-lg border border-violet-100">
                        {chatMessages.slice(-4).map((msg) => (
                          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[85%] rounded-lg p-2 text-xs ${
                              msg.role === 'user' ? 'bg-violet-600 text-white' : 'bg-stone-100 text-stone-700'
                            }`}>
                              {msg.content}
                            </div>
                          </div>
                        ))}
                        {sendMessageMutation.isPending && (
                          <div className="flex justify-start">
                            <div className="bg-stone-100 rounded-lg p-2 text-xs text-stone-500 flex items-center gap-2">
                              <Loader2 className="w-3 h-3 animate-spin" /> Thinking...
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <input
                        type="text"
                        value={aiMessage}
                        onChange={(e) => setAiMessage(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && aiMessage.trim() && hasWorkspace && sendMessageMutation.mutate(aiMessage.trim())}
                        placeholder="Ask AI about validating this opportunity..."
                        className="flex-1 px-3 py-2 border border-violet-200 rounded-lg text-sm focus:outline-none focus:border-violet-400 bg-white"
                      />
                      <button
                        onClick={() => aiMessage.trim() && hasWorkspace && sendMessageMutation.mutate(aiMessage.trim())}
                        disabled={!aiMessage.trim() || !hasWorkspace || sendMessageMutation.isPending}
                        className="p-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 disabled:opacity-50"
                      >
                        <Send className="w-4 h-4" />
                      </button>
                    </div>
                    {!hasWorkspace && (
                      <p className="text-xs text-violet-600 mt-2">Create a workspace to chat with the AI Co-Founder</p>
                    )}
                  </div>

                  <div className="flex justify-between items-center">
                    <button
                      onClick={() => generatePhaseReport('validate')}
                      disabled={saveReportMutation.isPending}
                      className="px-4 py-2 border border-violet-200 text-violet-700 rounded-lg text-sm font-medium hover:bg-violet-50 flex items-center gap-2 disabled:opacity-50"
                    >
                      <FileText className="w-4 h-4" />
                      {saveReportMutation.isPending ? 'Saving...' : 'Save Report'}
                    </button>
                    <button
                      onClick={() => setActiveTab('validating')}
                      className="px-6 py-3 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700 flex items-center gap-2"
                    >
                      Continue to Research
                      <ChevronRight className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              )}

              {/* RESEARCH STEP */}
              {activeTab === 'validating' && (
                <div className="space-y-6">
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
                    <h2 className="text-xl font-bold text-stone-900 mb-2 flex items-center gap-2">
                      <Search className="w-6 h-6 text-blue-600" />
                      Market Research
                    </h2>
                    <p className="text-stone-600">Deep dive into market dynamics, competition, and customer segments.</p>
                  </div>

                  <div className="grid lg:grid-cols-3 gap-6">
                    <div className="bg-white rounded-xl border border-stone-200 p-5">
                      <h3 className="font-semibold text-stone-900 mb-4 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-emerald-500" />
                        TAM / SAM / SOM
                      </h3>
                      <div className="space-y-4">
                        <div className="p-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg border border-emerald-100">
                          <p className="text-xs text-emerald-600 font-medium mb-1">Total Addressable Market</p>
                          <p className="text-2xl font-bold text-stone-900">{opp.ai_market_size_estimate || '$--'}</p>
                          <p className="text-xs text-stone-500 mt-1">Everyone who could use this solution</p>
                        </div>
                        <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-100">
                          <p className="text-xs text-blue-600 font-medium mb-1">Serviceable Addressable Market</p>
                          <p className="text-xl font-bold text-stone-900">Est. 20-30% of TAM</p>
                          <p className="text-xs text-stone-500 mt-1">Reachable with your business model</p>
                        </div>
                        <div className="p-4 bg-gradient-to-r from-violet-50 to-purple-50 rounded-lg border border-violet-100">
                          <p className="text-xs text-violet-600 font-medium mb-1">Serviceable Obtainable Market</p>
                          <p className="text-xl font-bold text-stone-900">Est. 5-10% of SAM</p>
                          <p className="text-xs text-stone-500 mt-1">Realistic first-year target</p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white rounded-xl border border-stone-200 p-5">
                      <h3 className="font-semibold text-stone-900 mb-4 flex items-center gap-2">
                        <Users className="w-5 h-5 text-violet-500" />
                        Customer Segments
                      </h3>
                      <div className="space-y-3">
                        {[
                          { segment: 'Early Adopters', desc: 'Tech-savvy innovators', pct: 15 },
                          { segment: 'Small Businesses', desc: 'Resource-constrained teams', pct: 35 },
                          { segment: 'Enterprise', desc: 'Large organizations', pct: 25 },
                          { segment: 'Consumers', desc: 'Individual end-users', pct: 25 },
                        ].map((seg, i) => (
                          <div key={i} className="p-3 bg-stone-50 rounded-lg">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-sm font-medium text-stone-900">{seg.segment}</span>
                              <span className="text-xs text-violet-600 font-medium">{seg.pct}%</span>
                            </div>
                            <p className="text-xs text-stone-500">{seg.desc}</p>
                            <div className="mt-2 h-1.5 bg-stone-200 rounded-full overflow-hidden">
                              <div className="h-full bg-violet-500" style={{ width: `${seg.pct}%` }} />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="bg-white rounded-xl border border-stone-200 p-5">
                      <h3 className="font-semibold text-stone-900 mb-4 flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-amber-500" />
                        Competitive Landscape
                      </h3>
                      <div className="space-y-3">
                        <div className="p-3 bg-amber-50 rounded-lg border border-amber-100">
                          <p className="text-xs text-amber-600 font-medium mb-1">Competition Level</p>
                          <p className="text-lg font-bold text-stone-900">{opp.ai_competition_level || 'Unknown'}</p>
                        </div>
                        {opp.ai_competitive_advantages && opp.ai_competitive_advantages.length > 0 && (
                          <div>
                            <p className="text-xs text-stone-500 mb-2">Potential Advantages:</p>
                            <div className="space-y-2">
                              {opp.ai_competitive_advantages.map((adv, i) => (
                                <div key={i} className="flex items-start gap-2 p-2 bg-emerald-50 rounded-lg">
                                  <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                                  <span className="text-xs text-stone-700">{adv}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        {opp.ai_key_risks && opp.ai_key_risks.length > 0 && (
                          <div>
                            <p className="text-xs text-stone-500 mb-2">Key Risks:</p>
                            <div className="space-y-2">
                              {opp.ai_key_risks.map((risk, i) => (
                                <div key={i} className="flex items-start gap-2 p-2 bg-red-50 rounded-lg">
                                  <X className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
                                  <span className="text-xs text-stone-700">{risk}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="grid lg:grid-cols-2 gap-6">
                    <div className="bg-white rounded-xl border border-stone-200 p-5">
                      <h3 className="font-semibold text-stone-900 mb-4 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-blue-500" />
                        Market Trends & Signals
                      </h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center p-4 bg-stone-50 rounded-lg">
                          <p className="text-2xl font-bold text-stone-900">{opp.validation_count}</p>
                          <p className="text-xs text-stone-500 mt-1">Validations</p>
                        </div>
                        <div className="text-center p-4 bg-stone-50 rounded-lg">
                          <p className="text-2xl font-bold text-emerald-600">{opp.growth_rate ? `+${opp.growth_rate}%` : '--'}</p>
                          <p className="text-xs text-stone-500 mt-1">Growth</p>
                        </div>
                        <div className="text-center p-4 bg-stone-50 rounded-lg">
                          <p className="text-2xl font-bold text-blue-600">{opp.geographic_scope || 'Global'}</p>
                          <p className="text-xs text-stone-500 mt-1">Scope</p>
                        </div>
                        <div className="text-center p-4 bg-stone-50 rounded-lg">
                          <p className="text-2xl font-bold text-violet-600">{opp.severity}/10</p>
                          <p className="text-xs text-stone-500 mt-1">Pain</p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white rounded-xl border border-stone-200 p-5">
                      <h3 className="font-semibold text-stone-900 mb-4 flex items-center gap-2">
                        <Users className="w-5 h-5 text-violet-500" />
                        Recommended Experts
                      </h3>
                      {experts.length > 0 ? (
                        <div className="space-y-3">
                          {experts.slice(0, 3).map((expert) => (
                            <div key={expert.id} className="flex items-center gap-3 p-3 bg-stone-50 rounded-lg">
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
                          <Link to="/network/experts" className="block text-center text-sm text-violet-600 font-medium hover:text-violet-700 mt-2">
                            View all experts
                          </Link>
                        </div>
                      ) : (
                        <p className="text-sm text-stone-500 p-4 bg-stone-50 rounded-lg text-center">No expert matches found yet.</p>
                      )}
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-5">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-stone-900 flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-blue-600" />
                        AI Co-Founder
                      </h3>
                      <span className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded-full">Research Stage</span>
                    </div>
                    <div className="grid md:grid-cols-3 gap-2 mb-4">
                      {[
                        'Help me calculate TAM/SAM/SOM',
                        'Who are my competitors?',
                        'What customer segments to target?',
                      ].map((prompt, i) => (
                        <button
                          key={i}
                          onClick={() => {
                            setAiMessage(prompt)
                            if (hasWorkspace) sendMessageMutation.mutate(prompt)
                          }}
                          className="p-2 text-xs text-left bg-white rounded-lg border border-blue-100 hover:border-blue-300 hover:bg-blue-50 transition-colors"
                        >
                          {prompt}
                        </button>
                      ))}
                    </div>
                    {chatMessages.length > 0 && (
                      <div className="mb-4 max-h-48 overflow-y-auto space-y-2 p-3 bg-white rounded-lg border border-blue-100">
                        {chatMessages.slice(-4).map((msg) => (
                          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[85%] rounded-lg p-2 text-xs ${
                              msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-stone-100 text-stone-700'
                            }`}>
                              {msg.content}
                            </div>
                          </div>
                        ))}
                        {sendMessageMutation.isPending && (
                          <div className="flex justify-start">
                            <div className="bg-stone-100 rounded-lg p-2 text-xs text-stone-500 flex items-center gap-2">
                              <Loader2 className="w-3 h-3 animate-spin" /> Thinking...
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <input
                        type="text"
                        value={aiMessage}
                        onChange={(e) => setAiMessage(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && aiMessage.trim() && hasWorkspace && sendMessageMutation.mutate(aiMessage.trim())}
                        placeholder="Ask AI about market research..."
                        className="flex-1 px-3 py-2 border border-blue-200 rounded-lg text-sm focus:outline-none focus:border-blue-400 bg-white"
                      />
                      <button
                        onClick={() => aiMessage.trim() && hasWorkspace && sendMessageMutation.mutate(aiMessage.trim())}
                        disabled={!aiMessage.trim() || !hasWorkspace || sendMessageMutation.isPending}
                        className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                      >
                        <Send className="w-4 h-4" />
                      </button>
                    </div>
                    {!hasWorkspace && (
                      <p className="text-xs text-blue-600 mt-2">Create a workspace to chat with the AI Co-Founder</p>
                    )}
                  </div>

                  <div className="flex justify-between items-center">
                    <button
                      onClick={() => setActiveTab('researching')}
                      className="px-6 py-3 bg-stone-100 text-stone-700 rounded-lg font-medium hover:bg-stone-200 flex items-center gap-2"
                    >
                      <ArrowLeft className="w-5 h-5" />
                      Back to Validate
                    </button>
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => generatePhaseReport('research')}
                        disabled={saveReportMutation.isPending}
                        className="px-4 py-2 border border-blue-200 text-blue-700 rounded-lg text-sm font-medium hover:bg-blue-50 flex items-center gap-2 disabled:opacity-50"
                      >
                        <FileText className="w-4 h-4" />
                        {saveReportMutation.isPending ? 'Saving...' : 'Save Report'}
                      </button>
                      <button
                        onClick={() => setActiveTab('planning')}
                        className="px-6 py-3 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700 flex items-center gap-2"
                      >
                        Continue to Plan
                        <ChevronRight className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* PLAN STEP */}
              {activeTab === 'planning' && (
                <div className="space-y-6">
                  <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-100">
                    <h2 className="text-xl font-bold text-stone-900 mb-2 flex items-center gap-2">
                      <Target className="w-6 h-6 text-purple-600" />
                      Business Planning
                    </h2>
                    <p className="text-stone-600">Create your strategy, business model, and go-to-market plan.</p>
                  </div>

                  <div className="grid lg:grid-cols-2 gap-6">
                    <div className="bg-white rounded-xl border border-stone-200 p-5">
                      <h3 className="font-semibold text-stone-900 mb-4 flex items-center gap-2">
                        <Briefcase className="w-5 h-5 text-purple-500" />
                        Business Model Canvas
                        <span className="text-xs text-stone-400 font-normal ml-auto">Click to edit</span>
                      </h3>
                      <div className="grid grid-cols-3 gap-2">
                        {canvasItemsBase.map((item) => {
                          const aiDefaults: Record<string, string | undefined> = {
                            customers: opp.ai_target_audience,
                            advantage: opp.ai_competition_level ? `Low competition: ${opp.ai_competition_level}` : undefined,
                          }
                          const aiValue = aiDefaults[item.key]
                          const displayValue = canvasData[item.key] || aiValue || item.placeholder
                          const hasValue = !!(canvasData[item.key] || aiValue)
                          
                          return (
                            <div key={item.key}>
                              {editingCanvas === item.key ? (
                                <div className="p-3 bg-purple-100 rounded-lg border-2 border-purple-400">
                                  <p className="text-xs font-medium text-purple-700 mb-1">{item.title}</p>
                                  <input
                                    type="text"
                                    autoFocus
                                    value={canvasEditValue}
                                    onChange={(e) => setCanvasEditValue(e.target.value)}
                                    onKeyDown={(e) => {
                                      if (e.key === 'Enter') {
                                        setCanvasData(prev => ({ ...prev, [item.key]: canvasEditValue }))
                                        setEditingCanvas(null)
                                      } else if (e.key === 'Escape') {
                                        setEditingCanvas(null)
                                      }
                                    }}
                                    onBlur={() => {
                                      setCanvasData(prev => ({ ...prev, [item.key]: canvasEditValue }))
                                      setEditingCanvas(null)
                                    }}
                                    className="w-full text-xs p-1 rounded border border-purple-300 focus:outline-none focus:border-purple-500"
                                    placeholder={item.placeholder}
                                  />
                                </div>
                              ) : (
                                <button
                                  onClick={() => {
                                    setEditingCanvas(item.key)
                                    setCanvasEditValue(canvasData[item.key] || aiValue || '')
                                  }}
                                  className={`w-full text-left p-3 rounded-lg border cursor-pointer transition-colors ${
                                    aiValue && !canvasData[item.key] 
                                      ? 'bg-blue-50 border-blue-100 hover:bg-blue-100 hover:border-blue-200' 
                                      : 'bg-purple-50 border-purple-100 hover:bg-purple-100 hover:border-purple-200'
                                  }`}
                                >
                                  <p className="text-xs font-medium text-purple-700 flex items-center gap-1">
                                    {item.title}
                                    {aiValue && !canvasData[item.key] && <Sparkles className="w-3 h-3 text-blue-500" />}
                                  </p>
                                  <p className={`text-xs mt-1 truncate ${hasValue ? 'text-stone-700' : 'text-stone-400 italic'}`}>
                                    {displayValue}
                                  </p>
                                </button>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    </div>

                    <div className="bg-white rounded-xl border border-stone-200 p-5">
                      <h3 className="font-semibold text-stone-900 mb-4 flex items-center gap-2">
                        <Lightbulb className="w-5 h-5 text-amber-500" />
                        Business Model Ideas
                      </h3>
                      {opp.ai_business_model_suggestions && opp.ai_business_model_suggestions.length > 0 ? (
                        <div className="space-y-3">
                          {opp.ai_business_model_suggestions.map((model, i) => (
                            <div key={i} className="p-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg border border-amber-100">
                              <div className="flex items-center gap-3">
                                <div className="w-8 h-8 bg-amber-100 rounded-full flex items-center justify-center text-amber-600 font-bold">
                                  {i + 1}
                                </div>
                                <span className="text-sm font-medium text-stone-900">{model}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-stone-500 p-4 bg-stone-50 rounded-lg">Complete AI analysis to get business model suggestions.</p>
                      )}
                    </div>
                  </div>

                  <div className="bg-white rounded-xl border border-stone-200 p-5">
                    <h3 className="font-semibold text-stone-900 mb-4 flex items-center gap-2">
                      <Rocket className="w-5 h-5 text-violet-500" />
                      Go-to-Market Strategy
                    </h3>
                    <div className="grid md:grid-cols-4 gap-4">
                      <div className="p-4 bg-violet-50 rounded-lg border border-violet-100">
                        <p className="text-xs text-violet-600 font-medium mb-2">Phase 1: Discovery</p>
                        <ul className="space-y-1">
                          <li className="text-xs text-stone-600 flex items-center gap-1">
                            <ChevronRight className="w-3 h-3 text-violet-400" /> Customer interviews
                          </li>
                          <li className="text-xs text-stone-600 flex items-center gap-1">
                            <ChevronRight className="w-3 h-3 text-violet-400" /> Problem validation
                          </li>
                        </ul>
                      </div>
                      <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                        <p className="text-xs text-blue-600 font-medium mb-2">Phase 2: MVP</p>
                        <ul className="space-y-1">
                          <li className="text-xs text-stone-600 flex items-center gap-1">
                            <ChevronRight className="w-3 h-3 text-blue-400" /> Core features
                          </li>
                          <li className="text-xs text-stone-600 flex items-center gap-1">
                            <ChevronRight className="w-3 h-3 text-blue-400" /> Beta testers
                          </li>
                        </ul>
                      </div>
                      <div className="p-4 bg-emerald-50 rounded-lg border border-emerald-100">
                        <p className="text-xs text-emerald-600 font-medium mb-2">Phase 3: Launch</p>
                        <ul className="space-y-1">
                          <li className="text-xs text-stone-600 flex items-center gap-1">
                            <ChevronRight className="w-3 h-3 text-emerald-400" /> Marketing push
                          </li>
                          <li className="text-xs text-stone-600 flex items-center gap-1">
                            <ChevronRight className="w-3 h-3 text-emerald-400" /> Public release
                          </li>
                        </ul>
                      </div>
                      <div className="p-4 bg-amber-50 rounded-lg border border-amber-100">
                        <p className="text-xs text-amber-600 font-medium mb-2">Phase 4: Scale</p>
                        <ul className="space-y-1">
                          <li className="text-xs text-stone-600 flex items-center gap-1">
                            <ChevronRight className="w-3 h-3 text-amber-400" /> Team growth
                          </li>
                          <li className="text-xs text-stone-600 flex items-center gap-1">
                            <ChevronRight className="w-3 h-3 text-amber-400" /> Market expansion
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-xl border border-stone-200 p-5">
                    <h3 className="font-semibold text-stone-900 mb-4 flex items-center gap-2">
                      <BarChart3 className="w-5 h-5 text-blue-500" />
                      Financial Projections
                    </h3>
                    <div className="grid md:grid-cols-3 gap-4">
                      <div className="p-4 bg-stone-50 rounded-lg">
                        <p className="text-xs text-stone-500 mb-1">Year 1 Target</p>
                        <p className="text-2xl font-bold text-stone-900">$50K - $100K</p>
                        <p className="text-xs text-emerald-600 mt-1">MVP + Early Adopters</p>
                      </div>
                      <div className="p-4 bg-stone-50 rounded-lg">
                        <p className="text-xs text-stone-500 mb-1">Year 2 Target</p>
                        <p className="text-2xl font-bold text-stone-900">$250K - $500K</p>
                        <p className="text-xs text-blue-600 mt-1">Product-Market Fit</p>
                      </div>
                      <div className="p-4 bg-stone-50 rounded-lg">
                        <p className="text-xs text-stone-500 mb-1">Year 3 Target</p>
                        <p className="text-2xl font-bold text-stone-900">$1M+</p>
                        <p className="text-xs text-violet-600 mt-1">Scale & Expansion</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-200 p-5">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-stone-900 flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-purple-600" />
                        AI Co-Founder
                      </h3>
                      <span className="text-xs text-purple-600 bg-purple-100 px-2 py-1 rounded-full">Plan Stage</span>
                    </div>
                    <div className="grid md:grid-cols-3 gap-2 mb-4">
                      {[
                        'Help me write a value proposition',
                        'What pricing model works best?',
                        'Create a go-to-market strategy',
                      ].map((prompt, i) => (
                        <button
                          key={i}
                          onClick={() => {
                            setAiMessage(prompt)
                            if (hasWorkspace) sendMessageMutation.mutate(prompt)
                          }}
                          className="p-2 text-xs text-left bg-white rounded-lg border border-purple-100 hover:border-purple-300 hover:bg-purple-50 transition-colors"
                        >
                          {prompt}
                        </button>
                      ))}
                    </div>
                    {chatMessages.length > 0 && (
                      <div className="mb-4 max-h-48 overflow-y-auto space-y-2 p-3 bg-white rounded-lg border border-purple-100">
                        {chatMessages.slice(-4).map((msg) => (
                          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[85%] rounded-lg p-2 text-xs ${
                              msg.role === 'user' ? 'bg-purple-600 text-white' : 'bg-stone-100 text-stone-700'
                            }`}>
                              {msg.content}
                            </div>
                          </div>
                        ))}
                        {sendMessageMutation.isPending && (
                          <div className="flex justify-start">
                            <div className="bg-stone-100 rounded-lg p-2 text-xs text-stone-500 flex items-center gap-2">
                              <Loader2 className="w-3 h-3 animate-spin" /> Thinking...
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <input
                        type="text"
                        value={aiMessage}
                        onChange={(e) => setAiMessage(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && aiMessage.trim() && hasWorkspace && sendMessageMutation.mutate(aiMessage.trim())}
                        placeholder="Ask AI about business planning..."
                        className="flex-1 px-3 py-2 border border-purple-200 rounded-lg text-sm focus:outline-none focus:border-purple-400 bg-white"
                      />
                      <button
                        onClick={() => aiMessage.trim() && hasWorkspace && sendMessageMutation.mutate(aiMessage.trim())}
                        disabled={!aiMessage.trim() || !hasWorkspace || sendMessageMutation.isPending}
                        className="p-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
                      >
                        <Send className="w-4 h-4" />
                      </button>
                    </div>
                    {!hasWorkspace && (
                      <p className="text-xs text-purple-600 mt-2">Create a workspace to chat with the AI Co-Founder</p>
                    )}
                  </div>

                  <div className="flex justify-between items-center">
                    <button
                      onClick={() => setActiveTab('validating')}
                      className="px-6 py-3 bg-stone-100 text-stone-700 rounded-lg font-medium hover:bg-stone-200 flex items-center gap-2"
                    >
                      <ArrowLeft className="w-5 h-5" />
                      Back to Research
                    </button>
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => generatePhaseReport('plan')}
                        disabled={saveReportMutation.isPending}
                        className="px-4 py-2 border border-purple-200 text-purple-700 rounded-lg text-sm font-medium hover:bg-purple-50 flex items-center gap-2 disabled:opacity-50"
                      >
                        <FileText className="w-4 h-4" />
                        {saveReportMutation.isPending ? 'Saving...' : 'Save Report'}
                      </button>
                      <button
                        onClick={() => setActiveTab('building')}
                        className="px-6 py-3 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700 flex items-center gap-2"
                      >
                        Continue to Execute
                        <ChevronRight className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* EXECUTE STEP */}
              {activeTab === 'building' && (
                <div className="space-y-6">
                  <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl p-6 border border-amber-100">
                    <h2 className="text-xl font-bold text-stone-900 mb-2 flex items-center gap-2">
                      <Zap className="w-6 h-6 text-amber-600" />
                      Execute Your Plan
                    </h2>
                    <p className="text-stone-600">Build your MVP, validate with customers, and launch to market.</p>
                  </div>

                  <div className="grid lg:grid-cols-3 gap-6">
                    <div className="lg:col-span-2 bg-white rounded-xl border border-stone-200 p-5">
                      <h3 className="font-semibold text-stone-900 mb-4 flex items-center gap-2">
                        <Rocket className="w-5 h-5 text-amber-500" />
                        MVP Development Roadmap
                      </h3>
                      <div className="space-y-4">
                        {[
                          { phase: 'Week 1-2', title: 'Core Features', tasks: ['Define MVP scope', 'Set up tech stack', 'Build core functionality'], status: 'current' },
                          { phase: 'Week 3-4', title: 'User Experience', tasks: ['Design UI/UX', 'Implement feedback', 'Polish interface'], status: 'upcoming' },
                          { phase: 'Week 5-6', title: 'Beta Testing', tasks: ['Recruit beta users', 'Gather feedback', 'Iterate on product'], status: 'upcoming' },
                          { phase: 'Week 7-8', title: 'Launch Prep', tasks: ['Final testing', 'Marketing setup', 'Public launch'], status: 'upcoming' },
                        ].map((milestone, i) => (
                          <div key={i} className={`p-4 rounded-lg border ${milestone.status === 'current' ? 'bg-amber-50 border-amber-200' : 'bg-stone-50 border-stone-200'}`}>
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center gap-3">
                                <span className={`text-xs font-medium px-2 py-1 rounded ${milestone.status === 'current' ? 'bg-amber-200 text-amber-800' : 'bg-stone-200 text-stone-600'}`}>
                                  {milestone.phase}
                                </span>
                                <span className="font-medium text-stone-900">{milestone.title}</span>
                              </div>
                              {milestone.status === 'current' && (
                                <span className="text-xs text-amber-600 font-medium">In Progress</span>
                              )}
                            </div>
                            <ul className="space-y-1 ml-16">
                              {milestone.tasks.map((task, j) => (
                                <li key={j} className="text-sm text-stone-600 flex items-center gap-2">
                                  <div className="w-1.5 h-1.5 rounded-full bg-stone-400" />
                                  {task}
                                </li>
                              ))}
                            </ul>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-6">
                      <div className="bg-white rounded-xl border border-stone-200 p-5">
                        <h3 className="font-semibold text-stone-900 mb-4 flex items-center gap-2">
                          <Users className="w-5 h-5 text-emerald-500" />
                          Customer Validation
                        </h3>
                        <div className="space-y-3">
                          <div className="p-3 bg-emerald-50 rounded-lg">
                            <div className="flex justify-between items-center mb-1">
                              <span className="text-sm text-stone-700">Interviews Completed</span>
                              <span className="text-sm font-bold text-emerald-600">0/10</span>
                            </div>
                            <div className="h-2 bg-stone-200 rounded-full overflow-hidden">
                              <div className="h-full bg-emerald-500" style={{ width: '0%' }} />
                            </div>
                          </div>
                          <div className="p-3 bg-blue-50 rounded-lg">
                            <div className="flex justify-between items-center mb-1">
                              <span className="text-sm text-stone-700">Beta Signups</span>
                              <span className="text-sm font-bold text-blue-600">0/50</span>
                            </div>
                            <div className="h-2 bg-stone-200 rounded-full overflow-hidden">
                              <div className="h-full bg-blue-500" style={{ width: '0%' }} />
                            </div>
                          </div>
                          <div className="p-3 bg-violet-50 rounded-lg">
                            <div className="flex justify-between items-center mb-1">
                              <span className="text-sm text-stone-700">Pre-orders</span>
                              <span className="text-sm font-bold text-violet-600">$0</span>
                            </div>
                            <div className="h-2 bg-stone-200 rounded-full overflow-hidden">
                              <div className="h-full bg-violet-500" style={{ width: '0%' }} />
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="bg-white rounded-xl border border-stone-200 p-5">
                        <h3 className="font-semibold text-stone-900 mb-4 flex items-center gap-2">
                          <CheckCircle2 className="w-5 h-5 text-amber-500" />
                          Launch Checklist
                        </h3>
                        <p className="text-xs text-stone-500 mb-3">
                          {Object.values(launchChecked).filter(Boolean).length}/{launchChecklistItems.length} completed
                        </p>
                        <div className="space-y-2">
                          {launchChecklistItems.map((item) => (
                            <button
                              key={item}
                              onClick={() => setLaunchChecked(prev => ({ ...prev, [item]: !prev[item] }))}
                              className={`w-full flex items-center gap-3 p-2 rounded-lg transition-colors cursor-pointer ${launchChecked[item] ? 'bg-amber-50 hover:bg-amber-100' : 'bg-stone-50 hover:bg-stone-100'}`}
                            >
                              <div className={`w-5 h-5 rounded flex items-center justify-center flex-shrink-0 ${launchChecked[item] ? 'bg-amber-500 text-white' : 'border-2 border-stone-300'}`}>
                                {launchChecked[item] && <CheckCircle2 className="w-3 h-3" />}
                              </div>
                              <span className={`text-sm text-left ${launchChecked[item] ? 'text-amber-700 line-through' : 'text-stone-600'}`}>{item}</span>
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  {opp.ai_next_steps && opp.ai_next_steps.length > 0 && (
                    <div className="bg-white rounded-xl border border-stone-200 p-5">
                      <h3 className="font-semibold text-stone-900 mb-4 flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-violet-500" />
                        AI Recommended Next Steps
                      </h3>
                      <div className="grid md:grid-cols-2 gap-3">
                        {opp.ai_next_steps.map((step, i) => (
                          <div key={i} className="flex items-start gap-3 p-3 bg-violet-50 rounded-lg border border-violet-100">
                            <div className="w-6 h-6 bg-violet-200 rounded-full flex items-center justify-center text-violet-700 text-xs font-bold flex-shrink-0">
                              {i + 1}
                            </div>
                            <span className="text-sm text-stone-700">{step}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl border border-amber-200 p-5">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-stone-900 flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-amber-600" />
                        AI Co-Founder
                      </h3>
                      <span className="text-xs text-amber-600 bg-amber-100 px-2 py-1 rounded-full">Execute Stage</span>
                    </div>
                    <div className="grid md:grid-cols-3 gap-2 mb-4">
                      {[
                        'What features for MVP?',
                        'How to find beta testers?',
                        'Help me plan the launch',
                      ].map((prompt, i) => (
                        <button
                          key={i}
                          onClick={() => {
                            setAiMessage(prompt)
                            if (hasWorkspace) sendMessageMutation.mutate(prompt)
                          }}
                          className="p-2 text-xs text-left bg-white rounded-lg border border-amber-100 hover:border-amber-300 hover:bg-amber-50 transition-colors"
                        >
                          {prompt}
                        </button>
                      ))}
                    </div>
                    {chatMessages.length > 0 && (
                      <div className="mb-4 max-h-48 overflow-y-auto space-y-2 p-3 bg-white rounded-lg border border-amber-100">
                        {chatMessages.slice(-4).map((msg) => (
                          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[85%] rounded-lg p-2 text-xs ${
                              msg.role === 'user' ? 'bg-amber-600 text-white' : 'bg-stone-100 text-stone-700'
                            }`}>
                              {msg.content}
                            </div>
                          </div>
                        ))}
                        {sendMessageMutation.isPending && (
                          <div className="flex justify-start">
                            <div className="bg-stone-100 rounded-lg p-2 text-xs text-stone-500 flex items-center gap-2">
                              <Loader2 className="w-3 h-3 animate-spin" /> Thinking...
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <input
                        type="text"
                        value={aiMessage}
                        onChange={(e) => setAiMessage(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && aiMessage.trim() && hasWorkspace && sendMessageMutation.mutate(aiMessage.trim())}
                        placeholder="Ask AI about execution..."
                        className="flex-1 px-3 py-2 border border-amber-200 rounded-lg text-sm focus:outline-none focus:border-amber-400 bg-white"
                      />
                      <button
                        onClick={() => aiMessage.trim() && hasWorkspace && sendMessageMutation.mutate(aiMessage.trim())}
                        disabled={!aiMessage.trim() || !hasWorkspace || sendMessageMutation.isPending}
                        className="p-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50"
                      >
                        <Send className="w-4 h-4" />
                      </button>
                    </div>
                    {!hasWorkspace && (
                      <p className="text-xs text-amber-600 mt-2">Create a workspace to chat with the AI Co-Founder</p>
                    )}
                  </div>

                  <div className="flex justify-between items-center">
                    <button
                      onClick={() => setActiveTab('planning')}
                      className="px-6 py-3 bg-stone-100 text-stone-700 rounded-lg font-medium hover:bg-stone-200 flex items-center gap-2"
                    >
                      <ArrowLeft className="w-5 h-5" />
                      Back to Plan
                    </button>
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => generatePhaseReport('execute')}
                        disabled={saveReportMutation.isPending}
                        className="px-4 py-2 border border-amber-200 text-amber-700 rounded-lg text-sm font-medium hover:bg-amber-50 flex items-center gap-2 disabled:opacity-50"
                      >
                        <FileText className="w-4 h-4" />
                        {saveReportMutation.isPending ? 'Saving...' : 'Save Report'}
                      </button>
                      <button
                        onClick={() => {
                          if (!hasWorkspace) {
                            createWorkspaceMutation.mutate()
                          } else {
                            setWorkspacePanelOpen(true)
                          }
                        }}
                        disabled={createWorkspaceMutation.isPending}
                        className="px-6 py-3 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 flex items-center gap-2"
                      >
                        <Rocket className="w-5 h-5" />
                        {hasWorkspace ? 'Open Workspace & Start' : 'Start Execution'}
                      </button>
                    </div>
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
