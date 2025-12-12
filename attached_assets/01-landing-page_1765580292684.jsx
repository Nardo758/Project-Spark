import React, { useState } from 'react';
import { Search, TrendingUp, Users, Sparkles, ArrowRight, CheckCircle, BarChart3, Globe, Zap, Target, Shield } from 'lucide-react';

export default function LandingPage() {
  const [email, setEmail] = useState('');

  return (
    <div className="min-h-screen bg-stone-50">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Spectral:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
        
        .spektral { font-family: 'Spectral', serif; }
        .inter { font-family: 'Inter', sans-serif; }
        
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-20px);
          }
        }
        
        .fade-in-up {
          animation: fadeInUp 0.8s ease-out forwards;
        }
        
        .float {
          animation: float 6s ease-in-out infinite;
        }
        
        .stagger-1 { animation-delay: 0.1s; opacity: 0; }
        .stagger-2 { animation-delay: 0.2s; opacity: 0; }
        .stagger-3 { animation-delay: 0.3s; opacity: 0; }
        .stagger-4 { animation-delay: 0.4s; opacity: 0; }
        .stagger-5 { animation-delay: 0.5s; opacity: 0; }
      `}</style>

      {/* Navigation */}
      <nav className="bg-white border-b border-stone-200">
        <div className="max-w-7xl mx-auto px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-stone-900 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-2xl spektral font-bold text-stone-900">Katalyst</span>
            </div>
            <div className="flex items-center gap-8">
              <a href="#how-it-works" className="inter text-sm text-stone-600 hover:text-stone-900 transition-colors">How It Works</a>
              <a href="#pricing" className="inter text-sm text-stone-600 hover:text-stone-900 transition-colors">Pricing</a>
              <a href="#browse-opportunities" className="inter text-sm text-stone-600 hover:text-stone-900 transition-colors">Browse Ideas</a>
              <button className="inter text-sm font-medium text-stone-600 hover:text-stone-900 transition-colors">Sign In</button>
              <button className="bg-stone-900 text-white px-4 py-2 rounded-lg inter text-sm font-medium hover:bg-stone-800 transition-colors">
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-stone-50 via-stone-100 to-stone-50">
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-20 left-20 w-72 h-72 bg-violet-200 rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-emerald-200 rounded-full blur-3xl"></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-8 py-24">
          <div className="grid grid-cols-2 gap-16 items-center">
            <div>
              <div className="inline-block bg-violet-100 text-violet-700 px-4 py-2 rounded-full text-sm inter font-medium mb-6 fade-in-up">
                2,847+ Validated Opportunities
              </div>
              <h1 className="text-6xl spektral font-bold text-stone-900 mb-6 leading-tight fade-in-up stagger-1">
                Transform Consumer Problems into 
                <span className="text-violet-600"> Business Opportunities</span>
              </h1>
              <p className="text-xl inter text-stone-600 mb-8 leading-relaxed fade-in-up stagger-2">
                Discover validated market opportunities backed by real consumer insights. From idea validation to execution playbooks, everything you need to build what people actually want.
              </p>
              <div className="flex items-center gap-4 fade-in-up stagger-3">
                <a 
                  href="/discover"
                  className="bg-stone-900 text-white px-8 py-4 rounded-lg inter font-medium text-lg hover:bg-stone-800 transition-all hover:shadow-xl flex items-center gap-2"
                >
                  Browse Opportunities
                  <ArrowRight className="w-5 h-5" />
                </a>
                <button className="border-2 border-stone-900 text-stone-900 px-8 py-4 rounded-lg inter font-medium text-lg hover:bg-stone-900 hover:text-white transition-all">
                  Watch Demo
                </button>
              </div>
              
              {/* Social Proof */}
              <div className="flex items-center gap-8 mt-12 fade-in-up stagger-4">
                <div>
                  <div className="text-3xl spektral font-bold text-stone-900">2,847</div>
                  <div className="text-sm inter text-stone-600">Validated Ideas</div>
                </div>
                <div className="w-px h-12 bg-stone-300"></div>
                <div>
                  <div className="text-3xl spektral font-bold text-stone-900">$47B+</div>
                  <div className="text-sm inter text-stone-600">Market Opportunity</div>
                </div>
                <div className="w-px h-12 bg-stone-300"></div>
                <div>
                  <div className="text-3xl spektral font-bold text-stone-900">6</div>
                  <div className="text-sm inter text-stone-600">Global Markets</div>
                </div>
              </div>
            </div>

            {/* Hero Visual */}
            <div className="fade-in-up stagger-2">
              <div className="relative">
                <div className="bg-white rounded-2xl shadow-2xl border border-stone-200 p-8">
                  <div className="flex items-start justify-between mb-6">
                    <div>
                      <div className="text-xs inter font-medium text-stone-500 mb-2">TRENDING OPPORTUNITY</div>
                      <h3 className="text-2xl spektral font-bold text-stone-900 mb-2">
                        On-Demand Home Maintenance
                      </h3>
                      <p className="text-sm inter text-stone-600">Subscription-based preventive care for homeowners</p>
                    </div>
                    <div className="bg-emerald-100 text-emerald-700 px-4 py-2 rounded-full">
                      <div className="text-2xl spektral font-bold">87</div>
                      <div className="text-xs inter">Score</div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="bg-stone-50 rounded-lg p-3">
                      <div className="text-xs inter text-stone-500 mb-1">Market Size</div>
                      <div className="text-lg spektral font-bold text-stone-900">$8.4B</div>
                    </div>
                    <div className="bg-stone-50 rounded-lg p-3">
                      <div className="text-xs inter text-stone-500 mb-1">Submissions</div>
                      <div className="text-lg spektral font-bold text-stone-900">2,847</div>
                    </div>
                    <div className="bg-stone-50 rounded-lg p-3">
                      <div className="text-xs inter text-stone-500 mb-1">Growth</div>
                      <div className="text-lg spektral font-bold text-emerald-600">+34%</div>
                    </div>
                  </div>
                  
                  <button className="w-full bg-gradient-to-r from-violet-600 to-purple-600 text-white py-3 rounded-lg inter font-medium hover:shadow-lg transition-all">
                    View Full Analysis →
                  </button>
                </div>
                
                {/* Floating elements */}
                <div className="absolute -top-6 -right-6 bg-white rounded-xl shadow-lg border border-stone-200 p-4 float" style={{animationDelay: '0s'}}>
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-violet-600" />
                    <span className="text-sm inter font-medium text-stone-900">2,847 users want this</span>
                  </div>
                </div>
                
                <div className="absolute -bottom-6 -left-6 bg-white rounded-xl shadow-lg border border-stone-200 p-4 float" style={{animationDelay: '1s'}}>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-emerald-600" />
                    <span className="text-sm inter font-medium text-stone-900">+34% monthly growth</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-8">
          <div className="text-center mb-16">
            <h2 className="text-5xl spektral font-bold text-stone-900 mb-4">
              From Problem to Execution in Three Steps
            </h2>
            <p className="text-xl inter text-stone-600 max-w-2xl mx-auto">
              Progressive depth gives you exactly what you need, when you need it
            </p>
          </div>

          <div className="grid grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="relative fade-in-up stagger-1">
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-8 border-2 border-green-200 h-full">
                <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mb-6">
                  <span className="text-3xl spektral font-bold text-white">1</span>
                </div>
                <h3 className="text-2xl spektral font-bold text-stone-900 mb-4">
                  Discover & Validate
                </h3>
                <p className="inter text-stone-700 mb-6">
                  Browse validated opportunities with quick validation metrics. See submissions, market size, and urgency at a glance.
                </p>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span className="text-sm inter text-stone-700">Validation scores (0-100)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span className="text-sm inter text-stone-700">Top consumer pain points</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span className="text-sm inter text-stone-700">Market size estimates</span>
                  </div>
                </div>
                <div className="mt-6 pt-6 border-t border-green-200">
                  <div className="text-xs inter font-medium text-green-700 mb-1">ACCESS TIER</div>
                  <div className="text-lg spektral font-bold text-stone-900">Free</div>
                </div>
              </div>
            </div>

            {/* Step 2 */}
            <div className="relative fade-in-up stagger-2">
              <div className="bg-gradient-to-br from-purple-50 to-violet-50 rounded-2xl p-8 border-2 border-purple-200 h-full">
                <div className="w-16 h-16 bg-purple-500 rounded-full flex items-center justify-center mb-6">
                  <span className="text-3xl spektral font-bold text-white">2</span>
                </div>
                <h3 className="text-2xl spektral font-bold text-stone-900 mb-4">
                  Research & Analyze
                </h3>
                <p className="inter text-stone-700 mb-6">
                  Deep dive into market validation, demographics, competition, and opportunity sizing across multiple dimensions.
                </p>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-purple-600" />
                    <span className="text-sm inter text-stone-700">Full competitive analysis</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-purple-600" />
                    <span className="text-sm inter text-stone-700">Geographic market intelligence</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-purple-600" />
                    <span className="text-sm inter text-stone-700">TAM/SAM/SOM estimates</span>
                  </div>
                </div>
                <div className="mt-6 pt-6 border-t border-purple-200">
                  <div className="text-xs inter font-medium text-purple-700 mb-1">ACCESS TIER</div>
                  <div className="text-lg spektral font-bold text-stone-900">Pro ($99/mo)</div>
                </div>
              </div>
            </div>

            {/* Step 3 */}
            <div className="relative fade-in-up stagger-3">
              <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-2xl p-8 border-2 border-indigo-200 h-full">
                <div className="w-16 h-16 bg-gradient-to-br from-violet-600 to-indigo-600 rounded-full flex items-center justify-center mb-6">
                  <Sparkles className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl spektral font-bold text-stone-900 mb-4">
                  Execute with AI
                </h3>
                <p className="inter text-stone-700 mb-6">
                  Get actionable execution playbooks, financial models, and an AI assistant to guide your strategy decisions.
                </p>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-indigo-600" />
                    <span className="text-sm inter text-stone-700">90-day execution playbook</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-indigo-600" />
                    <span className="text-sm inter text-stone-700">AI research assistant</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-indigo-600" />
                    <span className="text-sm inter text-stone-700">Financial modeling & exports</span>
                  </div>
                </div>
                <div className="mt-6 pt-6 border-t border-indigo-200">
                  <div className="text-xs inter font-medium text-indigo-700 mb-1">ACCESS TIER</div>
                  <div className="text-lg spektral font-bold text-stone-900">Business ($499/mo)</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Value Props */}
      <section className="py-24 bg-stone-50">
        <div className="max-w-7xl mx-auto px-8">
          <div className="grid grid-cols-2 gap-16 items-center mb-24">
            <div>
              <div className="w-12 h-12 bg-violet-100 rounded-lg flex items-center justify-center mb-6">
                <Target className="w-6 h-6 text-violet-600" />
              </div>
              <h2 className="text-4xl spektral font-bold text-stone-900 mb-6">
                Validated Consumer Insights, Not Scrapes
              </h2>
              <p className="text-lg inter text-stone-600 mb-6">
                Every opportunity is backed by real consumer submissions, not algorithmic guesses. We curate and verify insights so you get signal, not noise.
              </p>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-emerald-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <CheckCircle className="w-4 h-4 text-emerald-600" />
                  </div>
                  <div>
                    <div className="inter font-semibold text-stone-900 mb-1">Human-Verified Problems</div>
                    <p className="text-sm inter text-stone-600">Real people sharing real frustrations, not bot-generated content</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-emerald-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <CheckCircle className="w-4 h-4 text-emerald-600" />
                  </div>
                  <div>
                    <div className="inter font-semibold text-stone-900 mb-1">Clustered by Intelligence</div>
                    <p className="text-sm inter text-stone-600">AI groups similar problems to reveal patterns and opportunities</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-emerald-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <CheckCircle className="w-4 h-4 text-emerald-600" />
                  </div>
                  <div>
                    <div className="inter font-semibold text-stone-900 mb-1">Continuously Updated</div>
                    <p className="text-sm inter text-stone-600">New submissions flow in daily, keeping opportunities fresh</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-2xl shadow-xl p-8 border border-stone-200">
              <div className="text-xs inter font-medium text-stone-500 mb-3">EXAMPLE SUBMISSION CLUSTER</div>
              <div className="space-y-3">
                {[
                  "I never know when my HVAC is about to fail until it's a $5K emergency",
                  "Finding trustworthy contractors is impossible - I've been burned 3 times",
                  "I wish there was a subscription for preventive home maintenance",
                  "Home warranties are a scam - they never actually cover what breaks"
                ].map((quote, idx) => (
                  <div key={idx} className="border-l-4 border-violet-500 pl-4 py-2 bg-stone-50 rounded-r">
                    <p className="text-sm inter text-stone-700 italic">"{quote}"</p>
                  </div>
                ))}
              </div>
              <div className="mt-6 pt-6 border-t border-stone-200">
                <div className="flex items-center justify-between">
                  <span className="text-sm inter text-stone-600">Clustered into</span>
                  <span className="inter font-bold text-stone-900">On-Demand Home Maintenance</span>
                </div>
              </div>
            </div>
          </div>

          {/* Geographic Intelligence */}
          <div className="grid grid-cols-2 gap-16 items-center">
            <div className="bg-white rounded-2xl shadow-xl p-8 border border-stone-200">
              <div className="flex items-center gap-3 mb-6">
                <Globe className="w-6 h-6 text-stone-600" />
                <h3 className="text-xl spektral font-bold text-stone-900">Geographic Market Analysis</h3>
              </div>
              <div className="space-y-3">
                {[
                  { region: 'Southwest US', applicability: 'Very High', color: 'emerald' },
                  { region: 'US National', applicability: 'High', color: 'green' },
                  { region: 'Canada', applicability: 'High', color: 'green' },
                  { region: 'Australia', applicability: 'Medium', color: 'amber' }
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 bg-stone-50 rounded-lg">
                    <span className="inter font-medium text-stone-900">{item.region}</span>
                    <span className={`px-3 py-1 rounded-full text-xs inter font-medium bg-${item.color}-100 text-${item.color}-700`}>
                      {item.applicability}
                    </span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center mb-6">
                <Globe className="w-6 h-6 text-emerald-600" />
              </div>
              <h2 className="text-4xl spektral font-bold text-stone-900 mb-6">
                Know Where to Launch Before You Build
              </h2>
              <p className="text-lg inter text-stone-600 mb-6">
                Every opportunity includes geographic market intelligence across 6 global regions. Understand market size, competition, and regulatory complexity before you commit.
              </p>
              <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6">
                <div className="text-sm inter font-semibold text-blue-900 mb-2">Example: Home Maintenance</div>
                <p className="text-sm inter text-blue-800">
                  Launch in Southwest US first (Austin, Phoenix) - highest growth +52%, business-friendly regulations, medium competition. Expand nationally once proven.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-stone-900 via-stone-800 to-stone-900 text-white">
        <div className="max-w-4xl mx-auto px-8 text-center">
          <h2 className="text-5xl spektral font-bold mb-6">
            Stop Guessing. Start Building.
          </h2>
          <p className="text-xl inter text-stone-200 mb-12">
            Join hundreds of founders, VCs, and product teams discovering validated opportunities
          </p>
          <div className="flex flex-col items-center gap-4">
            <div className="flex gap-4 w-full max-w-md">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                className="flex-1 px-6 py-4 rounded-lg inter text-stone-900 focus:outline-none focus:ring-2 focus:ring-violet-400"
              />
              <button className="bg-violet-600 hover:bg-violet-700 px-8 py-4 rounded-lg inter font-medium transition-colors whitespace-nowrap">
                Get Started
              </button>
            </div>
            <p className="text-sm inter text-stone-400">Free tier available. No credit card required.</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-stone-200 py-12">
        <div className="max-w-7xl mx-auto px-8">
          <div className="grid grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-stone-900 rounded-lg flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl spektral font-bold text-stone-900">Katalyst</span>
              </div>
              <p className="text-sm inter text-stone-600">
                Transform consumer problems into validated business opportunities
              </p>
            </div>
            <div>
              <h4 className="inter font-semibold text-stone-900 mb-4">Product</h4>
              <ul className="space-y-2 text-sm inter text-stone-600">
                <li><a href="/discover" className="hover:text-stone-900">Browse Ideas</a></li>
                <li><a href="#pricing" className="hover:text-stone-900">Pricing</a></li>
                <li><a href="#" className="hover:text-stone-900">API</a></li>
              </ul>
            </div>
            <div>
              <h4 className="inter font-semibold text-stone-900 mb-4">Company</h4>
              <ul className="space-y-2 text-sm inter text-stone-600">
                <li><a href="#" className="hover:text-stone-900">About</a></li>
                <li><a href="#" className="hover:text-stone-900">Blog</a></li>
                <li><a href="#" className="hover:text-stone-900">Careers</a></li>
              </ul>
            </div>
            <div>
              <h4 className="inter font-semibold text-stone-900 mb-4">Legal</h4>
              <ul className="space-y-2 text-sm inter text-stone-600">
                <li><a href="#" className="hover:text-stone-900">Privacy</a></li>
                <li><a href="#" className="hover:text-stone-900">Terms</a></li>
                <li><a href="#" className="hover:text-stone-900">Security</a></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-stone-200">
            <p className="text-sm inter text-stone-600 text-center">
              © 2024 Katalyst. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
