import { Calendar, Clock, ArrowRight, TrendingUp, Lightbulb, Users, Target } from 'lucide-react'

export default function Blog() {
  const featuredPost = {
    title: 'The Rise of AI-Powered Market Intelligence: What It Means for Entrepreneurs',
    excerpt: 'How artificial intelligence is transforming the way we discover and validate business opportunities, and why early adopters have a significant advantage.',
    category: 'Industry Trends',
    date: 'January 10, 2026',
    readTime: '8 min read',
    image: 'bg-gradient-to-br from-purple-600 to-indigo-600'
  }

  const posts = [
    {
      title: '5 Signals That Indicate a High-Potential Market Opportunity',
      excerpt: 'Learn to identify the key indicators that separate fleeting trends from sustainable business opportunities.',
      category: 'Opportunity Discovery',
      date: 'January 8, 2026',
      readTime: '5 min read',
      icon: TrendingUp
    },
    {
      title: 'From Idea to Validation: A Step-by-Step Framework',
      excerpt: 'Our proven methodology for testing business ideas before you invest significant time and resources.',
      category: 'Validation',
      date: 'January 5, 2026',
      readTime: '10 min read',
      icon: Target
    },
    {
      title: 'Building Your Advisory Network: Why Expert Access Matters',
      excerpt: 'How connecting with the right mentors and advisors can accelerate your path to product-market fit.',
      category: 'Expert Network',
      date: 'January 2, 2026',
      readTime: '6 min read',
      icon: Users
    },
    {
      title: 'SBA Loans Demystified: A Guide for First-Time Founders',
      excerpt: 'Everything you need to know about securing government-backed funding for your startup.',
      category: 'Funding',
      date: 'December 28, 2025',
      readTime: '12 min read',
      icon: Lightbulb
    },
    {
      title: 'Market Sizing 101: How to Estimate Your Addressable Market',
      excerpt: 'Practical techniques for calculating TAM, SAM, and SOM that investors actually respect.',
      category: 'Market Research',
      date: 'December 22, 2025',
      readTime: '7 min read',
      icon: TrendingUp
    },
    {
      title: 'The Hidden Costs of Ignoring Competitor Analysis',
      excerpt: 'Why understanding your competitive landscape is crucial before entering any market.',
      category: 'Strategy',
      date: 'December 18, 2025',
      readTime: '6 min read',
      icon: Target
    }
  ]

  const categories = [
    'All Posts',
    'Opportunity Discovery',
    'Validation',
    'Market Research',
    'Funding',
    'Expert Network',
    'Strategy'
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <section className="bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 text-white py-16">
        <div className="max-w-6xl mx-auto px-6">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">OppGrid Blog</h1>
          <p className="text-xl text-purple-100 max-w-2xl">
            Insights, strategies, and playbooks to help you discover and capitalize on business opportunities.
          </p>
        </div>
      </section>

      <section className="py-12">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex gap-3 overflow-x-auto pb-4 scrollbar-hide">
            {categories.map((category, index) => (
              <button
                key={index}
                className={`px-4 py-2 rounded-full whitespace-nowrap font-medium transition-colors ${
                  index === 0 
                    ? 'bg-purple-600 text-white' 
                    : 'bg-white text-gray-700 hover:bg-purple-50 border border-gray-200'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="pb-12">
        <div className="max-w-6xl mx-auto px-6">
          <div className={`${featuredPost.image} rounded-2xl p-8 md:p-12 text-white`}>
            <span className="inline-block px-3 py-1 bg-white/20 rounded-full text-sm font-medium mb-4">
              {featuredPost.category}
            </span>
            <h2 className="text-2xl md:text-4xl font-bold mb-4 max-w-3xl">
              {featuredPost.title}
            </h2>
            <p className="text-lg text-white/90 mb-6 max-w-2xl">
              {featuredPost.excerpt}
            </p>
            <div className="flex flex-wrap items-center gap-6 mb-6">
              <div className="flex items-center gap-2 text-white/80">
                <Calendar className="w-4 h-4" />
                {featuredPost.date}
              </div>
              <div className="flex items-center gap-2 text-white/80">
                <Clock className="w-4 h-4" />
                {featuredPost.readTime}
              </div>
            </div>
            <button className="inline-flex items-center gap-2 px-6 py-3 bg-white text-purple-700 rounded-lg font-semibold hover:bg-purple-50 transition-colors">
              Read Article <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </section>

      <section className="pb-20">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-8">Latest Articles</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {posts.map((post, index) => (
              <article 
                key={index}
                className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg hover:border-purple-200 transition-all group"
              >
                <div className="p-6">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                    <post.icon className="w-6 h-6 text-purple-600" />
                  </div>
                  <span className="text-sm font-medium text-purple-600 mb-2 block">
                    {post.category}
                  </span>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-purple-700 transition-colors">
                    {post.title}
                  </h3>
                  <p className="text-gray-600 text-sm mb-4">
                    {post.excerpt}
                  </p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5" />
                      {post.date}
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      {post.readTime}
                    </div>
                  </div>
                </div>
              </article>
            ))}
          </div>

          <div className="mt-12 text-center">
            <button className="px-6 py-3 border-2 border-purple-600 text-purple-600 rounded-lg font-semibold hover:bg-purple-50 transition-colors">
              Load More Articles
            </button>
          </div>
        </div>
      </section>

      <section className="py-16 bg-white border-t border-gray-200">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Stay Updated</h2>
          <p className="text-gray-600 mb-6">
            Get the latest opportunity insights and platform updates delivered to your inbox.
          </p>
          <form className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
            <input
              type="email"
              placeholder="Enter your email"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none"
            />
            <button
              type="submit"
              className="px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition-colors"
            >
              Subscribe
            </button>
          </form>
          <p className="text-xs text-gray-500 mt-3">
            No spam. Unsubscribe anytime.
          </p>
        </div>
      </section>
    </div>
  )
}
