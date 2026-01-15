import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  ArrowLeft,
  Search,
  Download,
  RefreshCw,
  Users,
  ExternalLink,
  Loader2,
  CheckCircle,
  AlertCircle,
  Filter,
  Star,
  DollarSign
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

interface UpworkFreelancer {
  id: string
  name: string
  title: string
  hourly_rate: number | null
  country: string | null
  city: string | null
  job_success: number | null
  total_jobs: number | null
  total_hours: number | null
  avg_rating: number | null
  avatar_url: string | null
  profile_url: string | null
  skills: string[]
}

interface SearchResult {
  freelancers: UpworkFreelancer[]
  total: number
  error?: string
}

interface SyncResult {
  total_found: number
  imported: number
  updated: number
}

const upworkCategories = [
  { value: '', label: 'All Categories' },
  { value: 'developers', label: 'Web, Mobile & Software Dev' },
  { value: 'designers', label: 'Design & Creative' },
  { value: 'writers', label: 'Writing' },
  { value: 'admin', label: 'Admin Support' },
  { value: 'customer-service', label: 'Customer Service' },
  { value: 'sales', label: 'Sales & Marketing' },
  { value: 'accounting', label: 'Accounting & Consulting' },
  { value: 'legal', label: 'Legal' },
  { value: 'engineering', label: 'Engineering & Architecture' },
]

