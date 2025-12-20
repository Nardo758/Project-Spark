import { Link } from 'react-router-dom'
import { ArrowRight, BadgeCheck, Users } from 'lucide-react'
import SimplePage from '../components/SimplePage'

export default function Network() {
  return (
    <SimplePage
      title="Network"
      subtitle="Join founders, operators, and experts. Browse public activity and connect for free."
      actions={
        <>
          <Link to="/signup" className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium">
            Join free
          </Link>
          <Link to="/login" className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium">
            Sign in
          </Link>
        </>
      }
    >
      <div className="bg-white border border-gray-200 rounded-2xl p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-gray-900 font-semibold">
              <Users className="w-5 h-5" />
              Live community
            </div>
            <p className="mt-2 text-sm text-gray-600">
              Explore what people are building, who’s hiring, and which experts are available.
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-gray-900">6,234</div>
            <div className="text-xs text-gray-500">members</div>
          </div>
        </div>

        <div className="mt-6 grid md:grid-cols-3 gap-4">
          {[
            { title: 'Sarah launched her SaaS', detail: '$12k MRR • 45 days', tag: 'Launch' },
            { title: 'Tech Ventures seeking AI startups', detail: 'Pitch slots open', tag: 'Investors' },
            { title: 'Healthcare webinar tomorrow', detail: 'Free • 2pm ET', tag: 'Event' },
          ].map((item) => (
            <div key={item.title} className="border border-gray-200 rounded-xl p-4">
              <div className="text-xs text-gray-500">{item.tag}</div>
              <div className="mt-1 font-semibold text-gray-900">{item.title}</div>
              <div className="mt-1 text-sm text-gray-600">{item.detail}</div>
            </div>
          ))}
        </div>

        <div className="mt-6 flex flex-wrap gap-2">
          <div className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 text-sm">
            <BadgeCheck className="w-4 h-4" />
            Verified experts available
          </div>
          <div className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-50 text-gray-800 border border-gray-200 text-sm">
            <span className="font-medium">Tip:</span> Create a free account to message and save people.
          </div>
        </div>

        <div className="mt-6">
          <Link to="/signup" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium">
            Create your profile <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </SimplePage>
  )
}

