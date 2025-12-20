import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

function isPaidTier(tier?: string) {
  return tier === 'pro' || tier === 'business' || tier === 'enterprise'
}

export default function RequirePaid({ children }: { children: ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const isBootstrapped = useAuthStore((s) => s.isBootstrapped)
  const tier = useAuthStore((s) => s.user?.tier)
  const location = useLocation()

  if (!isBootstrapped) {
    return <div className="max-w-7xl mx-auto px-4 py-10">Loading…</div>
  }

  const next = location.pathname + location.search + location.hash

  if (!isAuthenticated) {
    return <Navigate to={`/login?next=${encodeURIComponent(next)}`} replace />
  }

  if (!isPaidTier(tier)) {
    return <Navigate to={`/pricing?next=${encodeURIComponent(next)}`} replace />
  }

  return <>{children}</>
}

