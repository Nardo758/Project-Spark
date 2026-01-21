import { useState } from 'react'
import {
  MapPin,
  TrendingUp,
  TrendingDown,
  Users,
  Building2,
  ChevronDown,
  ChevronUp,
  Star,
  AlertCircle,
  CheckCircle2
} from 'lucide-react'

interface LocationMetrics {
  market_size?: string
  competition?: string
  growth_rate?: string
  [key: string]: string | undefined
}

interface LocationScore {
  location: string
  latitude: number
  longitude: number
  overall_score: number
  market_fit: number
  competition_level: string
  demographic_match: number
  growth_potential: string
  strengths: string[]
  weaknesses: string[]
  recommendation: string
}

interface CityComparisonCardsProps {
  locations: LocationScore[]
  onSelectLocation?: (location: LocationScore) => void
  selectedLocation?: string
}

function getScoreColor(score: number): string {
  if (score >= 80) return 'text-green-400'
  if (score >= 65) return 'text-yellow-400'
  return 'text-red-400'
}

function getScoreBgColor(score: number): string {
  if (score >= 80) return 'bg-green-500/20 border-green-500/30'
  if (score >= 65) return 'bg-yellow-500/20 border-yellow-500/30'
  return 'bg-red-500/20 border-red-500/30'
}

function getCompetitionColor(level: string): string {
  switch (level.toLowerCase()) {
    case 'low': return 'text-green-400'
    case 'moderate': return 'text-yellow-400'
    case 'high': return 'text-red-400'
    default: return 'text-gray-400'
  }
}

function getGrowthIcon(potential: string) {
  if (potential.toLowerCase().includes('growing') || potential.toLowerCase().includes('booming')) {
    return <TrendingUp className="w-4 h-4 text-green-400" />
  }
  if (potential.toLowerCase().includes('declining')) {
    return <TrendingDown className="w-4 h-4 text-red-400" />
  }
  return <TrendingUp className="w-4 h-4 text-gray-400" />
}

export default function CityComparisonCards({
  locations,
  onSelectLocation,
  selectedLocation
}: CityComparisonCardsProps) {
  const [expandedCard, setExpandedCard] = useState<string | null>(null)

  if (!locations || locations.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        <MapPin className="w-12 h-12 mx-auto mb-3 opacity-50" />
        <p>No locations to compare</p>
        <p className="text-sm mt-1">Add locations to see comparison cards</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-300">Location Comparison</h3>
        <span className="text-xs text-gray-500">{locations.length} locations</span>
      </div>

      {locations.map((location, index) => {
        const isExpanded = expandedCard === location.location
        const isSelected = selectedLocation === location.location
        const isBestMatch = index === 0

        return (
          <div
            key={location.location}
            className={`rounded-lg border transition-all cursor-pointer ${
              isSelected
                ? 'border-purple-500 bg-purple-500/10'
                : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
            }`}
            onClick={() => onSelectLocation?.(location)}
          >
            <div className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div
                    className={`w-10 h-10 rounded-lg flex items-center justify-center border ${getScoreBgColor(
                      location.overall_score
                    )}`}
                  >
                    <span className={`text-lg font-bold ${getScoreColor(location.overall_score)}`}>
                      {Math.round(location.overall_score)}
                    </span>
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-white">{location.location}</h4>
                      {isBestMatch && (
                        <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded-full">
                          Best Match
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-400">{location.recommendation}</p>
                  </div>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setExpandedCard(isExpanded ? null : location.location)
                  }}
                  className="p-1 hover:bg-gray-700 rounded"
                >
                  {isExpanded ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </button>
              </div>

              <div className="mt-3 grid grid-cols-3 gap-3">
                <div className="text-center">
                  <div className="text-xs text-gray-500 mb-1">Market Fit</div>
                  <div className="text-sm font-medium text-white">
                    {Math.round(location.market_fit * 100)}%
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-gray-500 mb-1">Competition</div>
                  <div className={`text-sm font-medium ${getCompetitionColor(location.competition_level)}`}>
                    {location.competition_level}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-gray-500 mb-1">Growth</div>
                  <div className="flex items-center justify-center gap-1">
                    {getGrowthIcon(location.growth_potential)}
                    <span className="text-sm font-medium text-white">
                      {location.growth_potential}
                    </span>
                  </div>
                </div>
              </div>

              {isExpanded && (
                <div className="mt-4 pt-4 border-t border-gray-700 space-y-3">
                  <div>
                    <div className="flex items-center gap-2 text-xs text-gray-400 mb-2">
                      <Users className="w-3 h-3" />
                      Demographics Match
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-purple-500 h-2 rounded-full"
                        style={{ width: `${location.demographic_match * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500">
                      {Math.round(location.demographic_match * 100)}% match
                    </span>
                  </div>

                  {location.strengths.length > 0 && (
                    <div>
                      <div className="text-xs text-gray-400 mb-2 flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3 text-green-400" />
                        Strengths
                      </div>
                      <ul className="space-y-1">
                        {location.strengths.map((strength, idx) => (
                          <li key={idx} className="text-xs text-gray-300 flex items-start gap-2">
                            <span className="text-green-400 mt-0.5">+</span>
                            {strength}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {location.weaknesses.length > 0 && (
                    <div>
                      <div className="text-xs text-gray-400 mb-2 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3 text-yellow-400" />
                        Considerations
                      </div>
                      <ul className="space-y-1">
                        {location.weaknesses.map((weakness, idx) => (
                          <li key={idx} className="text-xs text-gray-300 flex items-start gap-2">
                            <span className="text-yellow-400 mt-0.5">-</span>
                            {weakness}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="pt-2">
                    <button
                      className="w-full py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded-lg transition-colors"
                      onClick={(e) => {
                        e.stopPropagation()
                        onSelectLocation?.(location)
                      }}
                    >
                      Select This Location
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
