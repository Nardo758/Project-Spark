import { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export default function RequireAdmin({ children }: { children: ReactNode }) {
  const isBootstrapped = useAuthStore((s) => s.isBootstrapped)
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const user = useAuthStore((s) => s.user)
  const location = useLocation()

  if (!isBootstrapped) {
    return <div className="max-w-7xl mx-auto px-4 py-10">Loading…</div>
  }

  if (!isAuthenticated) {
    const next = location.pathname + location.search + location.hash
    return <Navigate to={`/login?next=${encodeURIComponent(next)}`} replace />
  }

  if (!user?.is_admin) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-10">
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <div className="text-lg font-semibold text-gray-900">Access denied</div>
          <div className="mt-1 text-sm text-gray-600">You don’t have permission to view this page.</div>
        </div>
      </div>
    )
  }

  return <>{children}</>
}

