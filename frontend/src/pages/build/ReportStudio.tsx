import { useMemo } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import ReportLibrary from '../../components/ReportLibrary'

const TITLE_BY_TYPE: Record<string, string> = {
  'business-plan': 'Business Plan Reports',
  financials: 'Financial Reports',
  'pitch-deck': 'Pitch Deck Reports',
}

function parseOptionalPositiveInt(raw: string | null): number | undefined {
  if (!raw) return undefined
  const parsed = Number(raw)
  if (!Number.isFinite(parsed) || parsed <= 0) return undefined
  return Math.floor(parsed)
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

  const title = type ? TITLE_BY_TYPE[type] || 'Consultant Studio Reports' : 'Consultant Studio Reports'

  return (
    <div className="min-h-screen bg-stone-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-stone-900">{title}</h1>
          <p className="text-sm text-stone-600 mt-1">
            Generate AI-powered reports using your workspace and opportunity context.
          </p>
        </div>
        <ReportLibrary opportunityId={opportunityId} />
      </div>
    </div>
  )
}
