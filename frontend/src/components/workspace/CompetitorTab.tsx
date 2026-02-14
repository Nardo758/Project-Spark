import { useState } from 'react'
import {
  Swords, Sparkles, Loader2, AlertCircle, FileText,
  ChevronDown, ChevronRight
} from 'lucide-react'

interface Props {
  workspaceId: number
  workspace: any
  token: string
  onRefresh: () => void
}

export default function CompetitorTab({ workspaceId, workspace, token, onRefresh: _onRefresh }: Props) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [analysis, setAnalysis] = useState<any>(null)
  const [expandedSections, setExpandedSections] = useState<Set<number>>(new Set())

  const competitorArtifacts = (workspace.artifacts || []).filter((a: any) => a.artifact_type === 'competitor_analysis')

  const analyzeCompetitors = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`/api/v1/enhanced-workspaces/${workspaceId}/ai/insights`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ insight_type: 'competitor_analysis' }),
      })
      if (!res.ok) throw new Error('Failed to analyze competitors')
      const data = await res.json()
      setAnalysis(data)
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
      const framework = content.framework || content.analysis?.framework || null
      const areas = content.areas || content.analysis?.areas || content.categories || []
      const competitors = content.competitors || content.analysis?.competitors || []
      const comparison = content.comparison || content.analysis?.comparison || null

      return (
        <div className="space-y-4">
          {framework && (
            <div className="bg-stone-50 rounded-lg p-3">
              <h4 className="text-sm font-medium text-stone-900 mb-1">Framework</h4>
              <p className="text-sm text-stone-600">{typeof framework === 'string' ? framework : JSON.stringify(framework)}</p>
            </div>
          )}

          {areas.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-stone-900 mb-2">Analysis Areas</h4>
              {areas.map((area: any, idx: number) => (
                <div key={idx} className="border border-stone-100 rounded-lg overflow-hidden mb-2">
                  <button
                    onClick={() => toggleSection(idx)}
                    className="w-full flex items-center gap-2 p-3 text-left hover:bg-stone-50"
                  >
                    {expandedSections.has(idx) ? <ChevronDown className="w-4 h-4 text-stone-400" /> : <ChevronRight className="w-4 h-4 text-stone-400" />}
                    <span className="text-sm font-medium text-stone-900">{typeof area === 'string' ? area : area.name || area.title || `Area ${idx + 1}`}</span>
                  </button>
                  {expandedSections.has(idx) && typeof area === 'object' && (
                    <div className="px-4 pb-3">
                      {area.description && <p className="text-sm text-stone-600">{area.description}</p>}
                      {area.criteria && (
                        <ul className="mt-2 space-y-1">
                          {(Array.isArray(area.criteria) ? area.criteria : [area.criteria]).map((c: any, ci: number) => (
                            <li key={ci} className="text-sm text-stone-600 flex items-start gap-1">
                              <span className="text-violet-500">•</span>
                              <span>{typeof c === 'string' ? c : JSON.stringify(c)}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {competitors.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-stone-900 mb-2">Competitors</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {competitors.map((comp: any, i: number) => (
                  <div key={i} className="bg-stone-50 rounded-lg p-3 border border-stone-100">
                    <p className="text-sm font-medium text-stone-900">{typeof comp === 'string' ? comp : comp.name || `Competitor ${i + 1}`}</p>
                    {comp.strengths && <p className="text-xs text-emerald-600 mt-1">Strengths: {comp.strengths}</p>}
                    {comp.weaknesses && <p className="text-xs text-red-600 mt-0.5">Weaknesses: {comp.weaknesses}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {comparison && (
            <div className="bg-stone-50 rounded-lg p-3">
              <h4 className="text-sm font-medium text-stone-900 mb-1">Comparison Template</h4>
              <p className="text-sm text-stone-600 whitespace-pre-wrap">{typeof comparison === 'string' ? comparison : JSON.stringify(comparison, null, 2)}</p>
            </div>
          )}

          {!framework && areas.length === 0 && competitors.length === 0 && !comparison && (
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
            <Swords className="w-5 h-5 text-violet-500" />
            Competitor Analysis
          </h2>
          <button
            onClick={analyzeCompetitors}
            disabled={loading}
            className="px-4 py-2 bg-violet-600 text-white text-sm font-medium rounded-lg hover:bg-violet-700 disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            Analyze Competitors
          </button>
        </div>

        {error && (
          <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 rounded-lg p-3 mb-3">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {analysis ? (
          <div className="bg-violet-50 rounded-lg p-4">
            {renderContent(analysis.content)}
            {analysis.confidence != null && (
              <p className="text-xs text-stone-500 mt-3">Confidence: {Math.round(analysis.confidence * 100)}%</p>
            )}
          </div>
        ) : (
          <p className="text-sm text-stone-500">Analyze your competitive landscape with AI-powered insights.</p>
        )}
      </div>

      <div className="bg-white border border-stone-200 rounded-xl p-6">
        <h3 className="text-sm font-semibold text-stone-900 mb-3 flex items-center gap-2">
          <FileText className="w-4 h-4 text-red-500" />
          Competitor Analysis Artifacts ({competitorArtifacts.length})
        </h3>
        {competitorArtifacts.length === 0 ? (
          <p className="text-sm text-stone-500">No competitor analysis artifacts yet. Create one from the Research Hub.</p>
        ) : (
          <div className="space-y-2">
            {competitorArtifacts.map((artifact: any) => (
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
