import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Lightbulb, Target, Users, Zap, TrendingUp, Play, CheckCircle, BarChart3, Globe, Rocket } from 'lucide-react'

interface PlatformStats {
  validated_ideas: number
  total_market_opportunity: string
  global_markets: number
}

interface FeaturedOpportunity {
  id: number
  title: string
  description: string
  score: number
  market_size: string
  validation_count: number
  growth_rate: number
}

export default function Home() {
  const [stats, setStats] = useState<PlatformStats | null>(null)
  const [featured, setFeatured] = useState<FeaturedOpportunity | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const [statsRes, featuredRes] = await Promise.all([
          fetch('/api/v1/opportunities/stats/platform'),
          fetch('/api/v1/opportunities/featured/top')
        ])
        
        if (statsRes.ok) {
          const statsData = await statsRes.json()
          setStats(statsData)
        }
        
        if (featuredRes.ok) {
          const featuredData = await featuredRes.json()
          setFeatured(featuredData)
        }
      } catch (err) {
        console.error('Failed to fetch landing page data:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  return (
    <div className="bg-white">
      {/* Hero Section - Side by Side Layout */}
      <section className="relative overflow-hidden bg-gradient-to-br from-emerald-50 via-white to-purple-50">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(16,185,129,0.08),transparent_50%)]" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-24">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left - Hero Content */}
            <div>
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-100 text-emerald-700 rounded-full text-sm font-medium mb-6">
                {stats ? `${stats.validated_ideas}+` : '...'} Validated Opportunities
              </div>
              <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 tracking-tight leading-tight">
                Transform Market Signals into{' '}
                <span className="text-purple-600">Business Opportunities</span>
              </h1>
              <p className="mt-6 text-lg text-gray-600">
                Discover validated market opportunities backed by real consumer insights. 
                From AI-powered validation to expert execution playbooks—everything you need to build what people actually want.
              </p>
              <div className="mt-8 flex flex-col sm:flex-row gap-4">
                <Link
                  to="/idea-engine"
                  className="inline-flex items-center justify-center px-6 py-3.5 text-base font-medium text-white bg-black hover:bg-gray-800 rounded-lg gap-2"
                >
                  <Zap className="w-5 h-5" />
                  Validate Your Idea
                </Link>
                <button 
                  onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
                  className="inline-flex items-center justify-center px-6 py-3.5 text-base font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-lg gap-2"
                >
                  <Play className="w-5 h-5" />
                  Watch Demo
                </button>
              </div>
              
              {/* Stats Bar */}
              <div className="mt-12 flex gap-10">
                <div>
                  <div className="text-3xl font-bold text-gray-900">{stats?.validated_ideas ?? '...'}</div>
                  <div className="text-sm text-gray-500">Validated Ideas</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-gray-900">{stats?.total_market_opportunity ?? '...'}</div>
                  <div className="text-sm text-gray-500">Market Opportunity</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-gray-900">{stats?.global_markets ?? '...'}</div>
                  <div className="text-sm text-gray-500">Global Markets</div>
                </div>
              </div>
            </div>

            {/* Right - Opportunity Card Preview */}
            <div className="relative">
              {featured && (
                <>
                  <div className="absolute -top-4 right-0 inline-flex items-center gap-2 px-3 py-1.5 bg-white rounded-full shadow-md text-sm text-gray-600">
                    <Users className="w-4 h-4" />
                    {featured.validation_count} users want this
                  </div>
                  <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 mt-8">
                    <div className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Unlock This Week's Top Opportunity</div>
                    <div className="flex justify-between items-start">
                      <h3 className="text-lg font-semibold text-gray-900 pr-4">
                        {featured.title}
                      </h3>
                      <div className="flex-shrink-0 w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
                        <span className="text-emerald-600 font-bold text-lg">{featured.score}</span>
                      </div>
                    </div>
                    <p className="mt-3 text-sm text-gray-500">
                      {featured.description}
                    </p>
                    <div className="mt-5 grid grid-cols-3 gap-4 pt-4 border-t border-gray-100">
                      <div>
                        <div className="text-xs text-gray-400">Market Size</div>
                        <div className="font-semibold text-gray-900">{featured.market_size}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-400">Submissions</div>
                        <div className="font-semibold text-gray-900">{featured.validation_count}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-400">Growth</div>
                        <div className="font-semibold text-emerald-600">+{featured.growth_rate.toFixed(0)}%</div>
                      </div>
                    </div>
                    <div className="mt-4">
                      <div className="w-full bg-gray-100 rounded-full h-2">
                        <div className="bg-gradient-to-r from-emerald-400 to-emerald-500 h-2 rounded-full" style={{ width: `${Math.min(featured.score, 100)}%` }} />
                      </div>
                      <div className="mt-2 flex items-center gap-2 text-sm text-emerald-600">
                        <TrendingUp className="w-4 h-4" />
                        +{featured.growth_rate.toFixed(0)}% monthly growth
                      </div>
                    </div>
                  </div>
                </>
              )}
              {!featured && !loading && (
                <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 mt-8">
                  <div className="text-center py-8 text-gray-500">
                    <p>No opportunities available yet</p>
                    <Link to="/idea-engine" className="text-purple-600 hover:text-purple-700 font-medium mt-2 inline-block">
                      Submit your first idea
                    </Link>
                  </div>
                </div>
              )}
              {loading && (
                <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 mt-8 animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
                  <div className="h-6 bg-gray-200 rounded w-3/4 mb-3"></div>
                  <div className="h-4 bg-gray-200 rounded w-full mb-4"></div>
                  <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-100">
                    <div className="h-8 bg-gray-200 rounded"></div>
                    <div className="h-8 bg-gray-200 rounded"></div>
                    <div className="h-8 bg-gray-200 rounded"></div>
                  </div>
                </div>
              )}
              <Link to="/discover" className="mt-4 inline-flex items-center text-purple-600 hover:text-purple-700 font-medium text-sm">
                See More Opportunities <ArrowRight className="w-4 h-4 ml-1" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Three Paths to Success */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900">Choose Your Path to Success</h2>
            <p className="mt-4 text-lg text-gray-600">Whether you're building, advising, or creating content, OppGrid is designed for you.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-6">
                <Rocket className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Build & Launch</h3>
              <p className="text-gray-600 mb-6">
                Discover validated opportunities and execute with AI-powered guidance, step-by-step playbooks, and access to a vetted expert network.
              </p>
              <Link to="/discover" className="inline-flex items-center text-blue-600 font-medium hover:text-blue-700">
                Explore Opportunities <ArrowRight className="w-4 h-4 ml-1" />
              </Link>
            </div>
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mb-6">
                <Lightbulb className="w-6 h-6 text-amber-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Contribute & Earn</h3>
              <p className="text-gray-600 mb-6">
                Spot a trend? Submit market signals. Get paid when your contributions help identify top-tier opportunities and connect with teams.
              </p>
              <Link to="/signup" className="inline-flex items-center text-amber-600 font-medium hover:text-amber-700">
                Become a Scout <ArrowRight className="w-4 h-4 ml-1" />
              </Link>
            </div>
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-6">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Research & Create</h3>
              <p className="text-gray-600 mb-6">
                Use our AI analyst to generate deep-dive reports, trend analyses, and data-driven content. Instantly cite validated opportunities.
              </p>
              <Link to="/content" className="inline-flex items-center text-purple-600 font-medium hover:text-purple-700">
                Start Creating <ArrowRight className="w-4 h-4 ml-1" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* AI Co-founder Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-100 text-purple-700 rounded-full text-sm font-medium mb-4">
              <Zap className="w-4 h-4" />
              Your AI Co-founder is Ready
            </div>
            <h2 className="text-3xl font-bold text-gray-900">Meet Your AI Co-founder</h2>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              A persistent AI that understands your goals, skills, and progress. Get hyper-personalized guidance at every stage—from discovery to scale.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900 text-lg mb-2">Personal Paths</h3>
              <p className="text-gray-600">Get a custom roadmap tailored to your selected opportunity, skills, and resources.</p>
            </div>
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Target className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900 text-lg mb-2">Smart Matching</h3>
              <p className="text-gray-600">Automatically connect with the most relevant experts, tools, and playbooks in our network.</p>
            </div>
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900 text-lg mb-2">Expert Network</h3>
              <p className="text-gray-600">Access one-on-one consultations with industry operators, marketers, and engineers.</p>
            </div>
          </div>
        </div>
      </section>

      {/* From Signal to Launch */}
      <section id="how-it-works" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900">From Signal to Launch in Three Steps</h2>
            <p className="mt-4 text-lg text-gray-600">A systematic approach to turn noise into your next business.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="relative">
              <div className="absolute -top-3 -left-3 w-10 h-10 bg-black text-white rounded-full flex items-center justify-center font-bold">1</div>
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 pt-10">
                <h3 className="font-semibold text-gray-900 text-lg mb-3">Discover & Validate</h3>
                <p className="text-gray-600">
                  Browse our vault of scored opportunities. Each brief includes validated consumer pain points, market size analysis (TAM/SAM/SOM), and early signal strength.
                </p>
              </div>
            </div>
            <div className="relative">
              <div className="absolute -top-3 -left-3 w-10 h-10 bg-black text-white rounded-full flex items-center justify-center font-bold">2</div>
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 pt-10">
                <h3 className="font-semibold text-gray-900 text-lg mb-3">Plan & Assemble</h3>
                <p className="text-gray-600">
                  Activate your AI Co-founder. Generate a strategic action plan, assess resource needs, and get matched with experts for your core team.
                </p>
              </div>
            </div>
            <div className="relative">
              <div className="absolute -top-3 -left-3 w-10 h-10 bg-black text-white rounded-full flex items-center justify-center font-bold">3</div>
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 pt-10">
                <h3 className="font-semibold text-gray-900 text-lg mb-3">Execute with AI</h3>
                <p className="text-gray-600">
                  Launch with confidence. Your AI assistant helps track KPIs, automate tasks, and recommend pivots using real-time market data.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Validated Intelligence */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">Validated Market Intelligence, Not Just Data</h2>
              <p className="text-lg text-gray-600 mb-8">
                We analyze thousands of consumer discussions, reviews, and search trends to deliver structured, actionable briefs.
              </p>
              <div className="space-y-4">
                {[
                  { title: 'Problem Validation', desc: 'Quantified consumer pain points and demand signals' },
                  { title: 'Market Analysis', desc: 'TAM, SAM, SOM estimates and competitive landscape' },
                  { title: 'Execution Insights', desc: 'Geographic fit analysis, channel suggestions, and monetization models' },
                  { title: 'Source Transparency', desc: 'See the core discussions and data behind each insight' },
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-emerald-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-semibold text-gray-900">{item.title}</div>
                      <div className="text-gray-600 text-sm">{item.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-gradient-to-br from-emerald-50 to-purple-50 rounded-2xl p-8">
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Globe className="w-6 h-6 text-purple-600" />
                  <span className="font-semibold text-gray-900">Sample Opportunity Brief</span>
                </div>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Opportunity Score</span>
                    <span className="font-semibold text-emerald-600">87/100</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Market Size (TAM)</span>
                    <span className="font-semibold">$8.2B</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Competition Level</span>
                    <span className="font-semibold text-amber-600">Medium</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Growth Rate</span>
                    <span className="font-semibold text-emerald-600">+34% MoM</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 bg-gradient-to-r from-gray-900 to-gray-800">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to Build What's Next?</h2>
          <p className="text-gray-300 text-lg mb-8">Join hundreds of entrepreneurs discovering and validating opportunities every day.</p>
          <Link
            to="/signup"
            className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-gray-900 bg-white hover:bg-gray-100 rounded-lg gap-2"
          >
            Start Your First Opportunity — It's Free
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
