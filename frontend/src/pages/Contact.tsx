import { Link } from 'react-router-dom'
import SimplePage from '../components/SimplePage'

export default function Contact() {
  return (
    <SimplePage
      title="Contact"
      subtitle="Questions, partnerships, or enterprise?"
      actions={
        <Link to="/pricing" className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium">
          Pricing
        </Link>
      }
    >
      <div className="bg-white border border-gray-200 rounded-2xl p-6 text-gray-700">
        Placeholder page.
      </div>
    </SimplePage>
  )
}

