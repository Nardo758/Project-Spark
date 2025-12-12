import React, { useState } from 'react';
import { Sparkles, Send, TrendingUp, Award, CheckCircle, Zap } from 'lucide-react';

export default function ProblemSubmission() {
  const [problemText, setProblemText] = useState('');
  const [category, setCategory] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const categories = [
    'Home Services',
    'Health & Wellness',
    'B2B SaaS',
    'Pet Tech',
    'B2B Services',
    'Healthcare',
    'Finance',
    'Education',
    'Food & Beverage',
    'Transportation',
    'Entertainment',
    'Other'
  ];

  const exampleProblems = [
    "I never know when my HVAC is about to fail until it's a $5K emergency",
    "Finding trustworthy contractors is impossible - I've been burned 3 times",
    "Managing multiple dietary restrictions for my family takes hours every week",
    "Remote team bonding is impossible - we have no spontaneous interactions"
  ];

  const similarProblems = [
    {
      title: "On-Demand Home Maintenance Subscription",
      submissions: 2847,
      match: 94
    },
    {
      title: "Vetted Contractor Marketplace",
      submissions: 1432,
      match: 87
    }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);
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
        
        @keyframes confetti {
          0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
          }
          100% {
            transform: translateY(-100vh) rotate(360deg);
            opacity: 0;
          }
        }
        
        .fade-in-up {
          animation: fadeInUp 0.6s ease-out forwards;
        }
        
        .stagger-1 { animation-delay: 0.1s; opacity: 0; }
        .stagger-2 { animation-delay: 0.2s; opacity: 0; }
        .stagger-3 { animation-delay: 0.3s; opacity: 0; }
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
              <a href="/" className="inter text-sm text-stone-600 hover:text-stone-900 transition-colors">Home</a>
              <a href="/discover" className="inter text-sm text-stone-600 hover:text-stone-900 transition-colors">Browse Ideas</a>
              <button className="inter text-sm font-medium text-stone-600 hover:text-stone-900 transition-colors">Sign In</button>
              <button className="bg-stone-900 text-white px-4 py-2 rounded-lg inter text-sm font-medium hover:bg-stone-800 transition-colors">
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {!submitted ? (
        <>
          {/* Header */}
          <div className="bg-gradient-to-br from-violet-50 to-purple-50 border-b border-purple-200">
            <div className="max-w-4xl mx-auto px-8 py-16 text-center">
              <div className="inline-block bg-violet-100 text-violet-700 px-4 py-2 rounded-full text-sm inter font-medium mb-6 fade-in-up">
                Help Build the Future
              </div>
              <h1 className="text-5xl spektral font-bold text-stone-900 mb-4 fade-in-up stagger-1">
                What's Frustrating You?
              </h1>
              <p className="text-xl inter text-stone-600 max-w-2xl mx-auto fade-in-up stagger-2">
                Share your everyday problems and unmet needs. Your frustration could become the next validated business opportunity.
              </p>
            </div>
          </div>

          {/* Value Props */}
          <div className="bg-white border-b border-stone-200">
            <div className="max-w-4xl mx-auto px-8 py-8">
              <div className="grid grid-cols-3 gap-8 text-center">
                <div className="fade-in-up stagger-1">
                  <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <TrendingUp className="w-6 h-6 text-emerald-600" />
                  </div>
                  <h3 className="inter font-semibold text-stone-900 mb-1">You're Not Alone</h3>
                  <p className="text-sm inter text-stone-600">2,847 others have shared problems that became opportunities</p>
                </div>
                <div className="fade-in-up stagger-2">
                  <div className="w-12 h-12 bg-violet-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <Award className="w-6 h-6 text-violet-600" />
                  </div>
                  <h3 className="inter font-semibold text-stone-900 mb-1">Earn Recognition</h3>
                  <p className="text-sm inter text-stone-600">Get notified when your problem becomes validated</p>
                </div>
                <div className="fade-in-up stagger-3">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <Zap className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="inter font-semibold text-stone-900 mb-1">Shape Solutions</h3>
                  <p className="text-sm inter text-stone-600">Help builders create what you actually need</p>
                </div>
              </div>
            </div>
          </div>

          {/* Main Form */}
          <div className="max-w-4xl mx-auto px-8 py-12">
            <form onSubmit={handleSubmit} className="space-y-8">
              
              {/* Problem Description */}
              <div className="bg-white rounded-2xl border-2 border-stone-200 p-8 fade-in-up">
                <label className="block mb-4">
                  <span className="text-lg spektral font-bold text-stone-900 mb-2 block">
                    Describe Your Problem or Frustration
                  </span>
                  <span className="text-sm inter text-stone-600 mb-4 block">
                    Be specific. What's the situation? What makes it frustrating? What have you tried?
                  </span>
                  <textarea
                    value={problemText}
                    onChange={(e) => setProblemText(e.target.value)}
                    placeholder="Example: I never know when something in my home is about to break until it's too late and costs thousands to fix. I've tried preventive maintenance checklists but never follow through. Home warranties are a scam - they never cover what actually breaks."
                    rows={6}
                    className="w-full px-4 py-3 border-2 border-stone-200 rounded-lg inter text-stone-900 focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100 resize-none"
                    required
                  />
                </label>

                <div className="flex items-start gap-2 mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <Sparkles className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm inter text-blue-800">
                    <strong>Tip:</strong> The more detail you provide, the better we can understand and validate the opportunity. Include emotions, costs, time wasted, and what you wish existed.
                  </p>
                </div>
              </div>

              {/* Category Selection */}
              <div className="bg-white rounded-2xl border-2 border-stone-200 p-8 fade-in-up stagger-1">
                <label className="block">
                  <span className="text-lg spektral font-bold text-stone-900 mb-4 block">
                    What Category Does This Fall Under?
                  </span>
                  <div className="grid grid-cols-3 gap-3">
                    {categories.map((cat) => (
                      <button
                        key={cat}
                        type="button"
                        onClick={() => setCategory(cat)}
                        className={`p-4 rounded-lg border-2 transition-all inter font-medium text-sm ${
                          category === cat
                            ? 'border-violet-600 bg-violet-50 text-violet-700'
                            : 'border-stone-200 hover:border-stone-300 text-stone-700'
                        }`}
                      >
                        {cat}
                      </button>
                    ))}
                  </div>
                </label>
              </div>

              {/* Similar Problems (shown when typing) */}
              {problemText.length > 50 && (
                <div className="bg-amber-50 border-2 border-amber-200 rounded-2xl p-8 fade-in-up">
                  <div className="flex items-start gap-3 mb-4">
                    <CheckCircle className="w-6 h-6 text-amber-600 flex-shrink-0" />
                    <div>
                      <h3 className="text-lg spektral font-bold text-stone-900 mb-1">
                        Good News! Others Feel This Too
                      </h3>
                      <p className="text-sm inter text-stone-600">
                        We found similar problems already submitted. Your input will strengthen these opportunities.
                      </p>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    {similarProblems.map((similar, idx) => (
                      <div key={idx} className="bg-white rounded-lg p-4 border border-amber-200">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <h4 className="inter font-semibold text-stone-900 mb-1">{similar.title}</h4>
                            <p className="text-xs inter text-stone-600">{similar.submissions} submissions</p>
                          </div>
                          <div className="bg-emerald-100 text-emerald-700 px-3 py-1 rounded-full">
                            <span className="text-sm spektral font-bold">{similar.match}%</span>
                            <span className="text-xs inter ml-1">match</span>
                          </div>
                        </div>
                        <a href={`/opportunity/${idx + 1}`} className="text-sm inter text-violet-600 hover:text-violet-700 font-medium">
                          View opportunity →
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={!problemText || !category}
                className="w-full bg-gradient-to-r from-violet-600 to-purple-600 text-white py-5 rounded-xl inter font-semibold text-lg hover:shadow-2xl hover:shadow-violet-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 fade-in-up stagger-2"
              >
                <Send className="w-5 h-5" />
                Submit My Problem
              </button>
            </form>

            {/* Examples */}
            <div className="mt-16 fade-in-up stagger-3">
              <h3 className="text-2xl spektral font-bold text-stone-900 mb-6 text-center">
                Need Inspiration? Here's What Others Have Shared
              </h3>
              <div className="grid grid-cols-2 gap-4">
                {exampleProblems.map((example, idx) => (
                  <div key={idx} className="bg-white rounded-lg border border-stone-200 p-4">
                    <p className="text-sm inter text-stone-700 italic">"{example}"</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      ) : (
        /* Success State */
        <div className="max-w-3xl mx-auto px-8 py-24 text-center">
          <div className="bg-white rounded-2xl border-2 border-emerald-200 p-12 fade-in-up">
            <div className="w-20 h-20 bg-gradient-to-br from-emerald-500 to-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-12 h-12 text-white" />
            </div>
            
            <h2 className="text-4xl spektral font-bold text-stone-900 mb-4">
              Thank You for Sharing!
            </h2>
            <p className="text-xl inter text-stone-600 mb-8">
              Your problem has been submitted and will be reviewed by our team. If it clusters with similar submissions, you'll be notified when it becomes a validated opportunity.
            </p>

            <div className="grid grid-cols-3 gap-6 mb-8">
              <div className="bg-emerald-50 rounded-lg p-6">
                <div className="text-3xl spektral font-bold text-emerald-600 mb-2">+10</div>
                <div className="text-sm inter text-stone-600">Points Earned</div>
              </div>
              <div className="bg-violet-50 rounded-lg p-6">
                <div className="text-3xl spektral font-bold text-violet-600 mb-2">
                  <Award className="w-10 h-10 mx-auto" />
                </div>
                <div className="text-sm inter text-stone-600">Contributor Badge</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-6">
                <div className="text-3xl spektral font-bold text-blue-600 mb-2">📧</div>
                <div className="text-sm inter text-stone-600">Email Alerts On</div>
              </div>
            </div>

            <div className="space-y-4">
              <a
                href="/discover"
                className="block bg-stone-900 text-white px-8 py-4 rounded-lg inter font-medium hover:bg-stone-800 transition-colors"
              >
                Browse Validated Opportunities
              </a>
              <button
                onClick={() => {
                  setSubmitted(false);
                  setProblemText('');
                  setCategory('');
                }}
                className="block w-full border-2 border-stone-900 text-stone-900 px-8 py-4 rounded-lg inter font-medium hover:bg-stone-900 hover:text-white transition-colors"
              >
                Submit Another Problem
              </button>
            </div>
          </div>

          {/* What Happens Next */}
          <div className="mt-12 text-left bg-white rounded-xl border border-stone-200 p-8">
            <h3 className="text-xl spektral font-bold text-stone-900 mb-6">What Happens Next?</h3>
            <div className="space-y-4">
              <div className="flex gap-4">
                <div className="w-8 h-8 bg-violet-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-sm spektral font-bold text-violet-600">1</span>
                </div>
                <div>
                  <div className="inter font-semibold text-stone-900 mb-1">Review & Clustering</div>
                  <p className="text-sm inter text-stone-600">Our AI analyzes your submission and groups it with similar problems to identify patterns.</p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="w-8 h-8 bg-violet-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-sm spektral font-bold text-violet-600">2</span>
                </div>
                <div>
                  <div className="inter font-semibold text-stone-900 mb-1">Validation</div>
                  <p className="text-sm inter text-stone-600">As more people submit similar problems, the opportunity gains validation and rises in our rankings.</p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="w-8 h-8 bg-violet-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-sm spektral font-bold text-violet-600">3</span>
                </div>
                <div>
                  <div className="inter font-semibold text-stone-900 mb-1">You Get Notified</div>
                  <p className="text-sm inter text-stone-600">When your problem reaches validation threshold, we'll email you. You can then explore the full opportunity analysis.</p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="w-8 h-8 bg-violet-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-sm spektral font-bold text-violet-600">4</span>
                </div>
                <div>
                  <div className="inter font-semibold text-stone-900 mb-1">Builders Take Action</div>
                  <p className="text-sm inter text-stone-600">Entrepreneurs, VCs, and product teams use our platform to discover and validate solutions to your problem.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
