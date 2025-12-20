import { Link } from 'react-router-dom'
import SimplePage from '../components/SimplePage'

export default function Leads() {
  return (
    <SimplePage
      title="Leads"
      subtitle="Generate, package, and sell leads tied to specific opportunities."
      actions={
        <>
          <Link to="/discover" className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium">
            Find opportunity
          </Link>
          <Link to="/pricing" className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium">
            Upgrade
          </Link>
        </>
      }
    >
      <div className="bg-white border border-gray-200 rounded-2xl p-6 text-gray-700">
        This section is a placeholder for the updated wireframe. Next we can add lead sources, export, and billing flows.
      </div>
    </SimplePage>
  )
}

