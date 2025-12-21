import { useEffect, useMemo, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { 
  Bell, 
  Brain, 
  CircleHelp, 
  Menu, 
  MessageCircle, 
  Search, 
  ShoppingCart, 
  X,
  ChevronDown, 
  ChevronRight,
  Hammer,
  Users,
  DollarSign,
  Target,
  Code,
  Settings,
  FolderOpen
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

const guestNavItems = [
  { name: 'Discover', path: '/discover' },
  { name: 'Consultant Studio', path: '/build/reports' },
  { name: 'Leads', path: '/leads' },
  { name: 'Join Network', path: '/network' },
  { name: 'API', path: '/developers' },
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
      { name: 'Consultant Studio', path: '/build/reports', description: 'AI-powered feasibility studies' },
      { name: 'Business Plan Generator', path: '/build/business-plan', description: 'Comprehensive business plans' },
      { name: 'Pitch Deck', path: '/build/pitch-deck', description: 'Investor presentations' },
    ]
  },
  { 
    name: 'Find Expert Help', 
    icon: Users,
    path: '/find-expert-help'
  },
  { 
    name: 'Find Money', 
    icon: DollarSign,
    path: '/find-money'
  },
  { 
    name: 'Leads', 
    icon: Target,
    path: '/leads'
  },
  { 
    name: 'API', 
    icon: Code,
    path: '/developers'
  },
  { 
    name: 'Manage', 
    icon: Settings,
    dropdown: [
      { name: 'Dashboard', path: '/dashboard', description: 'Your personalized dashboard' },
      { name: 'My Projects', path: '/projects', description: 'View all your projects' },
      { name: 'Saved Ideas', path: '/saved', description: 'Bookmarked opportunities' },
      { name: 'Settings', path: '/settings', description: 'Account settings' },
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
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [search, setSearch] = useState('')

  const { isAuthenticated, user, logout } = useAuthStore()
  const token = useAuthStore((s) => s.token)
  const location = useLocation()
  const navigate = useNavigate()

  const paidMember = isAuthenticated && isPaidTier(user?.tier)

  const brainName = useBrainStore((s) => s.brainName)
  const brainScore = useBrainStore((s) => s.matchScore)
  const brainTokens = useBrainStore((s) => s.tokensUsed)
  const brainCost = useBrainStore((s) => s.estimatedCostUsd)
  const brainEnabled = useBrainStore((s) => s.isEnabled)
  const hydrateFromServer = useBrainStore((s) => s.hydrateFromServer)

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

  const navLinks: NavLink[] = useMemo(() => {
    if (!isAuthenticated) {
      return [
        { name: 'Home', path: '/' },
        { name: 'Discover', path: '/discover' },
        { name: 'Services', path: '/services' },
        { name: 'Network', path: '/network' },
        { name: 'Pricing', path: '/pricing' },
      ]
    }

    if (paidMember) {
      return [
        { name: 'Dashboard', path: '/dashboard' },
        { name: 'Discover', path: '/discover' },
        { name: 'Services', path: '/services' },
        { name: 'Network', path: '/network' },
        { name: 'Leads', path: '/marketplace' },
        { name: 'Builder', path: '/build/reports' },
        { name: 'Funding Tools', path: '/funding' },
        { name: 'Analytics', path: '/analytics' },
        { name: 'API', path: '/developer' },
      ]
    }

    return [
      { name: 'Dashboard', path: '/dashboard' },
      { name: 'Discover', path: '/discover' },
      { name: 'Services', path: '/services' },
      { name: 'Network', path: '/network' },
      { name: 'Leads', path: '/marketplace' },
      { name: 'My Purchases', path: '/purchases' },
      { name: 'Learn', path: '/learn' },
      { name: 'Account', path: '/account' },
    ]
  }, [isAuthenticated, paidMember])

  const cartCount = 0

  const onSubmitSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const q = search.trim()
    navigate(q ? `/discover?q=${encodeURIComponent(q)}` : '/discover')
    setMobileMenuOpen(false)
  }

  const linkClass = (path: string) =>
    `px-3 py-2 text-sm font-medium rounded-md transition-colors ${
      location.pathname === path ? 'text-gray-900 bg-gray-100' : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100'
    }`

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">OG</span>
              </div>
              <div className="flex flex-col">
                <span className="font-semibold text-xl text-gray-900 leading-tight">OppGrid</span>
                <span className="text-[9px] text-gray-500 leading-tight">The Opportunity Intelligence Platform</span>
              </div>
            </Link>
          </div>

          {/* Centered Navigation */}
          <div className="hidden md:flex items-center justify-center flex-1">
            <div className="flex items-center gap-1">
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
            <form onSubmit={onSubmitSearch} className="hidden lg:block">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search"
                  className="w-64 pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </form>

            <Link to="/cart" className="relative p-2 rounded-lg hover:bg-gray-50" title="Cart">
              <ShoppingCart className="w-5 h-5 text-gray-700" />
              <span className="absolute -top-1 -right-1 min-w-5 h-5 px-1 rounded-full bg-black text-white text-xs flex items-center justify-center">
                {cartCount}
              </span>
            </Link>

            {isAuthenticated && (
              <>
                <button type="button" className="p-2 rounded-lg hover:bg-gray-50" title="Notifications">
                  <Bell className="w-5 h-5 text-gray-700" />
                </button>
                {paidMember ? (
                  <button type="button" className="p-2 rounded-lg hover:bg-gray-50" title="Messages">
                    <MessageCircle className="w-5 h-5 text-gray-700" />
                  </button>
                ) : null}
                <Link to="/contact" className="p-2 rounded-lg hover:bg-gray-50" title="Help">
                  <CircleHelp className="w-5 h-5 text-gray-700" />
                </Link>
              </>
            )}

            {isAuthenticated ? (
              <>
                {brainEnabled ? (
                  <Link
                    to="/brain"
                    className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-purple-800 bg-purple-50 hover:bg-purple-100 rounded-full"
                    title="DeepSeek Brain: match score + tokens + cost"
                  >
                    <Brain className="w-4 h-4" />
                    <span className="max-w-[160px] truncate">{brainName ? brainName : 'DeepSeek Brain'}</span>
                    {brainName ? <span className="text-purple-700">{brainScore}%</span> : null}
                    {brainName ? (
                      <span className="text-xs text-purple-700/80">{brainTokens.toLocaleString()} tokens • ~${brainCost.toFixed(2)}</span>
                    ) : null}
                  </Link>
                ) : null}

                <div className="relative">
                  <button
                    type="button"
                    onClick={() => setUserMenuOpen((v) => !v)}
                    className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-lg hover:bg-gray-50"
                    title="Account"
                  >
                    <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-white">{user?.name?.charAt(0) || 'U'}</span>
                    </div>
                    <div className="hidden lg:flex flex-col items-start leading-tight">
                      <div className="text-sm font-medium text-gray-900">
                        {user?.name || 'Account'}
                        {paidMember ? <span className="ml-2 text-xs font-semibold text-purple-700">Pro</span> : null}
                      </div>
                      <div className="text-xs text-gray-500">{user?.email || ''}</div>
                    </div>
                  </button>

                  {userMenuOpen && (
                    <div className="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-lg shadow-lg py-1">
                      <Link to="/account" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50" onClick={() => setUserMenuOpen(false)}>
                        Account
                      </Link>
                      <Link to="/purchases" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50" onClick={() => setUserMenuOpen(false)}>
                        My Purchases
                      </Link>
                      <Link to="/saved" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50" onClick={() => setUserMenuOpen(false)}>
                        Saved
                      </Link>
                      <Link to="/brain" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50" onClick={() => setUserMenuOpen(false)}>
                        Brain
                      </Link>
                      <div className="my-1 border-t border-gray-100" />
                      <button
                        type="button"
                        onClick={() => {
                          setUserMenuOpen(false)
                          logout()
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        Sign out
                      </button>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <>
                <Link to="/login" className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors">
                  Sign In
                </Link>
                <Link to="/signup" className="px-4 py-2 text-sm font-medium text-white bg-black hover:bg-gray-800 rounded-lg transition-colors">
                  Get Started
                </Link>
              </>
            )}
          </div>

          <div className="md:hidden flex items-center gap-2">
            <Link to="/cart" className="relative p-2 rounded-lg hover:bg-gray-50" title="Cart" onClick={() => setMobileMenuOpen(false)}>
              <ShoppingCart className="w-5 h-5 text-gray-700" />
              <span className="absolute -top-1 -right-1 min-w-5 h-5 px-1 rounded-full bg-black text-white text-xs flex items-center justify-center">
                {cartCount}
              </span>
            </Link>
            <button onClick={() => setMobileMenuOpen((v) => !v)} className="p-2 text-gray-700">
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-200 bg-white">
          <div className="px-4 py-3 space-y-2">
            <form onSubmit={onSubmitSearch}>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search"
                  className="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </form>

            <div className="pt-1 space-y-1">
              {navLinks.map((l) => (
                <Link
                  key={l.path}
                  to={l.path}
                  className={`block px-3 py-2 text-sm font-medium rounded-md ${
                    location.pathname === l.path ? 'bg-gray-100 text-gray-900' : 'text-gray-700 hover:bg-gray-50'
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {l.name}
                </Link>
              ))}
            </div>

            {isAuthenticated ? (
              <div className="pt-2 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => {
                    logout()
                    setMobileMenuOpen(false)
                  }}
                  className="w-full text-left px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-md"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <div className="pt-2 border-t border-gray-200 space-y-2">
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

