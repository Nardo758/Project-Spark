import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Bookmark, Trash2, FolderPlus, Tag, StickyNote, Plus, X, Check } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { useState, useRef, useEffect } from 'react'
import { LifecycleTimeline, LifecycleStateBadge, type LifecycleState } from '../components/LifecycleTimeline'

type Opportunity = {
  id: number
  title: string
  description: string
  category: string
  market_size?: string | null
  ai_competition_level?: string | null
  created_at?: string
}

type UserTag = {
  id: number
  name: string
  color: string
}

type WatchlistItem = {
  id: number
  opportunity_id: number
  created_at: string
  collection_id?: number | null
  lifecycle_state?: LifecycleState
  state_changed_at?: string | null
  opportunity?: Opportunity | null
  tags?: UserTag[]
}

type Collection = {
  id: number
  name: string
  description?: string | null
  color: string
  created_at: string
}

const TAG_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16']

export default function Saved() {
  const { token } = useAuthStore()
  const queryClient = useQueryClient()
  const [selectedCollection, setSelectedCollection] = useState<number | null>(null)
  const [showNewCollection, setShowNewCollection] = useState(false)
  const [newCollectionName, setNewCollectionName] = useState('')
  const [showNewTag, setShowNewTag] = useState(false)
  const [newTagName, setNewTagName] = useState('')
  const [newTagColor, setNewTagColor] = useState(TAG_COLORS[0])
  const [activeTagDropdown, setActiveTagDropdown] = useState<number | null>(null)
  const [activeNoteEditor, setActiveNoteEditor] = useState<number | null>(null)
  const [noteContent, setNoteContent] = useState('')
  const [notesCache, setNotesCache] = useState<Record<number, string>>({})
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setActiveTagDropdown(null)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const watchlistQuery = useQuery({
    queryKey: ['watchlist', selectedCollection],
    queryFn: async (): Promise<WatchlistItem[]> => {
      const url = selectedCollection 
        ? `/api/v1/watchlist/?collection_id=${selectedCollection}`
        : '/api/v1/watchlist/'
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to load saved opportunities')
      return (await res.json()) as WatchlistItem[]
    },
  })

  const collectionsQuery = useQuery({
    queryKey: ['collections'],
    queryFn: async (): Promise<Collection[]> => {
      const res = await fetch('/api/v1/workhub/collections', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to load collections')
      return (await res.json()) as Collection[]
    },
  })

  const tagsQuery = useQuery({
    queryKey: ['tags'],
    queryFn: async (): Promise<UserTag[]> => {
      const res = await fetch('/api/v1/workhub/tags', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to load tags')
      return (await res.json()) as UserTag[]
    },
  })

  const createCollection = useMutation({
    mutationFn: async (name: string) => {
      const res = await fetch('/api/v1/workhub/collections', {
        method: 'POST',
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, color: TAG_COLORS[Math.floor(Math.random() * TAG_COLORS.length)] })
      })
      if (!res.ok) throw new Error('Failed to create collection')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collections'] })
      setNewCollectionName('')
      setShowNewCollection(false)
    }
  })

  const createTag = useMutation({
    mutationFn: async ({ name, color }: { name: string, color: string }) => {
      const res = await fetch('/api/v1/workhub/tags', {
        method: 'POST',
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, color })
      })
      if (!res.ok) throw new Error('Failed to create tag')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] })
      setNewTagName('')
      setShowNewTag(false)
    }
  })

  const invalidateWatchlist = () => {
    queryClient.invalidateQueries({ queryKey: ['watchlist'], exact: false })
    queryClient.invalidateQueries({ queryKey: ['watchlist', selectedCollection] })
  }

  const addTagToItem = useMutation({
    mutationFn: async ({ watchlistId, tagId }: { watchlistId: number, tagId: number }) => {
      const res = await fetch(`/api/v1/workhub/watchlist/${watchlistId}/tags/${tagId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!res.ok) throw new Error('Failed to add tag')
      return res.json()
    },
    onSuccess: () => invalidateWatchlist()
  })

  const removeTagFromItem = useMutation({
    mutationFn: async ({ watchlistId, tagId }: { watchlistId: number, tagId: number }) => {
      const res = await fetch(`/api/v1/workhub/watchlist/${watchlistId}/tags/${tagId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!res.ok && res.status !== 204) throw new Error('Failed to remove tag')
    },
    onSuccess: () => invalidateWatchlist()
  })

  const moveToCollection = useMutation({
    mutationFn: async ({ watchlistId, collectionId }: { watchlistId: number, collectionId: number | null }) => {
      const res = await fetch(`/api/v1/workhub/watchlist/${watchlistId}/collection`, {
        method: 'PUT',
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ collection_id: collectionId })
      })
      if (!res.ok) throw new Error('Failed to move item')
      return res.json()
    },
    onSuccess: () => invalidateWatchlist()
  })

  const fetchNote = async (opportunityId: number): Promise<string> => {
    try {
      const res = await fetch(`/api/v1/workhub/opportunities/${opportunityId}/note`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        return data?.content || ''
      }
    } catch (e) {
      console.error('Failed to fetch note', e)
    }
    return ''
  }

  const openNoteEditor = async (opportunityId: number) => {
    if (activeNoteEditor === opportunityId) {
      setActiveNoteEditor(null)
      setNoteContent('')
      return
    }
    
    let content = notesCache[opportunityId]
    if (content === undefined) {
      content = await fetchNote(opportunityId)
      setNotesCache(prev => ({ ...prev, [opportunityId]: content }))
    }
    setNoteContent(content)
    setActiveNoteEditor(opportunityId)
  }

  const saveNote = useMutation({
    mutationFn: async ({ opportunityId, content }: { opportunityId: number, content: string }) => {
      const res = await fetch(`/api/v1/workhub/opportunities/${opportunityId}/note`, {
        method: 'POST',
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content })
      })
      if (!res.ok) throw new Error('Failed to save note')
      return res.json()
    },
    onSuccess: (_, variables) => {
      setNotesCache(prev => ({ ...prev, [variables.opportunityId]: variables.content }))
      setActiveNoteEditor(null)
      setNoteContent('')
    }
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
    onSuccess: () => invalidateWatchlist(),
  })

  const items = watchlistQuery.data ?? []
  const collections = collectionsQuery.data ?? []
  const allTags = tagsQuery.data ?? []

  const getItemTags = (item: WatchlistItem): UserTag[] => {
    return item.tags || []
  }

  const isTagOnItem = (item: WatchlistItem, tagId: number): boolean => {
    return getItemTags(item).some(t => t.id === tagId)
  }

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

      <div className="flex gap-6">
        <div className="w-64 flex-shrink-0">
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                <FolderPlus className="w-4 h-4" />
                Collections
              </h3>
              <button
                onClick={() => setShowNewCollection(!showNewCollection)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <Plus className="w-4 h-4 text-gray-600" />
              </button>
            </div>

            {showNewCollection && (
              <div className="mb-3 flex gap-2">
                <input
                  type="text"
                  value={newCollectionName}
                  onChange={(e) => setNewCollectionName(e.target.value)}
                  placeholder="Collection name"
                  className="flex-1 px-2 py-1 text-sm border rounded"
                />
                <button
                  onClick={() => newCollectionName && createCollection.mutate(newCollectionName)}
                  disabled={!newCollectionName || createCollection.isPending}
                  className="px-2 py-1 bg-gray-900 text-white text-sm rounded disabled:opacity-50"
                >
                  Add
                </button>
              </div>
            )}

            <div className="space-y-1">
              <button
                onClick={() => setSelectedCollection(null)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                  selectedCollection === null ? 'bg-gray-100 font-medium' : 'hover:bg-gray-50'
                }`}
              >
                All Saved ({watchlistQuery.data?.length || 0})
              </button>
              {collections.map((col) => (
                <button
                  key={col.id}
                  onClick={() => setSelectedCollection(col.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm flex items-center gap-2 transition-colors ${
                    selectedCollection === col.id ? 'bg-gray-100 font-medium' : 'hover:bg-gray-50'
                  }`}
                >
                  <span 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: col.color }}
                  />
                  {col.name}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-4 mt-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                <Tag className="w-4 h-4" />
                Tags
              </h3>
              <button
                onClick={() => setShowNewTag(!showNewTag)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <Plus className="w-4 h-4 text-gray-600" />
              </button>
            </div>

            {showNewTag && (
              <div className="mb-3 space-y-2">
                <input
                  type="text"
                  value={newTagName}
                  onChange={(e) => setNewTagName(e.target.value)}
                  placeholder="Tag name"
                  className="w-full px-2 py-1 text-sm border rounded"
                />
                <div className="flex gap-1 flex-wrap">
                  {TAG_COLORS.map((color) => (
                    <button
                      key={color}
                      onClick={() => setNewTagColor(color)}
                      className={`w-5 h-5 rounded-full ${newTagColor === color ? 'ring-2 ring-offset-1 ring-gray-400' : ''}`}
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
                <button
                  onClick={() => newTagName && createTag.mutate({ name: newTagName, color: newTagColor })}
                  disabled={!newTagName || createTag.isPending}
                  className="w-full px-2 py-1 bg-gray-900 text-white text-sm rounded disabled:opacity-50"
                >
                  Create Tag
                </button>
              </div>
            )}

            <div className="flex flex-wrap gap-2">
              {allTags.map((tag) => (
                <span
                  key={tag.id}
                  className="px-2 py-1 text-xs rounded-full text-white"
                  style={{ backgroundColor: tag.color }}
                >
                  {tag.name}
                </span>
              ))}
              {allTags.length === 0 && !showNewTag && (
                <p className="text-sm text-gray-500">No tags yet</p>
              )}
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-4 mt-4">
            <h3 className="font-semibold text-gray-900 mb-3">Journey Stages</h3>
            <div className="space-y-2">
              {[
                { state: 'saved', label: 'Saved', color: '#3b82f6' },
                { state: 'analyzing', label: 'Analyzing', color: '#8b5cf6' },
                { state: 'planning', label: 'Planning', color: '#f59e0b' },
                { state: 'executing', label: 'Executing', color: '#10b981' },
                { state: 'launched', label: 'Launched', color: '#22c55e' },
                { state: 'paused', label: 'Paused', color: '#f97316' },
                { state: 'archived', label: 'Archived', color: '#9ca3af' },
              ].map(({ state, label, color }) => {
                const count = items.filter(i => (i.lifecycle_state || 'saved') === state).length
                return (
                  <div key={state} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
                      <span className="text-sm text-gray-700">{label}</span>
                    </div>
                    <span className="text-sm text-gray-500">{count}</span>
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        <div className="flex-1">
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
              <p className="text-gray-600">No saved opportunities {selectedCollection ? 'in this collection' : 'yet'}.</p>
              <p className="text-gray-500 text-sm mt-2">
                {selectedCollection ? 'Move opportunities here from your watchlist.' : 'Go to Discover and click "Save" on an opportunity.'}
              </p>
            </div>
          )}

          <div className="space-y-4">
            {items.map((item) => {
              const opp = item.opportunity
              const itemTags = getItemTags(item)

              return (
                <div key={item.id} className="bg-white rounded-xl border border-gray-200 p-6">
                  <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2 flex-wrap">
                        <LifecycleTimeline 
                          watchlistId={item.id} 
                          currentState={item.lifecycle_state || 'saved'} 
                          stateChangedAt={item.state_changed_at || undefined}
                          compact 
                        />
                        <span className="text-sm text-gray-500">{opp?.category || '—'}</span>
                        {itemTags.map((tag) => (
                          <span
                            key={tag.id}
                            className="px-2 py-0.5 text-xs rounded-full text-white flex items-center gap-1"
                            style={{ backgroundColor: tag.color }}
                          >
                            {tag.name}
                            <button
                              onClick={() => removeTagFromItem.mutate({ watchlistId: item.id, tagId: tag.id })}
                              className="hover:opacity-70"
                            >
                              <X className="w-3 h-3" />
                            </button>
                          </span>
                        ))}
                      </div>
                      <h2 className="text-lg font-semibold text-gray-900 mb-2">{opp?.title || `Opportunity #${item.opportunity_id}`}</h2>
                      <p className="text-sm text-gray-600 line-clamp-3">{opp?.description || '—'}</p>
                      <div className="mt-3 flex flex-wrap gap-4 text-sm text-gray-600">
                        <div>Market: {opp?.market_size || '—'}</div>
                        <div>Competition: {opp?.ai_competition_level || '—'}</div>
                      </div>

                      {activeNoteEditor === item.opportunity_id && (
                        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                          <textarea
                            value={noteContent}
                            onChange={(e) => setNoteContent(e.target.value)}
                            placeholder="Add your notes about this opportunity..."
                            className="w-full p-2 text-sm border rounded-lg resize-none"
                            rows={3}
                          />
                          <div className="flex justify-end gap-2 mt-2">
                            <button
                              onClick={() => { setActiveNoteEditor(null); setNoteContent('') }}
                              className="px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 rounded"
                            >
                              Cancel
                            </button>
                            <button
                              onClick={() => saveNote.mutate({ opportunityId: item.opportunity_id, content: noteContent })}
                              disabled={!noteContent || saveNote.isPending}
                              className="px-3 py-1 text-sm bg-gray-900 text-white rounded disabled:opacity-50"
                            >
                              Save Note
                            </button>
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="flex flex-col gap-2">
                      <div className="flex items-center gap-2">
                        <Link
                          to={`/opportunity/${item.opportunity_id}`}
                          className="px-3 py-2 rounded-lg border border-gray-200 text-gray-800 hover:bg-gray-50 font-medium"
                          title="View details"
                        >
                          View
                        </Link>

                        <div className="relative" ref={activeTagDropdown === item.id ? dropdownRef : null}>
                          <button
                            onClick={() => setActiveTagDropdown(activeTagDropdown === item.id ? null : item.id)}
                            className="p-2 rounded-lg border border-gray-200 text-gray-800 hover:bg-gray-50"
                            title="Add tags"
                          >
                            <Tag className="w-4 h-4" />
                          </button>
                          
                          {activeTagDropdown === item.id && (
                            <div className="absolute right-0 top-full mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10 p-2">
                              <p className="text-xs text-gray-500 mb-2">Add tags:</p>
                              {allTags.length === 0 && (
                                <p className="text-sm text-gray-500">Create tags first</p>
                              )}
                              {allTags.map((tag) => (
                                <button
                                  key={tag.id}
                                  onClick={() => {
                                    if (isTagOnItem(item, tag.id)) {
                                      removeTagFromItem.mutate({ watchlistId: item.id, tagId: tag.id })
                                    } else {
                                      addTagToItem.mutate({ watchlistId: item.id, tagId: tag.id })
                                    }
                                  }}
                                  className="w-full text-left px-2 py-1 text-sm rounded hover:bg-gray-50 flex items-center gap-2"
                                >
                                  <span
                                    className="w-3 h-3 rounded-full"
                                    style={{ backgroundColor: tag.color }}
                                  />
                                  {tag.name}
                                  {isTagOnItem(item, tag.id) && <Check className="w-3 h-3 ml-auto text-green-600" />}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>

                        <button
                          onClick={() => openNoteEditor(item.opportunity_id)}
                          className="p-2 rounded-lg border border-gray-200 text-gray-800 hover:bg-gray-50"
                          title={notesCache[item.opportunity_id] ? "Edit note" : "Add note"}
                        >
                          <StickyNote className={`w-4 h-4 ${notesCache[item.opportunity_id] ? 'text-yellow-600' : ''}`} />
                        </button>

                        <button
                          type="button"
                          onClick={() => remove.mutate(item.opportunity_id)}
                          disabled={remove.isPending}
                          className="p-2 rounded-lg border border-gray-200 text-gray-800 hover:bg-gray-50 disabled:opacity-50"
                          title="Remove from saved"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>

                      {collections.length > 0 && (
                        <select
                          value={item.collection_id || ''}
                          onChange={(e) => moveToCollection.mutate({ 
                            watchlistId: item.id, 
                            collectionId: e.target.value ? parseInt(e.target.value) : null 
                          })}
                          className="text-sm border border-gray-200 rounded-lg px-2 py-1"
                        >
                          <option value="">No collection</option>
                          {collections.map((col) => (
                            <option key={col.id} value={col.id}>{col.name}</option>
                          ))}
                        </select>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
