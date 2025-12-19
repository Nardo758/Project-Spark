import { Check, Brain } from 'lucide-react'
import { Link } from 'react-router-dom'

const plans = [
  {
    name: 'Free',
    price: '$0',
    description: 'Get started with basic features',
    features: [
      'Browse 10 opportunities/month',
      'Basic idea validation',
      'Community access',
      'Email support',
    ],
    cta: 'Start Free',
    highlighted: false,
  },
  {
    name: 'Pro',
    price: '$399',
    period: '/month',
    description: 'Everything you need to build',
    features: [
      'Unlimited opportunities',
      'Advanced AI validation',
      'Expert marketplace access',
      'AI Co-founder Basic included',
      'Priority support',
      'Custom roadmaps',
    ],
    cta: 'Get Pro',
    highlighted: true,
    badge: 'Most Popular',
  },
  {
    name: 'Business',
    price: '$599',
    period: '/month',
    description: 'For growing teams',
    features: [
      'Everything in Pro',
      'Team collaboration (5 seats)',
      '3 Brain AI profiles',
      'White-label content',
      'API access',
      'Dedicated support',
    ],
    cta: 'Get Business',
    highlighted: false,
  },
]

const brainAddons = [
  { name: 'Business Brain', price: '+$199', desc: '3 Brain profiles, team features' },
  { name: 'Expert Brain', price: '+$299', desc: '5 Brains, white-label AI, API' },
  { name: 'Enterprise Brain', price: 'Custom', desc: 'Unlimited, dedicated instances' },
]

export default function Pricing() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Simple, Transparent Pricing</h1>
        <p className="text-xl text-gray-600">Start free, upgrade when you're ready to scale</p>
      </div>

      <div className="grid md:grid-cols-3 gap-8 mb-16">
        {plans.map((plan) => (
          <div
            key={plan.name}
            className={`relative rounded-2xl p-8 ${
              plan.highlighted
                ? 'bg-gray-900 text-white ring-4 ring-gray-900'
                : 'bg-white border border-gray-200'
            }`}
          >
            {plan.badge && (
              <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                <span className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                  {plan.badge}
                </span>
              </div>
            )}
            <div className="mb-6">
              <h2 className={`text-2xl font-bold ${plan.highlighted ? 'text-white' : 'text-gray-900'}`}>
                {plan.name}
              </h2>
              <div className="mt-4 flex items-baseline">
                <span className={`text-4xl font-bold ${plan.highlighted ? 'text-white' : 'text-gray-900'}`}>
                  {plan.price}
                </span>
                {plan.period && (
                  <span className={`ml-1 ${plan.highlighted ? 'text-gray-300' : 'text-gray-500'}`}>
                    {plan.period}
                  </span>
                )}
              </div>
              <p className={`mt-2 ${plan.highlighted ? 'text-gray-300' : 'text-gray-600'}`}>
                {plan.description}
              </p>
            </div>
            <ul className="space-y-4 mb-8">
              {plan.features.map((feature) => (
                <li key={feature} className="flex items-start gap-3">
                  <Check className={`w-5 h-5 flex-shrink-0 ${plan.highlighted ? 'text-green-400' : 'text-green-500'}`} />
                  <span className={plan.highlighted ? 'text-gray-300' : 'text-gray-600'}>
                    {feature}
                  </span>
                </li>
              ))}
            </ul>
            <Link
              to="/signup"
              className={`block w-full text-center py-3 rounded-lg font-medium ${
                plan.highlighted
                  ? 'bg-white text-gray-900 hover:bg-gray-100'
                  : 'bg-gray-900 text-white hover:bg-gray-800'
              }`}
            >
              {plan.cta}
            </Link>
          </div>
        ))}
      </div>

      <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl p-8 lg:p-12">
        <div className="flex items-start gap-4 mb-8">
          <div className="w-14 h-14 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl flex items-center justify-center flex-shrink-0">
            <Brain className="w-7 h-7 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Brain AI Add-ons</h2>
            <p className="text-gray-600">Supercharge your subscription with AI Co-founder capabilities</p>
          </div>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {brainAddons.map((addon) => (
            <div key={addon.name} className="bg-white rounded-xl p-6 border border-purple-200">
              <h3 className="font-semibold text-gray-900 mb-1">{addon.name}</h3>
              <div className="text-2xl font-bold text-purple-600 mb-2">{addon.price}</div>
              <p className="text-sm text-gray-600">{addon.desc}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-16 text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Pay-Per-Unlock Options</h3>
        <div className="inline-flex gap-4 flex-wrap justify-center">
          <div className="bg-white border border-gray-200 rounded-lg px-6 py-3">
            <span className="text-gray-600">Archive:</span>
            <span className="ml-2 font-bold text-gray-900">$9</span>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg px-6 py-3">
            <span className="text-gray-600">Quick Look:</span>
            <span className="ml-2 font-bold text-gray-900">$29</span>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg px-6 py-3">
            <span className="text-gray-600">Fast Pass:</span>
            <span className="ml-2 font-bold text-gray-900">$99</span>
          </div>
        </div>
      </div>
    </div>
  )
}
