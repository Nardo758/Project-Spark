import React, { useState } from 'react';
import { Sparkles, Search, TrendingUp, MapPin, Target, DollarSign, FileText, BarChart3, Zap, CheckCircle, ArrowRight, Users, Globe, Calendar, Download, Share2, Send, ChevronRight, AlertCircle, Lock } from 'lucide-react';

export default function DesignShowcase() {
  const [activePage, setActivePage] = useState('landing');
  const [tier, setTier] = useState(1);

  const pages = [
    { id: 'landing', name: 'Landing Page', icon: Sparkles },
    { id: 'discovery', name: 'Discovery Feed', icon: Search },
    { id: 'tier1', name: 'Tier 1: Problem Detail', icon: FileText },
    { id: 'tier2', name: 'Tier 2: Research Dashboard', icon: TrendingUp },
    { id: 'tier3', name: 'Tier 3: Deep Dive + AI', icon: Sparkles },
    { id: 'submission', name: 'Problem Submission', icon: Target }
  ];

  return (
    <div className="min-h-screen bg-stone-100">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Spectral:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
        .spektral { font-family: 'Spectral', serif; }
        .inter { font-family: 'Inter', sans-serif; }
      `}</style>

      {/* Showcase Header */}
      <div className="bg-gradient-to-r from-stone-900 to-stone-800 text-white sticky top-0 z-50 shadow-2xl">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <h1 className="text-3xl spektral font-bold mb-2">Katalyst Design Showcase</h1>
          <p className="inter text-stone-300">Complete page designs from Landing to Deep Dive</p>
        </div>
      </div>

      {/* Page Navigation */}
      <div className="bg-white border-b-2 border-stone-300 sticky top-[88px] z-40">
        <div className="max-w-7xl mx-auto px-8 py-4">
          <div className="flex gap-2 overflow-x-auto">
            {pages.map((page) => {
              const Icon = page.icon;
              return (
                <button
                  key={page.id}
                  onClick={() => setActivePage(page.id)}
                  className={`flex items-center gap-2 px-4 py-3 rounded-lg inter text-sm font-medium whitespace-nowrap transition-all ${
                    activePage === page.id
                      ? 'bg-violet-600 text-white shadow-lg'
                      : 'bg-stone-100 text-stone-700 hover:bg-stone-200'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {page.name}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Page Content */}
      <div className="max-w-7xl mx-auto px-8 py-12">
        
        {/* LANDING PAGE */}
        {activePage === 'landing' && (
          <div className="space-y-8">
            <div className="bg-white rounded-xl shadow-lg p-8 border-2 border-stone-200">
              <h2 className="text-2xl spektral font-bold text-stone-900 mb-4">Landing Page Design</h2>
              <p className="inter text-stone-600 mb-6">Marketing homepage with hero, value props, and CTAs</p>
              
              {/* Hero Section Preview */}
              <div className="bg-gradient-to-br from-stone-50 via-stone-100 to-stone-50 rounded-xl p-12 border-2 border-stone-300">
                <div className="max-w-2xl">
                  <div className="inline-block bg-violet-100 text-violet-700 px-4 py-2 rounded-full text-sm inter font-medium mb-4">
                    2,847+ Validated Opportunities
                  </div>
                  <h1 className="text-5xl spektral font-bold text-stone-900 mb-4 leading-tight">
                    Transform Consumer Problems into 
                    <span className="text-violet-600"> Business Opportunities</span>
                  </h1>
                  <p className="text-xl inter text-stone-600 mb-6">
                    Discover validated market opportunities backed by real consumer insights.
                  </p>
                  
                  <div className="flex gap-4 mb-8">
                    <button className="bg-stone-900 text-white px-8 py-4 rounded-lg inter font-medium flex items-center gap-2 hover:shadow-xl transition-all">
                      Browse Opportunities
                      <ArrowRight className="w-5 h-5" />
                    </button>
                    <button className="border-2 border-stone-900 text-stone-900 px-8 py-4 rounded-lg inter font-medium hover:bg-stone-900 hover:text-white transition-all">
                      Watch Demo
                    </button>
                  </div>

                  {/* Social Proof */}
                  <div className="flex gap-8">
                    <div>
                      <div className="text-3xl spektral font-bold text-stone-900">2,847</div>
                      <div className="text-sm inter text-stone-600">Validated Ideas</div>
                    </div>
                    <div>
                      <div className="text-3xl spektral font-bold text-stone-900">$47B+</div>
                      <div className="text-sm inter text-stone-600">Market Opportunity</div>
                    </div>
                    <div>
                      <div className="text-3xl spektral font-bold text-stone-900">6</div>
                      <div className="text-sm inter text-stone-600">Global Markets</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* How It Works */}
              <div className="mt-8 grid grid-cols-3 gap-6">
                <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border-2 border-green-200">
                  <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mb-4">
                    <span className="text-2xl spektral font-bold text-white">1</span>
                  </div>
                  <h3 className="text-xl spektral font-bold text-stone-900 mb-2">Discover & Validate</h3>
                  <p className="text-sm inter text-stone-700">Browse validated opportunities with quick metrics</p>
                  <div className="mt-4 text-xs inter font-bold text-green-700">FREE</div>
                </div>
                
                <div className="bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl p-6 border-2 border-purple-200">
                  <div className="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center mb-4">
                    <span className="text-2xl spektral font-bold text-white">2</span>
                  </div>
                  <h3 className="text-xl spektral font-bold text-stone-900 mb-2">Research & Analyze</h3>
                  <p className="text-sm inter text-stone-700">Deep dive into market validation and competition</p>
                  <div className="mt-4 text-xs inter font-bold text-purple-700">PRO ($99/mo)</div>
                </div>
                
                <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-6 border-2 border-indigo-200">
                  <div className="w-12 h-12 bg-gradient-to-br from-violet-600 to-indigo-600 rounded-full flex items-center justify-center mb-4">
                    <Sparkles className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl spektral font-bold text-stone-900 mb-2">Execute with AI</h3>
                  <p className="text-sm inter text-stone-700">Get execution playbooks and AI guidance</p>
                  <div className="mt-4 text-xs inter font-bold text-indigo-700">BUSINESS ($499/mo)</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* DISCOVERY FEED */}
        {activePage === 'discovery' && (
          <div className="space-y-8">
            <div className="bg-white rounded-xl shadow-lg p-8 border-2 border-stone-200">
              <h2 className="text-2xl spektral font-bold text-stone-900 mb-4">Discovery Feed Design</h2>
              <p className="inter text-stone-600 mb-6">Browse all opportunities with filtering and search</p>
              
              {/* Filters */}
              <div className="mb-6 flex gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-stone-400" />
                  <input
                    type="text"
                    placeholder="Search opportunities..."
                    className="w-full pl-12 pr-4 py-3 border-2 border-stone-200 rounded-lg inter text-sm"
                  />
                </div>
                <select className="px-4 py-3 border-2 border-stone-200 rounded-lg inter text-sm">
                  <option>All Categories</option>
                  <option>Home Services</option>
                  <option>Health & Wellness</option>
                </select>
                <select className="px-4 py-3 border-2 border-stone-200 rounded-lg inter text-sm">
                  <option>All Regions</option>
                  <option>US National</option>
                  <option>Southwest</option>
                </select>
              </div>

              {/* Opportunity Cards */}
              <div className="grid grid-cols-2 gap-6">
                <div className="bg-white rounded-xl border-2 border-stone-200 hover:border-stone-900 transition-all p-6 cursor-pointer group">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs inter font-medium text-stone-500 uppercase">Home Services</span>
                        <span className="flex items-center gap-1 bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full text-xs inter font-medium">
                          <TrendingUp className="w-3 h-3" />
                          Trending
                        </span>
                      </div>
                      <h3 className="text-xl spektral font-bold text-stone-900 group-hover:text-violet-600 transition-colors">
                        On-Demand Home Maintenance
                      </h3>
                    </div>
                    <div className="bg-emerald-100 text-emerald-700 px-3 py-1 rounded-full">
                      <div className="text-2xl spektral font-bold">87</div>
                    </div>
                  </div>
                  
                  <p className="inter text-stone-700 text-sm mb-4">
                    Homeowners struggle with reactive, expensive emergency repairs...
                  </p>

                  <div className="grid grid-cols-4 gap-3 mb-4">
                    <div className="bg-stone-50 rounded-lg p-3">
                      <div className="text-xs inter text-stone-500 mb-1">Submissions</div>
                      <div className="text-lg spektral font-bold">2,847</div>
                    </div>
                    <div className="bg-stone-50 rounded-lg p-3">
                      <div className="text-xs inter text-stone-500 mb-1">Market</div>
                      <div className="text-lg spektral font-bold">$8.4B</div>
                    </div>
                    <div className="bg-stone-50 rounded-lg p-3">
                      <div className="text-xs inter text-stone-500 mb-1">Growth</div>
                      <div className="text-lg spektral font-bold text-emerald-600">+34%</div>
                    </div>
                    <div className="bg-stone-50 rounded-lg p-3">
                      <div className="text-xs inter text-stone-500 mb-1">Region</div>
                      <div className="text-xs spektral font-bold">US National</div>
                    </div>
                  </div>

                  <div className="pt-4 border-t border-stone-200 flex items-center justify-between">
                    <span className="text-sm inter text-stone-600">View full analysis</span>
                    <ArrowRight className="w-4 h-4 text-stone-400 group-hover:text-violet-600 transition-colors" />
                  </div>
                </div>

                <div className="bg-stone-100 rounded-xl border-2 border-stone-300 p-6 flex items-center justify-center">
                  <div className="text-center text-stone-500 inter text-sm">
                    <div className="mb-2">+2,846 more opportunities</div>
                    <div className="text-xs">Grid layout with filters</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TIER 1: PROBLEM DETAIL */}
        {activePage === 'tier1' && (
          <div className="space-y-8">
            <div className="bg-white rounded-xl shadow-lg p-8 border-2 border-emerald-200">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center">
                  <FileText className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl spektral font-bold text-stone-900">Tier 1: Problem Detail (FREE)</h2>
                  <p className="inter text-stone-600">Quick validation interface</p>
                </div>
              </div>

              {/* Geographic Selector */}
              <div className="mb-6">
                <h3 className="inter font-bold text-stone-900 mb-3">Geographic Market Selector</h3>
                <div className="grid grid-cols-3 gap-3 mb-4">
                  {['US National', 'Southwest', 'Canada', 'UK', 'Australia', 'Global'].map((region, idx) => (
                    <button
                      key={region}
                      className={`p-3 rounded-lg border-2 ${
                        idx === 0 ? 'border-violet-600 bg-violet-50' : 'border-stone-200 bg-white'
                      }`}
                    >
                      <div className="text-sm inter font-semibold">{region}</div>
                    </button>
                  ))}
                </div>
                <div className="bg-white rounded-lg border-2 border-stone-200 p-4">
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <div className="text-sm inter text-stone-500">Market Size</div>
                      <div className="text-2xl spektral font-bold">$8.4B</div>
                    </div>
                    <div>
                      <div className="text-sm inter text-stone-500">Submissions</div>
                      <div className="text-2xl spektral font-bold">2,847</div>
                    </div>
                    <div>
                      <div className="text-sm inter text-stone-500">Growth</div>
                      <div className="text-2xl spektral font-bold text-emerald-600">+34%</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Quick Metrics */}
              <div className="mb-6">
                <h3 className="inter font-bold text-stone-900 mb-3">Quick Validation Metrics</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-white rounded-lg border-2 border-stone-200 p-4">
                    <div className="text-sm inter text-stone-500 mb-1">Submissions</div>
                    <div className="text-3xl spektral font-bold">2,847</div>
                    <div className="text-sm inter text-emerald-600">↑ 34%/mo</div>
                  </div>
                  <div className="bg-white rounded-lg border-2 border-stone-200 p-4">
                    <div className="text-sm inter text-stone-500 mb-1">Market Size</div>
                    <div className="text-3xl spektral font-bold">$8.4B</div>
                  </div>
                  <div className="bg-white rounded-lg border-2 border-stone-200 p-4">
                    <div className="text-sm inter text-stone-500 mb-1">Urgency</div>
                    <div className="text-3xl spektral font-bold text-orange-600">High</div>
                  </div>
                </div>
              </div>

              {/* Pain Points */}
              <div className="mb-6">
                <h3 className="inter font-bold text-stone-900 mb-3">Top 3 Pain Points</h3>
                <div className="space-y-3">
                  <div className="bg-white rounded-lg border-l-4 border-red-500 p-4">
                    <p className="inter text-sm italic text-stone-800">"I never know when something's about to break..."</p>
                    <span className="inline-block mt-2 bg-red-100 text-red-700 px-2 py-1 rounded text-xs font-bold">CRITICAL</span>
                  </div>
                  <div className="bg-white rounded-lg border-l-4 border-orange-500 p-4">
                    <p className="inter text-sm italic text-stone-800">"Finding reliable contractors is a nightmare..."</p>
                    <span className="inline-block mt-2 bg-orange-100 text-orange-700 px-2 py-1 rounded text-xs font-bold">HIGH</span>
                  </div>
                </div>
              </div>

              {/* Paywall */}
              <div className="bg-gradient-to-br from-stone-900 to-stone-800 rounded-xl p-6 text-white">
                <div className="flex items-start gap-3 mb-4">
                  <Lock className="w-6 h-6 flex-shrink-0" />
                  <div>
                    <h3 className="text-xl spektral font-bold mb-2">Unlock Full Research Dashboard</h3>
                    <p className="text-stone-200 text-sm mb-3">Get market analysis, demographics, and competitive landscape</p>
                  </div>
                </div>
                <button className="bg-white text-stone-900 px-6 py-3 rounded-lg inter font-medium">
                  Upgrade to Pro ($99/mo)
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TIER 2: RESEARCH DASHBOARD */}
        {activePage === 'tier2' && (
          <div className="space-y-8">
            <div className="bg-white rounded-xl shadow-lg p-8 border-2 border-blue-200">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl spektral font-bold text-stone-900">Tier 2: Research Dashboard (PRO - $99/mo)</h2>
                  <p className="inter text-stone-600">Comprehensive market analysis</p>
                </div>
              </div>

              {/* Tabs */}
              <div className="mb-6 bg-stone-100 rounded-lg p-2 flex gap-2">
                {['Market Validation', 'Geographic', 'Problem', 'Sizing', 'Solutions'].map((tab, idx) => (
                  <button
                    key={tab}
                    className={`flex-1 py-2 px-3 rounded-lg inter text-sm font-medium ${
                      idx === 0 ? 'bg-blue-600 text-white' : 'text-stone-600 hover:bg-stone-50'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div className="space-y-4">
                <div className="bg-white rounded-lg border-2 border-stone-200 p-6">
                  <h3 className="inter font-bold text-stone-900 mb-4">Demand Signals</h3>
                  <div className="grid grid-cols-3 gap-6">
                    <div>
                      <div className="text-sm inter text-stone-500">Search Volume</div>
                      <div className="text-3xl spektral font-bold">127K/mo</div>
                    </div>
                    <div>
                      <div className="text-sm inter text-stone-500">YoY Growth</div>
                      <div className="text-3xl spektral font-bold text-emerald-600">+43%</div>
                    </div>
                    <div>
                      <div className="text-sm inter text-stone-500">Social Mentions</div>
                      <div className="text-3xl spektral font-bold">89K/mo</div>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg border-2 border-stone-200 p-6">
                  <h3 className="inter font-bold text-stone-900 mb-4">Competitive Landscape</h3>
                  <div className="space-y-3">
                    {['American Home Shield (23%)', 'HomeAdvisor (18%)', 'Thumbtack (12%)'].map((comp) => (
                      <div key={comp} className="bg-stone-50 rounded-lg p-4">
                        <div className="inter font-semibold text-stone-900">{comp}</div>
                        <div className="text-sm inter text-stone-600 mt-1">Key weakness: Poor service quality</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Second Paywall */}
              <div className="mt-6 bg-gradient-to-br from-violet-900 to-purple-900 rounded-xl p-6 text-white">
                <div className="flex items-start gap-3 mb-4">
                  <Sparkles className="w-6 h-6 flex-shrink-0" />
                  <div>
                    <h3 className="text-xl spektral font-bold mb-2">Unlock Deep Dive + AI Assistant</h3>
                    <p className="text-violet-100 text-sm mb-3">Get execution playbooks and AI guidance</p>
                  </div>
                </div>
                <button className="bg-white text-violet-900 px-6 py-3 rounded-lg inter font-medium">
                  Upgrade to Business ($499/mo)
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TIER 3: DEEP DIVE + AI */}
        {activePage === 'tier3' && (
          <div className="space-y-8">
            <div className="bg-white rounded-xl shadow-lg border-2 border-violet-200 overflow-hidden">
              <div className="bg-violet-50 p-6 border-b-2 border-violet-200">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-violet-600 rounded-lg flex items-center justify-center">
                    <Sparkles className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl spektral font-bold text-stone-900">Tier 3: Deep Dive + AI Console (BUSINESS - $499/mo)</h2>
                    <p className="inter text-violet-700">Execution-ready with AI assistance</p>
                  </div>
                </div>
              </div>

              <div className="flex" style={{ height: '600px' }}>
                {/* Sidebar */}
                <div className="w-64 bg-white border-r-2 border-stone-200 p-4 overflow-y-auto">
                  <div className="mb-4">
                    <div className="text-xs inter text-stone-600 mb-2">Progress: 67%</div>
                    <div className="h-2 bg-stone-100 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-violet-600 to-purple-600 w-2/3"></div>
                    </div>
                    <div className="text-xs inter text-stone-500 mt-1">6 of 9 sections</div>
                  </div>

                  <div className="space-y-2">
                    {[
                      { name: 'Market Validation', completed: false },
                      { name: 'Geographic', completed: true },
                      { name: 'Problem Analysis', completed: false },
                      { name: 'Opportunity Sizing', completed: false },
                      { name: 'Solution Pathways', completed: false },
                      { name: 'Executive Summary', completed: true },
                      { name: 'Financial Modeling', completed: false },
                      { name: 'Execution Playbook', completed: false },
                      { name: 'Data & Exports', completed: false }
                    ].map((section, idx) => (
                      <div key={idx} className={`p-2 rounded-lg border-2 ${
                        section.completed ? 'border-violet-300 bg-violet-50' : 'border-stone-200'
                      }`}>
                        <div className="flex items-center justify-between">
                          <span className="text-xs inter font-semibold text-stone-900">{section.name}</span>
                          {section.completed && <CheckCircle className="w-4 h-4 text-emerald-600" />}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* AI Console */}
                <div className="flex-1 flex flex-col">
                  <div className="border-b-2 border-stone-200 p-4 bg-white">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-violet-600 to-purple-700 rounded-lg flex items-center justify-center">
                          <Sparkles className="w-4 h-4 text-white" />
                        </div>
                        <div>
                          <div className="inter font-bold text-stone-900">AI Research Console</div>
                          <div className="text-xs inter text-stone-500">Ask anything about this opportunity</div>
                        </div>
                      </div>
                      <button className="flex items-center gap-2 px-3 py-2 bg-violet-600 text-white rounded-lg text-xs inter font-medium">
                        <Download className="w-3 h-3" />
                        Save
                      </button>
                    </div>
                  </div>

                  <div className="flex-1 bg-stone-50 p-6 overflow-y-auto">
                    <div className="max-w-2xl mx-auto text-center">
                      <div className="w-16 h-16 bg-gradient-to-br from-violet-100 to-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <Sparkles className="w-8 h-8 text-violet-600" />
                      </div>
                      <h3 className="text-xl spektral font-bold text-stone-900 mb-2">
                        How can I help you analyze this opportunity?
                      </h3>
                      <p className="inter text-stone-600 mb-6">
                        Generate business plans, roadmaps, financial models, and more
                      </p>

                      <div className="grid grid-cols-2 gap-3">
                        {[
                          { icon: FileText, text: 'Generate business plan' },
                          { icon: Calendar, text: 'Create roadmap' },
                          { icon: DollarSign, text: 'Build financial model' },
                          { icon: Target, text: 'Define MVP' }
                        ].map((action, idx) => {
                          const Icon = action.icon;
                          return (
                            <button key={idx} className="p-4 bg-white hover:bg-stone-50 border-2 border-stone-200 hover:border-violet-300 rounded-lg text-left transition-all">
                              <div className="w-8 h-8 bg-violet-100 rounded-lg flex items-center justify-center mb-2">
                                <Icon className="w-4 h-4 text-violet-600" />
                              </div>
                              <div className="text-sm inter font-medium text-stone-900">{action.text}</div>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  </div>

                  <div className="border-t-2 border-stone-200 p-4 bg-white">
                    <div className="relative">
                      <input
                        type="text"
                        placeholder="Ask anything..."
                        className="w-full px-4 py-3 pr-12 border-2 border-stone-200 rounded-lg inter text-sm"
                      />
                      <button className="absolute right-2 top-2 bg-gradient-to-r from-violet-600 to-purple-700 text-white p-2 rounded-lg">
                        <Send className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* PROBLEM SUBMISSION */}
        {activePage === 'submission' && (
          <div className="space-y-8">
            <div className="bg-white rounded-xl shadow-lg p-8 border-2 border-stone-200">
              <h2 className="text-2xl spektral font-bold text-stone-900 mb-4">Problem Submission Page</h2>
              <p className="inter text-stone-600 mb-6">Allow consumers to submit their problems</p>

              <div className="bg-gradient-to-br from-violet-50 to-purple-50 rounded-xl p-8 border-2 border-violet-200 mb-6">
                <div className="text-center mb-6">
                  <h3 className="text-3xl spektral font-bold text-stone-900 mb-2">What's Frustrating You?</h3>
                  <p className="text-lg inter text-stone-600">Share your everyday problems and unmet needs</p>
                </div>

                <div className="grid grid-cols-3 gap-6 mb-6">
                  <div className="bg-white rounded-lg p-4 text-center">
                    <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-2">
                      <Users className="w-6 h-6 text-emerald-600" />
                    </div>
                    <div className="text-sm inter font-semibold text-stone-900">You're Not Alone</div>
                    <div className="text-xs inter text-stone-600">2,847 others shared</div>
                  </div>
                  <div className="bg-white rounded-lg p-4 text-center">
                    <div className="w-12 h-12 bg-violet-100 rounded-full flex items-center justify-center mx-auto mb-2">
                      <Target className="w-6 h-6 text-violet-600" />
                    </div>
                    <div className="text-sm inter font-semibold text-stone-900">Earn Recognition</div>
                    <div className="text-xs inter text-stone-600">Get notified</div>
                  </div>
                  <div className="bg-white rounded-lg p-4 text-center">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                      <Zap className="w-6 h-6 text-blue-600" />
                    </div>
                    <div className="text-sm inter font-semibold text-stone-900">Shape Solutions</div>
                    <div className="text-xs inter text-stone-600">Help builders</div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border-2 border-stone-200 p-6">
                <label className="block mb-4">
                  <span className="text-lg inter font-bold text-stone-900 mb-2 block">Describe Your Problem</span>
                  <textarea
                    placeholder="Example: I never know when something in my home is about to break..."
                    rows={4}
                    className="w-full px-4 py-3 border-2 border-stone-200 rounded-lg inter"
                  />
                </label>

                <label className="block mb-4">
                  <span className="text-lg inter font-bold text-stone-900 mb-3 block">Category</span>
                  <div className="grid grid-cols-3 gap-3">
                    {['Home Services', 'Health & Wellness', 'B2B SaaS', 'Pet Tech', 'Finance', 'Other'].map((cat) => (
                      <button key={cat} className="p-3 rounded-lg border-2 border-stone-200 hover:border-violet-300 inter font-medium text-sm transition-all">
                        {cat}
                      </button>
                    ))}
                  </div>
                </label>

                <button className="w-full bg-gradient-to-r from-violet-600 to-purple-700 text-white py-4 rounded-lg inter font-bold hover:shadow-lg transition-all flex items-center justify-center gap-2">
                  <Send className="w-5 h-5" />
                  Submit My Problem
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
