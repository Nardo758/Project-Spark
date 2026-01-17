import { useAuthStore } from '../stores/authStore'
import { Navigate, Link } from 'react-router-dom'
import { 
  Users, 
  CreditCard, 
  TrendingUp, 
  Link2,
  Shield
} from 'lucide-react'

const adminTools = [
  {
    title: 'Subscription Management',
    description: 'View and manage user subscriptions, reset invalid tiers',
    href: '/admin/subscriptions',
    icon: CreditCard,
    color: 'bg-indigo-500'
  },
  {
    title: 'Marketing Dashboard',
    description: 'User analytics, email campaigns, and export tools',
    href: '/admin/marketing',
    icon: TrendingUp,
    color: 'bg-green-500'
  },
  {
    title: 'Expert Management',
    description: 'Manage experts, import from Upwork, review applications',
    href: '/admin/experts',
    icon: Users,
    color: 'bg-purple-500'
  },
  {
    title: 'Affiliate Tools',
    description: 'Manage affiliate links and tracking',
    href: '/admin/affiliate-tools',
    icon: Link2,
    color: 'bg-orange-500'
  }
]

export default function Admin() {
  const { user, isAuthenticated } = useAuthStore()

  if (!isAuthenticated || !user?.is_admin) {
    return <Navigate to="/" replace />
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-indigo-100 rounded-lg">
              <Shield className="w-6 h-6 text-indigo-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
          </div>
          <p className="text-gray-600">Manage subscriptions, users, experts, and platform settings</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {adminTools.map((tool) => (
            <Link
              key={tool.href}
              to={tool.href}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md hover:border-indigo-200 transition-all group"
            >
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-lg ${tool.color} group-hover:scale-110 transition-transform`}>
                  <tool.icon className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
                    {tool.title}
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">
                    {tool.description}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>

        <div className="mt-8 p-4 bg-gray-100 rounded-lg">
          <p className="text-sm text-gray-600">
            Logged in as <span className="font-medium">{user?.email}</span>
          </p>
        </div>
      </div>
    </div>
  )
}
