import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { 
  Menu, 
  X, 
  ChevronDown, 
  ChevronRight,
  Search,
  Hammer,
  Users,
  DollarSign,
  Target,
  Code,
  Settings,
  FolderOpen
} from 'lucide-react'

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
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null)
  const [activeSubmenu, setActiveSubmenu] = useState<string | null>(null)
  const { isAuthenticated, user, logout } = useAuthStore()
  const location = useLocation()

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
                <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg">
                  <FolderOpen className="w-4 h-4 text-gray-600" />
                  <select 
                    className="text-sm font-medium text-gray-700 bg-transparent border-none focus:outline-none cursor-pointer"
                    defaultValue="default"
                  >
                    <option value="default">My First Project</option>
                    <option value="new">+ New Project</option>
                  </select>
                </div>
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
