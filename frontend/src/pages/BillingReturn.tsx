import { useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

export default function BillingReturn() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const bootstrap = useAuthStore((s) => s.bootstrap)
  
  const status = searchParams.get('status')
  const returnTo = searchParams.get('return_to')
  
  useEffect(() => {
    if (status === 'success') {
      bootstrap()
      const timer = setTimeout(() => {
        navigate(returnTo || '/dashboard')
      }, 2000)
      return () => clearTimeout(timer)
    } else if (status === 'canceled') {
      const timer = setTimeout(() => {
        navigate(returnTo || '/dashboard')
      }, 2000)
      return () => clearTimeout(timer)
    }
  }, [status, returnTo, navigate, bootstrap])

  if (status === 'success') {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Successful!</h1>
          <p className="text-gray-600 mb-4">Your subscription has been activated.</p>
          <p className="text-sm text-gray-500">Redirecting you back...</p>
        </div>
      </div>
    )
  }

  if (status === 'canceled') {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <XCircle className="w-8 h-8 text-amber-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Canceled</h1>
          <p className="text-gray-600 mb-4">No charges were made to your account.</p>
          <p className="text-sm text-gray-500">Redirecting you back...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="w-8 h-8 text-gray-400 animate-spin mx-auto mb-4" />
        <p className="text-gray-600">Processing...</p>
      </div>
    </div>
  )
}
