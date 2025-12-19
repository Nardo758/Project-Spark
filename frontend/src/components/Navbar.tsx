import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { Menu, X, ChevronDown, Brain, Compass, Lightbulb, Users, DollarSign, Wrench, BookOpen } from 'lucide-react'

const guestNavItems = [
  { name: 'Home', path: '/' },
  { name: 'Browse Ideas', path: '/discover' },
  { name: 'Idea Engine', path: '/idea-engine' },
  { name: 'Pricing', path: '/pricing' },
]

const authNavItems = [
  { name: 'Dashboard', path: '/dashboard', icon: Compass },
  { name: 'Discover', path: '/discover', icon: Compass },
  { 
    name: 'Builder', 
    icon: Lightbulb,
    dropdown: [
      { name: 'Idea Engine', path: '/idea-engine' },
      { name: 'AI Expert Match', path: '/ai-match' },
      { name: 'AI Roadmap', path: '/ai-roadmap' },
      { name: 'Expert Marketplace', path: '/expert-marketplace' },
    ]
  },
  { name: 'Leads', path: '/leads', icon: Users },
  { name: 'Content', path: '/content', icon: BookOpen },
  { name: 'Network', path: '/network', icon: Users },
  { name: 'Funding', path: '/funding', icon: DollarSign },
  { name: 'Tools', path: '/tools', icon: Wrench },
  { name: 'Learn', path: '/learn', icon: BookOpen },
]

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [builderDropdownOpen, setBuilderDropdownOpen] = useState(false)
  const { isAuthenticated, user, logout } = useAuthStore()
  const location = useLocation()

  const navItems = isAuthenticated ? authNavItems : guestNavItems

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">OG</span>
              </div>
              <span className="font-semibold text-xl text-gray-900">OppGrid</span>
            </Link>
          </div>

          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              'dropdown' in item ? (
                <div key={item.name} className="relative">
                  <button
                    className="flex items-center gap-1 px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md"
                    onMouseEnter={() => setBuilderDropdownOpen(true)}
                    onMouseLeave={() => setBuilderDropdownOpen(false)}
                  >
                    {item.name}
                    <ChevronDown className="w-4 h-4" />
                  </button>
                  {builderDropdownOpen && (
                    <div 
                      className="absolute top-full left-0 mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg py-1"
                      onMouseEnter={() => setBuilderDropdownOpen(true)}
                      onMouseLeave={() => setBuilderDropdownOpen(false)}
                    >
                      {item.dropdown?.map((subItem) => (
                        <Link
                          key={subItem.path}
                          to={subItem.path}
                          className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          {subItem.name}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-3 py-2 text-sm font-medium rounded-md ${
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

          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated ? (
              <>
                {user?.brainTier && (
                  <Link
                    to="/brain"
                    className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-full"
                  >
                    <Brain className="w-4 h-4" />
                    AI Co-founder
                  </Link>
                )}
                <button
                  onClick={logout}
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
                >
                  Sign Out
                </button>
                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-gray-600">
                    {user?.name?.charAt(0) || 'U'}
                  </span>
                </div>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
                >
                  Sign In
                </Link>
                <Link
                  to="/signup"
                  className="px-4 py-2 text-sm font-medium text-white bg-black hover:bg-gray-800 rounded-lg"
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
        <div className="md:hidden border-t border-gray-200">
          <div className="px-4 py-3 space-y-1">
            {navItems.map((item) => (
              'dropdown' in item ? (
                <div key={item.name}>
                  <div className="px-3 py-2 text-sm font-medium text-gray-500">{item.name}</div>
                  {item.dropdown?.map((subItem) => (
                    <Link
                      key={subItem.path}
                      to={subItem.path}
                      className="block pl-6 pr-3 py-2 text-sm text-gray-700"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      {subItem.name}
                    </Link>
                  ))}
                </div>
              ) : (
                <Link
                  key={item.path}
                  to={item.path}
                  className="block px-3 py-2 text-sm font-medium text-gray-700"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.name}
                </Link>
              )
            ))}
            {!isAuthenticated && (
              <div className="pt-3 border-t border-gray-200 space-y-2">
                <Link
                  to="/login"
                  className="block px-3 py-2 text-sm font-medium text-gray-700"
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
