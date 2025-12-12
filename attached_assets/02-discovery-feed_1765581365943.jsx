import React, { useState } from 'react';
import { Search, Filter, TrendingUp, Users, DollarSign, ChevronDown, Sparkles, MapPin, ArrowUpRight } from 'lucide-react';

export default function DiscoveryFeed() {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('trending');
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterRegion, setFilterRegion] = useState('all');

  const opportunities = [
    {
      id: 2847,
      title: 'On-Demand Home Maintenance Subscription',
      category: 'Home Services',
      description: 'Homeowners struggle with reactive, expensive emergency repairs and lack a reliable way to maintain their homes proactively.',
      validationScore: 87,
      submissions: 2847,
      marketSize: '$8.4B',
      growth: '+34%',
      region: 'US National',
      trending: true,
      painPoints: ['Trust issues with contractors', 'Unpredictable emergency costs', 'No preventive maintenance plan']
    },
    {
      id: 2214,
      title: 'AI-Powered Meal Planning for Dietary Restrictions',
      category: 'Health & Wellness',
      description: 'People with multiple dietary restrictions spend hours planning meals and still struggle to find variety and nutrition.',
      validationScore: 82,
      submissions: 1876,
      marketSize: '$3.2B',
      growth: '+41%',
      region: 'Global',
      trending: true,
      painPoints: ['Limited recipe variety', 'Time-consuming planning', 'Conflicting dietary needs in families']
    },
    {
      id: 1998,
      title: 'Remote Team Culture & Engagement Platform',
      category: 'B2B SaaS',
      description: 'Remote teams lack informal connection opportunities and culture-building moments that happen naturally in offices.',
      validationScore: 79,
      submissions: 1542,
      marketSize: '$12.7B',
      growth: '+28%',
      region: 'Global',
      trending: false,
      painPoints: ['No spontaneous interactions', 'Feeling isolated', 'Weak team bonds']
    },
    {
      id: 1823,
      title: 'Pet Health Monitoring & Preventive Care',
      category: 'Pet Tech',
      description: 'Pet owners struggle to track health metrics and often miss early warning signs of serious conditions.',
      validationScore: 76,
      submissions: 1389,
      marketSize: '$4.8B',
      growth: '+52%',
      region: 'US National',
      trending: true,
      painPoints: ['Expensive emergency vet visits', 'Missing health warning signs', 'Difficulty tracking multiple pets']
    },
    {
      id: 1654,
      title: 'Fractional CFO Marketplace for Startups',
      category: 'B2B Services',
      description: 'Early-stage startups need financial expertise but can\'t afford or justify a full-time CFO.',
      validationScore: 84,
      submissions: 1247,
      marketSize: '$2.1B',
      growth: '+38%',
      region: 'US National',
      trending: false,
      painPoints: ['Can\'t afford full-time CFO', 'Poor financial planning', 'Investor reporting challenges']
    },
    {
      id: 1456,
      title: 'Smart Medication Adherence System',
      category: 'Healthcare',
      description: 'Patients with complex medication schedules struggle to take the right pills at the right time, leading to health complications.',
      validationScore: 81,
      submissions: 1098,
      marketSize: '$6.3B',
      growth: '+31%',
      region: 'Global',
      trending: false,
      painPoints: ['Missing doses regularly', 'Confusion about timing', 'Managing multiple medications']
    }
  ];

  const categories = [
    'All Categories',
    'Home Services',
    'Health & Wellness',
    'B2B SaaS',
    'Pet Tech',
    'B2B Services',
    'Healthcare'
  ];

  const regions = [
    'All Regions',
    'US National',
    'Global',
    'Canada',
    'UK',
    'Australia'
  ];

  return (
    <div className="min-h-screen bg-stone-50">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Spectral:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
        
        .spektral { font-family: 'Spectral', serif; }
        .inter { font-family: 'Inter', sans-serif; }
        
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        .fade-in {
          animation: fadeIn 0.4s ease-out;
        }
      `}</style>

      {/* Navigation */}
      <nav className="bg-white border-b border-stone-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-stone-900 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-2xl spektral font-bold text-stone-900">Katalyst</span>
            </div>
            <div className="flex items-center gap-8">
              <a href="/" className="inter text-sm text-stone-600 hover:text-stone-900 transition-colors">Home</a>
              <a href="/discover" className="inter text-sm text-stone-900 font-medium">Browse Ideas</a>
              <button className="inter text-sm font-medium text-stone-600 hover:text-stone-900 transition-colors">Sign In</button>
              <button className="bg-stone-900 text-white px-4 py-2 rounded-lg inter text-sm font-medium hover:bg-stone-800 transition-colors">
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Header */}
      <div className="bg-white border-b border-stone-200">
        <div className="max-w-7xl mx-auto px-8 py-12">
          <h1 className="text-5xl spektral font-bold text-stone-900 mb-4">
            Discover Validated Opportunities
          </h1>
          <p className="text-xl inter text-stone-600 max-w-3xl">
            Browse 2,847+ market opportunities backed by real consumer insights. Each idea is validated, categorized, and ready to explore.
          </p>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="bg-white border-b border-stone-200 sticky top-[73px] z-40">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <div className="flex items-center gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-stone-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search opportunities..."
                className="w-full pl-12 pr-4 py-3 border border-stone-200 rounded-lg inter text-sm focus:outline-none focus:border-stone-400 focus:ring-2 focus:ring-stone-100"
              />
            </div>

            {/* Category Filter */}
            <div className="relative">
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="appearance-none pl-4 pr-10 py-3 border border-stone-200 rounded-lg inter text-sm focus:outline-none focus:border-stone-400 bg-white cursor-pointer"
              >
                {categories.map((cat) => (
                  <option key={cat} value={cat.toLowerCase().replace(' ', '-')}>
                    {cat}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-stone-400 pointer-events-none" />
            </div>

            {/* Region Filter */}
            <div className="relative">
              <select
                value={filterRegion}
                onChange={(e) => setFilterRegion(e.target.value)}
                className="appearance-none pl-4 pr-10 py-3 border border-stone-200 rounded-lg inter text-sm focus:outline-none focus:border-stone-400 bg-white cursor-pointer"
              >
                {regions.map((region) => (
                  <option key={region} value={region.toLowerCase().replace(' ', '-')}>
                    {region}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-stone-400 pointer-events-none" />
            </div>

            {/* Sort */}
            <div className="relative">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="appearance-none pl-4 pr-10 py-3 border border-stone-200 rounded-lg inter text-sm focus:outline-none focus:border-stone-400 bg-white cursor-pointer"
              >
                <option value="trending">Trending</option>
                <option value="validation">Validation Score</option>
                <option value="market-size">Market Size</option>
                <option value="growth">Growth Rate</option>
                <option value="submissions">Submissions</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-stone-400 pointer-events-none" />
            </div>
          </div>
        </div>
      </div>

      {/* Opportunities Grid */}
      <div className="max-w-7xl mx-auto px-8 py-12">
        <div className="mb-6 flex items-center justify-between">
          <div className="inter text-sm text-stone-600">
            Showing <span className="font-medium text-stone-900">{opportunities.length}</span> opportunities
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6">
          {opportunities.map((opp, idx) => (
            <a
              key={opp.id}
              href={`/opportunity/${opp.id}`}
              className="block bg-white rounded-xl border-2 border-stone-200 hover:border-stone-900 transition-all hover:shadow-xl group fade-in"
              style={{animationDelay: `${idx * 0.1}s`}}
            >
              <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs inter font-medium text-stone-500 uppercase">{opp.category}</span>
                      {opp.trending && (
                        <span className="flex items-center gap-1 bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full text-xs inter font-medium">
                          <TrendingUp className="w-3 h-3" />
                          Trending
                        </span>
                      )}
                    </div>
                    <h3 className="text-xl spektral font-bold text-stone-900 mb-2 group-hover:text-violet-600 transition-colors">
                      {opp.title}
                    </h3>
                  </div>
                  <div className="flex flex-col items-end">
                    <div className="bg-emerald-100 text-emerald-700 px-3 py-1 rounded-full mb-1">
                      <div className="text-2xl spektral font-bold">{opp.validationScore}</div>
                    </div>
                    <div className="text-xs inter text-stone-500">Score</div>
                  </div>
                </div>

                {/* Description */}
                <p className="inter text-stone-700 text-sm mb-4 leading-relaxed">
                  {opp.description}
                </p>

                {/* Metrics */}
                <div className="grid grid-cols-4 gap-3 mb-4">
                  <div className="bg-stone-50 rounded-lg p-3">
                    <div className="text-xs inter text-stone-500 mb-1">Submissions</div>
                    <div className="text-lg spektral font-bold text-stone-900">{opp.submissions}</div>
                  </div>
                  <div className="bg-stone-50 rounded-lg p-3">
                    <div className="text-xs inter text-stone-500 mb-1">Market</div>
                    <div className="text-lg spektral font-bold text-stone-900">{opp.marketSize}</div>
                  </div>
                  <div className="bg-stone-50 rounded-lg p-3">
                    <div className="text-xs inter text-stone-500 mb-1">Growth</div>
                    <div className="text-lg spektral font-bold text-emerald-600">{opp.growth}</div>
                  </div>
                  <div className="bg-stone-50 rounded-lg p-3">
                    <div className="text-xs inter text-stone-500 mb-1 flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      Region
                    </div>
                    <div className="text-xs spektral font-bold text-stone-900">{opp.region}</div>
                  </div>
                </div>

                {/* Top Pain Points */}
                <div className="mb-4">
                  <div className="text-xs inter font-medium text-stone-500 mb-2">TOP PAIN POINTS</div>
                  <div className="space-y-1">
                    {opp.painPoints.slice(0, 2).map((pain, idx) => (
                      <div key={idx} className="text-xs inter text-stone-600 flex items-start gap-2">
                        <span className="text-violet-600">•</span>
                        <span>{pain}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* CTA */}
                <div className="pt-4 border-t border-stone-200">
                  <div className="flex items-center justify-between">
                    <span className="text-sm inter text-stone-600">View full analysis</span>
                    <ArrowUpRight className="w-4 h-4 text-stone-400 group-hover:text-violet-600 group-hover:translate-x-1 group-hover:-translate-y-1 transition-all" />
                  </div>
                </div>
              </div>
            </a>
          ))}
        </div>

        {/* Load More */}
        <div className="mt-12 text-center">
          <button className="bg-white border-2 border-stone-900 text-stone-900 px-8 py-4 rounded-lg inter font-medium hover:bg-stone-900 hover:text-white transition-all">
            Load More Opportunities
          </button>
        </div>
      </div>

      {/* Sticky CTA */}
      <div className="fixed bottom-8 right-8 bg-gradient-to-br from-violet-600 to-purple-700 text-white rounded-full shadow-2xl hover:shadow-violet-500/50 transition-all z-50">
        <a href="#" className="flex items-center gap-3 px-6 py-4 inter font-medium">
          <Sparkles className="w-5 h-5" />
          Submit Your Problem
        </a>
      </div>
    </div>
  );
}
