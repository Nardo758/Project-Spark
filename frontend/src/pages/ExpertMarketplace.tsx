import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { 
  Search, Star, Clock, DollarSign, CheckCircle, Loader2, 
  User, Briefcase, Calendar, X
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

type Expert = {
  id: number
  name: string
  headline?: string
  bio?: string
  skills: string[]
  specialization: string[]
  pricing_model: string
  hourly_rate_cents?: number
  fixed_price_cents?: number
  success_fee_bps?: number
  currency?: string
  is_active: boolean
}

type BookingFormData = {
  booking_type: string
  title: string
  description: string
  duration_minutes: number
}

function formatCents(cents: number): string {
  return `$${(cents / 100).toFixed(0)}`
}

export default function ExpertMarketplace() {
  const { token, isAuthenticated } = useAuthStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedExpert, setSelectedExpert] = useState<Expert | null>(null)
  const [showBookingModal, setShowBookingModal] = useState(false)
  const [bookingForm, setBookingForm] = useState<BookingFormData>({
    booking_type: 'session',
    title: '',
    description: '',
    duration_minutes: 60
  })
  const [bookingSuccess, setBookingSuccess] = useState(false)

  const { data: experts, isLoading, error } = useQuery({
    queryKey: ['experts'],
    queryFn: async (): Promise<Expert[]> => {
      const res = await fetch('/api/v1/experts/')
      if (!res.ok) throw new Error('Failed to load experts')
      return res.json()
    }
  })

  const bookingMutation = useMutation({
    mutationFn: async (expertId: number) => {
      if (!token) {
        throw new Error('Please log in to book an expert')
      }
      const res = await fetch(`/api/v1/experts/${expertId}/book`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          booking_type: bookingForm.booking_type,
          title: bookingForm.title || `Session with expert`,
          description: bookingForm.description,
          duration_minutes: bookingForm.duration_minutes
        })
      })
      if (res.status === 401 || res.status === 403) {
        throw new Error('Please log in to book an expert')
      }
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to book expert')
      }
      return res.json()
    },
    onSuccess: () => {
      setBookingSuccess(true)
      setTimeout(() => {
        setShowBookingModal(false)
        setBookingSuccess(false)
        setBookingForm({ booking_type: 'session', title: '', description: '', duration_minutes: 60 })
      }, 2000)
    }
  })

  const filteredExperts = experts?.filter(e => {
    if (!searchQuery) return true
    const q = searchQuery.toLowerCase()
    return (
      e.name.toLowerCase().includes(q) ||
      e.headline?.toLowerCase().includes(q) ||
      e.skills.some(s => s.toLowerCase().includes(q)) ||
      e.specialization.some(s => s.toLowerCase().includes(q))
    )
  }) || []

  const openBooking = (expert: Expert) => {
    setSelectedExpert(expert)
    setShowBookingModal(true)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Expert Marketplace</h1>
        <p className="text-gray-600">Find vetted operators to help you execute your business ideas.</p>
      </div>

      <div className="mb-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by name, skill, or specialty..."
            className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
      </div>

      {isLoading && (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500">Loading experts...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded-xl border border-red-200">
          Failed to load experts. Please try again later.
        </div>
      )}

      {!isLoading && !error && filteredExperts.length === 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <User className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Experts Found</h3>
          <p className="text-gray-500">
            {searchQuery ? 'Try a different search term.' : 'Experts will be listed here once available.'}
          </p>
        </div>
      )}

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredExperts.map((expert) => (
          <div key={expert.id} className="bg-white rounded-xl border border-gray-200 p-6 hover:border-gray-300 hover:shadow-md transition-all">
            <div className="flex items-start gap-4 mb-4">
              <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center text-white text-xl font-bold">
                {expert.name.charAt(0)}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 truncate">{expert.name}</h3>
                {expert.headline && (
                  <p className="text-sm text-gray-500 line-clamp-1">{expert.headline}</p>
                )}
                <div className="flex items-center gap-1 mt-1">
                  <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
                  <span className="text-sm text-gray-600">4.9</span>
                  <span className="text-gray-400 mx-1">•</span>
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span className="text-sm text-green-600">Verified</span>
                </div>
              </div>
            </div>

            {expert.bio && (
              <p className="text-sm text-gray-600 mb-4 line-clamp-2">{expert.bio}</p>
            )}

            {(expert.skills.length > 0 || expert.specialization.length > 0) && (
              <div className="flex flex-wrap gap-1.5 mb-4">
                {[...expert.skills, ...expert.specialization].slice(0, 4).map((skill, i) => (
                  <span key={i} className="px-2 py-0.5 bg-purple-50 text-purple-700 text-xs rounded-full">
                    {skill}
                  </span>
                ))}
                {[...expert.skills, ...expert.specialization].length > 4 && (
                  <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">
                    +{[...expert.skills, ...expert.specialization].length - 4}
                  </span>
                )}
              </div>
            )}

            <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
              {expert.hourly_rate_cents && (
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {formatCents(expert.hourly_rate_cents)}/hr
                </span>
              )}
              {expert.fixed_price_cents && (
                <span className="flex items-center gap-1">
                  <DollarSign className="w-4 h-4" />
                  From {formatCents(expert.fixed_price_cents)}
                </span>
              )}
              {expert.success_fee_bps && (
                <span className="flex items-center gap-1">
                  <Briefcase className="w-4 h-4" />
                  {(expert.success_fee_bps / 100).toFixed(0)}% success fee
                </span>
              )}
            </div>

            {isAuthenticated ? (
              <button
                onClick={() => openBooking(expert)}
                className="w-full py-2.5 bg-black text-white rounded-lg font-medium hover:bg-gray-800 transition-colors"
              >
                Book Consultation
              </button>
            ) : (
              <Link
                to="/login?next=/build/experts"
                className="block w-full py-2.5 bg-black text-white rounded-lg font-medium hover:bg-gray-800 transition-colors text-center"
              >
                Sign In to Book
              </Link>
            )}
          </div>
        ))}
      </div>

      {showBookingModal && selectedExpert && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Book Expert</h2>
              <button
                onClick={() => setShowBookingModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {bookingSuccess ? (
              <div className="text-center py-8">
                <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Booking Submitted!</h3>
                <p className="text-gray-600">We'll notify you when the expert confirms.</p>
              </div>
            ) : (
              <form onSubmit={(e) => { e.preventDefault(); bookingMutation.mutate(selectedExpert.id) }}>
                <div className="flex items-center gap-3 mb-6 p-3 bg-gray-50 rounded-lg">
                  <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold">
                    {selectedExpert.name.charAt(0)}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{selectedExpert.name}</p>
                    <p className="text-sm text-gray-500">{selectedExpert.headline}</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Session Type</label>
                    <select
                      value={bookingForm.booking_type}
                      onChange={(e) => setBookingForm({ ...bookingForm, booking_type: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="session">Quick Session (1hr)</option>
                      <option value="project">Project Consultation</option>
                      <option value="retainer">Monthly Retainer</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                    <input
                      type="text"
                      value={bookingForm.title}
                      onChange={(e) => setBookingForm({ ...bookingForm, title: e.target.value })}
                      placeholder="Brief description of what you need help with"
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Details</label>
                    <textarea
                      value={bookingForm.description}
                      onChange={(e) => setBookingForm({ ...bookingForm, description: e.target.value })}
                      placeholder="Describe your project, goals, and what expertise you need..."
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                    />
                  </div>
                </div>

                {bookingMutation.error && (
                  <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
                    {bookingMutation.error.message}
                  </div>
                )}

                <div className="flex gap-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setShowBookingModal(false)}
                    className="flex-1 py-2.5 border border-gray-200 rounded-lg font-medium hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={bookingMutation.isPending}
                    className="flex-1 py-2.5 bg-black text-white rounded-lg font-medium hover:bg-gray-800 disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {bookingMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Booking...
                      </>
                    ) : (
                      <>
                        <Calendar className="w-4 h-4" />
                        Request Booking
                      </>
                    )}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
