import { useState } from 'react'
import {
  Plus, Trash2, Loader2, AlertCircle, FileText,
  Search, X
} from 'lucide-react'

interface Props {
  workspaceId: number
  workspace: any
  token: string
  onRefresh: () => void
}

const ARTIFACT_TYPES = [
  { value: 'interview', label: 'Interview', color: 'bg-blue-100 text-blue-700' },
  { value: 'survey', label: 'Survey', color: 'bg-indigo-100 text-indigo-700' },
  { value: 'competitor_analysis', label: 'Competitor Analysis', color: 'bg-red-100 text-red-700' },
  { value: 'financial_model', label: 'Financial Model', color: 'bg-emerald-100 text-emerald-700' },
  { value: 'market_research', label: 'Market Research', color: 'bg-amber-100 text-amber-700' },
  { value: 'customer_persona', label: 'Customer Persona', color: 'bg-pink-100 text-pink-700' },
  { value: 'swot_analysis', label: 'SWOT Analysis', color: 'bg-purple-100 text-purple-700' },
  { value: 'notes', label: 'Notes', color: 'bg-stone-100 text-stone-700' },
  { value: 'ai_insight', label: 'AI Insight', color: 'bg-violet-100 text-violet-700' },
  { value: 'custom', label: 'Custom', color: 'bg-cyan-100 text-cyan-700' },
]

export default function ResearchHubTab({ workspaceId, workspace, token, onRefresh }: Props) {
  const [showForm, setShowForm] = useState(false)
  const [title, setTitle] = useState('')
  const [artifactType, setArtifactType] = useState('notes')
  const [summary, setSummary] = useState('')
  const [creating, setCreating] = useState(false)
  const [deleting, setDeleting] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState('')

  const artifacts: any[] = workspace.artifacts || []

  const filteredArtifacts = filter
    ? artifacts.filter((a: any) => a.artifact_type === filter)
    : artifacts

  const createArtifact = async () => {
    if (!title.trim()) return
    setCreating(true)
    setError(null)
    try {
      const res = await fetch(`/api/v1/enhanced-workspaces/${workspaceId}/artifacts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ artifact_type: artifactType, title: title.trim(), summary: summary.trim() || null }),
      })
      if (!res.ok) throw new Error('Failed to create artifact')
      setTitle('')
      setSummary('')
      setArtifactType('notes')
      setShowForm(false)
      onRefresh()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setCreating(false)
    }
  }

  const deleteArtifact = async (artifactId: number) => {
    setDeleting(artifactId)
    setError(null)
    try {
      const res = await fetch(`/api/v1/enhanced-workspaces/${workspaceId}/artifacts/${artifactId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to delete artifact')
      onRefresh()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setDeleting(null)
    }
  }

  const getTypeBadge = (type: string) => {
    const t = ARTIFACT_TYPES.find(a => a.value === type)
    return t || { label: type, color: 'bg-stone-100 text-stone-700' }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-stone-900 flex items-center gap-2">
          <FileText className="w-5 h-5 text-violet-500" />
          Research Artifacts ({artifacts.length})
        </h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-violet-600 text-white text-sm font-medium rounded-lg hover:bg-violet-700 flex items-center gap-2"
        >
          {showForm ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
          {showForm ? 'Cancel' : 'New Artifact'}
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 rounded-lg p-3">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {showForm && (
        <div className="bg-white border border-stone-200 rounded-xl p-5 space-y-3">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Artifact title..."
            className="w-full px-4 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:border-violet-400"
          />
          <select
            value={artifactType}
            onChange={(e) => setArtifactType(e.target.value)}
            className="w-full px-4 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:border-violet-400 bg-white"
          >
            {ARTIFACT_TYPES.map(t => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
          <textarea
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            placeholder="Summary or description..."
            rows={3}
            className="w-full px-4 py-3 border border-stone-200 rounded-lg text-sm focus:outline-none focus:border-violet-400 resize-none"
          />
          <button
            onClick={createArtifact}
            disabled={!title.trim() || creating}
            className="px-4 py-2 bg-violet-600 text-white text-sm font-medium rounded-lg hover:bg-violet-700 disabled:opacity-50 flex items-center gap-2"
          >
            {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            Create Artifact
          </button>
        </div>
      )}

      <div className="flex items-center gap-2 flex-wrap">
        <button
          onClick={() => setFilter('')}
          className={`px-3 py-1 text-xs rounded-full font-medium transition-colors ${!filter ? 'bg-violet-600 text-white' : 'bg-stone-100 text-stone-600 hover:bg-stone-200'}`}
        >
          All
        </button>
        {ARTIFACT_TYPES.map(t => {
          const count = artifacts.filter((a: any) => a.artifact_type === t.value).length
          if (count === 0) return null
          return (
            <button
              key={t.value}
              onClick={() => setFilter(t.value)}
              className={`px-3 py-1 text-xs rounded-full font-medium transition-colors ${filter === t.value ? 'bg-violet-600 text-white' : `${t.color} hover:opacity-80`}`}
            >
              {t.label} ({count})
            </button>
          )
        })}
      </div>

      <div className="space-y-3">
        {filteredArtifacts.length === 0 ? (
          <div className="text-center py-12 text-stone-500">
            <Search className="w-12 h-12 mx-auto mb-3 text-stone-300" />
            <p className="font-medium text-stone-900 mb-1">No artifacts found</p>
            <p className="text-sm">Create your first research artifact to get started.</p>
          </div>
        ) : (
          filteredArtifacts.map((artifact: any) => {
            const badge = getTypeBadge(artifact.artifact_type)
            return (
              <div key={artifact.id} className="bg-white border border-stone-200 rounded-xl p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-sm font-semibold text-stone-900 truncate">{artifact.title}</h3>
                      <span className={`px-2 py-0.5 text-xs rounded-full font-medium ${badge.color}`}>{badge.label}</span>
                    </div>
                    {artifact.summary && <p className="text-sm text-stone-600 line-clamp-2">{artifact.summary}</p>}
                    <p className="text-xs text-stone-400 mt-2">{new Date(artifact.created_at).toLocaleDateString()}</p>
                  </div>
                  <button
                    onClick={() => deleteArtifact(artifact.id)}
                    disabled={deleting === artifact.id}
                    className="p-2 text-stone-400 hover:text-red-500 transition-colors flex-shrink-0 ml-2"
                  >
                    {deleting === artifact.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
