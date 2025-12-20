import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { 
  Menu, 
  X, 
  ChevronDown, 
  Brain, 
  Lightbulb, 
  FileText, 
  FolderKanban,
  Search
} from 'lucide-react'

const guestNavItems = [
  { name: 'Home', path: '/' },
  { name: 'Explore', path: '/discover' },
  { name: 'Ideate', path: '/idea-engine' },
  { name: 'Pricing', path: '/pricing' },
]

const authNavItems = [
  { 
    name: 'My Projects', 
    path: '/dashboard',
    icon: FolderKanban,
  },
  { 
    name: 'Ideate', 
    icon: Lightbulb,
    dropdown: [
      { name: 'Idea Engine', path: '/idea-engine', description: 'Validate & refine your ideas' },
      { name: 'AI Expert Match', path: '/ai-match', description: 'Find the right expertise' },
    ]
  },
  { 
    name: 'Explore', 
    icon: Search,
    dropdown: [
      { name: 'Opportunities', path: '/discover', description: 'Browse AI-curated opportunities' },
      { name: 'Saved Ideas', path: '/saved', description: 'Your bookmarked opportunities' },
    ]
  },
  { 
    name: 'Build', 
    icon: FileText,
    dropdown: [
      { name: 'Business Plan', path: '/build/business-plan', description: 'Generate comprehensive plans' },
      { name: 'Report Studio', path: '/build/reports', description: 'SWOT, PESTLE, Feasibility' },
      { name: 'Financial Models', path: '/build/financials', description: 'Projections & analysis' },
      { name: 'Pitch Deck', path: '/build/pitch-deck', description: 'Investor presentations' },
    ]
  },
]

type NavItem = {
  name: string
  path?: string
  icon?: React.ComponentType<{ className?: string }>
  dropdown?: { name: string; path: string; description?: string }[]
}

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null)
  const { isAuthenticated, user, logout } = useAuthStore()
  const location = useLocation()

  const navItems = isAuthenticated ? authNavItems : guestNavItems

  const handleDropdownEnter = (name: string) => {
    setActiveDropdown(name)
  }

  const handleDropdownLeave = () => {
    setActiveDropdown(null)
  }

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
                    {item.icon && <item.icon className="w-4 h-4" />}
                    {item.name}
                    <ChevronDown className={`w-4 h-4 transition-transform ${activeDropdown === item.name ? 'rotate-180' : ''}`} />
                  </button>
                  {activeDropdown === item.name && (
                    <div className="absolute top-full left-0 mt-1 w-64 bg-white border border-gray-200 rounded-lg shadow-lg py-2">
                      {item.dropdown.map((subItem) => (
                        <Link
                          key={subItem.path}
                          to={subItem.path}
                          className="block px-4 py-3 hover:bg-gray-50 transition-colors"
                        >
                          <div className="text-sm font-medium text-gray-900">{subItem.name}</div>
                          {subItem.description && (
                            <div className="text-xs text-gray-500 mt-0.5">{subItem.description}</div>
                          )}
                        </Link>
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
                  {item.icon && <item.icon className="w-4 h-4" />}
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
                    className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-full transition-colors"
                  >
                    <Brain className="w-4 h-4" />
                    <span>AI Co-founder</span>
                  </Link>
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
            {navItems.map((item: NavItem) => (
              'dropdown' in item && item.dropdown ? (
                <div key={item.name} className="py-2">
                  <div className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-500">
                    {item.icon && <item.icon className="w-4 h-4" />}
                    {item.name}
                  </div>
                  <div className="ml-4 space-y-1">
                    {item.dropdown.map((subItem) => (
                      <Link
                        key={subItem.path}
                        to={subItem.path}
                        className="block px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md"
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        {subItem.name}
                      </Link>
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
                  {item.icon && <item.icon className="w-4 h-4" />}
                  {item.name}
                </Link>
              )
            ))}
            
            {isAuthenticated && user?.brainTier && (
              <Link
                to="/brain"
                className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-purple-700 bg-purple-50 rounded-md mt-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                <Brain className="w-4 h-4" />
                AI Co-founder
              </Link>
            )}
            
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
