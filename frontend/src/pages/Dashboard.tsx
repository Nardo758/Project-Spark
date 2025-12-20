import { Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { 
  Brain, Target, Lightbulb, Users, FileText, DollarSign, Zap
} from 'lucide-react'

const quickActions = [
  { icon: Target, label: 'Find Opportunity', path: '/discover', color: 'bg-blue-500' },
  { icon: Lightbulb, label: 'Validate Idea', path: '/idea-engine', color: 'bg-yellow-500' },
  { icon: Users, label: 'Generate Leads', path: '/leads', color: 'bg-green-500' },
  { icon: FileText, label: 'Create Business Plan', path: '/ai-roadmap', color: 'bg-purple-500' },
  { icon: Users, label: 'Find Co-founder', path: '/network', color: 'bg-pink-500' },
  { icon: DollarSign, label: 'Check Funding', path: '/funding', color: 'bg-orange-500' },
]

const mockOpportunities = [
  { id: 1, title: 'Healthcare SaaS Platform', match: 94, status: 'HOT', category: 'Healthcare' },
  { id: 2, title: 'FinTech Payment Solution', match: 88, status: 'FRESH', category: 'FinTech' },
  { id: 3, title: 'E-commerce Automation Tool', match: 76, status: 'VALIDATED', category: 'E-commerce' },
]

export default function Dashboard() {
  const { user } = useAuthStore()

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-2xl p-6 mb-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white mb-2">
              Welcome back, {user?.name || 'Entrepreneur'}!
            </h1>
            <p className="text-gray-300">
              Your AI Match Score: <span className="text-green-400 font-semibold">87%</span> • 
              3 new opportunities match your profile
            </p>
          </div>
          <div className="mt-4 md:mt-0 flex gap-3">
            <Link
              to="/brain"
              className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium"
            >
              <Brain className="w-5 h-5" />
              AI Co-founder
            </Link>
          </div>
        </div>
      </div>

      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {quickActions.map((action, i) => (
            <Link
              key={i}
              to={action.path}
              className="bg-white p-4 rounded-xl border border-gray-200 hover:border-gray-300 hover:shadow-md transition-all text-center"
            >
              <div className={`w-10 h-10 ${action.color} rounded-lg flex items-center justify-center mx-auto mb-3`}>
                <action.icon className="w-5 h-5 text-white" />
              </div>
              <span className="text-sm font-medium text-gray-700">{action.label}</span>
            </Link>
          ))}
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">AI-Curated Opportunities</h2>
            <Link to="/discover" className="text-sm text-blue-600 hover:text-blue-700 font-medium">
              View All →
            </Link>
          </div>
          <div className="space-y-4">
            {mockOpportunities.map((opp) => (
              <div key={opp.id} className="bg-white p-5 rounded-xl border border-gray-200 hover:border-gray-300 hover:shadow-md transition-all">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2 py-0.5 text-xs font-semibold rounded ${
                        opp.status === 'HOT' ? 'bg-red-100 text-red-700' :
                        opp.status === 'FRESH' ? 'bg-blue-100 text-blue-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {opp.status}
                      </span>
                      <span className="text-sm text-gray-500">{opp.category}</span>
                    </div>
                    <h3 className="font-semibold text-gray-900">{opp.title}</h3>
                  </div>
                  <div className="flex items-center gap-1 px-3 py-1 bg-green-50 rounded-full">
                    <Target className="w-4 h-4 text-green-600" />
                    <span className="text-sm font-semibold text-green-700">{opp.match}%</span>
                  </div>
                </div>
                <div className="mt-4 flex items-center gap-4">
                  <Link to={`/opportunity/${opp.id}`} className="text-sm text-blue-600 font-medium hover:text-blue-700">
                    View Details
                  </Link>
                  <button className="text-sm text-gray-500 hover:text-gray-700">
                    Save for Later
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Progress Tracker</h2>
          <div className="bg-white p-5 rounded-xl border border-gray-200 mb-6">
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Active Projects</span>
                  <span className="font-semibold text-gray-900">2</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full">
                  <div className="h-2 bg-blue-500 rounded-full" style={{ width: '40%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Leads Generated</span>
                  <span className="font-semibold text-gray-900">12</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full">
                  <div className="h-2 bg-green-500 rounded-full" style={{ width: '60%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Service Sales</span>
                  <span className="font-semibold text-gray-900">$248</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full">
                  <div className="h-2 bg-purple-500 rounded-full" style={{ width: '25%' }}></div>
                </div>
              </div>
            </div>
          </div>

          <h2 className="text-lg font-semibold text-gray-900 mb-4">AI Recommendations</h2>
          <div className="bg-gradient-to-br from-purple-50 to-indigo-50 p-5 rounded-xl border border-purple-200">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">Train Your AI Co-founder</h3>
                <p className="text-sm text-gray-600 mb-3">
                  Upload your business documents to get more personalized recommendations.
                </p>
                <Link to="/brain" className="text-sm text-purple-600 font-medium hover:text-purple-700">
                  Start Training →
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
