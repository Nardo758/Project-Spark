import React, { useState } from 'react';
import { Search, TrendingUp, Zap, Lock, CheckCircle, ArrowRight, Users, Eye, Star, Filter, Sparkles, CreditCard } from 'lucide-react';

export default function KatalystUserFlow() {
  const [activeFlow, setActiveFlow] = useState('browse');

  return (
    <div className="min-h-screen bg-stone-50">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Spectral:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
        
        .spektral { font-family: 'Spectral', serif; }
        .inter { font-family: 'Inter', sans-serif; }
        
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }
        
        .fade-in-up {
          animation: fadeInUp 0.6s ease-out forwards;
        }
        
        .stagger-1 { animation-delay: 0.1s; opacity: 0; }
        .stagger-2 { animation-delay: 0.2s; opacity: 0; }
        .stagger-3 { animation-delay: 0.3s; opacity: 0; }
        .stagger-4 { animation-delay: 0.4s; opacity: 0; }
        .stagger-5 { animation-delay: 0.5s; opacity: 0; }
        
        .flow-arrow {
          position: relative;
        }
        
        .flow-arrow::after {
          content: '';
          position: absolute;
          bottom: -20px;
          left: 50%;
          transform: translateX(-50%);
          width: 2px;
          height: 20px;
          background: linear-gradient(180deg, #0f172a 0%, transparent 100%);
        }
        
        .animated-arrow {
          animation: pulse 2s ease-in-out infinite;
        }
      `}</style>

      {/* Header */}
      <div className="border-b border-stone-200 bg-white">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <h1 className="text-3xl spektral font-bold text-stone-900 mb-2">
            Complete User Flow: Discovery → Deep Dive
          </h1>
          <p className="inter text-stone-600">Understanding how users navigate from initial interest to actionable insights</p>
        </div>
      </div>

      {/* Flow Type Selector */}
      <div className="border-b border-stone-200 bg-white">
        <div className="max-w-7xl mx-auto px-8">
          <div className="flex gap-4 inter">
            <button
              onClick={() => setActiveFlow('browse')}
              className={`py-4 px-2 text-sm font-medium transition-colors ${
                activeFlow === 'browse'
                  ? 'text-stone-900 border-b-2 border-stone-900'
                  : 'text-stone-500 hover:text-stone-700'
              }`}
            >
              Browse Flow (Organic Discovery)
            </button>
            <button
              onClick={() => setActiveFlow('search')}
              className={`py-4 px-2 text-sm font-medium transition-colors ${
                activeFlow === 'search'
                  ? 'text-stone-900 border-b-2 border-stone-900'
                  : 'text-stone-500 hover:text-stone-700'
              }`}
            >
              Search Flow (Intent-Driven)
            </button>
            <button
              onClick={() => setActiveFlow('submission')}
              className={`py-4 px-2 text-sm font-medium transition-colors ${
                activeFlow === 'submission'
                  ? 'text-stone-900 border-b-2 border-stone-900'
                  : 'text-stone-500 hover:text-stone-700'
              }`}
            >
              Submission Flow (Problem Submitter)
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-8 py-12">
        
        {/* BROWSE FLOW */}
        {activeFlow === 'browse' && (
          <div className="space-y-6">
            
            {/* Stage 1: Landing/Homepage */}
            <div className="fade-in-up stagger-1">
              <div className="text-center mb-4">
                <div className="inline-block bg-violet-100 text-violet-700 px-4 py-2 rounded-full text-sm inter font-medium mb-2">
                  STAGE 1: ENTRY POINT
                </div>
              </div>
              <div className="bg-white rounded-lg p-8 border-2 border-stone-900 shadow-lg">
                <div className="flex items-start gap-6">
                  <div className="w-16 h-16 bg-stone-900 rounded-lg flex items-center justify-center flex-shrink-0">
                    <TrendingUp className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-2xl spektral font-bold text-stone-900 mb-2">Landing Page / Homepage</h2>
                    <p className="inter text-stone-700 mb-4">
                      User discovers Katalyst through marketing, word-of-mouth, or organic search
                    </p>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="bg-stone-50 rounded p-4">
                        <div className="text-xs inter font-medium text-stone-500 mb-2">HERO SECTION</div>
                        <p className="text-sm inter text-stone-700">"Transform Consumer Friction into Validated Business Opportunities"</p>
                      </div>
                      <div className="bg-stone-50 rounded p-4">
                        <div className="text-xs inter font-medium text-stone-500 mb-2">VALUE PROPS</div>
                        <p className="text-sm inter text-stone-700">2,847+ validated ideas • Real consumer insights • Market-ready data</p>
                      </div>
                      <div className="bg-stone-50 rounded p-4">
                        <div className="text-xs inter font-medium text-stone-500 mb-2">CTA</div>
                        <p className="text-sm inter text-stone-700 font-medium">"Browse Trending Opportunities" →</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flow-arrow"></div>
              </div>
            </div>

            {/* Arrow */}
            <div className="flex justify-center my-8">
              <ArrowRight className="w-6 h-6 text-stone-400 transform rotate-90 animated-arrow" />
            </div>

            {/* Stage 2: Browse/Discovery Feed */}
            <div className="fade-in-up stagger-2">
              <div className="text-center mb-4">
                <div className="inline-block bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm inter font-medium mb-2">
                  STAGE 2: DISCOVERY
                </div>
              </div>
              <div className="bg-white rounded-lg p-8 border-2 border-blue-500 shadow-lg">
                <div className="flex items-start gap-6">
                  <div className="w-16 h-16 bg-blue-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Filter className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-2xl spektral font-bold text-stone-900 mb-2">Idea Discovery Feed</h2>
                    <p className="inter text-stone-700 mb-4">
                      User browses curated opportunities sorted by trending, validation score, or category
                    </p>
                    <div className="bg-stone-50 rounded-lg p-6 mb-4">
                      <div className="text-sm inter font-medium text-stone-500 mb-3">EXAMPLE CARD VIEW:</div>
                      <div className="bg-white border border-stone-200 rounded p-4">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <div className="text-xs inter text-stone-500 mb-1">HOME SERVICES</div>
                            <h3 className="inter font-semibold text-stone-900">On-Demand Home Maintenance Subscription</h3>
                          </div>
                          <div className="bg-emerald-100 text-emerald-700 px-3 py-1 rounded-full text-sm inter font-bold">
                            87/100
                          </div>
                        </div>
                        <p className="text-sm inter text-stone-600 mb-3">Homeowners struggle with reactive, expensive emergency repairs...</p>
                        <div className="flex gap-3 text-xs inter text-stone-500">
                          <span>📊 2,847 submissions</span>
                          <span>💰 $8.4B market</span>
                          <span>📈 +34% growth</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-3">
                      <div className="flex-1 bg-amber-50 border border-amber-200 rounded p-3">
                        <div className="text-xs inter font-medium text-amber-700 mb-1">🔒 FREE TIER</div>
                        <p className="text-sm inter text-stone-700">Can see validation score, basic metrics, problem statement</p>
                      </div>
                      <div className="flex-1 bg-stone-50 border border-stone-200 rounded p-3">
                        <div className="text-xs inter font-medium text-stone-500 mb-1">USER ACTION</div>
                        <p className="text-sm inter text-stone-700 font-medium">Click card → Problem Detail page</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flow-arrow"></div>
              </div>
            </div>

            {/* Arrow */}
            <div className="flex justify-center my-8">
              <ArrowRight className="w-6 h-6 text-stone-400 transform rotate-90 animated-arrow" />
            </div>

            {/* Stage 3: Problem Detail (Tier 1) */}
            <div className="fade-in-up stagger-3">
              <div className="text-center mb-4">
                <div className="inline-block bg-green-100 text-green-700 px-4 py-2 rounded-full text-sm inter font-medium mb-2">
                  STAGE 3: TIER 1 - PROBLEM DETAIL (FREE)
                </div>
              </div>
              <div className="bg-white rounded-lg p-8 border-2 border-green-500 shadow-lg">
                <div className="flex items-start gap-6">
                  <div className="w-16 h-16 bg-green-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Eye className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-2xl spektral font-bold text-stone-900 mb-2">Problem Detail Page</h2>
                    <p className="inter text-stone-700 mb-4">
                      Quick validation view - helps user decide if this opportunity is worth deeper exploration
                    </p>
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div className="bg-stone-50 rounded p-4">
                        <div className="text-xs inter font-medium text-stone-500 mb-2">WHAT THEY SEE</div>
                        <ul className="text-sm inter text-stone-700 space-y-1">
                          <li>✓ Quick metrics (submissions, market size, urgency)</li>
                          <li>✓ Problem statement</li>
                          <li>✓ Top 3 consumer pain points</li>
                          <li>✓ Related opportunities</li>
                        </ul>
                      </div>
                      <div className="bg-stone-50 rounded p-4">
                        <div className="text-xs inter font-medium text-stone-500 mb-2">WHAT THEY DON'T SEE</div>
                        <ul className="text-sm inter text-stone-700 space-y-1">
                          <li>✗ Demographics breakdown</li>
                          <li>✗ Competitive landscape</li>
                          <li>✗ Financial modeling</li>
                          <li>✗ Execution playbook</li>
                        </ul>
                      </div>
                    </div>
                    <div className="bg-gradient-to-br from-stone-900 to-stone-700 rounded-lg p-6 text-white">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="spektral font-bold text-lg mb-1">🔓 Unlock Full Research Dashboard</h3>
                          <p className="inter text-sm text-stone-200">Market analysis • Demographics • Competition • Opportunity sizing</p>
                        </div>
                        <button className="bg-white text-stone-900 px-5 py-3 rounded-lg inter font-medium hover:bg-stone-100 transition-colors whitespace-nowrap">
                          Upgrade to Pro
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flow-arrow"></div>
              </div>
            </div>

            {/* Decision Point */}
            <div className="flex justify-center my-8">
              <div className="bg-amber-50 border-2 border-amber-400 rounded-lg p-4 text-center max-w-md">
                <div className="text-sm inter font-bold text-amber-700 mb-2">⚡ CONVERSION MOMENT</div>
                <p className="text-sm inter text-stone-700">User decides: Is this worth $X/month to explore deeper?</p>
              </div>
            </div>

            {/* Stage 4: Upgrade & Research Dashboard */}
            <div className="fade-in-up stagger-4">
              <div className="text-center mb-4">
                <div className="inline-block bg-purple-100 text-purple-700 px-4 py-2 rounded-full text-sm inter font-medium mb-2">
                  STAGE 4: TIER 2 - RESEARCH DASHBOARD (PRO TIER)
                </div>
              </div>
              <div className="bg-white rounded-lg p-8 border-2 border-purple-500 shadow-lg">
                <div className="flex items-start gap-6">
                  <div className="w-16 h-16 bg-purple-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <CheckCircle className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-2xl spektral font-bold text-stone-900 mb-2">Research Dashboard (Paid)</h2>
                    <p className="inter text-stone-700 mb-4">
                      User has upgraded and unlocks comprehensive validation data across 4 key dimensions
                    </p>
                    <div className="grid grid-cols-4 gap-3 mb-4">
                      <div className="bg-purple-50 border border-purple-200 rounded p-3 text-center">
                        <div className="text-xs inter font-medium text-purple-700 mb-1">TAB 1</div>
                        <p className="text-sm inter text-stone-900 font-medium">Market Validation</p>
                      </div>
                      <div className="bg-purple-50 border border-purple-200 rounded p-3 text-center">
                        <div className="text-xs inter font-medium text-purple-700 mb-1">TAB 2</div>
                        <p className="text-sm inter text-stone-900 font-medium">Problem Analysis</p>
                      </div>
                      <div className="bg-purple-50 border border-purple-200 rounded p-3 text-center">
                        <div className="text-xs inter font-medium text-purple-700 mb-1">TAB 3</div>
                        <p className="text-sm inter text-stone-900 font-medium">Opportunity Sizing</p>
                      </div>
                      <div className="bg-purple-50 border border-purple-200 rounded p-3 text-center">
                        <div className="text-xs inter font-medium text-purple-700 mb-1">TAB 4</div>
                        <p className="text-sm inter text-stone-900 font-medium">Solution Pathways</p>
                      </div>
                    </div>
                    <div className="bg-stone-50 rounded p-4 mb-4">
                      <div className="text-xs inter font-medium text-stone-500 mb-2">USER BEHAVIOR AT THIS STAGE</div>
                      <p className="text-sm inter text-stone-700">Explores tabs, takes notes, assesses if opportunity is worth pursuing. Can export basic reports.</p>
                    </div>
                    <div className="bg-gradient-to-br from-violet-600 to-purple-700 rounded-lg p-6 text-white">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="spektral font-bold text-lg mb-1">🚀 Unlock Deep Dive Analysis</h3>
                          <p className="inter text-sm text-white/80">Execution playbook • Financial models • AI Assistant • Full intelligence</p>
                        </div>
                        <button className="bg-white text-violet-700 px-5 py-3 rounded-lg inter font-medium hover:bg-stone-100 transition-colors whitespace-nowrap">
                          Upgrade to Business
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flow-arrow"></div>
              </div>
            </div>

            {/* Decision Point 2 */}
            <div className="flex justify-center my-8">
              <div className="bg-orange-50 border-2 border-orange-400 rounded-lg p-4 text-center max-w-md">
                <div className="text-sm inter font-bold text-orange-700 mb-2">⚡ SECOND CONVERSION MOMENT</div>
                <p className="text-sm inter text-stone-700">User decides: Ready to move from research to execution?</p>
              </div>
            </div>

            {/* Stage 5: Deep Dive */}
            <div className="fade-in-up stagger-5">
              <div className="text-center mb-4">
                <div className="inline-block bg-indigo-100 text-indigo-700 px-4 py-2 rounded-full text-sm inter font-medium mb-2">
                  STAGE 5: TIER 3 - DEEP DIVE (BUSINESS/ENTERPRISE)
                </div>
              </div>
              <div className="bg-white rounded-lg p-8 border-2 border-indigo-500 shadow-lg">
                <div className="flex items-start gap-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-violet-600 to-indigo-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-2xl spektral font-bold text-stone-900 mb-2">Deep Dive Analysis + AI Assistant</h2>
                    <p className="inter text-stone-700 mb-4">
                      Complete actionable intelligence for moving from insight to execution
                    </p>
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div className="space-y-2">
                        <div className="bg-indigo-50 border border-indigo-200 rounded p-3">
                          <div className="text-xs inter font-medium text-indigo-700 mb-1">📊 STATIC CONTENT</div>
                          <ul className="text-sm inter text-stone-700 space-y-1">
                            <li>• Executive summary</li>
                            <li>• Market intelligence</li>
                            <li>• Product strategy</li>
                            <li>• Financial modeling</li>
                            <li>• 90-day playbook</li>
                            <li>• Raw data exports</li>
                          </ul>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="bg-gradient-to-br from-violet-50 to-purple-50 border border-violet-300 rounded p-3">
                          <div className="text-xs inter font-medium text-violet-700 mb-1 flex items-center gap-1">
                            <Sparkles className="w-3 h-3" />
                            AI ASSISTANT (INTERACTIVE)
                          </div>
                          <ul className="text-sm inter text-stone-700 space-y-1">
                            <li>• Ask custom questions</li>
                            <li>• Get strategic recommendations</li>
                            <li>• Explore scenarios</li>
                            <li>• Compare alternatives</li>
                            <li>• Generate custom analysis</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                    <div className="bg-emerald-50 border border-emerald-300 rounded-lg p-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-emerald-500 rounded-full flex items-center justify-center">
                          <CheckCircle className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <div className="text-sm inter font-bold text-emerald-900">End State: Actionable Decision</div>
                          <p className="text-sm inter text-stone-700">User has everything needed to pursue or pass on this opportunity</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        )}

        {/* SEARCH FLOW */}
        {activeFlow === 'search' && (
          <div className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
              <h3 className="inter font-bold text-blue-900 mb-2">Intent-Driven User Path</h3>
              <p className="inter text-blue-800">User arrives with specific problem domain or market in mind</p>
            </div>

            {/* Stage 1: Search Entry */}
            <div className="fade-in-up stagger-1">
              <div className="text-center mb-4">
                <div className="inline-block bg-violet-100 text-violet-700 px-4 py-2 rounded-full text-sm inter font-medium mb-2">
                  STAGE 1: SEARCH QUERY
                </div>
              </div>
              <div className="bg-white rounded-lg p-8 border-2 border-stone-900 shadow-lg">
                <div className="flex items-start gap-6">
                  <div className="w-16 h-16 bg-stone-900 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Search className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-2xl spektral font-bold text-stone-900 mb-2">Search Interface</h2>
                    <p className="inter text-stone-700 mb-4">User searches for specific domain, problem type, or market</p>
                    <div className="bg-stone-50 rounded-lg p-6 mb-4">
                      <div className="text-sm inter font-medium text-stone-500 mb-3">EXAMPLE SEARCHES:</div>
                      <div className="space-y-2">
                        <div className="bg-white border border-stone-200 rounded px-4 py-3 inter text-stone-700">
                          "home maintenance" → 14 related opportunities
                        </div>
                        <div className="bg-white border border-stone-200 rounded px-4 py-3 inter text-stone-700">
                          "B2B SaaS healthcare" → 8 related opportunities
                        </div>
                        <div className="bg-white border border-stone-200 rounded px-4 py-3 inter text-stone-700">
                          "subscription models" → 23 related opportunities
                        </div>
                      </div>
                    </div>
                    <div className="bg-amber-50 border border-amber-200 rounded p-4">
                      <div className="text-xs inter font-medium text-amber-700 mb-1">KEY DIFFERENCE</div>
                      <p className="text-sm inter text-stone-700">Higher intent = faster conversion. User already knows what they're looking for.</p>
                    </div>
                  </div>
                </div>
                <div className="flow-arrow"></div>
              </div>
            </div>

            {/* Arrow */}
            <div className="flex justify-center my-8">
              <ArrowRight className="w-6 h-6 text-stone-400 transform rotate-90 animated-arrow" />
            </div>

            {/* Stage 2: Search Results */}
            <div className="fade-in-up stagger-2">
              <div className="text-center mb-4">
                <div className="inline-block bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm inter font-medium mb-2">
                  STAGE 2: FILTERED RESULTS
                </div>
              </div>
              <div className="bg-white rounded-lg p-8 border-2 border-blue-500 shadow-lg">
                <div className="flex items-start gap-6">
                  <div className="w-16 h-16 bg-blue-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Filter className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-2xl spektral font-bold text-stone-900 mb-2">Search Results Page</h2>
                    <p className="inter text-stone-700 mb-4">Filtered list of opportunities matching search criteria</p>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-stone-50 rounded p-4">
                        <div className="text-xs inter font-medium text-stone-500 mb-2">SORTING OPTIONS</div>
                        <ul className="text-sm inter text-stone-700 space-y-1">
                          <li>• Relevance (default)</li>
                          <li>• Validation score</li>
                          <li>• Market size</li>
                          <li>• Submission growth</li>
                        </ul>
                      </div>
                      <div className="bg-stone-50 rounded p-4">
                        <div className="text-xs inter font-medium text-stone-500 mb-2">USER ACTION</div>
                        <p className="text-sm inter text-stone-700">Click most relevant result → Problem Detail</p>
                        <p className="text-xs inter text-stone-500 mt-2">Faster path than browse flow</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flow-arrow"></div>
              </div>
            </div>

            {/* Arrow */}
            <div className="flex justify-center my-8">
              <div className="bg-green-50 border border-green-400 rounded-lg p-4 text-center max-w-md">
                <div className="text-sm inter font-bold text-green-700 mb-1">↓ Same flow from here ↓</div>
                <p className="text-xs inter text-stone-600">Problem Detail → Research Dashboard → Deep Dive</p>
              </div>
            </div>

            {/* Condensed remaining flow */}
            <div className="bg-white rounded-lg p-6 border border-stone-200">
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-2">
                    <span className="text-white font-bold">3</span>
                  </div>
                  <div className="text-sm inter font-medium text-stone-900">Problem Detail (Free)</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg border border-purple-200">
                  <div className="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center mx-auto mb-2">
                    <span className="text-white font-bold">4</span>
                  </div>
                  <div className="text-sm inter font-medium text-stone-900">Research Dashboard (Pro)</div>
                </div>
                <div className="text-center p-4 bg-indigo-50 rounded-lg border border-indigo-200">
                  <div className="w-12 h-12 bg-indigo-500 rounded-full flex items-center justify-center mx-auto mb-2">
                    <span className="text-white font-bold">5</span>
                  </div>
                  <div className="text-sm inter font-medium text-stone-900">Deep Dive (Business)</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* SUBMISSION FLOW */}
        {activeFlow === 'submission' && (
          <div className="space-y-6">
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-6 mb-8">
              <h3 className="inter font-bold text-purple-900 mb-2">Problem Submitter Journey</h3>
              <p className="inter text-purple-800">User who submitted a problem comes back to see if it's validated as an opportunity</p>
            </div>

            {/* Stage 1: Problem Submission */}
            <div className="fade-in-up stagger-1">
              <div className="text-center mb-4">
                <div className="inline-block bg-violet-100 text-violet-700 px-4 py-2 rounded-full text-sm inter font-medium mb-2">
                  STAGE 1: INITIAL SUBMISSION
                </div>
              </div>
              <div className="bg-white rounded-lg p-8 border-2 border-stone-900 shadow-lg">
                <div className="flex items-start gap-6">
                  <div className="w-16 h-16 bg-stone-900 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Zap className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-2xl spektral font-bold text-stone-900 mb-2">Submit a Problem (Months Ago)</h2>
                    <p className="inter text-stone-700 mb-4">User submitted a personal frustration or unmet need</p>
                    <div className="bg-stone-50 rounded-lg p-4 mb-4">
                      <p className="text-sm inter text-stone-700 italic">
                        "I'm so frustrated trying to find reliable contractors for home maintenance. I never know when something's about to break and it always costs a fortune when it does."
                      </p>
                    </div>
                    <div className="bg-blue-50 border border-blue-200 rounded p-4">
                      <div className="text-xs inter font-medium text-blue-700 mb-1">INITIAL REWARD</div>
                      <p className="text-sm inter text-stone-700">User earned points/badges for contributing. Gets email notifications when their problem gains traction.</p>
                    </div>
                  </div>
                </div>
                <div className="flow-arrow"></div>
              </div>
            </div>

            {/* Arrow */}
            <div className="flex justify-center my-8">
              <div className="bg-amber-50 border border-amber-400 rounded-lg p-3 text-center max-w-md">
                <p className="text-xs inter font-medium text-amber-700">⏱️ Time passes... Problem clusters with similar submissions</p>
              </div>
            </div>

            {/* Stage 2: Notification */}
            <div className="fade-in-up stagger-2">
              <div className="text-center mb-4">
                <div className="inline-block bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm inter font-medium mb-2">
                  STAGE 2: RE-ENGAGEMENT
                </div>
              </div>
              <div className="bg-white rounded-lg p-8 border-2 border-blue-500 shadow-lg">
                <div className="flex items-start gap-6">
                  <div className="w-16 h-16 bg-blue-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Users className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-2xl spektral font-bold text-stone-900 mb-2">Email Notification</h2>
                    <p className="inter text-stone-700 mb-4">User receives notification that their problem has been validated</p>
                    <div className="bg-stone-50 rounded-lg p-6 mb-4 border-l-4 border-blue-500">
                      <div className="text-xs inter font-medium text-stone-500 mb-2">EMAIL PREVIEW:</div>
                      <h3 className="inter font-bold text-stone-900 mb-2">🎉 Your problem is now a validated opportunity!</h3>
                      <p className="text-sm inter text-stone-700 mb-3">
                        "On-Demand Home Maintenance Subscription" now has 2,847 submissions and an 87/100 validation score.
                      </p>
                      <button className="bg-blue-500 text-white px-4 py-2 rounded inter text-sm font-medium">
                        See Full Opportunity →
                      </button>
                    </div>
                    <div className="bg-green-50 border border-green-200 rounded p-4">
                      <div className="text-xs inter font-medium text-green-700 mb-1">GAMIFICATION HOOK</div>
                      <p className="text-sm inter text-stone-700">User feels validated, wants to see what others said about THEIR problem</p>
                    </div>
                  </div>
                </div>
                <div className="flow-arrow"></div>
              </div>
            </div>

            {/* Arrow */}
            <div className="flex justify-center my-8">
              <ArrowRight className="w-6 h-6 text-stone-400 transform rotate-90 animated-arrow" />
            </div>

            {/* Stage 3: Return Visit */}
            <div className="fade-in-up stagger-3">
              <div className="text-center mb-4">
                <div className="inline-block bg-green-100 text-green-700 px-4 py-2 rounded-full text-sm inter font-medium mb-2">
                  STAGE 3: PROBLEM DETAIL (FREE)
                </div>
              </div>
              <div className="bg-white rounded-lg p-8 border-2 border-green-500 shadow-lg">
                <div className="flex items-start gap-6">
                  <div className="w-16 h-16 bg-green-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Star className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-2xl spektral font-bold text-stone-900 mb-2">Viewing "Their" Opportunity</h2>
                    <p className="inter text-stone-700 mb-4">User has emotional investment - this was THEIR frustration</p>
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div className="bg-green-50 rounded p-4">
                        <div className="text-xs inter font-medium text-green-700 mb-2">EMOTIONAL DRIVERS</div>
                        <ul className="text-sm inter text-stone-700 space-y-1">
                          <li>• "I wasn't alone!"</li>
                          <li>• "2,847 others felt this too"</li>
                          <li>• Validation of personal experience</li>
                          <li>• Curiosity about solutions</li>
                        </ul>
                      </div>
                      <div className="bg-purple-50 rounded p-4">
                        <div className="text-xs inter font-medium text-purple-700 mb-2">CONVERSION ADVANTAGE</div>
                        <ul className="text-sm inter text-stone-700 space-y-1">
                          <li>• Higher engagement than browse users</li>
                          <li>• Personal stake in the outcome</li>
                          <li>• More likely to upgrade</li>
                          <li>• Potential to become customer of solution</li>
                        </ul>
                      </div>
                    </div>
                    <div className="bg-gradient-to-br from-stone-900 to-stone-700 rounded-lg p-6 text-white">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="spektral font-bold text-lg mb-1">Want to see what everyone said?</h3>
                          <p className="inter text-sm text-stone-200">Unlock all 2,847 submissions and full market analysis</p>
                        </div>
                        <button className="bg-white text-stone-900 px-5 py-3 rounded-lg inter font-medium">
                          Upgrade Now
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flow-arrow"></div>
              </div>
            </div>

            {/* Arrow */}
            <div className="flex justify-center my-8">
              <div className="bg-green-50 border border-green-400 rounded-lg p-4 text-center max-w-md">
                <div className="text-sm inter font-bold text-green-700 mb-1">↓ Same flow from here ↓</div>
                <p className="text-xs inter text-stone-600">Research Dashboard → Deep Dive (but with higher conversion rates)</p>
              </div>
            </div>

            {/* Condensed remaining flow */}
            <div className="bg-white rounded-lg p-6 border border-stone-200">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-purple-50 rounded-lg border border-purple-200">
                  <div className="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center mx-auto mb-2">
                    <span className="text-white font-bold">4</span>
                  </div>
                  <div className="text-sm inter font-medium text-stone-900 mb-2">Research Dashboard (Pro)</div>
                  <div className="text-xs inter text-stone-600">Higher conversion: wants to see ALL submissions</div>
                </div>
                <div className="text-center p-4 bg-indigo-50 rounded-lg border border-indigo-200">
                  <div className="w-12 h-12 bg-indigo-500 rounded-full flex items-center justify-center mx-auto mb-2">
                    <span className="text-white font-bold">5</span>
                  </div>
                  <div className="text-sm inter font-medium text-stone-900 mb-2">Deep Dive (Business)</div>
                  <div className="text-xs inter text-stone-600">May become founding customer of solution!</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Summary Section */}
        <div className="mt-16 bg-gradient-to-br from-stone-900 to-stone-700 rounded-lg p-8 text-white">
          <h2 className="text-2xl spektral font-bold mb-4">Key Flow Insights</h2>
          <div className="grid grid-cols-3 gap-6">
            <div>
              <h3 className="inter font-semibold mb-2">Browse Flow</h3>
              <p className="text-sm text-stone-200">Largest volume, lowest intent. Needs strong validation at each step.</p>
            </div>
            <div>
              <h3 className="inter font-semibold mb-2">Search Flow</h3>
              <p className="text-sm text-stone-200">Medium volume, high intent. Faster conversion, skip discovery phase.</p>
            </div>
            <div>
              <h3 className="inter font-semibold mb-2">Submission Flow</h3>
              <p className="text-sm text-stone-200">Smallest volume, highest conversion. Emotional investment drives upgrades.</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
