import { useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import { useAuthStore } from '../stores/authStore'
import BrainLearningToast from './BrainLearningToast'

export default function Layout() {
  const bootstrap = useAuthStore((s) => s.bootstrap)
  const isBootstrapped = useAuthStore((s) => s.isBootstrapped)

  useEffect(() => {
    // Best-effort: hydrate auth from cookies/storage and fetch /users/me.
    bootstrap().catch(() => {})
  }, [bootstrap])

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main>
        {isBootstrapped ? <Outlet /> : <div className="max-w-7xl mx-auto px-4 py-10">Loading…</div>}
      </main>
      <BrainLearningToast />
    </div>
  )
}
