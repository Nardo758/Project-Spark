import { Link } from 'react-router-dom'
import { ArrowRight, Lightbulb, Target, Users, Brain, Zap, TrendingUp } from 'lucide-react'

export default function Home() {
  return (
    <div className="bg-white">
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-50 text-purple-700 rounded-full text-sm font-medium mb-6">
              <Brain className="w-4 h-4" />
              Now with AI Co-founder
            </div>
            <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 tracking-tight">
              Your AI-Powered
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600">
                Startup Factory
              </span>
            </h1>
            <p className="mt-6 text-xl text-gray-600 max-w-2xl mx-auto">
              Discover validated opportunities, build with AI guidance, and connect with experts 
              to turn your ideas into successful businesses.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/signup"
                className="inline-flex items-center justify-center px-6 py-3 text-base font-medium text-white bg-black hover:bg-gray-800 rounded-lg gap-2"
              >
                Start Free Trial
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                to="/discover"
                className="inline-flex items-center justify-center px-6 py-3 text-base font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-lg"
              >
                Browse Opportunities
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900">Three Paths to Success</h2>
            <p className="mt-4 text-lg text-gray-600">Choose your journey or combine all three</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-2xl shadow-card hover:shadow-card-hover transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-6">
                <Lightbulb className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Build Business</h3>
              <p className="text-gray-600 mb-4">
                Discover validated opportunities and build your startup with AI-powered guidance and expert support.
              </p>
              <Link to="/discover" className="text-blue-600 font-medium hover:text-blue-700">
                Explore Opportunities →
              </Link>
            </div>
            <div className="bg-white p-8 rounded-2xl shadow-card hover:shadow-card-hover transition-shadow">
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-6">
                <Target className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Generate Leads</h3>
              <p className="text-gray-600 mb-4">
                Create and sell services to entrepreneurs. Earn 70% revenue share with our marketplace.
              </p>
              <Link to="/expert-marketplace" className="text-green-600 font-medium hover:text-green-700">
                Become an Expert →
              </Link>
            </div>
            <div className="bg-white p-8 rounded-2xl shadow-card hover:shadow-card-hover transition-shadow">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-6">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Create Content</h3>
              <p className="text-gray-600 mb-4">
                Use AI templates to create white-label content. Earn 60% on every sale.
              </p>
              <Link to="/content" className="text-purple-600 font-medium hover:text-purple-700">
                Start Creating →
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-50 text-purple-700 rounded-full text-sm font-medium mb-4">
              <Zap className="w-4 h-4" />
              New Feature
            </div>
            <h2 className="text-3xl font-bold text-gray-900">Meet Your AI Co-founder</h2>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              Train a personal AI that understands your goals, skills, and preferences. 
              Get hyper-personalized guidance at every step.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: Brain, title: 'Personal Brain', desc: 'AI that learns your style' },
              { icon: Target, title: 'Smart Matching', desc: '94% opportunity match rate' },
              { icon: TrendingUp, title: 'Faster Growth', desc: 'Save 5+ hours weekly' },
              { icon: Users, title: 'Expert Network', desc: 'Connect with founders' },
            ].map((item, i) => (
              <div key={i} className="text-center p-6">
                <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <item.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-sm text-gray-600">{item.desc}</p>
              </div>
            ))}
          </div>
          <div className="text-center mt-10">
            <Link
              to="/pricing"
              className="inline-flex items-center justify-center px-6 py-3 text-base font-medium text-white bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 rounded-lg gap-2"
            >
              Upgrade to Pro + Brain AI
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center gap-2 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                <span className="text-gray-900 font-bold text-sm">OG</span>
              </div>
              <span className="font-semibold text-xl">OppGrid</span>
            </div>
            <p className="text-gray-400 text-sm">
              © 2024 OppGrid. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
