import { useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import { AICopilotPanel } from './AICopilotPanel'
import { useAuthStore } from '../stores/authStore'

export default function Layout() {
  const bootstrap = useAuthStore((s) => s.bootstrap)
  const isBootstrapped = useAuthStore((s) => s.isBootstrapped)

  useEffect(() => {
    bootstrap().catch(() => {})
  }, [bootstrap])

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main>
        {isBootstrapped ? <Outlet /> : <div className="max-w-7xl mx-auto px-4 py-10">Loading…</div>}
      </main>
      <AICopilotPanel />
    </div>
  )
}
