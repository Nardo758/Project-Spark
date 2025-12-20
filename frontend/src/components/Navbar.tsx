import { useEffect, useMemo, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Bell, Brain, CircleHelp, Menu, MessageCircle, Search, ShoppingCart, X } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import { useBrainStore } from '../stores/brainStore'
import { fetchActiveBrain } from '../services/brainApi'

type NavLink = { name: string; path: string }

function isPaidTier(tier?: string) {
  return tier === 'pro' || tier === 'business' || tier === 'enterprise'
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
        <div className="flex justify-between h-16">
          <div className="flex items-center gap-8">
            <Link to="/" className="flex items-center gap-2" onClick={() => setMobileMenuOpen(false)}>
              <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">OG</span>
              </div>
              <span className="font-semibold text-xl text-gray-900">OppGrid</span>
            </Link>

            <div className="hidden md:flex items-center gap-1">
              {navLinks.map((l) => (
                <Link key={l.path} to={l.path} className={linkClass(l.path)}>
                  {l.name}
                </Link>
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

