import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { 
  ArrowRight, 
  Search, 
  Lightbulb, 
  TrendingUp, 
  Globe, 
  CheckCircle, 
  FileText,
  Upload,
  Sparkles,
  BarChart3,
  Target,
  Users
} from 'lucide-react'

interface PlatformStats {
  validated_ideas: number
  total_market_opportunity: string
  global_markets: number
  validated_opportunities?: number
}

interface TrendingCategory {
  name: string
  growth: number
}

export default function Home() {
  const [stats, setStats] = useState<PlatformStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [ideaDescription, setIdeaDescription] = useState('')
  const navigate = useNavigate()

  const trendingCategories: TrendingCategory[] = [
    { name: 'AI-Powered Healthcare', growth: 32 },
    { name: 'Sustainable Packaging', growth: 28 },
    { name: 'Local Fintech', growth: 19 },
  ]

  useEffect(() => {
    async function fetchData() {
      try {
        const statsRes = await fetch('/api/v1/opportunities/stats/platform')
        if (statsRes.ok) {
          const statsData = await statsRes.json()
          setStats(statsData)
        }
      } catch (err) {
        console.error('Failed to fetch landing page data:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const handleExplorerSearch = (e: React.FormEvent) => {
    e.preventDefault()
    navigate(`/discover?q=${encodeURIComponent(searchQuery)}`)
  }

  const handleIdeatorSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    navigate(`/idea-engine?idea=${encodeURIComponent(ideaDescription)}`)
  }

  return (
    <div className="bg-white">
      {/* Hero Section - Dual Entry Point */}
      <section className="relative overflow-hidden bg-gradient-to-br from-slate-50 via-white to-purple-50">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(16,185,129,0.05),transparent_50%)]" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-20">
          
          {/* Hero Title */}
          <div className="text-center mb-12">
            <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 tracking-tight">
              Transform Ideas into{' '}
              <span className="text-purple-600">Viable Businesses</span>
            </h1>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              AI-powered opportunity discovery and validation platform for entrepreneurs
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Left Column - Dual Entry Points */}
            <div className="lg:col-span-2 space-y-6">
              
              {/* Explorer Path */}
              <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center">
                    <Search className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">Search & Discover</h2>
                    <p className="text-sm text-gray-500">Browse AI-curated opportunities</p>
                  </div>
                </div>
                <form onSubmit={handleExplorerSearch} className="space-y-4">
                  <div className="relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder='Try "sustainable tech" or "healthcare AI"'
                      className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none"
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <Link 
                      to="/discover" 
                      className="text-sm text-emerald-600 hover:text-emerald-700 font-medium"
                    >
                      Browse all opportunities
                    </Link>
                    <button
                      type="submit"
                      className="inline-flex items-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-lg transition-colors"
                    >
                      Start as Explorer
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </form>
              </div>

              {/* Ideator Path */}
              <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
                    <Lightbulb className="w-5 h-5 text-purple-600" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">Build & Validate</h2>
                    <p className="text-sm text-gray-500">Validate your own idea with AI</p>
                  </div>
                </div>
                <form onSubmit={handleIdeatorSubmit} className="space-y-4">
                  <textarea
                    value={ideaDescription}
                    onChange={(e) => setIdeaDescription(e.target.value)}
                    placeholder="Describe your business idea..."
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none resize-none"
                  />
                  <div className="flex items-center justify-between">
                    <button
                      type="button"
                      className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700"
                    >
                      <Upload className="w-4 h-4" />
                      Upload Business Plan
                    </button>
                    <button
                      type="submit"
                      className="inline-flex items-center gap-2 px-5 py-2.5 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors"
                    >
                      Start as Ideator
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </form>
              </div>
            </div>

            {/* Right Column - Live Metrics */}
            <div className="space-y-6">
              {/* Live Platform Metrics */}
              <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-4">
                  Live Platform Metrics
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                    <div className="flex items-center gap-3">
                      <Lightbulb className="w-5 h-5 text-amber-500" />
                      <span className="text-sm text-gray-600">Validated Ideas</span>
                    </div>
                    <span className="text-lg font-bold text-gray-900">
                      {loading ? '...' : stats?.validated_ideas?.toLocaleString() || '12.4K'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                    <div className="flex items-center gap-3">
                      <TrendingUp className="w-5 h-5 text-emerald-500" />
                      <span className="text-sm text-gray-600">Market Opportunity</span>
                    </div>
                    <span className="text-lg font-bold text-gray-900">
                      {loading ? '...' : stats?.total_market_opportunity || '$2.1B'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                    <div className="flex items-center gap-3">
                      <Globe className="w-5 h-5 text-blue-500" />
                      <span className="text-sm text-gray-600">Active Markets</span>
                    </div>
                    <span className="text-lg font-bold text-gray-900">
                      {loading ? '...' : stats?.global_markets || '142'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="w-5 h-5 text-purple-500" />
                      <span className="text-sm text-gray-600">Validated Opps</span>
                    </div>
                    <span className="text-lg font-bold text-gray-900">
                      {loading ? '...' : stats?.validated_opportunities || '847'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Trending This Week */}
              <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-4">
                  Trending This Week
                </h3>
                <div className="space-y-3">
                  {trendingCategories.map((category, index) => (
                    <Link
                      key={index}
                      to={`/discover?category=${encodeURIComponent(category.name)}`}
                      className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg transition-colors"
                    >
                      <span className="text-sm text-gray-700">{category.name}</span>
                      <span className="text-sm font-medium text-emerald-600">
                        +{category.growth}%
                      </span>
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured: Consultant Report Studio */}
      <section className="py-16 bg-gradient-to-r from-slate-900 to-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-purple-500/20 text-purple-300 rounded-full text-sm font-medium mb-4">
                <Sparkles className="w-4 h-4" />
                Featured Tool
              </div>
              <h2 className="text-3xl font-bold text-white mb-4">
                Consultant Report Studio
              </h2>
              <p className="text-lg text-gray-300 mb-6">
                Get investor-ready analysis in minutes. Generate comprehensive feasibility studies, 
                market analyses, and strategic assessments powered by AI.
              </p>
              <div className="flex flex-wrap gap-3 mb-8">
                {['Feasibility Study', 'Market Analysis', 'SWOT', 'PESTLE', 'Pitch Deck'].map((item) => (
                  <span key={item} className="px-3 py-1.5 bg-white/10 text-white text-sm rounded-lg">
                    {item}
                  </span>
                ))}
              </div>
              <div className="flex gap-4">
                <Link
                  to="/build/reports"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-white text-gray-900 font-medium rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <FileText className="w-5 h-5" />
                  See Examples
                </Link>
                <Link
                  to="/build/reports/sample"
                  className="inline-flex items-center gap-2 px-6 py-3 border border-white/30 text-white font-medium rounded-lg hover:bg-white/10 transition-colors"
                >
                  Try Free Sample
                </Link>
              </div>
            </div>
            <div className="hidden lg:block">
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-purple-500 rounded-xl flex items-center justify-center">
                    <BarChart3 className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <div className="text-white font-medium">Sample Report</div>
                    <div className="text-gray-400 text-sm">Market Analysis</div>
                  </div>
                </div>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between text-gray-300">
                    <span>Market Size (TAM)</span>
                    <span className="text-white font-medium">$8.2B</span>
                  </div>
                  <div className="flex justify-between text-gray-300">
                    <span>Growth Rate</span>
                    <span className="text-emerald-400 font-medium">+24% YoY</span>
                  </div>
                  <div className="flex justify-between text-gray-300">
                    <span>Competition Level</span>
                    <span className="text-amber-400 font-medium">Medium</span>
                  </div>
                  <div className="flex justify-between text-gray-300">
                    <span>Confidence Score</span>
                    <span className="text-white font-medium">87%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900">How It Works</h2>
            <p className="mt-4 text-lg text-gray-600">From discovery to execution in three steps</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="relative">
              <div className="absolute -top-3 -left-3 w-10 h-10 bg-black text-white rounded-full flex items-center justify-center font-bold">1</div>
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 pt-10">
                <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mb-4">
                  <Search className="w-6 h-6 text-emerald-600" />
                </div>
                <h3 className="font-semibold text-gray-900 text-lg mb-3">Discover or Ideate</h3>
                <p className="text-gray-600">
                  Browse AI-curated opportunities or validate your own idea with our intelligent analysis engine.
                </p>
              </div>
            </div>
            <div className="relative">
              <div className="absolute -top-3 -left-3 w-10 h-10 bg-black text-white rounded-full flex items-center justify-center font-bold">2</div>
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 pt-10">
                <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
                  <Target className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="font-semibold text-gray-900 text-lg mb-3">Validate & Plan</h3>
                <p className="text-gray-600">
                  Get AI-powered market analysis, feasibility studies, and strategic recommendations.
                </p>
              </div>
            </div>
            <div className="relative">
              <div className="absolute -top-3 -left-3 w-10 h-10 bg-black text-white rounded-full flex items-center justify-center font-bold">3</div>
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 pt-10">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
                  <Users className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="font-semibold text-gray-900 text-lg mb-3">Build & Launch</h3>
                <p className="text-gray-600">
                  Generate business plans, pitch decks, and connect with experts to bring your idea to life.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 bg-gradient-to-r from-purple-600 to-indigo-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to Build What's Next?</h2>
          <p className="text-purple-100 text-lg mb-8">
            Join thousands of entrepreneurs discovering and validating opportunities every day.
          </p>
          <Link
            to="/signup"
            className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-purple-600 bg-white hover:bg-gray-100 rounded-lg gap-2"
          >
            Get Started Free
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center gap-2 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                <span className="text-gray-900 font-bold text-sm">OG</span>
              </div>
              <span className="font-semibold text-xl">OppGrid</span>
            </div>
            <div className="flex gap-6 text-sm text-gray-400 mb-4 md:mb-0">
              <Link to="/about" className="hover:text-white">About</Link>
              <Link to="/pricing" className="hover:text-white">Pricing</Link>
              <Link to="/blog" className="hover:text-white">Blog</Link>
              <Link to="/contact" className="hover:text-white">Contact</Link>
              <Link to="/terms" className="hover:text-white">Terms</Link>
              <Link to="/privacy" className="hover:text-white">Privacy</Link>
            </div>
            <p className="text-gray-500 text-sm">
              © 2024 OppGrid. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
