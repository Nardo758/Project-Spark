import { Link } from 'react-router-dom'
import SimplePage from '../components/SimplePage'

export default function ExpertMarketplace() {
  return (
    <SimplePage
      title="Expert Marketplace"
      subtitle="Find vetted operators to help you execute."
      actions={
        <>
          <Link to="/network" className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium">
            View network
          </Link>
          <Link to="/services" className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium">
            Services
          </Link>
        </>
      }
    >
      <div className="bg-white border border-gray-200 rounded-2xl p-6 text-gray-700">
        Placeholder page. Next we can add expert profiles, availability, and booking.
      </div>
    </SimplePage>
  )
}

