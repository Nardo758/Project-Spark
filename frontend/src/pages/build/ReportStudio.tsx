import { useMemo } from 'react'
import { useParams, useSearchParams, Link } from 'react-router-dom'
import { ArrowLeft, Lightbulb, Search, MapPin, Target } from 'lucide-react'
import ReportLibrary from '../../components/ReportLibrary'

const TITLE_BY_TYPE: Record<string, string> = {
  'business-plan': 'Business Plan Reports',
  financials: 'Financial Reports',
  'pitch-deck': 'Pitch Deck Reports',
}

const SOURCE_META: Record<string, { label: string; icon: React.ComponentType<{ className?: string }>; color: string }> = {
  validate: { label: 'Idea Validation', icon: Lightbulb, color: 'emerald' },
  search: { label: 'Opportunity Search', icon: Search, color: 'purple' },
  location: { label: 'Location Analysis', icon: MapPin, color: 'blue' },
  clone: { label: 'Clone Success', icon: Target, color: 'orange' },
}

function parseOptionalPositiveInt(raw: string | null): number | undefined {
  if (!raw) return undefined
  const parsed = Number(raw)
  if (!Number.isFinite(parsed) || parsed <= 0) return undefined
  return Math.floor(parsed)
}

function parseContext(raw: string | null): Record<string, unknown> | null {
  if (!raw) return null
  try {
    return JSON.parse(decodeURIComponent(raw))
  } catch {
    return null
  }
}

function buildCustomContext(source: string | null, context: Record<string, unknown> | null): string {
  if (!context) return ''
  const parts: string[] = []

  if (source === 'validate') {
    if (context.idea) parts.push(`Business Idea: ${context.idea}`)
    if (context.recommendation) parts.push(`Recommended Model: ${context.recommendation}`)
    if (context.viability_report) {
      const vr = context.viability_report as Record<string, unknown>
      if (vr.strengths) parts.push(`Strengths: ${(vr.strengths as string[]).join(', ')}`)
      if (vr.weaknesses) parts.push(`Weaknesses: ${(vr.weaknesses as string[]).join(', ')}`)
    }
  } else if (source === 'search') {
    if (context.title) parts.push(`Opportunity: ${context.title}`)
    if (context.description) parts.push(`Description: ${context.description}`)
    if (context.category) parts.push(`Category: ${context.category}`)
  } else if (source === 'location') {
    if (context.city) parts.push(`Location: ${context.city}${context.state ? `, ${context.state}` : ''}`)
    if (context.business_description) parts.push(`Business: ${context.business_description}`)
    if (context.inferred_category) parts.push(`Category: ${context.inferred_category}`)
    const mr = context.market_report as Record<string, unknown> | undefined
    if (mr?.market_score) parts.push(`Market Score: ${mr.market_score}/100`)
    if (mr?.recommendation) parts.push(`Market Recommendation: ${mr.recommendation}`)
  } else if (source === 'clone') {
    const sb = context.source_business as Record<string, unknown> | undefined
    if (sb?.name) parts.push(`Source Business: ${sb.name}`)
    if (sb?.address) parts.push(`Original Location: ${sb.address}`)
    const tl = context.target_location as Record<string, unknown> | undefined
    if (tl?.city) parts.push(`Target: ${tl.city}, ${tl.state || ''}`)
    if (tl?.similarity_score) parts.push(`Match Score: ${Math.round(tl.similarity_score as number)}/100`)
  }

  return parts.join('\n')
}

export default function ReportStudio() {
  const { type } = useParams()
  const [searchParams] = useSearchParams()

  const opportunityId = useMemo(() => {
    return (
      parseOptionalPositiveInt(searchParams.get('opp')) ??
      parseOptionalPositiveInt(searchParams.get('opportunityId'))
    )
  }, [searchParams])

  const source = searchParams.get('source')
  const contextData = useMemo(() => parseContext(searchParams.get('context')), [searchParams])
  const customContext = useMemo(() => buildCustomContext(source, contextData), [source, contextData])

  const sourceMeta = source ? SOURCE_META[source] : null
  const title = type ? TITLE_BY_TYPE[type] || 'Consultant Studio Reports' : 'Consultant Studio Reports'

  const colorMap: Record<string, string> = {
    emerald: 'from-emerald-500 to-teal-500',
    purple: 'from-purple-500 to-indigo-500',
    blue: 'from-blue-500 to-indigo-500',
    orange: 'from-orange-500 to-red-500',
  }

  return (
    <div className="min-h-screen bg-stone-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <Link
            to="/build/consultant-studio"
            className="inline-flex items-center gap-1 text-sm text-purple-600 hover:text-purple-700 mb-3"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Consultant Studio
          </Link>
          <h1 className="text-2xl font-bold text-stone-900">{title}</h1>
          <p className="text-sm text-stone-600 mt-1">
            Generate AI-powered reports using your workspace and opportunity context.
          </p>
        </div>

        {sourceMeta && contextData && (
          <div className={`mb-6 rounded-xl overflow-hidden border border-gray-200`}>
            <div className={`bg-gradient-to-r ${colorMap[sourceMeta.color] || 'from-purple-500 to-indigo-500'} px-5 py-3 text-white`}>
              <div className="flex items-center gap-2">
                <sourceMeta.icon className="w-5 h-5" />
                <span className="font-medium">Context from {sourceMeta.label}</span>
              </div>
            </div>
            <div className="bg-white px-5 py-4">
              <div className="text-sm text-gray-700 whitespace-pre-line leading-relaxed">
                {customContext}
              </div>
            </div>
          </div>
        )}

        <ReportLibrary
          opportunityId={opportunityId}
          customContext={customContext || undefined}
        />
      </div>
    </div>
  )
}
