import { Link } from 'react-router-dom'
import SimplePage from '../components/SimplePage'

export default function Blog() {
  return (
    <SimplePage
      title="Blog"
      subtitle="Updates, playbooks, and market notes."
      actions={
        <Link to="/learn" className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium">
          Learn
        </Link>
      }
    >
      <div className="bg-white border border-gray-200 rounded-2xl p-6 text-gray-700">
        Placeholder page.
      </div>
    </SimplePage>
  )
}