export default function AdminExperts() {
  const navigate = useNavigate()
  const { token, user } = useAuthStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [minJobSuccess, setMinJobSuccess] = useState('80')
  const [searchResults, setSearchResults] = useState<SearchResult | null>(null)
  const [isSearching, setIsSearching] = useState(false)
  const [isSyncing, setIsSyncing] = useState(false)
  const [syncResult, setSyncResult] = useState<SyncResult | null>(null)
  const [importingId, setImportingId] = useState<string | null>(null)
  const [importedIds, setImportedIds] = useState<Set<string>>(new Set())
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  useEffect(() => {
    if (!user?.is_admin) {
      navigate('/')
    }
  }, [user, navigate])

  const handleSearch = async () => {
    setIsSearching(true)
    setError(null)
    setSyncResult(null)
    
    try {
      const params = new URLSearchParams()
      if (searchQuery) params.append('q', searchQuery)
      if (selectedCategory) params.append('category', selectedCategory)
      if (minJobSuccess) params.append('job_success_min', minJobSuccess)
      params.append('limit', '50')

      const response = await fetch(`/api/v1/upwork/search?${params.toString()}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!response.ok) {
        throw new Error('Search failed')
      }
      
      const data = await response.json()
      setSearchResults(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setIsSearching(false)
    }
  }

  const handleSync = async () => {
    setIsSyncing(true)
    setError(null)
    setSuccessMessage(null)
    
    try {
      const params = new URLSearchParams()
      if (selectedCategory) params.append('category', selectedCategory)
      params.append('limit', '50')

      const response = await fetch(`/api/v1/upwork/sync?${params.toString()}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Sync failed')
      }
      
      const data = await response.json()
      setSyncResult(data)
      setSuccessMessage(`Sync complete: ${data.imported} imported, ${data.updated} updated`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sync failed')
    } finally {
      setIsSyncing(false)
    }
  }

  const handleImport = async (freelancerId: string) => {
    setImportingId(freelancerId)
    setError(null)
    
    try {
      const response = await fetch(`/api/v1/upwork/import/${freelancerId}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Import failed')
      }
      
      setImportedIds(prev => new Set([...prev, freelancerId]))
      setSuccessMessage('Freelancer imported successfully')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Import failed')
    } finally {
      setImportingId(null)
    }
  }

  if (!user?.is_admin) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>

        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="bg-indigo-600 px-6 py-6 text-white">
            <h1 className="text-2xl font-bold flex items-center gap-3">
              <Users className="w-7 h-7" />
              Upwork Expert Import Tool
            </h1>
            <p className="text-indigo-100 mt-1">
              Search and import top freelancers from Upwork to your expert marketplace
            </p>
          </div>

          <div className="p-6">
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                <p className="text-red-800">{error}</p>
              </div>
            )}

            {successMessage && (
              <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                <p className="text-green-800">{successMessage}</p>
              </div>
            )}

            <div className="grid gap-4 md:grid-cols-4 mb-6">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Search Query
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="e.g., React developer, Python expert..."
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Filter className="w-4 h-4 inline mr-1" />
                  Category
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  {upworkCategories.map(cat => (
                    <option key={cat.value} value={cat.value}>{cat.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Min Job Success %
                </label>
                <input
                  type="number"
                  value={minJobSuccess}
                  onChange={(e) => setMinJobSuccess(e.target.value)}
                  min="0"
                  max="100"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="flex gap-3 mb-6">
              <button
                onClick={handleSearch}
                disabled={isSearching}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                {isSearching ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Search className="w-4 h-4" />
                )}
                Search
              </button>

              <button
                onClick={handleSync}
                disabled={isSyncing}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {isSyncing ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <RefreshCw className="w-4 h-4" />
                )}
                Bulk Sync Top Experts
              </button>
            </div>

            {syncResult && (
              <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">Sync Results</h3>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold text-blue-600">{syncResult.total_found}</div>
                    <div className="text-sm text-blue-700">Found</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-green-600">{syncResult.imported}</div>
                    <div className="text-sm text-green-700">Imported</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-amber-600">{syncResult.updated}</div>
                    <div className="text-sm text-amber-700">Updated</div>
                  </div>
                </div>
              </div>
            )}

            {searchResults && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Search Results ({searchResults.freelancers?.length || 0} freelancers)
                </h3>
                
                {searchResults.error && (
                  <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg mb-4">
                    <p className="text-yellow-800">{searchResults.error}</p>
                  </div>
                )}

                <div className="grid gap-4">
                  {searchResults.freelancers?.map(freelancer => (
                    <div
                      key={freelancer.id}
                      className="border border-gray-200 rounded-lg p-4 hover:border-indigo-300 transition-colors"
                    >
                      <div className="flex items-start gap-4">
                        {freelancer.avatar_url ? (
                          <img
                            src={freelancer.avatar_url}
                            alt={freelancer.name}
                            className="w-14 h-14 rounded-full object-cover"
                          />
                        ) : (
                          <div className="w-14 h-14 bg-gray-200 rounded-full flex items-center justify-center">
                            <Users className="w-6 h-6 text-gray-500" />
                          </div>
                        )}
                        
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h4 className="font-semibold text-gray-900">{freelancer.name}</h4>
                            {freelancer.profile_url && (
                              <a
                                href={freelancer.profile_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-indigo-600 hover:text-indigo-700"
                              >
                                <ExternalLink className="w-4 h-4" />
                              </a>
                            )}
                          </div>
                          <p className="text-gray-600 text-sm">{freelancer.title}</p>
                          <p className="text-gray-500 text-xs">
                            {freelancer.city && `${freelancer.city}, `}{freelancer.country}
                          </p>
                          
                          <div className="flex flex-wrap gap-4 mt-2 text-sm">
                            {freelancer.hourly_rate != null && (
                              <span className="flex items-center gap-1 text-gray-600">
                                <DollarSign className="w-4 h-4" />
                                ${freelancer.hourly_rate}/hr
                              </span>
                            )}
                            {freelancer.job_success != null && (
                              <span className="flex items-center gap-1 text-green-600">
                                <CheckCircle className="w-4 h-4" />
                                {freelancer.job_success}% Success
                              </span>
                            )}
                            {freelancer.avg_rating != null && (
                              <span className="flex items-center gap-1 text-amber-600">
                                <Star className="w-4 h-4" />
                                {freelancer.avg_rating.toFixed(1)}
                              </span>
                            )}
                            {freelancer.total_jobs != null && (
                              <span className="text-gray-500">
                                {freelancer.total_jobs} jobs
                              </span>
                            )}
                          </div>

                          {freelancer.skills && freelancer.skills.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {freelancer.skills.slice(0, 5).map(skill => (
                                <span
                                  key={skill}
                                  className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded"
                                >
                                  {skill}
                                </span>
                              ))}
                              {freelancer.skills.length > 5 && (
                                <span className="text-gray-400 text-xs">
                                  +{freelancer.skills.length - 5} more
                                </span>
                              )}
                            </div>
                          )}
                        </div>

                        <div>
                          {importedIds.has(freelancer.id) ? (
                            <span className="flex items-center gap-1 text-green-600 text-sm">
                              <CheckCircle className="w-4 h-4" />
                              Imported
                            </span>
                          ) : (
                            <button
                              onClick={() => handleImport(freelancer.id)}
                              disabled={importingId === freelancer.id}
                              className="flex items-center gap-2 px-3 py-1.5 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                            >
                              {importingId === freelancer.id ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                              ) : (
                                <Download className="w-4 h-4" />
                              )}
                              Import
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
