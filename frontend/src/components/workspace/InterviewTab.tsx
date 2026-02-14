import { useState } from 'react'
import {
  Mic, Sparkles, Loader2, AlertCircle, FileText, ChevronDown, ChevronRight
} from 'lucide-react'

interface Props {
  workspaceId: number
  workspace: any
  token: string
  onRefresh: () => void
}

export default function InterviewTab({ workspaceId, workspace, token, onRefresh: _onRefresh }: Props) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [guide, setGuide] = useState<any>(null)
  const [expandedSections, setExpandedSections] = useState<Set<number>>(new Set())

  const interviewArtifacts = (workspace.artifacts || []).filter((a: any) => a.artifact_type === 'interview')

  const generateGuide = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`/api/v1/enhanced-workspaces/${workspaceId}/ai/insights`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ insight_type: 'interview_guide' }),
      })
      if (!res.ok) throw new Error('Failed to generate interview guide')
      const data = await res.json()
      setGuide(data)
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
      const sections = content.sections || content.guide?.sections || []
      const tips = content.tips || content.guide?.tips || []
      const questions = content.questions || content.guide?.questions || []

      return (
        <div className="space-y-4">
          {sections.length > 0 && sections.map((section: any, idx: number) => (
            <div key={idx} className="border border-stone-100 rounded-lg overflow-hidden">
              <button
                onClick={() => toggleSection(idx)}
                className="w-full flex items-center gap-2 p-3 text-left hover:bg-stone-50"
              >
                {expandedSections.has(idx) ? <ChevronDown className="w-4 h-4 text-stone-400" /> : <ChevronRight className="w-4 h-4 text-stone-400" />}
                <span className="text-sm font-medium text-stone-900">{section.title || section.name || `Section ${idx + 1}`}</span>
              </button>
              {expandedSections.has(idx) && (
                <div className="px-4 pb-3 space-y-2">
                  {(section.questions || []).map((q: any, qi: number) => (
                    <div key={qi} className="flex items-start gap-2">
                      <span className="text-violet-500 font-medium text-sm mt-0.5">{qi + 1}.</span>
                      <p className="text-sm text-stone-600">{typeof q === 'string' ? q : q.question || q.text || JSON.stringify(q)}</p>
                    </div>
                  ))}
                  {section.description && <p className="text-xs text-stone-500 mt-2">{section.description}</p>}
                </div>
              )}
            </div>
          ))}

          {questions.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-stone-900 mb-2">Questions</h4>
              <ol className="space-y-2 list-decimal list-inside">
                {questions.map((q: any, i: number) => (
                  <li key={i} className="text-sm text-stone-600">{typeof q === 'string' ? q : q.question || q.text || JSON.stringify(q)}</li>
                ))}
              </ol>
            </div>
          )}

          {tips.length > 0 && (
            <div className="bg-amber-50 rounded-lg p-3">
              <h4 className="text-sm font-medium text-amber-800 mb-2">Tips</h4>
              <ul className="space-y-1">
                {tips.map((tip: any, i: number) => (
                  <li key={i} className="text-sm text-amber-700 flex items-start gap-1">
                    <span>•</span>
                    <span>{typeof tip === 'string' ? tip : JSON.stringify(tip)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {sections.length === 0 && questions.length === 0 && (
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
            <Mic className="w-5 h-5 text-violet-500" />
            Interview Guide
          </h2>
          <button
            onClick={generateGuide}
            disabled={loading}
            className="px-4 py-2 bg-violet-600 text-white text-sm font-medium rounded-lg hover:bg-violet-700 disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            Generate Interview Guide
          </button>
        </div>

        {error && (
          <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 rounded-lg p-3 mb-3">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {guide ? (
          <div className="bg-violet-50 rounded-lg p-4">
            {renderContent(guide.content)}
            {guide.confidence != null && (
              <p className="text-xs text-stone-500 mt-3">Confidence: {Math.round(guide.confidence * 100)}%</p>
            )}
          </div>
        ) : (
          <p className="text-sm text-stone-500">Generate a tailored interview guide based on your opportunity and research context.</p>
        )}
      </div>

      <div className="bg-white border border-stone-200 rounded-xl p-6">
        <h3 className="text-sm font-semibold text-stone-900 mb-3 flex items-center gap-2">
          <FileText className="w-4 h-4 text-blue-500" />
          Interview Artifacts ({interviewArtifacts.length})
        </h3>
        {interviewArtifacts.length === 0 ? (
          <p className="text-sm text-stone-500">No interview artifacts yet. Create one from the Research Hub.</p>
        ) : (
          <div className="space-y-2">
            {interviewArtifacts.map((artifact: any) => (
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
