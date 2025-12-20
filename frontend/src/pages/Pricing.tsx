import { Check } from 'lucide-react'
import { Link } from 'react-router-dom'

const plans = [
  {
    name: 'Explorer',
    price: '$0',
    period: '/month',
    description: 'Start free and browse the archive',
    features: [
      'Browse 91+ day opportunities (Archive)',
      'Basic search & filters',
      'Save opportunities',
      'Pay‑per‑unlock ($15 / opportunity)',
    ],
    cta: 'Get Started',
    highlighted: false,
  },
  {
    name: 'Builder',
    price: '$99',
    period: '/month',
    description: 'Early access + AI co-founder basics',
    features: [
      'Unlimited access to 31+ day opportunities (Validated)',
      'Preview 8–30 day opportunities (Fresh)',
      'AI Co‑founder (Basic)',
      'Deep Dive add‑on ($49 / opportunity)',
      'CSV export + advanced filters',
    ],
    cta: 'Start Free Trial',
    highlighted: true,
    badge: 'Most Popular',
  },
  {
    name: 'Scaler',
    price: '$499',
    period: '/month',
    description: 'Full access to Fresh + deeper intelligence',
    features: [
      'Full access to 8+ day opportunities (Fresh)',
      'Full Layer 1 & 2 on all accessible opportunities',
      'Fast Pass ($99) for HOT 0–7 day opportunities',
      'Team-ready exports & reporting',
      'API access (coming soon)',
    ],
    cta: 'Get Scaler',
    highlighted: false,
  },
]

export default function Pricing() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Simple, Transparent Pricing</h1>
        <p className="text-xl text-gray-600">Start for free, upgrade as you grow. Cancel anytime.</p>
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

      <div className="mt-16 text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">One‑time unlock options</h3>
        <div className="inline-flex gap-4 flex-wrap justify-center">
          <div className="bg-white border border-gray-200 rounded-lg px-6 py-3">
            <span className="text-gray-600">Archive:</span>
            <span className="ml-2 font-bold text-gray-900">$15</span>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg px-6 py-3">
            <span className="text-gray-600">Deep Dive add‑on:</span>
            <span className="ml-2 font-bold text-gray-900">$49</span>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg px-6 py-3">
            <span className="text-gray-600">Fast Pass:</span>
            <span className="ml-2 font-bold text-gray-900">$99</span>
          </div>
        </div>
        <div className="mt-6 text-sm text-gray-600">
          Need earliest access (HOT 0–7 days)?{' '}
          <a className="text-blue-600 hover:text-blue-700 font-medium" href="mailto:enterprise@oppgrid.com">
            Contact sales for Enterprise
          </a>
          .
        </div>
      </div>
    </div>
  )
}
