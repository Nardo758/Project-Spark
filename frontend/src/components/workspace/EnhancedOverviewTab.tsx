import { useState } from 'react'
import {
  Sparkles, Target, CheckCircle2, FileText, BarChart3,
  Loader2, AlertCircle, TrendingUp, Layers
} from 'lucide-react'

interface Props {
  workspaceId: number
  workspace: any
  token: string
  onRefresh: () => void
}

export default function EnhancedOverviewTab({ workspaceId, workspace, token, onRefresh: _onRefresh }: Props) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [summary, setSummary] = useState<any>(null)

  const allTasks = (workspace.stages || []).flatMap((s: any) => s.tasks || [])
  const completedTasks = allTasks.filter((t: any) => t.is_completed).length
  const totalTasks = allTasks.length
  const artifactCount = (workspace.artifacts || []).length

  const generateSummary = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`/api/v1/enhanced-workspaces/${workspaceId}/ai/insights`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ insight_type: 'summary' }),
      })
      if (!res.ok) throw new Error('Failed to generate summary')
      const data = await res.json()
      setSummary(data)
    } catch (e: any) {
      setError(e.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const workflowTypeLabel: Record<string, string> = {
    lean_validation: 'Lean Validation',
    full_research: 'Full Research',
    competitor_focused: 'Competitor Focused',
    financial_first: 'Financial First',
    custom: 'Custom',
  }

  const recommendations = workspace.ai_recommendations || []

  return (
    <div className="space-y-6">
      <div className="bg-white border border-stone-200 rounded-xl p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-stone-900">
              {workspace.custom_title || workspace.opportunity?.title || 'Workspace Overview'}
            </h2>
            <p className="text-sm text-stone-600 mt-1">
              {workspace.opportunity?.category || 'Uncategorized'}
              {workspace.opportunity?.description && (
                <span className="block mt-1">{workspace.opportunity.description}</span>
              )}
            </p>
          </div>
          <span className="px-3 py-1 text-xs font-medium rounded-full bg-violet-100 text-violet-700">
            {workflowTypeLabel[workspace.workflow_type] || workspace.workflow_type}
          </span>
        </div>

        <div className="mb-4">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-stone-600">Overall Progress</span>
            <span className="font-medium text-stone-900">{workspace.progress_percent || 0}%</span>
          </div>
          <div className="h-3 bg-stone-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-violet-500 to-purple-500 transition-all duration-500 rounded-full"
              style={{ width: `${workspace.progress_percent || 0}%` }}
            />
          </div>
        </div>

        {workspace.current_stage && (
          <div className="flex items-center gap-2 text-sm text-stone-600">
            <Layers className="w-4 h-4 text-violet-500" />
            <span>Current Stage: <span className="font-medium text-stone-900">{workspace.current_stage}</span></span>
          </div>
        )}

        {workspace.validation_score != null && (
          <div className="flex items-center gap-2 text-sm text-stone-600 mt-2">
            <TrendingUp className="w-4 h-4 text-emerald-500" />
            <span>Validation Score: <span className="font-medium text-stone-900">{workspace.validation_score}/100</span></span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white border border-stone-200 rounded-xl p-5 text-center">
          <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
          <p className="text-2xl font-bold text-stone-900">{completedTasks}/{totalTasks}</p>
          <p className="text-sm text-stone-600">Tasks Completed</p>
        </div>
        <div className="bg-white border border-stone-200 rounded-xl p-5 text-center">
          <FileText className="w-8 h-8 text-blue-500 mx-auto mb-2" />
          <p className="text-2xl font-bold text-stone-900">{artifactCount}</p>
          <p className="text-sm text-stone-600">Research Artifacts</p>
        </div>
        <div className="bg-white border border-stone-200 rounded-xl p-5 text-center">
          <BarChart3 className="w-8 h-8 text-violet-500 mx-auto mb-2" />
          <p className="text-2xl font-bold text-stone-900">{(workspace.stages || []).length}</p>
          <p className="text-sm text-stone-600">Workflow Stages</p>
        </div>
      </div>

      {recommendations.length > 0 && (
        <div className="bg-white border border-stone-200 rounded-xl p-6">
          <h3 className="text-sm font-semibold text-stone-900 mb-3 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-violet-500" />
            AI Recommendations
          </h3>
          <ul className="space-y-2">
            {recommendations.map((rec: string, i: number) => (
              <li key={i} className="flex items-start gap-2 text-sm text-stone-600">
                <Target className="w-4 h-4 text-violet-400 mt-0.5 flex-shrink-0" />
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="bg-white border border-stone-200 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-stone-900 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-violet-500" />
            AI Summary
          </h3>
          <button
            onClick={generateSummary}
            disabled={loading}
            className="px-4 py-2 bg-violet-600 text-white text-sm font-medium rounded-lg hover:bg-violet-700 disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            Generate Summary
          </button>
        </div>

        {error && (
          <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 rounded-lg p-3 mb-3">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {summary ? (
          <div className="bg-violet-50 rounded-lg p-4">
            <p className="text-sm text-stone-700 whitespace-pre-wrap">
              {typeof summary.content === 'string' ? summary.content : JSON.stringify(summary.content, null, 2)}
            </p>
            {summary.confidence != null && (
              <p className="text-xs text-stone-500 mt-3">Confidence: {Math.round(summary.confidence * 100)}%</p>
            )}
          </div>
        ) : (
          <p className="text-sm text-stone-500">Click "Generate Summary" to get an AI-powered overview of your workspace progress.</p>
        )}
      </div>
    </div>
  )
}
