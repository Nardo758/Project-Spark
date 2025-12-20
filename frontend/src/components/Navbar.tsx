import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { Menu, X, ChevronDown, Brain, Compass, Lightbulb, Users, DollarSign, Wrench, BookOpen, Bookmark } from 'lucide-react'
import { useBrainStore } from '../stores/brainStore'
import { useQuery } from '@tanstack/react-query'
import { fetchActiveBrain } from '../services/brainApi'

const guestNavItems = [
  { name: 'Discover', path: '/discover' },
  { name: 'Build', path: '/idea-engine' },
  { name: 'Pricing', path: '/pricing' },
]

const authNavItems = [
  { 
    name: 'Discover', 
    icon: Search,
    dropdown: [
      { name: 'Opportunity Feed', path: '/discover', description: 'Browse AI-curated opportunities' },
      { name: 'Validate Idea', path: '/idea-engine', description: 'Idea Engine - refine your concepts' },
    ]
  },
  { 
    name: 'Build', 
    icon: Hammer,
    dropdown: [
      { name: 'Report Studio', path: '/build/reports', description: 'Feasibility, Market & Strategic analysis' },
      { name: 'Business Plan', path: '/build/reports?type=business-plan', description: 'Comprehensive business plans' },
      { name: 'Pitch Deck', path: '/build/reports?type=pitch-deck', description: 'Investor presentations' },
    ]
  },
  { 
    name: 'Manage', 
    icon: Settings,
    dropdown: [
      { name: 'My Projects', path: '/dashboard', description: 'View all your projects' },
      { name: 'Saved Ideas', path: '/saved', description: 'Bookmarked opportunities' },
      { name: 'AI Co-founder', path: '/brain', description: 'Your AI assistant' },
    ]
  },
]

type SubMenuItem = {
  name: string
  path: string
}

type DropdownItem = {
  name: string
  path: string
  description?: string
  submenu?: SubMenuItem[]
}

