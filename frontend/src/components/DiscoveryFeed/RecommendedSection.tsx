import { useState, useEffect } from 'react'
import { ChevronLeft, ChevronRight, ArrowRight, Sparkles, TrendingUp, CheckCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'
import { fetchRecommendedOpportunities, quickValidateOpportunity } from '../../services/opportunityApi'
import MatchScoreBadge from './MatchScoreBadge'
import SocialProof from './SocialProof'
import type { Opportunity } from '../../types/opportunity'

type RecommendedSectionProps = {
  limit?: number
  onValidate?: (opportunityId: number) => void
}

/**
 * RecommendedSection - Personalized opportunity recommendations carousel
 * Displays top matches for the user based on their profile, interests, and past activity
 */
export default function RecommendedSection({ limit = 6, onValidate }: RecommendedSectionProps) {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [loading, setLoading] = useState(true)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [validatingIds, setValidatingIds] = useState<Set<number>>(new Set())
  
  const { token, isAuthenticated, user } = useAuthStore()
  const navigate = useNavigate()

  // Fetch recommendations on mount
  useEffect(() => {
    if (!isAuthenticated || !token) {
      setLoading(false)
      return
    }

    const loadRecommendations = async () => {
      setLoading(true)
      const recommended = await fetchRecommendedOpportunities(token, limit)
      setOpportunities(recommended)
      setLoading(false)
    }

    loadRecommendations()
  }, [token, isAuthenticated, limit])

  // Don't render for unauthenticated users
  if (!isAuthenticated) return null

  // Carousel controls
  const canScrollLeft = currentIndex > 0
  const canScrollRight = currentIndex < opportunities.length - 3
  
  const scrollLeft = () => {
    if (canScrollLeft) {
      setCurrentIndex(prev => Math.max(0, prev - 1))
    }
  }
  
  const scrollRight = () => {
    if (canScrollRight) {
      setCurrentIndex(prev => Math.min(opportunities.length - 3, prev + 1))
    }
  }

  // Handle quick validation
  const handleQuickValidate = async (opportunityId: number) => {
    if (!token || validatingIds.has(opportunityId)) return

    setValidatingIds(prev => new Set(prev).add(opportunityId))
    
    const success = await quickValidateOpportunity(opportunityId, token)
    
    if (success) {
      // Update local state
      setOpportunities(prev => prev.map(opp => 
        opp.id === opportunityId 
          ? { ...opp, user_validated: true, validation_count: opp.validation_count + 1 }
          : opp
      ))
      
      // Notify parent
      onValidate?.(opportunityId)
    }
    
    setValidatingIds(prev => {
      const next = new Set(prev)
      next.delete(opportunityId)
      return next
    })
  }

  // Loading state
  if (loading) {
    return (
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 mb-8 border border-purple-100">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-5 h-5 text-purple-600 animate-pulse" />
          <h2 className="text-xl font-bold text-gray-900">Recommended for You</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="bg-white rounded-lg p-4 border border-gray-200 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-full mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-20"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // No recommendations state
  if (opportunities.length === 0) {
    return (
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 mb-8 border border-purple-100">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="w-5 h-5 text-purple-600" />
          <h2 className="text-xl font-bold text-gray-900">Recommended for You</h2>
        </div>
        <p className="text-gray-600 text-sm">
          We're learning your preferences. Validate a few opportunities to get personalized recommendations!
        </p>
      </div>
    )
  }

  const visibleOpportunities = opportunities.slice(currentIndex, currentIndex + 3)

  return (
    <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 mb-8 border border-purple-100 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-600" />
          <h2 className="text-xl font-bold text-gray-900">Recommended for You</h2>
          <span className="text-sm text-gray-500">
            (Based on your profile and activity)
          </span>
        </div>
        
        <button
          onClick={() => navigate('/discover?sort=recommended')}
          className="flex items-center gap-1 text-sm text-purple-600 hover:text-purple-700 font-medium transition-colors"
        >
          View All
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Carousel */}
      <div className="relative">
        {/* Navigation Buttons */}
        {opportunities.length > 3 && (
          <>
            <button
              onClick={scrollLeft}
              disabled={!canScrollLeft}
              className={`
                absolute left-0 top-1/2 -translate-y-1/2 -translate-x-3 z-10
                w-8 h-8 rounded-full bg-white shadow-lg border border-gray-200
                flex items-center justify-center transition-all
                ${canScrollLeft 
                  ? 'hover:bg-gray-50 hover:scale-110 cursor-pointer' 
                  : 'opacity-50 cursor-not-allowed'}
              `}
            >
              <ChevronLeft className="w-5 h-5 text-gray-700" />
            </button>
            
            <button
              onClick={scrollRight}
              disabled={!canScrollRight}
              className={`
                absolute right-0 top-1/2 -translate-y-1/2 translate-x-3 z-10
                w-8 h-8 rounded-full bg-white shadow-lg border border-gray-200
                flex items-center justify-center transition-all
                ${canScrollRight 
                  ? 'hover:bg-gray-50 hover:scale-110 cursor-pointer' 
                  : 'opacity-50 cursor-not-allowed'}
              `}
            >
              <ChevronRight className="w-5 h-5 text-gray-700" />
            </button>
          </>
        )}

        {/* Opportunity Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {visibleOpportunities.map(opp => (
            <OpportunityCard
              key={opp.id}
              opportunity={opp}
              onValidate={handleQuickValidate}
              isValidating={validatingIds.has(opp.id)}
            />
          ))}
        </div>
      </div>

      {/* Pagination Indicator */}
      {opportunities.length > 3 && (
        <div className="flex justify-center gap-2 mt-4">
          {Array.from({ length: Math.ceil(opportunities.length / 3) }).map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrentIndex(i * 3)}
              className={`
                w-2 h-2 rounded-full transition-all
                ${Math.floor(currentIndex / 3) === i 
                  ? 'bg-purple-600 w-6' 
                  : 'bg-gray-300 hover:bg-gray-400'}
              `}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// Individual Opportunity Card
type OpportunityCardProps = {
  opportunity: Opportunity
  onValidate: (id: number) => void
  isValidating: boolean
}

function OpportunityCard({ opportunity, onValidate, isValidating }: OpportunityCardProps) {
  const navigate = useNavigate()
  const { 
    id, 
    title, 
    description, 
    category, 
    feasibility_score, 
    validation_count,
    growth_rate,
    match_score,
    match_reasons,
    social_proof,
    user_validated 
  } = opportunity

  return (
    <div 
      className="bg-white rounded-lg p-5 border border-gray-200 hover:border-purple-300 hover:shadow-md transition-all cursor-pointer group"
      onClick={() => navigate(`/opportunity/${id}`)}
    >
      {/* Match Score Badge */}
      {match_score !== undefined && (
        <div className="mb-3">
          <MatchScoreBadge score={match_score} size="sm" />
        </div>
      )}

      {/* Category Tag */}
      {category && (
        <div className="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded mb-2">
          {category}
        </div>
      )}

      {/* Title */}
      <h3 className="font-bold text-gray-900 mb-2 line-clamp-2 group-hover:text-purple-600 transition-colors">
        {title}
      </h3>

      {/* Description */}
      <p className="text-sm text-gray-600 mb-3 line-clamp-2">
        {description}
      </p>

      {/* Match Reasons */}
      {match_reasons && match_reasons.length > 0 && (
        <div className="mb-3 text-xs text-gray-600 space-y-1">
          <p className="font-semibold text-purple-700">Match because:</p>
          {match_reasons.slice(0, 2).map((reason, idx) => (
            <div key={idx} className="flex items-center gap-1">
              <span className="text-purple-600">•</span>
              <span>{reason.description}</span>
            </div>
          ))}
        </div>
      )}

      {/* Metrics */}
      <div className="flex items-center gap-3 mb-3 text-xs text-gray-600">
        <div className="flex items-center gap-1" title={`Feasibility: ${feasibility_score}/100`}>
          <div className={`w-2 h-2 rounded-full ${
            feasibility_score >= 75 ? 'bg-green-500' : 
            feasibility_score >= 50 ? 'bg-yellow-500' : 
            'bg-gray-400'
          }`} />
          <span className="font-medium">{feasibility_score}</span>
        </div>
        <div className="flex items-center gap-1">
          <CheckCircle className="w-3 h-3" />
          <span>{validation_count} validations</span>
        </div>
        {growth_rate && growth_rate > 0 && (
          <div className="flex items-center gap-1 text-orange-600">
            <TrendingUp className="w-3 h-3" />
            <span>+{growth_rate}%</span>
          </div>
        )}
      </div>

      {/* Social Proof */}
      {social_proof && (
        <div className="mb-3">
          <SocialProof socialProof={social_proof} compact />
        </div>
      )}

      {/* Quick Validate Button */}
      <button
        onClick={(e) => {
          e.stopPropagation()
          if (!user_validated) {
            onValidate(id)
          }
        }}
        disabled={user_validated || isValidating}
        className={`
          w-full py-2 px-4 rounded-lg font-medium text-sm transition-all
          ${user_validated 
            ? 'bg-green-100 text-green-700 cursor-default' 
            : isValidating
            ? 'bg-gray-200 text-gray-500 cursor-wait'
            : 'bg-purple-600 text-white hover:bg-purple-700 hover:shadow-md active:scale-95'
          }
        `}
      >
        {user_validated ? (
          <span className="flex items-center justify-center gap-1">
            <CheckCircle className="w-4 h-4" />
            Validated
          </span>
        ) : isValidating ? (
          'Validating...'
        ) : (
          'Quick Validate'
        )}
      </button>
    </div>
  )
}
