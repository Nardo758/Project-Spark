import { Link } from 'react-router-dom'
import SimplePage from '../components/SimplePage'

export default function Cart() {
  return (
    <SimplePage
      title="Cart"
      subtitle="Guest checkout is supported — you can review items here before paying."
      actions={
        <>
          <Link to="/services" className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 font-medium">
            Browse services
          </Link>
          <Link to="/discover" className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 font-medium">
            Find opportunities
          </Link>
        </>
      }
    >
      <div className="bg-white border border-gray-200 rounded-2xl p-6 text-gray-700">
        Your cart is empty (placeholder). Next step: connect the unlock/report purchase flows to cart line items.
      </div>
    </SimplePage>
  )
}

