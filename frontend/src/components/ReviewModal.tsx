import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Star, X, Loader2 } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

interface ReviewModalProps {
  engagementId: number
  expertName: string
  onClose: () => void
}

interface ReviewData {
  overall_rating: number
  expertise_rating?: number
  communication_rating?: number
  responsiveness_rating?: number
  value_for_money_rating?: number
  review_text?: string
  would_recommend?: boolean
  would_work_again?: boolean
}

function StarRating({ 
  value, 
  onChange, 
  label 
}: { 
  value: number
  onChange: (val: number) => void
  label: string
}) {
  const [hovered, setHovered] = useState(0)
  
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-slate-400">{label}</span>
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            className="p-1 hover:scale-110 transition-transform"
            onMouseEnter={() => setHovered(star)}
            onMouseLeave={() => setHovered(0)}
            onClick={() => onChange(star)}
          >
            <Star
              className={`w-5 h-5 ${
                star <= (hovered || value)
                  ? 'fill-yellow-400 text-yellow-400'
                  : 'text-slate-600'
              }`}
            />
          </button>
        ))}
      </div>
    </div>
  )
}

export default function ReviewModal({ engagementId, expertName, onClose }: ReviewModalProps) {
  const { token } = useAuthStore()
  const queryClient = useQueryClient()
  
  const [formData, setFormData] = useState<ReviewData>({
    overall_rating: 0,
    expertise_rating: 0,
    communication_rating: 0,
    responsiveness_rating: 0,
    value_for_money_rating: 0,
    review_text: '',
    would_recommend: undefined,
    would_work_again: undefined
  })
  
  const submitReview = useMutation({
    mutationFn: async (data: ReviewData) => {
      const payload: Record<string, unknown> = { overall_rating: data.overall_rating }
      if (data.expertise_rating && data.expertise_rating > 0) payload.expertise_rating = data.expertise_rating
      if (data.communication_rating && data.communication_rating > 0) payload.communication_rating = data.communication_rating
      if (data.responsiveness_rating && data.responsiveness_rating > 0) payload.responsiveness_rating = data.responsiveness_rating
      if (data.value_for_money_rating && data.value_for_money_rating > 0) payload.value_for_money_rating = data.value_for_money_rating
      if (data.review_text) payload.review_text = data.review_text
      if (data.would_recommend !== undefined) payload.would_recommend = data.would_recommend
      if (data.would_work_again !== undefined) payload.would_work_again = data.would_work_again
      
      const res = await fetch(`/api/v1/expert-network/engagements/${engagementId}/reviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to submit review')
      }
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-engagements'] })
      queryClient.invalidateQueries({ queryKey: ['engagement-detail', engagementId] })
      onClose()
    }
  })
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.overall_rating === 0) return
    submitReview.mutate(formData)
  }
  
  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <h2 className="text-xl font-semibold text-white">Review {expertName}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div className="space-y-4">
            <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
              <StarRating
                value={formData.overall_rating}
                onChange={(val) => setFormData(prev => ({ ...prev, overall_rating: val }))}
                label="Overall Rating *"
              />
            </div>
            
            <div className="grid gap-3">
              <StarRating
                value={formData.expertise_rating || 0}
                onChange={(val) => setFormData(prev => ({ ...prev, expertise_rating: val }))}
                label="Expertise"
              />
              <StarRating
                value={formData.communication_rating || 0}
                onChange={(val) => setFormData(prev => ({ ...prev, communication_rating: val }))}
                label="Communication"
              />
              <StarRating
                value={formData.responsiveness_rating || 0}
                onChange={(val) => setFormData(prev => ({ ...prev, responsiveness_rating: val }))}
                label="Responsiveness"
              />
              <StarRating
                value={formData.value_for_money_rating || 0}
                onChange={(val) => setFormData(prev => ({ ...prev, value_for_money_rating: val }))}
                label="Value for Money"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Your Review
            </label>
            <textarea
              value={formData.review_text}
              onChange={(e) => setFormData(prev => ({ ...prev, review_text: e.target.value }))}
              placeholder="Share your experience working with this expert..."
              rows={4}
              className="w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Would you recommend?
              </label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, would_recommend: true }))}
                  className={`flex-1 py-2 px-4 rounded-lg border transition-colors ${
                    formData.would_recommend === true
                      ? 'bg-green-600 border-green-500 text-white'
                      : 'border-slate-600 text-slate-400 hover:border-slate-500'
                  }`}
                >
                  Yes
                </button>
                <button
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, would_recommend: false }))}
                  className={`flex-1 py-2 px-4 rounded-lg border transition-colors ${
                    formData.would_recommend === false
                      ? 'bg-red-600 border-red-500 text-white'
                      : 'border-slate-600 text-slate-400 hover:border-slate-500'
                  }`}
                >
                  No
                </button>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Would you work again?
              </label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, would_work_again: true }))}
                  className={`flex-1 py-2 px-4 rounded-lg border transition-colors ${
                    formData.would_work_again === true
                      ? 'bg-green-600 border-green-500 text-white'
                      : 'border-slate-600 text-slate-400 hover:border-slate-500'
                  }`}
                >
                  Yes
                </button>
                <button
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, would_work_again: false }))}
                  className={`flex-1 py-2 px-4 rounded-lg border transition-colors ${
                    formData.would_work_again === false
                      ? 'bg-red-600 border-red-500 text-white'
                      : 'border-slate-600 text-slate-400 hover:border-slate-500'
                  }`}
                >
                  No
                </button>
              </div>
            </div>
          </div>
          
          {submitReview.isError && (
            <p className="text-red-400 text-sm">{submitReview.error.message}</p>
          )}
          
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 px-4 border border-slate-600 text-slate-300 rounded-lg hover:bg-slate-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={formData.overall_rating === 0 || submitReview.isPending}
              className="flex-1 py-3 px-4 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg hover:from-cyan-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
            >
              {submitReview.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                'Submit Review'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
