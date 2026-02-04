/**
 * OpportunityCard Component - Matches existing OppGrid card design
 */

import { FileText, Bookmark } from 'lucide-react'
import { useState } from 'react'

interface OpportunityCardProps {
  opportunity: {
    id: number
    title: string
    description?: string
    category?: string
    feasibility_score?: number
    validation_count?: number
    market_size?: string
    growth_rate?: number
    access_state?: 'unlocked' | 'locked' | 'preview'
    user_validated?: boolean
    user_saved?: boolean
    ai_generated_title?: string
    ai_summary?: string
  }
  userTier?: string
  onValidate?: (id: number) => void
  onSave?: (id: number) => void
  onAnalyze?: (id: number) => void
  onShare?: (id: number) => void
  isValidated?: boolean
  isSaved?: boolean
  className?: string
}

export default function OpportunityCard({
  opportunity,
  userTier,
  onValidate,
  onSave,
  onAnalyze,
  onShare,
  isValidated: externalIsValidated,
  isSaved: externalIsSaved,
  className = ''
}: OpportunityCardProps) {
  const [isValidated, setIsValidated] = useState(externalIsValidated || opportunity.user_validated || false)
  const [isSaved, setIsSaved] = useState(externalIsSaved || opportunity.user_saved || false)

  const handleValidate = (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsValidated(!isValidated)
    onValidate?.(opportunity.id)
  }

  const handleSave = (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsSaved(!isSaved)
    onSave?.(opportunity.id)
  }

  const handleAnalyze = (e: React.MouseEvent) => {
    e.stopPropagation()
    onAnalyze?.(opportunity.id)
  }

  // Get feasibility color
  const getFeasibilityColor = (score: number) => {
    if (score >= 75) return 'text-emerald-600 bg-emerald-50'
    if (score >= 50) return 'text-amber-600 bg-amber-50'
    return 'text-gray-600 bg-gray-50'
  }

  // Format market size
  const formatMarketSize = (size: string) => {
    if (size.includes('$')) return size
    return `~$${size}`
  }

  // Format growth rate
  const formatGrowth = (rate: number) => {
    return rate > 0 ? `+${rate}%` : `${rate}%`
  }

  return (
    <div
      className={`
        bg-white rounded-lg border border-gray-200 p-6
        hover:border-emerald-200 hover:shadow-md
        transition-all duration-200 cursor-pointer
        ${className}
      `}
      onClick={() => window.location.href = `/opportunity/${opportunity.id}`}
    >
      {/* Header - Category + Score */}
      <div className="flex items-start justify-between mb-4">
        {/* Category + Status Badge */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            {opportunity.category}
          </span>
          {opportunity.access_state === 'unlocked' && (
            <span className="px-2 py-0.5 bg-emerald-100 text-emerald-700 text-xs font-medium rounded">
              Unlocked
            </span>
          )}
          {opportunity.access_state === 'locked' && (
            <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs font-medium rounded">
              Locked
            </span>
          )}
        </div>

        {/* Feasibility Score */}
        <div className={`
          w-14 h-14 rounded-full flex items-center justify-center
          text-2xl font-bold
          ${getFeasibilityColor(opportunity.feasibility_score || 0)}
        `}>
          {opportunity.feasibility_score || 0}
        </div>
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2 hover:text-emerald-600 transition-colors">
        {opportunity.title}
      </h3>

      {/* Description */}
      <p className="text-sm text-gray-600 mb-4 line-clamp-2">
        {opportunity.description}
      </p>

      {/* Metrics Row */}
      <div className="grid grid-cols-3 gap-4 mb-4 pb-4 border-b border-gray-100">
        <div>
          <div className="text-xs text-gray-500 mb-1">Signals</div>
          <div className="text-lg font-semibold text-gray-900">
            {opportunity.validation_count}
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-500 mb-1">Market</div>
          <div className="text-lg font-semibold text-gray-900">
            {formatMarketSize(opportunity.market_size || '')}
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-500 mb-1">Growth</div>
          <div className={`text-lg font-semibold ${
            (opportunity.growth_rate || 0) > 0 ? 'text-emerald-600' : 'text-gray-900'
          }`}>
            {formatGrowth(opportunity.growth_rate || 0)}
          </div>
        </div>
      </div>

      {/* Actions Row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {/* Report Button */}
          <button
            onClick={handleAnalyze}
            className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-emerald-600 transition-colors"
            aria-label="View report"
          >
            <FileText className="w-4 h-4" />
            <span className="hidden sm:inline">Report</span>
          </button>

          {/* Save Button */}
          <button
            onClick={handleSave}
            className={`flex items-center gap-1.5 text-sm transition-colors ${
              isSaved
                ? 'text-emerald-600'
                : 'text-gray-600 hover:text-emerald-600'
            }`}
            aria-label={isSaved ? 'Unsave' : 'Save'}
          >
            <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
            <span className="hidden sm:inline">Save</span>
          </button>
        </div>

        {/* View Full Analysis Link */}
        <button
          onClick={handleAnalyze}
          className="text-sm text-gray-600 hover:text-emerald-600 transition-colors flex items-center gap-1"
        >
          View full analysis
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  )
}
