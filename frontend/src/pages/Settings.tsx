import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { 
  User, 
  Bell, 
  CreditCard, 
  Shield, 
  Users, 
  Briefcase,
  HandCoins,
  Handshake,
  Building2,
  ChevronRight
} from 'lucide-react'

type NetworkRole = 'expert' | 'partner' | 'investor' | 'lender'

interface NetworkRoleConfig {
  id: NetworkRole
  title: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  benefits: string[]
}

const networkRoles: NetworkRoleConfig[] = [
  {
    id: 'expert',
    title: 'Expert/Consultant',
    description: 'Offer your expertise to entrepreneurs and startups',
    icon: Briefcase,
    benefits: [
      'Get matched with relevant opportunities',
      'Set your own rates and availability',
      'Build your professional reputation',
      'Earn from consulting engagements'
    ]
  },
  {
    id: 'partner',
    title: 'Find Partners',
    description: 'Connect with potential co-founders and business partners',
    icon: Handshake,
    benefits: [
      'Browse validated opportunities',
      'Connect with like-minded entrepreneurs',
      'Form strategic partnerships',
      'Access exclusive networking events'
    ]
  },
  {
    id: 'investor',
    title: 'Investor',
    description: 'Discover and invest in vetted opportunities',
    icon: HandCoins,
    benefits: [
      'Access pre-validated deals',
      'AI-powered opportunity matching',
      'Due diligence reports included',
      'Direct founder connections'
    ]
  },
  {
    id: 'lender',
    title: 'Lender',
    description: 'Provide funding to qualified startups and businesses',
    icon: Building2,
    benefits: [
      'Vetted borrower profiles',
      'Risk assessment reports',
      'Flexible lending options',
      'Platform-secured transactions'
    ]
  }
]

export default function Settings() {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState('profile')

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'billing', label: 'Billing', icon: CreditCard },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'network', label: 'Join Our Network', icon: Users },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Account Settings</h1>
        
        <div className="flex flex-col md:flex-row gap-6">
          {/* Sidebar */}
          <div className="w-full md:w-64 bg-white rounded-xl border border-gray-200 p-4">
            <nav className="space-y-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-gray-900 text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <tab.icon className="w-5 h-5" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
          
          {/* Content */}
          <div className="flex-1 bg-white rounded-xl border border-gray-200 p-6">
            {activeTab === 'profile' && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Profile Information</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                    <input 
                      type="text" 
                      defaultValue={user?.name || ''} 
                      className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input 
                      type="email" 
                      defaultValue={user?.email || ''} 
                      className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900"
                    />
                  </div>
                  <button className="px-6 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors">
                    Save Changes
                  </button>
                </div>
              </div>
            )}
            
            {activeTab === 'notifications' && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Notification Preferences</h2>
                <div className="space-y-4">
                  {['New opportunities matching your interests', 'Weekly digest emails', 'Partner connection requests', 'Platform updates and news'].map((item) => (
                    <label key={item} className="flex items-center gap-3 cursor-pointer">
                      <input type="checkbox" defaultChecked className="w-4 h-4 rounded border-gray-300" />
                      <span className="text-sm text-gray-700">{item}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}
            
            {activeTab === 'billing' && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Billing & Subscription</h2>
                <div className="p-4 bg-gray-50 rounded-lg border border-gray-200 mb-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">Current Plan: {user?.tier === 'free' ? 'Free' : user?.tier?.charAt(0).toUpperCase() + (user?.tier?.slice(1) || '')}</p>
                      <p className="text-sm text-gray-500 mt-1">Manage your subscription and payment methods</p>
                    </div>
                    <Link to="/pricing" className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors text-sm">
                      Upgrade
                    </Link>
                  </div>
                </div>
              </div>
            )}
            
            {activeTab === 'security' && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Security Settings</h2>
                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">Password</p>
                        <p className="text-sm text-gray-500">Last changed 30 days ago</p>
                      </div>
                      <button className="text-sm font-medium text-gray-900 hover:underline">
                        Change
                      </button>
                    </div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">Two-Factor Authentication</p>
                        <p className="text-sm text-gray-500">Add an extra layer of security</p>
                      </div>
                      <button className="text-sm font-medium text-gray-900 hover:underline">
                        Enable
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {activeTab === 'network' && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Join Our Network</h2>
                <p className="text-gray-600 mb-6">Select a role to join the OppGrid professional network using your LinkedIn profile.</p>
                
                <div className="grid md:grid-cols-2 gap-4">
                  {networkRoles.map((role) => {
                    const Icon = role.icon
                    
                    return (
                      <div
                        key={role.id}
                        onClick={() => window.location.href = `/api/v1/auth/linkedin/login?role=${role.id}`}
                        className="p-5 rounded-xl border-2 cursor-pointer transition-all border-gray-200 hover:border-indigo-500 hover:bg-indigo-50 group"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="p-2 rounded-lg bg-gray-100 text-gray-600 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                            <Icon className="w-5 h-5" />
                          </div>
                          <span className="text-xs text-gray-400 group-hover:text-indigo-600">Click to join →</span>
                        </div>
                        
                        <h3 className="font-semibold text-gray-900 mb-1">{role.title}</h3>
                        <p className="text-sm text-gray-600 mb-3">{role.description}</p>
                        
                        <ul className="space-y-1.5">
                          {role.benefits.map((benefit, idx) => (
                            <li key={idx} className="flex items-center gap-2 text-xs text-gray-500">
                              <ChevronRight className="w-3 h-3 text-gray-400" />
                              {benefit}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )
                  })}
                </div>
                
                <p className="mt-6 text-sm text-gray-500 text-center">
                  You'll be redirected to LinkedIn to verify your professional profile.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
      
    </div>
  )
}
