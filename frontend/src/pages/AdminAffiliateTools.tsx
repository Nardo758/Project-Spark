import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { 
  ArrowLeft, Edit2, ExternalLink, Loader2, Plus, 
  Save, Trash2, X, Wrench, DollarSign
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

type AffiliateTool = {
  id: number
  name: string
  category: string
  description: string | null
  base_url: string
  affiliate_url: string | null
  affiliate_code: string | null
  commission_rate: number | null
  commission_type: string | null
  price_display: string | null
  best_for: string | null
  logo_url: string | null
  is_active: boolean
  priority: number
  click_count: number
  conversion_count: number
  created_at: string | null
}

type ToolFormData = {
  name: string
  category: string
  description: string
  base_url: string
  affiliate_url: string
  affiliate_code: string
  commission_rate: string
  commission_type: string
  price_display: string
  best_for: string
  logo_url: string
  priority: string
  is_active: boolean
}

const categories = ['design', 'development', 'talent', 'nocode', 'marketing', 'project', 'financial']

const emptyForm: ToolFormData = {
  name: '',
  category: 'development',
  description: '',
  base_url: '',
  affiliate_url: '',
  affiliate_code: '',
  commission_rate: '',
  commission_type: 'percentage',
  price_display: '',
  best_for: '',
  logo_url: '',
  priority: '0',
  is_active: true,
}

export default function AdminAffiliateTools() {
  const { token } = useAuthStore()
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editingTool, setEditingTool] = useState<AffiliateTool | null>(null)
  const [formData, setFormData] = useState<ToolFormData>(emptyForm)
  const [filterCategory, setFilterCategory] = useState<string>('all')

  const toolsQuery = useQuery({
    queryKey: ['admin-affiliate-tools'],
    queryFn: async (): Promise<AffiliateTool[]> => {
      const res = await fetch('/api/v1/affiliate-tools/admin/all', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to fetch tools')
      return await res.json()
    },
  })

  const createMutation = useMutation({
    mutationFn: async (data: ToolFormData) => {
      const res = await fetch('/api/v1/affiliate-tools/admin/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          name: data.name,
          category: data.category,
          description: data.description || null,
          base_url: data.base_url,
          affiliate_url: data.affiliate_url || null,
          affiliate_code: data.affiliate_code || null,
          commission_rate: data.commission_rate ? parseFloat(data.commission_rate) : null,
          commission_type: data.commission_type || null,
          price_display: data.price_display || null,
          best_for: data.best_for || null,
          logo_url: data.logo_url || null,
          priority: parseInt(data.priority) || 0,
          is_active: data.is_active,
        }),
      })
      if (!res.ok) throw new Error('Failed to create tool')
      return await res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-affiliate-tools'] })
      setShowForm(false)
      setFormData(emptyForm)
    },
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<ToolFormData> }) => {
      const res = await fetch(`/api/v1/affiliate-tools/admin/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          ...data,
          commission_rate: data.commission_rate ? parseFloat(data.commission_rate) : null,
          priority: data.priority ? parseInt(data.priority) : undefined,
        }),
      })
      if (!res.ok) throw new Error('Failed to update tool')
      return await res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-affiliate-tools'] })
      setEditingTool(null)
      setFormData(emptyForm)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      const res = await fetch(`/api/v1/affiliate-tools/admin/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to delete tool')
      return await res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-affiliate-tools'] })
    },
  })

  const seedMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/v1/affiliate-tools/admin/seed-defaults', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to seed tools')
      return await res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-affiliate-tools'] })
    },
  })

  const openEditForm = (tool: AffiliateTool) => {
    setEditingTool(tool)
    setFormData({
      name: tool.name,
      category: tool.category,
      description: tool.description || '',
      base_url: tool.base_url,
      affiliate_url: tool.affiliate_url || '',
      affiliate_code: tool.affiliate_code || '',
      commission_rate: tool.commission_rate?.toString() || '',
      commission_type: tool.commission_type || 'percentage',
      price_display: tool.price_display || '',
      best_for: tool.best_for || '',
      logo_url: tool.logo_url || '',
      priority: tool.priority.toString(),
      is_active: tool.is_active,
    })
    setShowForm(true)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (editingTool) {
      updateMutation.mutate({ id: editingTool.id, data: formData })
    } else {
      createMutation.mutate(formData)
    }
  }

  const filteredTools = toolsQuery.data?.filter(t => 
    filterCategory === 'all' || t.category === filterCategory
  ) || []

  const groupedTools = filteredTools.reduce((acc, tool) => {
    if (!acc[tool.category]) acc[tool.category] = []
    acc[tool.category].push(tool)
    return acc
  }, {} as Record<string, AffiliateTool[]>)

  if (toolsQuery.isLoading) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-violet-600" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-stone-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Link to="/admin" className="text-stone-500 hover:text-stone-700">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-stone-900">Affiliate Tools</h1>
              <p className="text-stone-600">Manage tool recommendations and affiliate links</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => seedMutation.mutate()}
              disabled={seedMutation.isPending}
              className="px-4 py-2 bg-stone-100 text-stone-700 rounded-lg hover:bg-stone-200 text-sm font-medium"
            >
              {seedMutation.isPending ? 'Seeding...' : 'Seed Defaults'}
            </button>
            <button
              onClick={() => {
                setEditingTool(null)
                setFormData(emptyForm)
                setShowForm(true)
              }}
              className="flex items-center gap-2 px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 text-sm font-medium"
            >
              <Plus className="w-4 h-4" />
              Add Tool
            </button>
          </div>
        </div>

        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          <button
            onClick={() => setFilterCategory('all')}
            className={`px-3 py-1.5 rounded-full text-sm font-medium whitespace-nowrap ${
              filterCategory === 'all' ? 'bg-violet-600 text-white' : 'bg-white text-stone-600 hover:bg-stone-100'
            }`}
          >
            All ({toolsQuery.data?.length || 0})
          </button>
          {categories.map(cat => {
            const count = toolsQuery.data?.filter(t => t.category === cat).length || 0
            return (
              <button
                key={cat}
                onClick={() => setFilterCategory(cat)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium capitalize whitespace-nowrap ${
                  filterCategory === cat ? 'bg-violet-600 text-white' : 'bg-white text-stone-600 hover:bg-stone-100'
                }`}
              >
                {cat} ({count})
              </button>
            )
          })}
        </div>

        <div className="space-y-6">
          {Object.entries(groupedTools).map(([category, tools]) => (
            <div key={category} className="bg-white rounded-xl border border-stone-200 overflow-hidden">
              <div className="px-4 py-3 bg-stone-50 border-b border-stone-200">
                <h2 className="font-semibold text-stone-900 capitalize flex items-center gap-2">
                  <Wrench className="w-4 h-4 text-violet-600" />
                  {category}
                </h2>
              </div>
              <div className="divide-y divide-stone-100">
                {tools.map(tool => (
                  <div key={tool.id} className="p-4 flex items-center justify-between hover:bg-stone-50">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-medium text-stone-900">{tool.name}</h3>
                        {!tool.is_active && (
                          <span className="px-2 py-0.5 bg-stone-100 text-stone-500 text-xs rounded">Inactive</span>
                        )}
                        {tool.affiliate_url && (
                          <span className="px-2 py-0.5 bg-emerald-100 text-emerald-700 text-xs rounded flex items-center gap-1">
                            <DollarSign className="w-3 h-3" />
                            Affiliate
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-stone-500 mt-1">{tool.description}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-stone-400">
                        <span>Clicks: {tool.click_count}</span>
                        <span>Conversions: {tool.conversion_count}</span>
                        {tool.commission_rate && (
                          <span>Commission: {tool.commission_rate}%</span>
                        )}
                        <span>Priority: {tool.priority}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <a
                        href={tool.affiliate_url || tool.base_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-stone-400 hover:text-stone-600 hover:bg-stone-100 rounded-lg"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                      <button
                        onClick={() => openEditForm(tool)}
                        className="p-2 text-stone-400 hover:text-violet-600 hover:bg-violet-50 rounded-lg"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => {
                          if (confirm('Delete this tool?')) {
                            deleteMutation.mutate(tool.id)
                          }
                        }}
                        className="p-2 text-stone-400 hover:text-red-600 hover:bg-red-50 rounded-lg"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {filteredTools.length === 0 && (
            <div className="text-center py-12 bg-white rounded-xl border border-stone-200">
              <Wrench className="w-12 h-12 text-stone-300 mx-auto mb-4" />
              <p className="text-stone-500">No tools found. Click "Seed Defaults" to add starter tools.</p>
            </div>
          )}
        </div>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white px-6 py-4 border-b border-stone-200 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-stone-900">
                {editingTool ? 'Edit Tool' : 'Add New Tool'}
              </h2>
              <button
                onClick={() => {
                  setShowForm(false)
                  setEditingTool(null)
                  setFormData(emptyForm)
                }}
                className="text-stone-400 hover:text-stone-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-1">Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={e => setFormData(f => ({ ...f, name: e.target.value }))}
                    className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:outline-none focus:border-violet-400"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-1">Category</label>
                  <select
                    value={formData.category}
                    onChange={e => setFormData(f => ({ ...f, category: e.target.value }))}
                    className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:outline-none focus:border-violet-400"
                  >
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={e => setFormData(f => ({ ...f, description: e.target.value }))}
                  className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:outline-none focus:border-violet-400"
                  rows={2}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">Base URL</label>
                <input
                  type="url"
                  value={formData.base_url}
                  onChange={e => setFormData(f => ({ ...f, base_url: e.target.value }))}
                  className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:outline-none focus:border-violet-400"
                  placeholder="https://example.com"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">Affiliate URL</label>
                <input
                  type="url"
                  value={formData.affiliate_url}
                  onChange={e => setFormData(f => ({ ...f, affiliate_url: e.target.value }))}
                  className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:outline-none focus:border-violet-400"
                  placeholder="https://example.com?ref=oppgrid"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-1">Commission Rate (%)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.commission_rate}
                    onChange={e => setFormData(f => ({ ...f, commission_rate: e.target.value }))}
                    className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:outline-none focus:border-violet-400"
                    placeholder="10"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-1">Price Display</label>
                  <input
                    type="text"
                    value={formData.price_display}
                    onChange={e => setFormData(f => ({ ...f, price_display: e.target.value }))}
                    className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:outline-none focus:border-violet-400"
                    placeholder="Free - $20/mo"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">Best For</label>
                <input
                  type="text"
                  value={formData.best_for}
                  onChange={e => setFormData(f => ({ ...f, best_for: e.target.value }))}
                  className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:outline-none focus:border-violet-400"
                  placeholder="Small businesses, startups"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-1">Priority</label>
                  <input
                    type="number"
                    value={formData.priority}
                    onChange={e => setFormData(f => ({ ...f, priority: e.target.value }))}
                    className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:outline-none focus:border-violet-400"
                  />
                </div>
                <div className="flex items-end pb-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={e => setFormData(f => ({ ...f, is_active: e.target.checked }))}
                      className="w-4 h-4 rounded border-stone-300 text-violet-600 focus:ring-violet-500"
                    />
                    <span className="text-sm text-stone-700">Active</span>
                  </label>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false)
                    setEditingTool(null)
                    setFormData(emptyForm)
                  }}
                  className="px-4 py-2 text-stone-600 hover:bg-stone-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending || updateMutation.isPending}
                  className="flex items-center gap-2 px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 disabled:opacity-50"
                >
                  <Save className="w-4 h-4" />
                  {editingTool ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
