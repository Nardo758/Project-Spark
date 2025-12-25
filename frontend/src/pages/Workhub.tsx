import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { 
  Folder, Tag, Plus, Search, Filter, MoreHorizontal, 
  Trash2, Edit2, ChevronRight, Sparkles, TrendingUp,
  Archive, Play, Pause, CheckCircle, Clock, Lightbulb
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

type Collection = {
  id: number
  name: string
  description: string | null
  color: string
  icon: string
  is_default: boolean
  opportunity_count: number
  created_at: string
}

type TagType = {
  id: number
  name: string
  color: string
  created_at: string
}

type SavedOpportunity = {
  id: number
  opportunity_id: number
  collection_id: number | null
  notes: string | null
  lifecycle_state: string
  created_at: string
  updated_at: string
  opportunity: {
    id: number
    title: string
    category: string
    severity: number
    market_size: string | null
    validation_count: number
  }
  tags: TagType[]
}

type WorkhubStats = {
  total_saved: number
  total_collections: number
  total_tags: number
  by_lifecycle_state: Record<string, number>
}

const lifecycleStates = [
  { key: 'saved', label: 'Saved', icon: Folder, color: 'bg-stone-100 text-stone-700' },
  { key: 'analyzing', label: 'Analyzing', icon: Search, color: 'bg-blue-100 text-blue-700' },
  { key: 'planning', label: 'Planning', icon: Lightbulb, color: 'bg-amber-100 text-amber-700' },
  { key: 'executing', label: 'Executing', icon: Play, color: 'bg-violet-100 text-violet-700' },
  { key: 'launched', label: 'Launched', icon: CheckCircle, color: 'bg-emerald-100 text-emerald-700' },
  { key: 'paused', label: 'Paused', icon: Pause, color: 'bg-orange-100 text-orange-700' },
  { key: 'archived', label: 'Archived', icon: Archive, color: 'bg-stone-100 text-stone-500' },
]

export default function Workhub() {
  const { token, isAuthenticated } = useAuthStore()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  const [selectedCollection, setSelectedCollection] = useState<number | null>(null)
  const [selectedTag, setSelectedTag] = useState<number | null>(null)
  const [selectedState, setSelectedState] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [showNewCollection, setShowNewCollection] = useState(false)
  const [newCollectionName, setNewCollectionName] = useState('')
  const [showNewTag, setShowNewTag] = useState(false)
  const [newTagName, setNewTagName] = useState('')

  const statsQuery = useQuery({
    queryKey: ['workhub-stats'],
    enabled: isAuthenticated && Boolean(token),
    queryFn: async (): Promise<WorkhubStats> => {
      const res = await fetch('/api/v1/workhub/stats', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to fetch stats')
      return res.json()
    },
  })

  const collectionsQuery = useQuery({
    queryKey: ['collections'],
    enabled: isAuthenticated && Boolean(token),
    queryFn: async (): Promise<Collection[]> => {
      const res = await fetch('/api/v1/workhub/collections', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to fetch collections')
      return res.json()
    },
  })

  const tagsQuery = useQuery({
    queryKey: ['tags'],
    enabled: isAuthenticated && Boolean(token),
    queryFn: async (): Promise<TagType[]> => {
      const res = await fetch('/api/v1/workhub/tags', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to fetch tags')
      return res.json()
    },
  })

  const savedQuery = useQuery({
    queryKey: ['saved-opportunities', selectedCollection, selectedTag, selectedState],
    enabled: isAuthenticated && Boolean(token),
    queryFn: async (): Promise<SavedOpportunity[]> => {
      const params = new URLSearchParams()
      if (selectedCollection) params.set('collection_id', String(selectedCollection))
      if (selectedTag) params.set('tag_id', String(selectedTag))
      if (selectedState) params.set('lifecycle_state', selectedState)
      const res = await fetch(`/api/v1/workhub/saved?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to fetch saved opportunities')
      return res.json()
    },
  })

  const createCollectionMutation = useMutation({
    mutationFn: async (name: string) => {
      const res = await fetch('/api/v1/workhub/collections', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ name }),
      })
      if (!res.ok) throw new Error('Failed to create collection')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collections'] })
      setNewCollectionName('')
      setShowNewCollection(false)
    },
  })

  const createTagMutation = useMutation({
    mutationFn: async (name: string) => {
      const res = await fetch('/api/v1/workhub/tags', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ name }),
      })
      if (!res.ok) throw new Error('Failed to create tag')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] })
      setNewTagName('')
      setShowNewTag(false)
    },
  })

  const updateStateMutation = useMutation({
    mutationFn: async ({ savedId, state }: { savedId: number; state: string }) => {
      const res = await fetch(`/api/v1/workhub/saved/${savedId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ lifecycle_state: state }),
      })
      if (!res.ok) throw new Error('Failed to update state')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['saved-opportunities'] })
      queryClient.invalidateQueries({ queryKey: ['workhub-stats'] })
    },
  })

  const deleteSavedMutation = useMutation({
    mutationFn: async (savedId: number) => {
      const res = await fetch(`/api/v1/workhub/saved/${savedId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to delete')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['saved-opportunities'] })
      queryClient.invalidateQueries({ queryKey: ['workhub-stats'] })
      queryClient.invalidateQueries({ queryKey: ['collections'] })
    },
  })

  if (!isAuthenticated) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <Folder className="w-16 h-16 mx-auto text-stone-300 mb-4" />
        <h1 className="text-2xl font-bold text-stone-900 mb-2">Sign in to access Workhub</h1>
        <p className="text-stone-600 mb-6">Save and organize opportunities, track your progress from idea to launch.</p>
        <button
          onClick={() => navigate('/login')}
          className="px-6 py-3 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700"
        >
          Sign In
        </button>
      </div>
    )
  }

  const stats = statsQuery.data
  const collections = collectionsQuery.data || []
  const tags = tagsQuery.data || []
  const savedOpportunities = savedQuery.data || []

  const filteredOpportunities = savedOpportunities.filter(so => 
    searchQuery === '' || 
    so.opportunity.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    so.opportunity.category.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="min-h-screen bg-stone-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-stone-900">Workhub</h1>
            <p className="text-stone-600 mt-1">Organize and track your opportunities from discovery to launch</p>
          </div>
          <button
            onClick={() => navigate('/discover')}
            className="flex items-center gap-2 px-4 py-2 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700"
          >
            <Plus className="w-4 h-4" />
            Find Opportunities
          </button>
        </div>

        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-xl border border-stone-200 p-4">
              <div className="text-2xl font-bold text-stone-900">{stats.total_saved}</div>
              <div className="text-sm text-stone-600">Saved Ideas</div>
            </div>
            <div className="bg-white rounded-xl border border-stone-200 p-4">
              <div className="text-2xl font-bold text-violet-600">{stats.by_lifecycle_state.executing || 0}</div>
              <div className="text-sm text-stone-600">In Progress</div>
            </div>
            <div className="bg-white rounded-xl border border-stone-200 p-4">
              <div className="text-2xl font-bold text-emerald-600">{stats.by_lifecycle_state.launched || 0}</div>
              <div className="text-sm text-stone-600">Launched</div>
            </div>
            <div className="bg-white rounded-xl border border-stone-200 p-4">
              <div className="text-2xl font-bold text-stone-900">{stats.total_collections}</div>
              <div className="text-sm text-stone-600">Collections</div>
            </div>
          </div>
        )}

        <div className="flex flex-wrap gap-2 mb-6">
          {lifecycleStates.map(state => {
            const count = stats?.by_lifecycle_state[state.key] || 0
            const Icon = state.icon
            return (
              <button
                key={state.key}
                onClick={() => setSelectedState(selectedState === state.key ? null : state.key)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                  selectedState === state.key 
                    ? 'bg-violet-600 text-white' 
                    : `${state.color} hover:ring-2 ring-violet-200`
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {state.label} ({count})
              </button>
            )
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1 space-y-4">
            <div className="bg-white rounded-xl border border-stone-200 p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-stone-900">Collections</h3>
                <button
                  onClick={() => setShowNewCollection(true)}
                  className="p-1 text-stone-400 hover:text-violet-600"
                >
                  <Plus className="w-4 h-4" />
                </button>
              </div>
              
              {showNewCollection && (
                <div className="mb-3 flex gap-2">
                  <input
                    type="text"
                    value={newCollectionName}
                    onChange={e => setNewCollectionName(e.target.value)}
                    placeholder="Collection name"
                    className="flex-1 px-3 py-1.5 text-sm border border-stone-200 rounded-lg focus:outline-none focus:border-violet-400"
                    autoFocus
                  />
                  <button
                    onClick={() => newCollectionName.trim() && createCollectionMutation.mutate(newCollectionName.trim())}
                    disabled={!newCollectionName.trim()}
                    className="px-3 py-1.5 bg-violet-600 text-white text-sm rounded-lg disabled:opacity-50"
                  >
                    Add
                  </button>
                </div>
              )}
              
              <div className="space-y-1">
                <button
                  onClick={() => setSelectedCollection(null)}
                  className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-left transition-colors ${
                    selectedCollection === null ? 'bg-violet-50 text-violet-700' : 'text-stone-600 hover:bg-stone-50'
                  }`}
                >
                  <Folder className="w-4 h-4" />
                  All Saved ({stats?.total_saved || 0})
                </button>
                {collections.map(col => (
                  <button
                    key={col.id}
                    onClick={() => setSelectedCollection(selectedCollection === col.id ? null : col.id)}
                    className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-left transition-colors ${
                      selectedCollection === col.id ? 'bg-violet-50 text-violet-700' : 'text-stone-600 hover:bg-stone-50'
                    }`}
                  >
                    <Folder className="w-4 h-4" style={{ color: col.color }} />
                    {col.name} ({col.opportunity_count})
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl border border-stone-200 p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-stone-900">Tags</h3>
                <button
                  onClick={() => setShowNewTag(true)}
                  className="p-1 text-stone-400 hover:text-violet-600"
                >
                  <Plus className="w-4 h-4" />
                </button>
              </div>
              
              {showNewTag && (
                <div className="mb-3 flex gap-2">
                  <input
                    type="text"
                    value={newTagName}
                    onChange={e => setNewTagName(e.target.value)}
                    placeholder="Tag name"
                    className="flex-1 px-3 py-1.5 text-sm border border-stone-200 rounded-lg focus:outline-none focus:border-violet-400"
                    autoFocus
                  />
                  <button
                    onClick={() => newTagName.trim() && createTagMutation.mutate(newTagName.trim())}
                    disabled={!newTagName.trim()}
                    className="px-3 py-1.5 bg-emerald-600 text-white text-sm rounded-lg disabled:opacity-50"
                  >
                    Add
                  </button>
                </div>
              )}
              
              <div className="flex flex-wrap gap-2">
                {tags.map(tag => (
                  <button
                    key={tag.id}
                    onClick={() => setSelectedTag(selectedTag === tag.id ? null : tag.id)}
                    className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium transition-all ${
                      selectedTag === tag.id 
                        ? 'bg-violet-600 text-white' 
                        : 'bg-stone-100 text-stone-600 hover:bg-stone-200'
                    }`}
                    style={selectedTag !== tag.id ? { backgroundColor: tag.color + '20', color: tag.color } : {}}
                  >
                    <Tag className="w-3 h-3" />
                    {tag.name}
                  </button>
                ))}
                {tags.length === 0 && !showNewTag && (
                  <p className="text-xs text-stone-500">No tags yet</p>
                )}
              </div>
            </div>
          </div>

          <div className="lg:col-span-3">
            <div className="bg-white rounded-xl border border-stone-200 p-4 mb-4">
              <div className="flex items-center gap-3">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    placeholder="Search saved opportunities..."
                    className="w-full pl-10 pr-4 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:border-violet-400"
                  />
                </div>
                <button className="flex items-center gap-2 px-3 py-2 border border-stone-200 rounded-lg text-sm text-stone-600 hover:bg-stone-50">
                  <Filter className="w-4 h-4" />
                  Filter
                </button>
              </div>
            </div>

            {filteredOpportunities.length === 0 ? (
              <div className="bg-white rounded-xl border border-stone-200 p-12 text-center">
                <Folder className="w-12 h-12 mx-auto text-stone-300 mb-4" />
                <h3 className="text-lg font-semibold text-stone-900 mb-2">No opportunities saved yet</h3>
                <p className="text-stone-600 mb-4">Browse the Discover page and save opportunities you want to work on.</p>
                <button
                  onClick={() => navigate('/discover')}
                  className="px-4 py-2 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700"
                >
                  Discover Opportunities
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {filteredOpportunities.map(so => {
                  const stateInfo = lifecycleStates.find(s => s.key === so.lifecycle_state) || lifecycleStates[0]
                  const StateIcon = stateInfo.icon
                  return (
                    <div
                      key={so.id}
                      className="bg-white rounded-xl border border-stone-200 p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-xs font-medium text-stone-500 uppercase">{so.opportunity.category}</span>
                            <span className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${stateInfo.color}`}>
                              <StateIcon className="w-3 h-3" />
                              {stateInfo.label}
                            </span>
                          </div>
                          <h3 
                            className="text-lg font-semibold text-stone-900 mb-1 cursor-pointer hover:text-violet-600"
                            onClick={() => navigate(`/opportunity/${so.opportunity_id}/hub`)}
                          >
                            {so.opportunity.title}
                          </h3>
                          <div className="flex items-center gap-4 text-sm text-stone-500">
                            <span className="flex items-center gap-1">
                              <TrendingUp className="w-3.5 h-3.5" />
                              {so.opportunity.market_size || 'Unknown'}
                            </span>
                            <span>{so.opportunity.validation_count} validations</span>
                          </div>
                          {so.tags.length > 0 && (
                            <div className="flex gap-1 mt-2">
                              {so.tags.map(tag => (
                                <span
                                  key={tag.id}
                                  className="px-2 py-0.5 rounded-full text-xs"
                                  style={{ backgroundColor: tag.color + '20', color: tag.color }}
                                >
                                  {tag.name}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="bg-emerald-100 text-emerald-700 px-3 py-2 rounded-xl text-center">
                            <div className="text-xl font-bold">{so.opportunity.severity * 20}</div>
                            <div className="text-xs">Score</div>
                          </div>
                          <div className="relative group">
                            <button className="p-2 text-stone-400 hover:text-stone-600 rounded-lg hover:bg-stone-50">
                              <MoreHorizontal className="w-5 h-5" />
                            </button>
                            <div className="absolute right-0 top-full mt-1 bg-white border border-stone-200 rounded-lg shadow-lg py-1 w-48 hidden group-hover:block z-10">
                              <button
                                onClick={() => navigate(`/opportunity/${so.opportunity_id}/hub`)}
                                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-stone-700 hover:bg-stone-50"
                              >
                                <ChevronRight className="w-4 h-4" />
                                Open Hub
                              </button>
                              {so.lifecycle_state !== 'analyzing' && (
                                <button
                                  onClick={() => updateStateMutation.mutate({ savedId: so.id, state: 'analyzing' })}
                                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-stone-700 hover:bg-stone-50"
                                >
                                  <Search className="w-4 h-4" />
                                  Start Analyzing
                                </button>
                              )}
                              {so.lifecycle_state !== 'planning' && (
                                <button
                                  onClick={() => updateStateMutation.mutate({ savedId: so.id, state: 'planning' })}
                                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-stone-700 hover:bg-stone-50"
                                >
                                  <Lightbulb className="w-4 h-4" />
                                  Start Planning
                                </button>
                              )}
                              {so.lifecycle_state !== 'executing' && (
                                <button
                                  onClick={() => updateStateMutation.mutate({ savedId: so.id, state: 'executing' })}
                                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-stone-700 hover:bg-stone-50"
                                >
                                  <Play className="w-4 h-4" />
                                  Start Building
                                </button>
                              )}
                              <hr className="my-1 border-stone-100" />
                              <button
                                onClick={() => deleteSavedMutation.mutate(so.id)}
                                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                              >
                                <Trash2 className="w-4 h-4" />
                                Remove
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
