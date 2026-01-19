import { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export default function RequireAuth({ children }: { children: ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const isBootstrapped = useAuthStore((s) => s.isBootstrapped)
  const location = useLocation()

  if (!isBootstrapped) {
    return <div className="max-w-7xl mx-auto px-4 py-10">Loading…</div>
  }

  if (!isAuthenticated) {
    const next = location.pathname + location.search + location.hash
    return <Navigate to={`/login?next=${encodeURIComponent(next)}`} />
  }

  return <>{children}</>
}

