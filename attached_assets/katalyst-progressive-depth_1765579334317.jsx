import React, { useState } from 'react';
import { ChevronRight, TrendingUp, Users, DollarSign, Map, Target, BarChart3, FileText, Lock, ArrowRight, Sparkles, MessageSquare, Send, MapPin, Globe } from 'lucide-react';

export default function KatalystProgressiveDepth() {
  const [currentTier, setCurrentTier] = useState('detail');
  const [activeTab, setActiveTab] = useState('market');
  const [aiChatOpen, setAiChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('us-national');
  const [messages, setMessages] = useState([
    { type: 'ai', text: 'Hi! I\'m your AI research assistant. I can help you explore this opportunity in depth. Try asking me:', timestamp: new Date() },
    { type: 'suggestions', options: [
      'What are the biggest risks with this business model?',
      'Where should I launch this geographically?',
      'How would you recommend pricing the product?',
      'What should the MVP feature set look like?'
    ]}
  ]);

  // Geographic market data
  const geographicData = {
    'us-national': {
      label: 'United States (National)',
      applicability: 'High',
      marketSize: '$8.4B',
      submissions: 2847,
      growth: '+34%',
      topCities: ['Austin, TX', 'Denver, CO', 'Portland, OR', 'Nashville, TN', 'Charlotte, NC'],
      demographics: 'Homeowners 35-54, $75K-150K income',
      competitiveDensity: 'High',
      regulatoryComplexity: 'Medium - State-by-state licensing',
      opportunity: 'National opportunity with strong metro-by-metro demand'
    },
    'us-regional': {
      label: 'Southwest Region',
      applicability: 'Very High',
      marketSize: '$1.2B',
      submissions: 847,
      growth: '+52%',
      topCities: ['Austin, TX', 'Phoenix, AZ', 'Las Vegas, NV', 'Albuquerque, NM'],
      demographics: 'New homeowners, high growth markets',
      competitiveDensity: 'Medium',
      regulatoryComplexity: 'Low - Business-friendly states',
      opportunity: 'Best launch region - high growth + lower competition + favorable regulations'
    },
    'canada': {
      label: 'Canada',
      applicability: 'High',
      marketSize: '$2.1B CAD',
      submissions: 412,
      growth: '+28%',
      topCities: ['Toronto, ON', 'Vancouver, BC', 'Calgary, AB', 'Montreal, QC'],
      demographics: 'Similar to US, slightly higher income threshold',
      competitiveDensity: 'Low',
      regulatoryComplexity: 'High - Provincial regulations + bilingual requirements',
      opportunity: 'Strong market but complex entry requirements'
    },
    'uk': {
      label: 'United Kingdom',
      applicability: 'Medium',
      marketSize: '£1.8B',
      submissions: 234,
      growth: '+19%',
      topCities: ['London', 'Manchester', 'Birmingham', 'Edinburgh'],
      demographics: 'Homeowners skew older (45-65)',
      competitiveDensity: 'High',
      regulatoryComplexity: 'High - Different trade certifications',
      opportunity: 'Established market but requires localization and certification alignment'
    },
    'australia': {
      label: 'Australia',
      applicability: 'Medium',
      marketSize: '$1.4B AUD',
      submissions: 189,
      growth: '+31%',
      topCities: ['Sydney', 'Melbourne', 'Brisbane', 'Perth'],
      demographics: 'High homeownership rate (65%)',
      competitiveDensity: 'Low',
      regulatoryComplexity: 'Medium - State-based licensing',
      opportunity: 'Emerging opportunity with less competition but smaller market size'
    },
    'global': {
      label: 'Global Market',
      applicability: 'Varies',
      marketSize: '$47B+',
      submissions: 4821,
      growth: '+29%',
      topCities: ['N/A - Multiple markets'],
      demographics: 'Varies by region',
      competitiveDensity: 'Highly variable',
      regulatoryComplexity: 'Extremely complex',
      opportunity: 'Long-term expansion opportunity - prioritize proven markets first'
    }
  };

  const handleSendMessage = (text) => {
    if (!text.trim()) return;
    
    // Add user message
    setMessages(prev => [...prev, { type: 'user', text, timestamp: new Date() }]);
    setChatInput('');
    
    // Simulate AI response
    setTimeout(() => {
      const responses = {
        'risk': 'Based on the data, the three biggest risks are:\n\n1. **Contractor Quality Control** - With 847 mentions of trust issues, maintaining service quality at scale is critical. Recommend implementing a rigorous 3-tier vetting process and real-time quality scoring.\n\n2. **Unit Economics** - CAC of $127 is solid, but you\'ll need to hit 500+ customers per metro to achieve profitable density. Start with high-value markets (Austin, Denver) where willingness-to-pay is highest.\n\n3. **Churn Management** - Subscription fatigue is real. The data shows 67% would subscribe at $49/mo, but retention will depend on demonstrating value before the first maintenance issue occurs.',
        'pricing': 'The data reveals clear pricing tiers:\n\n**Recommended Strategy:**\n- **Starter ($49/mo)** - Annual inspection + 2 preventive visits + 10% discount on repairs\n- **Premium ($99/mo)** - Everything in Starter + priority scheduling + $500 emergency coverage\n- **Comprehensive ($149/mo)** - Everything in Premium + unlimited visits + full parts coverage\n\n67% of respondents would pay $49/mo, creating a strong funnel. The key is converting 30% of Starter users to Premium within 6 months through demonstrating value.',
        'mvp': 'Based on user priorities, your MVP should focus on solving the top 3 pain points:\n\n**Must-Have Features:**\n1. Vetted Contractor Matching (Priority #1, 1,247 mentions)\n2. Preventive Maintenance Scheduler (Priority #2, 1,089 mentions)\n3. Transparent Fixed Pricing (Priority #3, 923 mentions)\n\n**Phase 1 Scope:**\n- Simple subscription signup\n- Annual home inspection booking\n- Contractor profile & reviews\n- Basic scheduling dashboard\n\n**Defer to Phase 2:**\n- 24/7 emergency support (876 mentions, but complex operationally)\n- Home monitoring systems (734 mentions, requires hardware partnerships)',
        'competitor': 'Here\'s how you differentiate from the top 3 competitors:\n\n**vs. American Home Shield (23% share)**\n- Their weakness: Poor service quality (avg 2.3★ rating)\n- Your advantage: Vetted network with real-time quality scoring\n- Positioning: "Premium service, not just warranty coverage"\n\n**vs. HomeAdvisor (18% share)**\n- Their weakness: Lead generation only, no ongoing relationship\n- Your advantage: Preventive subscription model\n- Positioning: "Proactive care, not reactive bidding"\n\n**vs. Thumbtack (12% share)**\n- Their weakness: One-off transactions, trust issues\n- Your advantage: Trusted ongoing relationship\n- Positioning: "Your home\'s maintenance partner"\n\n**Key Differentiator:** You\'re the only solution combining prevention + trusted relationships + predictable costs.',
        'geograph': 'Based on geographic analysis across 6 markets:\n\n**Recommended Launch Sequence:**\n\n**Phase 1 (Months 0-12): Southwest US**\n- Start: Austin, TX → Phoenix, AZ\n- Why: Highest growth (+52%), $1.2B market, business-friendly regulations\n- Market size: 847 validated submissions\n- Competition: Medium (easier entry)\n\n**Phase 2 (Months 13-24): National Expansion**\n- Add: Denver, Portland, Nashville, Charlotte\n- Why: Strong demand signals, expanding from proven base\n- Challenge: State-by-state licensing complexity\n\n**Phase 3 (Months 25-36): International**\n- Markets: Canada ($2.1B CAD), Australia ($1.4B AUD)\n- Why: Similar demographics, lower competition\n- Challenge: Regulatory complexity, localization needed\n\n**Why NOT start global?** The UK has high competition and complex certifications. Better to dominate US first, then expand to similar English-speaking markets.',
        'where': 'Based on geographic analysis across 6 markets:\n\n**Recommended Launch Sequence:**\n\n**Phase 1 (Months 0-12): Southwest US**\n- Start: Austin, TX → Phoenix, AZ\n- Why: Highest growth (+52%), $1.2B market, business-friendly regulations\n- Market size: 847 validated submissions\n- Competition: Medium (easier entry)\n\n**Phase 2 (Months 13-24): National Expansion**\n- Add: Denver, Portland, Nashville, Charlotte\n- Why: Strong demand signals, expanding from proven base\n- Challenge: State-by-state licensing complexity\n\n**Phase 3 (Months 25-36): International**\n- Markets: Canada ($2.1B CAD), Australia ($1.4B AUD)\n- Why: Similar demographics, lower competition\n- Challenge: Regulatory complexity, localization needed\n\n**Why NOT start global?** The UK has high competition and complex certifications. Better to dominate US first, then expand to similar English-speaking markets.'
      };
      
      let responseText = 'I can analyze that for you. Based on the research data:\n\nCould you be more specific about what aspect you\'d like me to explore?';
      
      const lowerText = text.toLowerCase();
      if (lowerText.includes('risk')) responseText = responses.risk;
      else if (lowerText.includes('pric')) responseText = responses.pricing;
      else if (lowerText.includes('mvp') || lowerText.includes('feature')) responseText = responses.mvp;
      else if (lowerText.includes('compet')) responseText = responses.competitor;
      else if (lowerText.includes('geograph') || lowerText.includes('where') || lowerText.includes('market') || lowerText.includes('region') || lowerText.includes('location')) responseText = responses.geograph;
      
      setMessages(prev => [...prev, { type: 'ai', text: responseText, timestamp: new Date() }]);
    }, 1000);
  };

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
        
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(-10px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        .fade-in-up {
          animation: fadeInUp 0.6s ease-out forwards;
        }
        
        .slide-in {
          animation: slideIn 0.4s ease-out forwards;
        }
        
        .stagger-1 { animation-delay: 0.1s; opacity: 0; }
        .stagger-2 { animation-delay: 0.2s; opacity: 0; }
        .stagger-3 { animation-delay: 0.3s; opacity: 0; }
        .stagger-4 { animation-delay: 0.4s; opacity: 0; }
        .stagger-5 { animation-delay: 0.5s; opacity: 0; }
        
        .tier-indicator {
          position: relative;
          overflow: hidden;
        }
        
        .tier-indicator::after {
          content: '';
          position: absolute;
          bottom: 0;
          left: 0;
          height: 2px;
          background: linear-gradient(90deg, #0f172a, #475569);
          transition: width 0.3s ease;
        }
        
        .tier-detail::after { width: 33.33%; }
        .tier-research::after { width: 66.66%; }
        .tier-deep::after { width: 100%; }
      `}</style>

      {/* Header */}
      <div className="border-b border-stone-200 bg-white">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm inter font-medium text-stone-500 mb-1">IDEA #2847</div>
              <h1 className="text-3xl spektral font-bold text-stone-900">
                On-Demand Home Maintenance Subscription
              </h1>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="text-xs inter text-stone-500">Validation Score</div>
                <div className="text-2xl spektral font-bold text-emerald-600">87/100</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tier Navigation */}
      <div className={`border-b border-stone-200 bg-white tier-indicator tier-${currentTier}`}>
        <div className="max-w-7xl mx-auto px-8">
          <div className="flex gap-8 inter">
            <button
              onClick={() => setCurrentTier('detail')}
              className={`py-4 text-sm font-medium transition-colors ${
                currentTier === 'detail'
                  ? 'text-stone-900 border-b-2 border-stone-900'
                  : 'text-stone-500 hover:text-stone-700'
              }`}
            >
              Problem Detail
            </button>
            <button
              onClick={() => setCurrentTier('research')}
              className={`py-4 text-sm font-medium transition-colors flex items-center gap-2 ${
                currentTier === 'research'
                  ? 'text-stone-900 border-b-2 border-stone-900'
                  : 'text-stone-500 hover:text-stone-700'
              }`}
            >
              Research Dashboard
              {currentTier === 'detail' && (
                <Lock className="w-3 h-3" />
              )}
            </button>
            <button
              onClick={() => setCurrentTier('deep')}
              className={`py-4 text-sm font-medium transition-colors flex items-center gap-2 ${
                currentTier === 'deep'
                  ? 'text-stone-900 border-b-2 border-stone-900'
                  : 'text-stone-500 hover:text-stone-700'
              }`}
            >
              Deep Dive
              {currentTier !== 'deep' && (
                <Lock className="w-3 h-3" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="max-w-7xl mx-auto px-8 py-12">
        {/* TIER 1: PROBLEM DETAIL */}
        {currentTier === 'detail' && (
          <div className="space-y-8">
            {/* Geographic Market Selector */}
            <div className="bg-white rounded-lg p-6 border border-stone-200 fade-in-up">
              <div className="flex items-center gap-3 mb-4">
                <Globe className="w-5 h-5 text-stone-600" />
                <h3 className="text-lg spektral font-bold text-stone-900">Geographic Market Analysis</h3>
              </div>
              <div className="grid grid-cols-6 gap-2">
                {Object.entries(geographicData).map(([key, data]) => (
                  <button
                    key={key}
                    onClick={() => setSelectedRegion(key)}
                    className={`p-3 rounded-lg text-sm inter font-medium transition-all ${
                      selectedRegion === key
                        ? 'bg-stone-900 text-white'
                        : 'bg-stone-50 text-stone-600 hover:bg-stone-100'
                    }`}
                  >
                    {data.label.split(' ')[0]}
                  </button>
                ))}
              </div>
              <div className="mt-4 p-4 bg-stone-50 rounded-lg">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="text-xs inter font-medium text-stone-500 mb-1">SELECTED MARKET</div>
                    <div className="text-lg spektral font-bold text-stone-900">{geographicData[selectedRegion].label}</div>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm inter font-medium ${
                    geographicData[selectedRegion].applicability === 'Very High' ? 'bg-emerald-100 text-emerald-700' :
                    geographicData[selectedRegion].applicability === 'High' ? 'bg-green-100 text-green-700' :
                    'bg-amber-100 text-amber-700'
                  }`}>
                    {geographicData[selectedRegion].applicability} Applicability
                  </div>
                </div>
                <div className="grid grid-cols-4 gap-4 mb-3">
                  <div>
                    <div className="text-xs inter text-stone-500">Market Size</div>
                    <div className="text-lg spektral font-bold text-stone-900">{geographicData[selectedRegion].marketSize}</div>
                  </div>
                  <div>
                    <div className="text-xs inter text-stone-500">Submissions</div>
                    <div className="text-lg spektral font-bold text-stone-900">{geographicData[selectedRegion].submissions}</div>
                  </div>
                  <div>
                    <div className="text-xs inter text-stone-500">Growth</div>
                    <div className="text-lg spektral font-bold text-emerald-600">{geographicData[selectedRegion].growth}</div>
                  </div>
                  <div>
                    <div className="text-xs inter text-stone-500">Competition</div>
                    <div className="text-lg spektral font-bold text-stone-900">{geographicData[selectedRegion].competitiveDensity}</div>
                  </div>
                </div>
                <div className="pt-3 border-t border-stone-200">
                  <div className="text-xs inter font-medium text-stone-500 mb-1">OPPORTUNITY ASSESSMENT</div>
                  <p className="text-sm inter text-stone-700">{geographicData[selectedRegion].opportunity}</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-6 fade-in-up stagger-1">
              <div className="bg-white rounded-lg p-6 border border-stone-200">
                <div className="flex items-center gap-3 mb-2">
                  <Users className="w-5 h-5 text-stone-600" />
                  <div className="text-xs inter font-medium text-stone-500">SUBMISSIONS</div>
                </div>
                <div className="text-3xl spektral font-bold text-stone-900">2,847</div>
                <div className="text-sm inter text-emerald-600 mt-1">↑ 34% this month</div>
              </div>
              
              <div className="bg-white rounded-lg p-6 border border-stone-200">
                <div className="flex items-center gap-3 mb-2">
                  <TrendingUp className="w-5 h-5 text-stone-600" />
                  <div className="text-xs inter font-medium text-stone-500">MARKET SIZE</div>
                </div>
                <div className="text-3xl spektral font-bold text-stone-900">$8.4B</div>
                <div className="text-sm inter text-stone-600 mt-1">TAM estimate</div>
              </div>
              
              <div className="bg-white rounded-lg p-6 border border-stone-200">
                <div className="flex items-center gap-3 mb-2">
                  <Target className="w-5 h-5 text-stone-600" />
                  <div className="text-xs inter font-medium text-stone-500">URGENCY</div>
                </div>
                <div className="text-3xl spektral font-bold text-stone-900">High</div>
                <div className="text-sm inter text-stone-600 mt-1">Immediate need</div>
              </div>
            </div>

            <div className="bg-white rounded-lg p-8 border border-stone-200 fade-in-up stagger-2">
              <h2 className="text-xl spektral font-bold text-stone-900 mb-4">Problem Statement</h2>
              <p className="inter text-stone-700 leading-relaxed text-lg">
                Homeowners struggle with reactive, expensive emergency repairs and lack a reliable way to maintain their homes proactively. Finding trustworthy contractors, scheduling multiple services, and managing home maintenance creates significant friction and anxiety.
              </p>
            </div>

            <div className="bg-white rounded-lg p-8 border border-stone-200 fade-in-up stagger-3">
              <h2 className="text-xl spektral font-bold text-stone-900 mb-6">Top Consumer Pain Points</h2>
              <div className="space-y-4">
                {[
                  { quote: "I never know when something's about to break until it's too late and costs thousands", severity: "Critical" },
                  { quote: "Finding reliable contractors is a nightmare - I've been burned too many times", severity: "High" },
                  { quote: "I have no idea what maintenance my home actually needs or when", severity: "High" }
                ].map((pain, idx) => (
                  <div key={idx} className="border-l-4 border-stone-900 pl-4 py-2 slide-in" style={{animationDelay: `${0.4 + idx * 0.1}s`, opacity: 0}}>
                    <div className="flex items-start justify-between gap-4">
                      <p className="inter text-stone-700 italic">"{pain.quote}"</p>
                      <span className="text-xs inter font-medium text-stone-500 whitespace-nowrap">{pain.severity}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-lg p-8 border border-stone-200 fade-in-up stagger-4">
              <h2 className="text-xl spektral font-bold text-stone-900 mb-4">Related Opportunities</h2>
              <div className="space-y-3">
                {[
                  "Home Warranty Alternatives",
                  "Preventive HVAC Monitoring",
                  "Property Management for Owners"
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 bg-stone-50 rounded hover:bg-stone-100 transition-colors cursor-pointer">
                    <span className="inter text-stone-700">{item}</span>
                    <ChevronRight className="w-4 h-4 text-stone-400" />
                  </div>
                ))}
              </div>
            </div>

            {/* Upgrade CTA */}
            <div className="bg-gradient-to-br from-stone-900 to-stone-700 rounded-lg p-8 text-white fade-in-up stagger-5">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl spektral font-bold mb-2">Unlock Full Research Dashboard</h3>
                  <p className="inter text-stone-200">Get detailed market analysis, user demographics, competitive landscape, and opportunity sizing</p>
                </div>
                <button
                  onClick={() => setCurrentTier('research')}
                  className="bg-white text-stone-900 px-6 py-3 rounded-lg inter font-medium flex items-center gap-2 hover:bg-stone-100 transition-colors whitespace-nowrap"
                >
                  See Full Research
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TIER 2: RESEARCH DASHBOARD */}
        {currentTier === 'research' && (
          <div className="space-y-8">
            {/* Tab Navigation */}
            <div className="bg-white rounded-lg border border-stone-200 fade-in-up">
              <div className="flex border-b border-stone-200 inter">
                {[
                  { id: 'market', label: 'Market Validation', icon: TrendingUp },
                  { id: 'geography', label: 'Geographic Distribution', icon: MapPin },
                  { id: 'problem', label: 'Problem Analysis', icon: Map },
                  { id: 'opportunity', label: 'Opportunity Sizing', icon: DollarSign },
                  { id: 'solution', label: 'Solution Pathways', icon: Target }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex-1 py-4 text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
                      activeTab === tab.id
                        ? 'text-stone-900 border-b-2 border-stone-900'
                        : 'text-stone-500 hover:text-stone-700'
                    }`}
                  >
                    <tab.icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                ))}
              </div>

              <div className="p-8">
                {activeTab === 'market' && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-2 gap-6 fade-in-up stagger-1">
                      <div>
                        <h3 className="text-sm inter font-medium text-stone-500 mb-3">DEMAND SIGNALS</h3>
                        <div className="space-y-3">
                          <div className="flex justify-between items-center">
                            <span className="inter text-stone-700">Search Volume (monthly)</span>
                            <span className="spektral font-bold text-stone-900">127K</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="inter text-stone-700">YoY Growth</span>
                            <span className="spektral font-bold text-emerald-600">+43%</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="inter text-stone-700">Social Mentions</span>
                            <span className="spektral font-bold text-stone-900">89K/mo</span>
                          </div>
                        </div>
                      </div>
                      
                      <div>
                        <h3 className="text-sm inter font-medium text-stone-500 mb-3">DEMOGRAPHICS</h3>
                        <div className="space-y-3">
                          <div className="flex justify-between items-center">
                            <span className="inter text-stone-700">Primary Age Range</span>
                            <span className="spektral font-bold text-stone-900">35-54</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="inter text-stone-700">Income Level</span>
                            <span className="spektral font-bold text-stone-900">$75K-150K</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="inter text-stone-700">Home Ownership</span>
                            <span className="spektral font-bold text-stone-900">87%</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="border-t border-stone-200 pt-6 fade-in-up stagger-2">
                      <h3 className="text-sm inter font-medium text-stone-500 mb-4">COMPETITIVE LANDSCAPE</h3>
                      <div className="space-y-3">
                        {[
                          { name: "American Home Shield", share: "23%", weakness: "Poor service quality" },
                          { name: "HomeAdvisor", share: "18%", weakness: "Lead generation only" },
                          { name: "Thumbtack", share: "12%", weakness: "No ongoing relationship" }
                        ].map((comp, idx) => (
                          <div key={idx} className="p-4 bg-stone-50 rounded">
                            <div className="flex justify-between items-start mb-2">
                              <span className="inter font-medium text-stone-900">{comp.name}</span>
                              <span className="text-xs inter font-medium text-stone-500">{comp.share} market share</span>
                            </div>
                            <p className="text-sm inter text-stone-600">Key weakness: {comp.weakness}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'geography' && (
                  <div className="space-y-6">
                    <div className="fade-in-up stagger-1">
                      <h3 className="text-sm inter font-medium text-stone-500 mb-4">MARKET APPLICABILITY BY REGION</h3>
                      <div className="space-y-3">
                        {Object.entries(geographicData).map(([key, data]) => (
                          <div 
                            key={key}
                            className={`p-5 rounded-lg border-2 transition-all cursor-pointer ${
                              selectedRegion === key
                                ? 'border-stone-900 bg-stone-50'
                                : 'border-stone-200 hover:border-stone-300'
                            }`}
                            onClick={() => setSelectedRegion(key)}
                          >
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                  <h4 className="inter font-semibold text-stone-900">{data.label}</h4>
                                  <div className={`px-2 py-1 rounded text-xs inter font-medium ${
                                    data.applicability === 'Very High' ? 'bg-emerald-100 text-emerald-700' :
                                    data.applicability === 'High' ? 'bg-green-100 text-green-700' :
                                    'bg-amber-100 text-amber-700'
                                  }`}>
                                    {data.applicability}
                                  </div>
                                </div>
                              </div>
                              <div className="text-right">
                                <div className="text-xs inter text-stone-500">Market Size</div>
                                <div className="spektral font-bold text-xl text-stone-900">{data.marketSize}</div>
                              </div>
                            </div>
                            
                            <div className="grid grid-cols-3 gap-4 mb-3">
                              <div>
                                <div className="text-xs inter text-stone-500">Submissions</div>
                                <div className="text-sm spektral font-bold text-stone-900">{data.submissions}</div>
                              </div>
                              <div>
                                <div className="text-xs inter text-stone-500">Growth Rate</div>
                                <div className="text-sm spektral font-bold text-emerald-600">{data.growth}</div>
                              </div>
                              <div>
                                <div className="text-xs inter text-stone-500">Competition</div>
                                <div className="text-sm spektral font-bold text-stone-900">{data.competitiveDensity}</div>
                              </div>
                            </div>

                            {key !== 'global' && (
                              <div className="pt-3 border-t border-stone-200">
                                <div className="text-xs inter font-medium text-stone-500 mb-2">TOP MARKETS</div>
                                <div className="flex flex-wrap gap-2">
                                  {data.topCities.map((city, idx) => (
                                    <span key={idx} className="px-2 py-1 bg-stone-100 rounded text-xs inter text-stone-700">
                                      {city}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="fade-in-up stagger-2 bg-blue-50 border border-blue-200 rounded-lg p-6">
                      <h3 className="text-sm inter font-medium text-blue-900 mb-3">🎯 RECOMMENDED LAUNCH STRATEGY</h3>
                      <div className="space-y-3">
                        <div className="bg-white rounded p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <div className="w-6 h-6 bg-emerald-500 rounded-full text-white text-xs flex items-center justify-center font-bold">1</div>
                            <span className="inter font-semibold text-stone-900">Phase 1: Southwest US Launch</span>
                          </div>
                          <p className="text-sm inter text-stone-700 pl-8">Highest growth (+52%), favorable regulations, medium competition. Start Austin → Phoenix.</p>
                        </div>
                        <div className="bg-white rounded p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <div className="w-6 h-6 bg-blue-500 rounded-full text-white text-xs flex items-center justify-center font-bold">2</div>
                            <span className="inter font-semibold text-stone-900">Phase 2: National Expansion</span>
                          </div>
                          <p className="text-sm inter text-stone-700 pl-8">Expand to top 20 metro areas. Address state licensing complexity.</p>
                        </div>
                        <div className="bg-white rounded p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <div className="w-6 h-6 bg-purple-500 rounded-full text-white text-xs flex items-center justify-center font-bold">3</div>
                            <span className="inter font-semibold text-stone-900">Phase 3: International (Canada/Australia)</span>
                          </div>
                          <p className="text-sm inter text-stone-700 pl-8">After US market leadership established. Similar demographics, lower competition.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'problem' && (
                  <div className="space-y-6">
                    <div className="fade-in-up stagger-1">
                      <h3 className="text-sm inter font-medium text-stone-500 mb-4">PAIN POINT CATEGORIZATION</h3>
                      <div className="space-y-4">
                        {[
                          { category: "Trust & Reliability", count: 847, severity: 9.2, top: "Can't find trustworthy contractors" },
                          { category: "Cost Predictability", count: 623, severity: 8.8, top: "Emergency repairs are financially devastating" },
                          { category: "Knowledge Gap", count: 512, severity: 7.9, top: "Don't know what maintenance is needed" },
                          { category: "Time & Convenience", count: 421, severity: 7.4, top: "Coordinating multiple services is exhausting" }
                        ].map((pain, idx) => (
                          <div key={idx} className="border border-stone-200 rounded-lg p-4">
                            <div className="flex justify-between items-start mb-2">
                              <div>
                                <h4 className="inter font-medium text-stone-900">{pain.category}</h4>
                                <p className="text-sm inter text-stone-600 mt-1">{pain.top}</p>
                              </div>
                              <div className="text-right">
                                <div className="text-xs inter text-stone-500">Severity</div>
                                <div className="spektral font-bold text-lg text-stone-900">{pain.severity}/10</div>
                              </div>
                            </div>
                            <div className="text-xs inter text-stone-500">{pain.count} mentions</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'opportunity' && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-3 gap-4 fade-in-up stagger-1">
                      <div className="bg-stone-50 rounded-lg p-6">
                        <div className="text-xs inter font-medium text-stone-500 mb-2">TAM</div>
                        <div className="spektral font-bold text-3xl text-stone-900">$8.4B</div>
                        <div className="text-sm inter text-stone-600 mt-1">Total addressable</div>
                      </div>
                      <div className="bg-stone-50 rounded-lg p-6">
                        <div className="text-xs inter font-medium text-stone-500 mb-2">SAM</div>
                        <div className="spektral font-bold text-3xl text-stone-900">$2.1B</div>
                        <div className="text-sm inter text-stone-600 mt-1">Serviceable available</div>
                      </div>
                      <div className="bg-stone-50 rounded-lg p-6">
                        <div className="text-xs inter font-medium text-stone-500 mb-2">SOM</div>
                        <div className="spektral font-bold text-3xl text-stone-900">$187M</div>
                        <div className="text-sm inter text-stone-600 mt-1">5-year target</div>
                      </div>
                    </div>

                    <div className="fade-in-up stagger-2">
                      <h3 className="text-sm inter font-medium text-stone-500 mb-4">WILLINGNESS TO PAY</h3>
                      <div className="space-y-3">
                        {[
                          { tier: "Basic Plan", price: "$49/mo", adoption: "67% would subscribe" },
                          { tier: "Premium Plan", price: "$99/mo", adoption: "34% would subscribe" },
                          { tier: "Comprehensive", price: "$149/mo", adoption: "18% would subscribe" }
                        ].map((tier, idx) => (
                          <div key={idx} className="flex items-center justify-between p-4 border border-stone-200 rounded">
                            <div>
                              <div className="inter font-medium text-stone-900">{tier.tier}</div>
                              <div className="text-sm inter text-stone-600">{tier.adoption}</div>
                            </div>
                            <div className="spektral font-bold text-xl text-stone-900">{tier.price}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'solution' && (
                  <div className="space-y-6">
                    <div className="fade-in-up stagger-1">
                      <h3 className="text-sm inter font-medium text-stone-500 mb-4">DESIRED SOLUTION FEATURES</h3>
                      <div className="space-y-3">
                        {[
                          { feature: "Vetted contractor network", priority: 1, mentions: 1247 },
                          { feature: "Preventive maintenance scheduling", priority: 2, mentions: 1089 },
                          { feature: "Fixed pricing guarantee", priority: 3, mentions: 923 },
                          { feature: "24/7 emergency support", priority: 4, mentions: 876 },
                          { feature: "Home systems monitoring", priority: 5, mentions: 734 }
                        ].map((feature, idx) => (
                          <div key={idx} className="flex items-center justify-between p-4 bg-stone-50 rounded">
                            <div className="flex items-center gap-4">
                              <div className="w-8 h-8 rounded-full bg-stone-900 text-white flex items-center justify-center spektral font-bold">
                                {feature.priority}
                              </div>
                              <div>
                                <div className="inter font-medium text-stone-900">{feature.feature}</div>
                                <div className="text-sm inter text-stone-600">{feature.mentions} user mentions</div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Upgrade to Deep Dive CTA */}
            <div className="bg-gradient-to-br from-stone-900 to-stone-700 rounded-lg p-8 text-white fade-in-up stagger-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl spektral font-bold mb-2">Unlock Deep Dive Analysis</h3>
                  <p className="inter text-stone-200">Get actionable execution playbook, financial models, full competitive intelligence, and product roadmap</p>
                </div>
                <button
                  onClick={() => setCurrentTier('deep')}
                  className="bg-white text-stone-900 px-6 py-3 rounded-lg inter font-medium flex items-center gap-2 hover:bg-stone-100 transition-colors whitespace-nowrap"
                >
                  Deep Dive
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TIER 3: DEEP DIVE */}
        {currentTier === 'deep' && (
          <div className="space-y-8">
            {/* AI Assistant Floating Button */}
            {!aiChatOpen && (
              <button
                onClick={() => setAiChatOpen(true)}
                className="fixed bottom-8 right-8 bg-gradient-to-br from-violet-600 to-purple-700 text-white px-6 py-4 rounded-full shadow-2xl hover:shadow-violet-500/50 transition-all duration-300 flex items-center gap-3 inter font-medium z-50 fade-in-up group hover:scale-105"
              >
                <Sparkles className="w-5 h-5 group-hover:rotate-12 transition-transform" />
                Ask AI Assistant
              </button>
            )}

            {/* AI Chat Panel */}
            {aiChatOpen && (
              <div className="fixed bottom-8 right-8 w-[480px] h-[600px] bg-white rounded-2xl shadow-2xl border border-stone-200 flex flex-col z-50 fade-in-up">
                {/* Chat Header */}
                <div className="bg-gradient-to-br from-violet-600 to-purple-700 text-white p-6 rounded-t-2xl">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center backdrop-blur">
                        <Sparkles className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="spektral font-bold text-lg">AI Research Assistant</h3>
                        <p className="text-xs text-white/80 inter">Powered by deep analysis of 2,847 data points</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setAiChatOpen(false)}
                      className="text-white/60 hover:text-white transition-colors text-2xl leading-none"
                    >
                      ×
                    </button>
                  </div>
                </div>

                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-stone-50">
                  {messages.map((msg, idx) => (
                    <div key={idx}>
                      {msg.type === 'ai' && (
                        <div className="flex gap-3 slide-in">
                          <div className="w-8 h-8 bg-gradient-to-br from-violet-600 to-purple-700 rounded-full flex items-center justify-center flex-shrink-0">
                            <Sparkles className="w-4 h-4 text-white" />
                          </div>
                          <div className="flex-1 bg-white rounded-2xl rounded-tl-none p-4 shadow-sm border border-stone-200">
                            <p className="inter text-stone-800 text-sm leading-relaxed whitespace-pre-line">{msg.text}</p>
                          </div>
                        </div>
                      )}
                      
                      {msg.type === 'user' && (
                        <div className="flex gap-3 justify-end slide-in">
                          <div className="bg-gradient-to-br from-violet-600 to-purple-700 text-white rounded-2xl rounded-tr-none p-4 shadow-sm max-w-[80%]">
                            <p className="inter text-sm">{msg.text}</p>
                          </div>
                        </div>
                      )}
                      
                      {msg.type === 'suggestions' && (
                        <div className="flex gap-3 slide-in">
                          <div className="w-8 h-8 flex-shrink-0" />
                          <div className="flex-1 space-y-2">
                            {msg.options.map((option, i) => (
                              <button
                                key={i}
                                onClick={() => handleSendMessage(option)}
                                className="block w-full text-left bg-white hover:bg-violet-50 border border-stone-200 hover:border-violet-300 rounded-lg p-3 inter text-sm text-stone-700 hover:text-violet-700 transition-all"
                              >
                                {option}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Input Area */}
                <div className="p-4 border-t border-stone-200 bg-white rounded-b-2xl">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(chatInput)}
                      placeholder="Ask me anything about this opportunity..."
                      className="flex-1 px-4 py-3 border border-stone-200 rounded-lg inter text-sm focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100"
                    />
                    <button
                      onClick={() => handleSendMessage(chatInput)}
                      className="bg-gradient-to-br from-violet-600 to-purple-700 text-white p-3 rounded-lg hover:shadow-lg transition-all"
                    >
                      <Send className="w-5 h-5" />
                    </button>
                  </div>
                  <p className="text-xs inter text-stone-500 mt-2">AI can analyze data, suggest strategies, and answer questions</p>
                </div>
              </div>
            )}

            {/* Executive Summary */}
            <div className="bg-white rounded-lg p-8 border border-stone-200 fade-in-up stagger-1">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-2xl spektral font-bold text-stone-900 mb-2">Executive Summary</h2>
                  <p className="inter text-stone-600">Comprehensive analysis and investment thesis</p>
                </div>
                <FileText className="w-6 h-6 text-stone-400" />
              </div>
              
              {/* AI Assistant Teaser */}
              <div className="mb-6 bg-gradient-to-br from-violet-50 to-purple-50 border border-violet-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-violet-600 to-purple-700 rounded-full flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="inter font-semibold text-stone-900 mb-1">AI Research Assistant Available</h3>
                    <p className="inter text-sm text-stone-700 mb-3">
                      Get instant answers, strategic recommendations, and custom analysis. Click the AI Assistant button to explore this opportunity interactively.
                    </p>
                    <button
                      onClick={() => setAiChatOpen(true)}
                      className="bg-gradient-to-br from-violet-600 to-purple-700 text-white px-4 py-2 rounded-lg inter text-sm font-medium hover:shadow-lg transition-all flex items-center gap-2"
                    >
                      <MessageSquare className="w-4 h-4" />
                      Start Conversation
                    </button>
                  </div>
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h3 className="inter font-semibold text-stone-900 mb-2">Investment Thesis</h3>
                  <p className="inter text-stone-700 leading-relaxed">
                    The home maintenance market represents a $8.4B opportunity with clear pain points around trust, predictability, and convenience. A subscription-based preventive model can capture significant market share by solving the reactive, expensive nature of current solutions while building recurring revenue through trusted contractor networks.
                  </p>
                </div>
                
                <div className="grid grid-cols-2 gap-6 pt-4">
                  <div>
                    <h3 className="inter font-semibold text-stone-900 mb-3">Key Opportunities</h3>
                    <ul className="space-y-2 inter text-stone-700">
                      <li className="flex items-start gap-2">
                        <span className="text-emerald-600 mt-1">●</span>
                        <span>Market growing 43% YoY with increasing homeownership among millennials</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-emerald-600 mt-1">●</span>
                        <span>Existing solutions focus on reactive repairs, not prevention</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-emerald-600 mt-1">●</span>
                        <span>High willingness to pay for peace of mind and fixed costs</span>
                      </li>
                    </ul>
                  </div>
                  
                  <div>
                    <h3 className="inter font-semibold text-stone-900 mb-3">Key Risks & Mitigations</h3>
                    <ul className="space-y-2 inter text-stone-700">
                      <li className="flex items-start gap-2">
                        <span className="text-amber-600 mt-1">●</span>
                        <span>Contractor quality control → Rigorous vetting + quality scoring system</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-amber-600 mt-1">●</span>
                        <span>Unit economics at scale → Start with high-value metro areas</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-amber-600 mt-1">●</span>
                        <span>Customer acquisition cost → Referral program + content marketing</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            {/* Section Grid */}
            <div className="grid grid-cols-2 gap-6">
              {/* Geographic Market Intelligence */}
              <div className="bg-white rounded-lg p-6 border border-stone-200 fade-in-up stagger-2">
                <div className="flex items-center gap-2 mb-4">
                  <MapPin className="w-5 h-5 text-stone-600" />
                  <h2 className="text-lg spektral font-bold text-stone-900">Geographic Market Intelligence</h2>
                </div>
                <div className="space-y-3 text-sm">
                  <div className="bg-emerald-50 border border-emerald-200 rounded p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                      <span className="inter font-semibold text-emerald-900">Priority 1: Southwest US</span>
                    </div>
                    <p className="text-xs inter text-emerald-800 pl-4">$1.2B market, +52% growth, business-friendly regulations</p>
                  </div>
                  <div className="bg-blue-50 border border-blue-200 rounded p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <span className="inter font-semibold text-blue-900">Priority 2: National Expansion</span>
                    </div>
                    <p className="text-xs inter text-blue-800 pl-4">Top 20 metros, state-by-state playbook included</p>
                  </div>
                  <div className="bg-purple-50 border border-purple-200 rounded p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                      <span className="inter font-semibold text-purple-900">Priority 3: International</span>
                    </div>
                    <p className="text-xs inter text-purple-800 pl-4">Canada & Australia - $3.5B combined opportunity</p>
                  </div>
                  <div className="pt-2 border-t border-stone-200">
                    <div className="flex justify-between items-center pb-2">
                      <span className="inter text-stone-700">Market Entry Playbooks</span>
                      <ChevronRight className="w-4 h-4 text-stone-400" />
                    </div>
                    <div className="flex justify-between items-center pb-2">
                      <span className="inter text-stone-700">Regulatory Compliance Guides</span>
                      <ChevronRight className="w-4 h-4 text-stone-400" />
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="inter text-stone-700">Regional Pricing Analysis</span>
                      <ChevronRight className="w-4 h-4 text-stone-400" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Detailed Market Intelligence */}
              <div className="bg-white rounded-lg p-6 border border-stone-200 fade-in-up stagger-2">
                <h2 className="text-lg spektral font-bold text-stone-900 mb-4">Detailed Market Intelligence</h2>
                <div className="space-y-3 text-sm inter text-stone-700">
                  <div className="flex justify-between items-center pb-2 border-b border-stone-100">
                    <span>Full Competitive Analysis</span>
                    <ChevronRight className="w-4 h-4 text-stone-400" />
                  </div>
                  <div className="flex justify-between items-center pb-2 border-b border-stone-100">
                    <span>Customer Segmentation Models</span>
                    <ChevronRight className="w-4 h-4 text-stone-400" />
                  </div>
                  <div className="flex justify-between items-center pb-2 border-b border-stone-100">
                    <span>Pricing Strategy Recommendations</span>
                    <ChevronRight className="w-4 h-4 text-stone-400" />
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Distribution Channel Analysis</span>
                    <ChevronRight className="w-4 h-4 text-stone-400" />
                  </div>
                </div>
              </div>

              {/* Product Strategy */}
              <div className="bg-white rounded-lg p-6 border border-stone-200 fade-in-up stagger-2">
                <h2 className="text-lg spektral font-bold text-stone-900 mb-4">Product Strategy</h2>
                <div className="space-y-3 text-sm inter text-stone-700">
                  <div className="flex justify-between items-center pb-2 border-b border-stone-100">
                    <span>Detailed Feature Roadmap</span>
                    <ChevronRight className="w-4 h-4 text-stone-400" />
                  </div>
                  <div className="flex justify-between items-center pb-2 border-b border-stone-100">
                    <span>MVP Scope Definition</span>
                    <ChevronRight className="w-4 h-4 text-stone-400" />
                  </div>
                  <div className="flex justify-between items-center pb-2 border-b border-stone-100">
                    <span>User Stories & Acceptance Criteria</span>
                    <ChevronRight className="w-4 h-4 text-stone-400" />
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Technical Architecture</span>
                    <ChevronRight className="w-4 h-4 text-stone-400" />
                  </div>
                </div>
              </div>

              {/* Financial Modeling */}
              <div className="bg-white rounded-lg p-6 border border-stone-200 fade-in-up stagger-3">
                <h2 className="text-lg spektral font-bold text-stone-900 mb-4">Financial Modeling</h2>
                <div className="space-y-4">
                  <div>
                    <div className="text-xs inter text-stone-500 mb-1">5-Year Revenue Projection</div>
                    <div className="spektral font-bold text-2xl text-stone-900">$47M → $312M</div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="inter text-stone-600">CAC</div>
                      <div className="spektral font-bold text-stone-900">$127</div>
                    </div>
                    <div>
                      <div className="inter text-stone-600">LTV</div>
                      <div className="spektral font-bold text-stone-900">$2,340</div>
                    </div>
                    <div>
                      <div className="inter text-stone-600">LTV:CAC</div>
                      <div className="spektral font-bold text-emerald-600">18.4x</div>
                    </div>
                    <div>
                      <div className="inter text-stone-600">Payback</div>
                      <div className="spektral font-bold text-stone-900">3.2mo</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Execution Playbook */}
              <div className="bg-white rounded-lg p-6 border border-stone-200 fade-in-up stagger-3">
                <h2 className="text-lg spektral font-bold text-stone-900 mb-4">Execution Playbook</h2>
                <div className="space-y-3">
                  <div className="bg-stone-50 rounded p-3">
                    <div className="text-xs inter font-medium text-stone-500 mb-1">PHASE 1: Days 1-30</div>
                    <div className="text-sm inter text-stone-900">Build MVP, recruit 10 vetted contractors, launch beta in Austin</div>
                  </div>
                  <div className="bg-stone-50 rounded p-3">
                    <div className="text-xs inter font-medium text-stone-500 mb-1">PHASE 2: Days 31-60</div>
                    <div className="text-sm inter text-stone-900">Acquire 100 customers, refine product-market fit, optimize unit economics</div>
                  </div>
                  <div className="bg-stone-50 rounded p-3">
                    <div className="text-xs inter font-medium text-stone-500 mb-1">PHASE 3: Days 61-90</div>
                    <div className="text-sm inter text-stone-900">Scale to 500 customers, expand contractor network, prepare Series A</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Raw Data Access */}
            <div className="bg-white rounded-lg p-8 border border-stone-200 fade-in-up stagger-4">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-2xl spektral font-bold text-stone-900 mb-2">Raw Data & Exports</h2>
                  <p className="inter text-stone-600">Full consumer verbatims, statistical analysis, and export options</p>
                </div>
                <BarChart3 className="w-6 h-6 text-stone-400" />
              </div>
              
              <div className="grid grid-cols-4 gap-4">
                <button className="p-4 border border-stone-200 rounded hover:bg-stone-50 transition-colors">
                  <div className="text-sm inter font-medium text-stone-900 mb-1">Full Dataset</div>
                  <div className="text-xs inter text-stone-500">2,847 verbatims</div>
                </button>
                <button className="p-4 border border-stone-200 rounded hover:bg-stone-50 transition-colors">
                  <div className="text-sm inter font-medium text-stone-900 mb-1">Export PDF</div>
                  <div className="text-xs inter text-stone-500">Complete report</div>
                </button>
                <button className="p-4 border border-stone-200 rounded hover:bg-stone-50 transition-colors">
                  <div className="text-sm inter font-medium text-stone-900 mb-1">Export CSV</div>
                  <div className="text-xs inter text-stone-500">Raw data</div>
                </button>
                <button className="p-4 border border-stone-200 rounded hover:bg-stone-50 transition-colors">
                  <div className="text-sm inter font-medium text-stone-900 mb-1">API Access</div>
                  <div className="text-xs inter text-stone-500">Real-time data</div>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
