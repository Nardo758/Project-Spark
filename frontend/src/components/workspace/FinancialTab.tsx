import { useState } from 'react'
import {
  DollarSign, Sparkles, Loader2, AlertCircle, FileText,
  TrendingUp, ChevronDown, ChevronRight
} from 'lucide-react'

interface Props {
  workspaceId: number
  workspace: any
  token: string
  onRefresh: () => void
}

export default function FinancialTab({ workspaceId, workspace, token, onRefresh: _onRefresh }: Props) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [model, setModel] = useState<any>(null)
  const [expandedSections, setExpandedSections] = useState<Set<number>>(new Set())

  const financialArtifacts = (workspace.artifacts || []).filter((a: any) => a.artifact_type === 'financial_model')

  const generateModel = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`/api/v1/enhanced-workspaces/${workspaceId}/ai/insights`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ insight_type: 'financial_model' }),
      })
      if (!res.ok) throw new Error('Failed to generate financial model')
      const data = await res.json()
      setModel(data)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const toggleSection = (idx: number) => {
    const next = new Set(expandedSections)
    if (next.has(idx)) next.delete(idx)
    else next.add(idx)
    setExpandedSections(next)
  }

  const renderContent = (content: any) => {
    if (typeof content === 'string') {
      return <p className="text-sm text-stone-700 whitespace-pre-wrap">{content}</p>
    }
    if (content && typeof content === 'object') {
      const projections = content.projections || content.model?.projections || content.revenue_projections || []
      const metrics = content.key_metrics || content.metrics || content.model?.key_metrics || []
      const assumptions = content.assumptions || content.model?.assumptions || []
      const sections = content.sections || []

      return (
        <div className="space-y-4">
          {projections.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-stone-900 mb-2 flex items-center gap-1">
                <TrendingUp className="w-4 h-4 text-emerald-500" />
                Projections
              </h4>
              <div className="overflow-x-auto">
                <div className="space-y-2">
                  {projections.map((proj: any, i: number) => (
                    <div key={i} className="bg-stone-50 rounded-lg p-3 border border-stone-100">
                      {typeof proj === 'string' ? (
                        <p className="text-sm text-stone-600">{proj}</p>
                      ) : (
                        <div>
                          <p className="text-sm font-medium text-stone-900">{proj.period || proj.year || proj.label || `Period ${i + 1}`}</p>
                          {proj.revenue != null && <p className="text-xs text-emerald-600">Revenue: {proj.revenue}</p>}
                          {proj.costs != null && <p className="text-xs text-red-600">Costs: {proj.costs}</p>}
                          {proj.profit != null && <p className="text-xs text-blue-600">Profit: {proj.profit}</p>}
                          {proj.description && <p className="text-xs text-stone-500 mt-1">{proj.description}</p>}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {metrics.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-stone-900 mb-2">Key Metrics</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {metrics.map((metric: any, i: number) => (
                  <div key={i} className="bg-emerald-50 rounded-lg p-3 border border-emerald-100">
                    {typeof metric === 'string' ? (
                      <p className="text-sm text-stone-700">{metric}</p>
                    ) : (
                      <div>
                        <p className="text-xs text-stone-500">{metric.name || metric.label}</p>
                        <p className="text-lg font-bold text-stone-900">{metric.value || metric.amount}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {assumptions.length > 0 && (
            <div className="bg-amber-50 rounded-lg p-3">
              <h4 className="text-sm font-medium text-amber-800 mb-2">Assumptions</h4>
              <ul className="space-y-1">
                {assumptions.map((a: any, i: number) => (
                  <li key={i} className="text-sm text-amber-700 flex items-start gap-1">
                    <span>•</span>
                    <span>{typeof a === 'string' ? a : a.description || a.text || JSON.stringify(a)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {sections.length > 0 && (
            <div className="space-y-2">
              {sections.map((section: any, idx: number) => (
                <div key={idx} className="border border-stone-100 rounded-lg overflow-hidden">
                  <button
                    onClick={() => toggleSection(idx)}
                    className="w-full flex items-center gap-2 p-3 text-left hover:bg-stone-50"
                  >
                    {expandedSections.has(idx) ? <ChevronDown className="w-4 h-4 text-stone-400" /> : <ChevronRight className="w-4 h-4 text-stone-400" />}
                    <span className="text-sm font-medium text-stone-900">{section.title || section.name || `Section ${idx + 1}`}</span>
                  </button>
                  {expandedSections.has(idx) && (
                    <div className="px-4 pb-3">
                      <p className="text-sm text-stone-600 whitespace-pre-wrap">{typeof section.content === 'string' ? section.content : JSON.stringify(section.content || section, null, 2)}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {projections.length === 0 && metrics.length === 0 && assumptions.length === 0 && sections.length === 0 && (
            <p className="text-sm text-stone-700 whitespace-pre-wrap">{JSON.stringify(content, null, 2)}</p>
          )}
        </div>
      )
    }
    return null
  }

  return (
    <div className="space-y-6">
      <div className="bg-white border border-stone-200 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-stone-900 flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-violet-500" />
            Financial Model
          </h2>
          <button
            onClick={generateModel}
            disabled={loading}
            className="px-4 py-2 bg-violet-600 text-white text-sm font-medium rounded-lg hover:bg-violet-700 disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            Generate Financial Model
          </button>
        </div>

        {error && (
          <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 rounded-lg p-3 mb-3">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {model ? (
          <div className="bg-violet-50 rounded-lg p-4">
            {renderContent(model.content)}
            {model.confidence != null && (
              <p className="text-xs text-stone-500 mt-3">Confidence: {Math.round(model.confidence * 100)}%</p>
            )}
          </div>
        ) : (
          <p className="text-sm text-stone-500">Generate a financial model with projections, key metrics, and assumptions.</p>
        )}
      </div>

      <div className="bg-white border border-stone-200 rounded-xl p-6">
        <h3 className="text-sm font-semibold text-stone-900 mb-3 flex items-center gap-2">
          <FileText className="w-4 h-4 text-emerald-500" />
          Financial Model Artifacts ({financialArtifacts.length})
        </h3>
        {financialArtifacts.length === 0 ? (
          <p className="text-sm text-stone-500">No financial model artifacts yet. Create one from the Research Hub.</p>
        ) : (
          <div className="space-y-2">
            {financialArtifacts.map((artifact: any) => (
              <div key={artifact.id} className="bg-stone-50 rounded-lg p-3 border border-stone-100">
                <h4 className="text-sm font-medium text-stone-900">{artifact.title}</h4>
                {artifact.summary && <p className="text-xs text-stone-600 mt-1">{artifact.summary}</p>}
                <p className="text-xs text-stone-400 mt-1">{new Date(artifact.created_at).toLocaleDateString()}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
