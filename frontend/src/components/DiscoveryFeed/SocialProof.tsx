import { Users, TrendingUp, Award } from 'lucide-react'
import type { SocialProof as SocialProofType } from '../../types/opportunity'

type SocialProofProps = {
  socialProof: SocialProofType
  compact?: boolean
}

/**
 * SocialProof - Display social validation indicators
 * Shows similar users who validated, expert validations, and trending status
 */
export default function SocialProof({ socialProof, compact = false }: SocialProofProps) {
  const { 
    similar_users_validated, 
    similar_users_text, 
    expert_validation_count,
    trending_indicator 
  } = socialProof

  // Don't render if no social proof data
  const hasSocialProof = similar_users_validated > 0 || expert_validation_count || trending_indicator
  if (!hasSocialProof) return null

  if (compact) {
    return (
      <div className="flex items-center gap-3 text-xs text-gray-600">
        {similar_users_validated > 0 && (
          <div className="flex items-center gap-1" title={similar_users_text}>
            <Users className="w-3 h-3" />
            <span>{similar_users_validated}</span>
          </div>
        )}
        {expert_validation_count && expert_validation_count > 0 && (
          <div className="flex items-center gap-1" title={`${expert_validation_count} expert validations`}>
            <Award className="w-3 h-3 text-purple-600" />
            <span>{expert_validation_count}</span>
          </div>
        )}
        {trending_indicator && (
          <div className="flex items-center gap-1 text-orange-600" title="Trending opportunity">
            <TrendingUp className="w-3 h-3" />
            <span>Trending</span>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {similar_users_validated > 0 && (
        <div className="flex items-start gap-2 p-2 bg-blue-50 border border-blue-100 rounded-lg">
          <Users className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-blue-800">
            <span className="font-semibold">{similar_users_text}</span>
          </p>
        </div>
      )}

      {expert_validation_count && expert_validation_count > 0 && (
        <div className="flex items-start gap-2 p-2 bg-purple-50 border border-purple-100 rounded-lg">
          <Award className="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-purple-800">
            <span className="font-semibold">{expert_validation_count} expert{expert_validation_count > 1 ? 's' : ''}</span> validated this opportunity
          </p>
        </div>
      )}

      {trending_indicator && (
        <div className="flex items-start gap-2 p-2 bg-orange-50 border border-orange-100 rounded-lg">
          <TrendingUp className="w-4 h-4 text-orange-600 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-orange-800">
            <span className="font-semibold">Trending</span> - Growing validation momentum
          </p>
        </div>
      )}
    </div>
  )
}
