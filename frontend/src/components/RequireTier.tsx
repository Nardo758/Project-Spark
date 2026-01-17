import { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { useUpgrade } from '../contexts/UpgradeContext'
import { Lock } from 'lucide-react'
import { type Tier, TIER_LEVELS, getTierLevel } from '../constants/pricing'

type Props = {
  children: ReactNode
  requiredTier: Tier
  featureName?: string
}

export default function RequireTier({ children, requiredTier, featureName }: Props) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const isBootstrapped = useAuthStore((s) => s.isBootstrapped)
  const user = useAuthStore((s) => s.user)
  const location = useLocation()
  const { showUpgradeModal } = useUpgrade()

  if (!isBootstrapped) {
    return <div className="max-w-7xl mx-auto px-4 py-10">Loading…</div>
  }

  if (!isAuthenticated) {
    const next = location.pathname + location.search + location.hash
    return <Navigate to={`/login?next=${encodeURIComponent(next)}`} replace />
  }

  const userTier = (user?.tier || 'free') as Tier
  const userLevel = getTierLevel(userTier)
  const requiredLevel = TIER_LEVELS[requiredTier]

  if (userLevel < requiredLevel) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16">
        <div className="bg-white rounded-2xl border-2 border-stone-200 p-12 text-center">
          <div className="w-16 h-16 bg-stone-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Lock className="w-8 h-8 text-stone-400" />
          </div>
          <h1 className="text-2xl font-bold text-stone-900 mb-3">
            {featureName || 'This Feature'} Requires {requiredTier.charAt(0).toUpperCase() + requiredTier.slice(1)}
          </h1>
          <p className="text-stone-600 mb-6 max-w-md mx-auto">
            Upgrade your plan to unlock {featureName?.toLowerCase() || 'this feature'} and get access to premium tools and insights.
          </p>
          <button
            onClick={() => showUpgradeModal('general', featureName || 'Premium Feature')}
            className="inline-flex items-center gap-2 bg-stone-900 text-white px-6 py-3 rounded-lg font-medium hover:bg-stone-800 transition-colors"
          >
            Upgrade to {requiredTier.charAt(0).toUpperCase() + requiredTier.slice(1)}
          </button>
          <p className="text-sm text-stone-500 mt-4">
            Current plan: <span className="font-medium capitalize">{userTier}</span>
          </p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
