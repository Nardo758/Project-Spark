import { useState, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { X, Folder, Tag, Plus, Check, Bookmark } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

type Collection = {
  id: number
  name: string
  color: string
  icon: string
  opportunity_count: number
}

type TagType = {
  id: number
  name: string
  color: string
}

type Props = {
  opportunityId: number
  opportunityTitle: string
  isOpen: boolean
  onClose: () => void
  onSaved?: () => void
}

export default function SaveToWorkhubModal({ opportunityId, opportunityTitle, isOpen, onClose, onSaved }: Props) {
  const { token } = useAuthStore()
  const queryClient = useQueryClient()
  
  const [selectedCollection, setSelectedCollection] = useState<number | null>(null)
  const [selectedTags, setSelectedTags] = useState<number[]>([])
  const [notes, setNotes] = useState('')
  const [showNewCollection, setShowNewCollection] = useState(false)
  const [newCollectionName, setNewCollectionName] = useState('')
  const [showNewTag, setShowNewTag] = useState(false)
  const [newTagName, setNewTagName] = useState('')

  const collectionsQuery = useQuery({
    queryKey: ['collections'],
    enabled: isOpen && Boolean(token),
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
    enabled: isOpen && Boolean(token),
    queryFn: async (): Promise<TagType[]> => {
      const res = await fetch('/api/v1/workhub/tags', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to fetch tags')
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
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['collections'] })
      setSelectedCollection(data.id)
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
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['tags'] })
      setSelectedTags(prev => [...prev, data.id])
      setNewTagName('')
      setShowNewTag(false)
    },
  })

  const saveMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/v1/workhub/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          opportunity_id: opportunityId,
          collection_id: selectedCollection,
          tag_ids: selectedTags,
          notes: notes || null,
        }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to save')
      }
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['saved-opportunities'] })
      queryClient.invalidateQueries({ queryKey: ['workhub-stats'] })
      queryClient.invalidateQueries({ queryKey: ['collections'] })
      onSaved?.()
      onClose()
    },
  })

  useEffect(() => {
    if (!isOpen) {
      setSelectedCollection(null)
      setSelectedTags([])
      setNotes('')
      setShowNewCollection(false)
      setShowNewTag(false)
    }
  }, [isOpen])

  if (!isOpen) return null

  const collections = collectionsQuery.data || []
  const tags = tagsQuery.data || []

  const toggleTag = (tagId: number) => {
    setSelectedTags(prev => 
      prev.includes(tagId) ? prev.filter(id => id !== tagId) : [...prev, tagId]
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-stone-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-violet-100 rounded-lg">
              <Bookmark className="w-5 h-5 text-violet-600" />
            </div>
            <h2 className="text-lg font-semibold text-stone-900">Save to Workhub</h2>
          </div>
          <button onClick={onClose} className="p-2 text-stone-400 hover:text-stone-600 rounded-lg hover:bg-stone-50">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-5">
          <div className="p-3 bg-stone-50 rounded-lg">
            <p className="text-sm text-stone-500">Saving opportunity:</p>
            <p className="font-medium text-stone-900 truncate">{opportunityTitle}</p>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-stone-700">Collection</label>
              <button
                onClick={() => setShowNewCollection(true)}
                className="text-xs text-violet-600 hover:text-violet-700 flex items-center gap-1"
              >
                <Plus className="w-3 h-3" />
                New
              </button>
            </div>
            
            {showNewCollection && (
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={newCollectionName}
                  onChange={e => setNewCollectionName(e.target.value)}
                  placeholder="Collection name"
                  className="flex-1 px-3 py-2 text-sm border border-stone-200 rounded-lg focus:outline-none focus:border-violet-400"
                  autoFocus
                />
                <button
                  onClick={() => newCollectionName.trim() && createCollectionMutation.mutate(newCollectionName.trim())}
                  disabled={!newCollectionName.trim() || createCollectionMutation.isPending}
                  className="px-3 py-2 bg-violet-600 text-white text-sm rounded-lg disabled:opacity-50"
                >
                  Add
                </button>
                <button
                  onClick={() => { setShowNewCollection(false); setNewCollectionName(''); }}
                  className="px-3 py-2 text-stone-500 hover:text-stone-700"
                >
                  Cancel
                </button>
              </div>
            )}
            
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => setSelectedCollection(null)}
                className={`flex items-center gap-2 p-3 rounded-lg border text-sm text-left transition-all ${
                  selectedCollection === null 
                    ? 'border-violet-400 bg-violet-50 text-violet-700' 
                    : 'border-stone-200 text-stone-600 hover:border-stone-300'
                }`}
              >
                <Folder className="w-4 h-4" />
                No Collection
                {selectedCollection === null && <Check className="w-4 h-4 ml-auto" />}
              </button>
              {collections.map(col => (
                <button
                  key={col.id}
                  onClick={() => setSelectedCollection(col.id)}
                  className={`flex items-center gap-2 p-3 rounded-lg border text-sm text-left transition-all ${
                    selectedCollection === col.id 
                      ? 'border-violet-400 bg-violet-50 text-violet-700' 
                      : 'border-stone-200 text-stone-600 hover:border-stone-300'
                  }`}
                >
                  <Folder className="w-4 h-4" style={{ color: col.color }} />
                  <span className="truncate">{col.name}</span>
                  {selectedCollection === col.id && <Check className="w-4 h-4 ml-auto flex-shrink-0" />}
                </button>
              ))}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-stone-700">Tags</label>
              <button
                onClick={() => setShowNewTag(true)}
                className="text-xs text-emerald-600 hover:text-emerald-700 flex items-center gap-1"
              >
                <Plus className="w-3 h-3" />
                New
              </button>
            </div>
            
            {showNewTag && (
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={newTagName}
                  onChange={e => setNewTagName(e.target.value)}
                  placeholder="Tag name"
                  className="flex-1 px-3 py-2 text-sm border border-stone-200 rounded-lg focus:outline-none focus:border-emerald-400"
                  autoFocus
                />
                <button
                  onClick={() => newTagName.trim() && createTagMutation.mutate(newTagName.trim())}
                  disabled={!newTagName.trim() || createTagMutation.isPending}
                  className="px-3 py-2 bg-emerald-600 text-white text-sm rounded-lg disabled:opacity-50"
                >
                  Add
                </button>
                <button
                  onClick={() => { setShowNewTag(false); setNewTagName(''); }}
                  className="px-3 py-2 text-stone-500 hover:text-stone-700"
                >
                  Cancel
                </button>
              </div>
            )}
            
            <div className="flex flex-wrap gap-2">
              {tags.length === 0 && !showNewTag && (
                <p className="text-xs text-stone-500">No tags yet. Create one to organize your opportunities.</p>
              )}
              {tags.map(tag => (
                <button
                  key={tag.id}
                  onClick={() => toggleTag(tag.id)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                    selectedTags.includes(tag.id)
                      ? 'bg-violet-600 text-white'
                      : 'bg-stone-100 text-stone-600 hover:bg-stone-200'
                  }`}
                  style={!selectedTags.includes(tag.id) ? { backgroundColor: tag.color + '20', color: tag.color } : {}}
                >
                  <Tag className="w-3 h-3" />
                  {tag.name}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-stone-700 mb-2 block">Notes (optional)</label>
            <textarea
              value={notes}
              onChange={e => setNotes(e.target.value)}
              placeholder="Add notes about why you're saving this opportunity..."
              className="w-full px-3 py-2 text-sm border border-stone-200 rounded-lg focus:outline-none focus:border-violet-400 resize-none"
              rows={3}
            />
          </div>
        </div>

        <div className="px-6 py-4 border-t border-stone-100 bg-stone-50 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-stone-600 hover:text-stone-800 font-medium"
          >
            Cancel
          </button>
          <button
            onClick={() => saveMutation.mutate()}
            disabled={saveMutation.isPending}
            className="flex items-center gap-2 px-5 py-2 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700 disabled:opacity-50"
          >
            {saveMutation.isPending ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Bookmark className="w-4 h-4" />
                Save to Workhub
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
