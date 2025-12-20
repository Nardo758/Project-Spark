import { Link } from 'react-router-dom'
import SimplePage from '../components/SimplePage'

export default function Funding() {
  return (
    <SimplePage
      title="Funding"
      subtitle="Track grants, angels, and programs relevant to your opportunity."
      actions={
        <>
          <Link to="/discover" className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium">
            Browse opportunities
          </Link>
          <Link to="/network" className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium">
            Join network
          </Link>
        </>
      }
    >
      <div className="bg-white border border-gray-200 rounded-2xl p-6 text-gray-700">
        Placeholder page. Next we can add funding alerts and application checklists.
      </div>
    </SimplePage>
  )
}

