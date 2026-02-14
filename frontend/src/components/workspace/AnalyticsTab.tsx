import { useState, useEffect } from 'react'
import {
  BarChart3, Loader2, AlertCircle, TrendingUp, CheckCircle2,
  FileText, Layers
} from 'lucide-react'

interface Props {
  workspaceId: number
  workspace: any
  token: string
  onRefresh: () => void
}

export default function AnalyticsTab({ workspaceId, workspace, token, onRefresh: _onRefresh }: Props) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [analytics, setAnalytics] = useState<any>(null)

  useEffect(() => {
    fetchAnalytics()
  }, [workspaceId])

  const fetchAnalytics = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`/api/v1/enhanced-workspaces/${workspaceId}/analytics`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to load analytics')
      const data = await res.json()
      setAnalytics(data)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="w-8 h-8 animate-spin text-violet-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white border border-stone-200 rounded-xl p-6">
        <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 rounded-lg p-3">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
        <button
          onClick={fetchAnalytics}
          className="mt-3 px-4 py-2 bg-violet-600 text-white text-sm font-medium rounded-lg hover:bg-violet-700"
        >
          Retry
        </button>
      </div>
    )
  }

  const completionRate = analytics?.completion_rate ?? analytics?.progress_percent ?? workspace.progress_percent ?? 0
  const totalTasks = analytics?.total_tasks ?? 0
  const completedTasks = analytics?.completed_tasks ?? 0
  const artifactsByType: Record<string, number> = analytics?.artifacts_by_type || {}
  const stageProgress: any[] = analytics?.stage_progress || analytics?.stages || []
  const validationScore = analytics?.validation_score ?? workspace.validation_score

  const maxArtifactCount = Math.max(...Object.values(artifactsByType).map(Number), 1)

  const TYPE_COLORS: Record<string, string> = {
    interview: 'bg-blue-500',
    survey: 'bg-indigo-500',
    competitor_analysis: 'bg-red-500',
    financial_model: 'bg-emerald-500',
    market_research: 'bg-amber-500',
    customer_persona: 'bg-pink-500',
    swot_analysis: 'bg-purple-500',
    notes: 'bg-stone-500',
    ai_insight: 'bg-violet-500',
    custom: 'bg-cyan-500',
  }

  const TYPE_LABELS: Record<string, string> = {
    interview: 'Interview',
    survey: 'Survey',
    competitor_analysis: 'Competitor',
    financial_model: 'Financial',
    market_research: 'Market',
    customer_persona: 'Persona',
    swot_analysis: 'SWOT',
    notes: 'Notes',
    ai_insight: 'AI Insight',
    custom: 'Custom',
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white border border-stone-200 rounded-xl p-6 text-center">
          <BarChart3 className="w-8 h-8 text-violet-500 mx-auto mb-2" />
          <p className="text-4xl font-bold text-stone-900">{Math.round(completionRate)}%</p>
          <p className="text-sm text-stone-600">Completion Rate</p>
        </div>
        <div className="bg-white border border-stone-200 rounded-xl p-6 text-center">
          <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
          <p className="text-4xl font-bold text-stone-900">{completedTasks}/{totalTasks}</p>
          <p className="text-sm text-stone-600">Tasks Done</p>
        </div>
        {validationScore != null && (
          <div className="bg-white border border-stone-200 rounded-xl p-6 text-center">
            <TrendingUp className="w-8 h-8 text-blue-500 mx-auto mb-2" />
            <p className="text-4xl font-bold text-stone-900">{validationScore}</p>
            <p className="text-sm text-stone-600">Validation Score</p>
          </div>
        )}
        {validationScore == null && (
          <div className="bg-white border border-stone-200 rounded-xl p-6 text-center">
            <FileText className="w-8 h-8 text-blue-500 mx-auto mb-2" />
            <p className="text-4xl font-bold text-stone-900">{Object.values(artifactsByType).reduce((a: number, b: any) => a + Number(b), 0)}</p>
            <p className="text-sm text-stone-600">Total Artifacts</p>
          </div>
        )}
      </div>

      <div className="bg-white border border-stone-200 rounded-xl p-6">
        <h3 className="text-sm font-semibold text-stone-900 mb-4 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-violet-500" />
          Tasks Progress
        </h3>
        <div className="flex items-center gap-3">
          <div className="flex-1 h-4 bg-stone-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-violet-500 to-purple-500 rounded-full transition-all duration-500"
              style={{ width: `${totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0}%` }}
            />
          </div>
          <span className="text-sm font-medium text-stone-700 whitespace-nowrap">
            {completedTasks} / {totalTasks}
          </span>
        </div>
      </div>

      {Object.keys(artifactsByType).length > 0 && (
        <div className="bg-white border border-stone-200 rounded-xl p-6">
          <h3 className="text-sm font-semibold text-stone-900 mb-4 flex items-center gap-2">
            <FileText className="w-4 h-4 text-violet-500" />
            Artifacts by Type
          </h3>
          <div className="space-y-3">
            {Object.entries(artifactsByType).map(([type, count]) => (
              <div key={type} className="flex items-center gap-3">
                <span className="text-xs text-stone-600 w-20 truncate">{TYPE_LABELS[type] || type}</span>
                <div className="flex-1 h-6 bg-stone-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${TYPE_COLORS[type] || 'bg-stone-400'}`}
                    style={{ width: `${(Number(count) / maxArtifactCount) * 100}%` }}
                  />
                </div>
                <span className="text-sm font-medium text-stone-700 w-8 text-right">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {stageProgress.length > 0 && (
        <div className="bg-white border border-stone-200 rounded-xl p-6">
          <h3 className="text-sm font-semibold text-stone-900 mb-4 flex items-center gap-2">
            <Layers className="w-4 h-4 text-violet-500" />
            Stage Progress
          </h3>
          <div className="space-y-4">
            {stageProgress.map((stage: any, idx: number) => {
              const progress = stage.progress_percent ?? stage.progress ?? 0
              const statusColor = stage.status === 'completed' ? 'text-emerald-600' : stage.status === 'in_progress' ? 'text-blue-600' : 'text-stone-400'
              return (
                <div key={idx}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-stone-900">{stage.name || `Stage ${idx + 1}`}</span>
                    <span className={`text-xs font-medium ${statusColor}`}>
                      {stage.status === 'completed' ? 'Completed' : stage.status === 'in_progress' ? 'In Progress' : 'Not Started'}
                    </span>
                  </div>
                  <div className="h-2 bg-stone-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${stage.status === 'completed' ? 'bg-emerald-500' : 'bg-gradient-to-r from-violet-500 to-purple-500'}`}
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-stone-400 mt-0.5">{Math.round(progress)}% complete</p>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
