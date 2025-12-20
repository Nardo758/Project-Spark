import { Link } from 'react-router-dom'
import SimplePage from '../components/SimplePage'

export default function AIRoadmap() {
  return (
    <SimplePage
      title="AI Roadmap"
      subtitle="Generate a step-by-step execution plan for your selected opportunity."
      actions={
        <>
          <Link to="/idea-engine" className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium">
            Validate first
          </Link>
          <Link to="/services" className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium">
            Buy a report
          </Link>
        </>
      }
    >
      <div className="bg-white border border-gray-200 rounded-2xl p-6 text-gray-700">
        Placeholder page for the updated wireframe’s roadmap tool.
      </div>
    </SimplePage>
  )
}

