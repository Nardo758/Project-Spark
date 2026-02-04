import { Sparkles } from 'lucide-react'

type MatchScoreBadgeProps = {
  score: number
  size?: 'sm' | 'md' | 'lg'
  showIcon?: boolean
  showLabel?: boolean
}

/**
 * MatchScoreBadge - Color-coded badge showing opportunity match percentage
 * 
 * Color scheme:
 * - 90-100%: Green (excellent match)
 * - 70-89%: Yellow/Amber (good match)
 * - 0-69%: Gray (decent match)
 */
export default function MatchScoreBadge({ 
  score, 
  size = 'md', 
  showIcon = true,
  showLabel = true 
}: MatchScoreBadgeProps) {
  // Determine color based on score
  const getColorClasses = () => {
    if (score >= 90) {
      return {
        bg: 'bg-green-50',
        text: 'text-green-700',
        border: 'border-green-200',
        ring: 'ring-green-100'
      }
    } else if (score >= 70) {
      return {
        bg: 'bg-amber-50',
        text: 'text-amber-700',
        border: 'border-amber-200',
        ring: 'ring-amber-100'
      }
    } else {
      return {
        bg: 'bg-gray-50',
        text: 'text-gray-600',
        border: 'border-gray-200',
        ring: 'ring-gray-100'
      }
    }
  }

  // Size variants
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return {
          container: 'px-2 py-1 text-xs gap-1',
          icon: 'w-3 h-3',
          text: 'text-xs'
        }
      case 'lg':
        return {
          container: 'px-4 py-2 text-base gap-2',
          icon: 'w-5 h-5',
          text: 'text-base'
        }
      case 'md':
      default:
        return {
          container: 'px-3 py-1.5 text-sm gap-1.5',
          icon: 'w-4 h-4',
          text: 'text-sm'
        }
    }
  }

  const colors = getColorClasses()
  const sizes = getSizeClasses()

  // Get match quality label
  const getMatchLabel = () => {
    if (score >= 90) return 'Excellent Match'
    if (score >= 70) return 'Good Match'
    return 'Match'
  }

  return (
    <div 
      className={`
        inline-flex items-center font-semibold rounded-full border
        ${colors.bg} ${colors.text} ${colors.border}
        ${sizes.container}
        transition-all duration-200
        hover:shadow-sm hover:scale-105
      `}
      title={`${score}% match - ${getMatchLabel()}`}
    >
      {showIcon && (
        <Sparkles className={`${sizes.icon} ${score >= 90 ? 'animate-pulse' : ''}`} />
      )}
      <span className={`font-bold ${sizes.text}`}>
        {score}%
      </span>
      {showLabel && size !== 'sm' && (
        <span className="font-normal opacity-90">match</span>
      )}
    </div>
  )
}
