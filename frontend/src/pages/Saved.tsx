import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Bookmark, Trash2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

type Opportunity = {
  id: number
  title: string
  description: string
  category: string
  market_size?: string | null
  ai_competition_level?: string | null
  created_at?: string
}

type WatchlistItem = {
  id: number
  opportunity_id: number
  created_at: string
  opportunity?: Opportunity | null
}

export default function Saved() {
  const { token } = useAuthStore()
  const queryClient = useQueryClient()

  const watchlistQuery = useQuery({
    queryKey: ['watchlist'],
    queryFn: async (): Promise<WatchlistItem[]> => {
      const res = await fetch('/api/v1/watchlist/', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to load saved opportunities')
      return (await res.json()) as WatchlistItem[]
    },
  })

  const remove = useMutation({
    mutationFn: async (opportunityId: number) => {
      const res = await fetch(`/api/v1/watchlist/opportunity/${opportunityId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok && res.status !== 204) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data?.detail || 'Failed to remove')
      }
      return true
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] })
    },
  })

  const items = watchlistQuery.data ?? []

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-yellow-100 rounded-xl flex items-center justify-center">
            <Bookmark className="w-5 h-5 text-yellow-700" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Saved</h1>
            <p className="text-gray-600">Your watchlist of opportunities</p>
          </div>
        </div>
      </div>

      {watchlistQuery.isLoading && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">Loading saved opportunities…</div>
      )}

      {watchlistQuery.isError && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 text-red-700">
          Failed to load saved opportunities. Please try again.
        </div>
      )}

      {!watchlistQuery.isLoading && items.length === 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-10 text-center">
          <p className="text-gray-600">No saved opportunities yet.</p>
          <p className="text-gray-500 text-sm mt-2">Go to Discover and click “Save” on an opportunity.</p>
        </div>
      )}

      <div className="grid gap-4">
        {items.map((item) => {
          const opp = item.opportunity
          return (
            <div key={item.id} className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                <div className="flex-1">
                  <div className="text-sm text-gray-500 mb-2">{opp?.category || '—'}</div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-2">{opp?.title || `Opportunity #${item.opportunity_id}`}</h2>
                  <p className="text-sm text-gray-600 line-clamp-3">{opp?.description || '—'}</p>
                  <div className="mt-3 flex flex-wrap gap-4 text-sm text-gray-600">
                    <div>Market: {opp?.market_size || '—'}</div>
                    <div>Competition: {opp?.ai_competition_level || '—'}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Link
                    to={`/opportunity/${item.opportunity_id}`}
                    className="px-3 py-2 rounded-lg border border-gray-200 text-gray-800 hover:bg-gray-50 font-medium"
                    title="View details"
                  >
                    View
                  </Link>
                  <button
                    type="button"
                    onClick={() => remove.mutate(item.opportunity_id)}
                    disabled={remove.isPending}
                    className="px-3 py-2 rounded-lg border border-gray-200 text-gray-800 hover:bg-gray-50 font-medium flex items-center gap-2 disabled:opacity-50"
                    title="Remove from saved"
                  >
                    <Trash2 className="w-4 h-4" />
                    Remove
                  </button>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

