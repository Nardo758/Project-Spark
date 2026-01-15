import { Link } from 'react-router-dom'
import { Lightbulb, Users, TrendingUp, Shield, Zap, Target, ArrowRight } from 'lucide-react'

export default function About() {
  const features = [
    {
      icon: Lightbulb,
      title: 'AI-Powered Discovery',
      description: 'Our algorithms scan millions of data points to surface high-potential opportunities before they become mainstream.'
    },
    {
      icon: Target,
      title: 'Validation Framework',
      description: 'Move from idea to validated opportunity with our structured Design Thinking methodology and AI analysis.'
    },
    {
      icon: Users,
      title: 'Expert Network',
      description: 'Connect with verified consultants, investors, and partners who can help accelerate your business growth.'
    },
    {
      icon: TrendingUp,
      title: 'Market Intelligence',
      description: 'Access real-time demographic data, competitor analysis, and market sizing powered by authoritative sources.'
    },
    {
      icon: Zap,
      title: 'Execution Tools',
      description: 'From business formation guides to funding discovery, we provide the resources to turn opportunities into reality.'
    },
    {
      icon: Shield,
      title: 'Enterprise Ready',
      description: 'Bank-grade security, team collaboration features, and API access for organizations of any size.'
    }
  ]

  const stats = [
    { value: '10,000+', label: 'Opportunities Analyzed' },
    { value: '500+', label: 'Verified Experts' },
    { value: '95%', label: 'User Satisfaction' },
    { value: '24/7', label: 'AI Support' }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <section className="bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 text-white py-20">
        <div className="max-w-6xl mx-auto px-6">
          <div className="max-w-3xl">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              Democratizing Access to Business Intelligence
            </h1>
            <p className="text-xl text-purple-100 mb-8 leading-relaxed">
              OppGrid is an AI-powered opportunity intelligence platform that helps entrepreneurs, 
              investors, and business leaders discover, validate, and act on high-potential opportunities 
              with confidence.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link 
                to="/discover" 
                className="inline-flex items-center gap-2 px-6 py-3 bg-white text-purple-900 rounded-lg font-semibold hover:bg-purple-50 transition-colors"
              >
                Explore Opportunities <ArrowRight className="w-4 h-4" />
              </Link>
              <Link 
                to="/pricing" 
                className="inline-flex items-center gap-2 px-6 py-3 border-2 border-white text-white rounded-lg font-semibold hover:bg-white/10 transition-colors"
              >
                View Pricing
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-purple-600 mb-2">{stat.value}</div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Our Mission</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We believe that great opportunities shouldn't be hidden behind expensive consultants 
              or exclusive networks. OppGrid levels the playing field by giving everyone access to 
              the same intelligence that drives successful business decisions.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div 
                key={index} 
                className="bg-white rounded-xl p-6 border border-gray-200 hover:border-purple-200 hover:shadow-lg transition-all"
              >
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">The OppGrid Approach</h2>
              <div className="space-y-6">
                <div className="flex gap-4">
                  <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold shrink-0">1</div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">Discover</h3>
                    <p className="text-gray-600">Our AI continuously scans market signals, trends, and emerging patterns to surface opportunities you'd otherwise miss.</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold shrink-0">2</div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">Validate</h3>
                    <p className="text-gray-600">Use our structured validation framework to stress-test ideas with real data, demographic insights, and competitive analysis.</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold shrink-0">3</div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">Execute</h3>
                    <p className="text-gray-600">Connect with experts, access funding resources, and use our execution tools to turn validated opportunities into real businesses.</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-gradient-to-br from-purple-100 to-indigo-100 rounded-2xl p-8">
              <blockquote className="text-lg text-gray-700 italic mb-4">
                "OppGrid transformed how we identify market opportunities. What used to take our team weeks now happens in hours with better accuracy."
              </blockquote>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold">JD</div>
                <div>
                  <div className="font-semibold text-gray-900">James Davidson</div>
                  <div className="text-sm text-gray-600">Venture Partner, Innovation Capital</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 text-white">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Discover Your Next Opportunity?</h2>
          <p className="text-xl text-purple-100 mb-8">
            Join thousands of entrepreneurs and investors using OppGrid to find their competitive edge.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link 
              to="/signup" 
              className="inline-flex items-center gap-2 px-8 py-4 bg-white text-purple-900 rounded-lg font-semibold hover:bg-purple-50 transition-colors"
            >
              Get Started Free <ArrowRight className="w-4 h-4" />
            </Link>
            <Link 
              to="/contact" 
              className="inline-flex items-center gap-2 px-8 py-4 border-2 border-white text-white rounded-lg font-semibold hover:bg-white/10 transition-colors"
            >
              Contact Sales
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
