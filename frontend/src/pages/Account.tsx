import SimplePage from '../components/SimplePage'
import { useAuthStore } from '../stores/authStore'

export default function Account() {
  const user = useAuthStore((s) => s.user)

  return (
    <SimplePage title="Account" subtitle="Manage your profile, tier, and settings.">
      <div className="bg-white border border-gray-200 rounded-2xl p-6">
        <div className="text-sm text-gray-500">Signed in as</div>
        <div className="mt-1 text-lg font-semibold text-gray-900">{user?.name || 'User'}</div>
        <div className="mt-1 text-sm text-gray-700">{user?.email || ''}</div>
        <div className="mt-4 text-sm text-gray-700">
          <span className="font-medium">Tier:</span> {user?.tier || 'free'}
        </div>
      </div>
    </SimplePage>
  )
}