type NavItem = {
  name: string
  path?: string
  icon?: React.ComponentType<{ className?: string }>
  dropdown?: DropdownItem[]
}

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null)
  const [activeSubmenu, setActiveSubmenu] = useState<string | null>(null)
  const { isAuthenticated, user, logout } = useAuthStore()
  const location = useLocation()
  const brainName = useBrainStore((s) => s.brainName)
  const brainScore = useBrainStore((s) => s.matchScore)
  const brainTokens = useBrainStore((s) => s.tokensUsed)
  const brainCost = useBrainStore((s) => s.estimatedCostUsd)
  const brainEnabled = useBrainStore((s) => s.isEnabled)
  const hydrateFromServer = useBrainStore((s) => s.hydrateFromServer)
  const noteLearning = useBrainStore((s) => s.noteLearning)
  const token = useAuthStore((s) => s.token)

  const brainQuery = useQuery({
    queryKey: ['brain-active'],
    enabled: Boolean(isAuthenticated && token),
    queryFn: async () => fetchActiveBrain(String(token)),
    refetchInterval: 30_000,
    retry: false,
  })

  useEffect(() => {
    if (!brainQuery.data) return
    hydrateFromServer(brainQuery.data)
  }, [brainQuery.data, hydrateFromServer])

  const navItems = isAuthenticated ? authNavItems : guestNavItems

  const handleDropdownEnter = (name: string) => {
    setActiveDropdown(name)
  }

  const handleDropdownLeave = () => {
    setActiveDropdown(null)
    setActiveSubmenu(null)
  }

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center gap-8">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">OG</span>
              </div>
              <span className="font-semibold text-xl text-gray-900">OppGrid</span>
            </Link>

            <div className="hidden md:flex items-center gap-1">
              {navItems.map((item: NavItem) => (
                'dropdown' in item && item.dropdown ? (
                  <div 
                    key={item.name} 
                    className="relative"
                    onMouseEnter={() => handleDropdownEnter(item.name)}
                    onMouseLeave={handleDropdownLeave}
                  >
                    <button
                      className={`flex items-center gap-1 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                        activeDropdown === item.name
                          ? 'text-gray-900 bg-gray-100'
                          : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100'
                      }`}
                    >
                      {item.name}
                      <ChevronDown className={`w-4 h-4 transition-transform ${activeDropdown === item.name ? 'rotate-180' : ''}`} />
                    </button>
                    {activeDropdown === item.name && (
                      <div className="absolute top-full left-0 mt-1 w-72 bg-white border border-gray-200 rounded-lg shadow-lg py-2">
                        {item.dropdown.map((subItem) => (
                          <div
                            key={subItem.path}
                            className="relative"
                            onMouseEnter={() => subItem.submenu && setActiveSubmenu(subItem.name)}
                            onMouseLeave={() => setActiveSubmenu(null)}
                          >
                            <Link
                              to={subItem.path}
                              className="flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition-colors"
                            >
                              <div>
                                <div className="text-sm font-medium text-gray-900">{subItem.name}</div>
                                {subItem.description && (
                                  <div className="text-xs text-gray-500 mt-0.5">{subItem.description}</div>
                                )}
                              </div>
                              {subItem.submenu && (
                                <ChevronRight className="w-4 h-4 text-gray-400" />
                              )}
                            </Link>
                            {subItem.submenu && activeSubmenu === subItem.name && (
                              <div className="absolute left-full top-0 ml-1 w-56 bg-white border border-gray-200 rounded-lg shadow-lg py-2">
                                {subItem.submenu.map((sub) => (
                                  <Link
                                    key={sub.path}
                                    to={sub.path}
                                    className="block px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                                  >
                                    {sub.name}
                                  </Link>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  <Link
                    key={item.path}
                    to={item.path || '/'}
                    className={`flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      location.pathname === item.path
                        ? 'text-gray-900 bg-gray-100'
                        : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    {item.name}
                  </Link>
                )
              ))}
            </div>
          </div>

          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated ? (
              <>
                {brainEnabled && (
                  <div className="flex items-center gap-2">
                    <Link
                      to="/brain"
                      className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-purple-800 bg-purple-50 hover:bg-purple-100 rounded-full"
                      title="DeepSeek Brain: match score + tokens + cost"
                    >
                      <Brain className="w-4 h-4" />
                      <span className="max-w-[160px] truncate">{brainName ? `${brainName}` : 'DeepSeek Brain'}</span>
                      {brainName ? (
                        <span className="text-purple-700">{brainScore}%</span>
                      ) : null}
                      {brainName ? (
                        <span className="text-xs text-purple-700/80">{brainTokens.toLocaleString()} tokens • ~${brainCost.toFixed(2)}</span>
                      ) : null}
                    </Link>
                    {brainName && (
                      <button
                        type="button"
                        onClick={() => noteLearning('Quick training is server-driven (coming next).', 0)}
                        className="px-3 py-1.5 text-sm font-medium text-gray-800 border border-gray-200 rounded-full hover:bg-gray-50"
                        title="Quick Train"
                      >
                        Quick train
                      </button>
                    )}
                  </div>
                )}
                <button
                  onClick={logout}
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
                >
                  Sign Out
                </button>
                <Link to="/dashboard" className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-white">
                      {user?.name?.charAt(0) || 'U'}
                    </span>
                  </div>
                </Link>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/signup"
                  className="px-4 py-2 text-sm font-medium text-white bg-black hover:bg-gray-800 rounded-lg transition-colors"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>

          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-gray-700"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-200 bg-white">
          <div className="px-4 py-3 space-y-1">
            {isAuthenticated && (
              <div className="flex items-center gap-2 px-3 py-2 mb-2 bg-gray-100 rounded-lg">
                <FolderOpen className="w-4 h-4 text-gray-600" />
                <select 
                  className="text-sm font-medium text-gray-700 bg-transparent border-none focus:outline-none flex-1"
                  defaultValue="default"
                >
                  <option value="default">My First Project</option>
                  <option value="new">+ New Project</option>
                </select>
              </div>
            )}
            
            {navItems.map((item: NavItem) => (
              'dropdown' in item && item.dropdown ? (
                <div key={item.name} className="py-2">
                  <div className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-500">
                    {item.name}
                  </div>
                  <div className="ml-4 space-y-1">
                    {item.dropdown.map((subItem) => (
                      <div key={subItem.path}>
                        <Link
                          to={subItem.path}
                          className="block px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md"
                          onClick={() => setMobileMenuOpen(false)}
                        >
                          {subItem.name}
                        </Link>
                        {subItem.submenu && (
                          <div className="ml-4 space-y-1">
                            {subItem.submenu.map((sub) => (
                              <Link
                                key={sub.path}
                                to={sub.path}
                                className="block px-3 py-1.5 text-xs text-gray-500 hover:bg-gray-50 rounded-md"
                                onClick={() => setMobileMenuOpen(false)}
                              >
                                {sub.name}
                              </Link>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <Link
                  key={item.path}
                  to={item.path || '/'}
                  className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-md"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.name}
                </Link>
              )
            ))}
            
            {isAuthenticated ? (
              <button
                onClick={() => {
                  logout()
                  setMobileMenuOpen(false)
                }}
                className="w-full text-left px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-md"
              >
                Sign Out
              </button>
            ) : (
              <div className="pt-3 border-t border-gray-200 space-y-2">
                <Link
                  to="/login"
                  className="block px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-md"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Sign In
                </Link>
                <Link
                  to="/signup"
                  className="block px-3 py-2 text-sm font-medium text-white bg-black rounded-lg text-center"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  )
}
