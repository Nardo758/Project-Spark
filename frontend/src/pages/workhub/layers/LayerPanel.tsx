import { useState, useCallback, useRef, useEffect } from 'react'
import { Sparkles, Plus, X, Eye, EyeOff, MapPin, Loader2, Send, FileText, TrendingUp, Users, Store, CheckCircle, Target } from 'lucide-react'
import { layerRegistry, defaultLayerTabs, createLayerInstance } from './registry'
import type { LayerType, LayerInstance, LocationFinderState } from './types'
import { LayerInputRenderer } from './LayerInputRenderer'
import { findOptimalZones } from './layerService'

function useDebounce<T extends (...args: any[]) => any>(fn: T, delay: number) {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)
  
  const debouncedFn = useCallback((...args: Parameters<T>) => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    timeoutRef.current = setTimeout(() => fn(...args), delay)
  }, [fn, delay])
  
  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    }
  }, [])
  
  return debouncedFn
}

const radiusOptions = [
  { value: 0.25, label: '0.25 mi' },
  { value: 0.5, label: '0.5 mi' },
  { value: 1, label: '1 mi' },
  { value: 2, label: '2 mi' },
  { value: 5, label: '5 mi' },
  { value: 10, label: '10 mi' }
]

interface LayerPanelProps {
  state: LocationFinderState
  onStateChange: (state: LocationFinderState) => void
  onAiPrompt: (prompt: string) => void
  aiLoading?: boolean
  aiMessage?: string | null
}

export function LayerPanel({ state, onStateChange, onAiPrompt, aiLoading, aiMessage }: LayerPanelProps) {
  const [aiPromptText, setAiPromptText] = useState('')
  const [addressInput, setAddressInput] = useState(state.center?.address || '')
  const [addressSuggestions, setAddressSuggestions] = useState<any[]>([])
  const [addressLoading, setAddressLoading] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [analyzingLayers, setAnalyzingLayers] = useState<Record<string, boolean>>({})
  const [showSummaryModal, setShowSummaryModal] = useState(false)
  const [findingZones, setFindingZones] = useState(false)

  useEffect(() => {
    if (state.center?.address) {
      setAddressInput(state.center.address)
    } else if (!state.center) {
      setAddressInput('')
    }
  }, [state.center])

  const fetchDemographicsData = useCallback(async (layerId: string) => {
    if (!state.center) return

    setAnalyzingLayers(prev => ({ ...prev, [layerId]: true }))
    try {
      const response = await fetch('/api/v1/maps/demographics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lat: state.center.lat,
          lng: state.center.lng,
          radius_miles: state.radius,
          metrics: ['population', 'income']
        })
      })

      if (!response.ok) throw new Error('Failed to fetch demographics')

      const data = await response.json()
      const updatedLayers = state.layers.map(layer =>
        layer.id === layerId ? { ...layer, data, loading: false, error: null } : layer
      )
      onStateChange({ ...state, layers: updatedLayers })
    } catch (error) {
      console.error('Demographics fetch error:', error)
      const updatedLayers = state.layers.map(layer =>
        layer.id === layerId ? { ...layer, loading: false, error: 'Failed to load demographics' } : layer
      )
      onStateChange({ ...state, layers: updatedLayers })
    } finally {
      setAnalyzingLayers(prev => ({ ...prev, [layerId]: false }))
    }
  }, [state, onStateChange])

  const fetchCompetitionData = useCallback(async (layerId: string, category: string) => {
    if (!state.center || !category) return

    setAnalyzingLayers(prev => ({ ...prev, [layerId]: true }))
    try {
      const response = await fetch('/api/v1/maps/places/nearby', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lat: state.center.lat,
          lng: state.center.lng,
          radius_miles: state.radius,
          business_type: category,
          limit: 20
        })
      })

      if (!response.ok) throw new Error('Failed to fetch competition data')

      const data = await response.json()
      const updatedLayers = state.layers.map(layer =>
        layer.id === layerId ? { ...layer, data: data.places || [], loading: false, error: null } : layer
      )
      onStateChange({ ...state, layers: updatedLayers })
    } catch (error) {
      console.error('Competition fetch error:', error)
      const updatedLayers = state.layers.map(layer =>
        layer.id === layerId ? { ...layer, loading: false, error: 'Failed to load competition' } : layer
      )
      onStateChange({ ...state, layers: updatedLayers })
    } finally {
      setAnalyzingLayers(prev => ({ ...prev, [layerId]: false }))
    }
  }, [state, onStateChange])

  const prevCenterRef = useRef(state.center)
  const prevRadiusRef = useRef(state.radius)
  const prevLayerCountRef = useRef(state.layers.length)

  useEffect(() => {
    if (!state.center) return

    const centerChanged = prevCenterRef.current?.lat !== state.center.lat || prevCenterRef.current?.lng !== state.center.lng
    const radiusChanged = prevRadiusRef.current !== state.radius
    const layersAdded = state.layers.length > prevLayerCountRef.current

    prevCenterRef.current = state.center
    prevRadiusRef.current = state.radius
    prevLayerCountRef.current = state.layers.length

    if (centerChanged || radiusChanged || layersAdded) {
      state.layers.forEach(layer => {
        if (layer.type === 'demographics' && (centerChanged || radiusChanged || !layer.data)) {
          fetchDemographicsData(layer.id)
        }
        if (layer.type === 'competition' && layer.config?.searchQuery && (centerChanged || radiusChanged || !layer.data)) {
          fetchCompetitionData(layer.id, layer.config.searchQuery)
        }
      })
    }
  }, [state.center, state.radius, state.layers.length, fetchDemographicsData, fetchCompetitionData])

  const doAddressSearch = useCallback(async (query: string) => {
    if (query.length < 3) {
      setAddressSuggestions([])
      return
    }
    
    setAddressLoading(true)
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&countrycodes=us`
      )
      const data = await response.json()
      setAddressSuggestions(data)
      setShowSuggestions(true)
    } catch (error) {
      console.error('Address search error:', error)
    } finally {
      setAddressLoading(false)
    }
  }, [])

  const searchAddress = useDebounce(doAddressSearch, 300)

  const handleAddressSelect = (suggestion: any) => {
    const newCenter = {
      lat: parseFloat(suggestion.lat),
      lng: parseFloat(suggestion.lon),
      address: suggestion.display_name
    }
    setAddressInput(suggestion.display_name)
    onStateChange({ ...state, center: newCenter })
    setShowSuggestions(false)
    setAddressSuggestions([])
  }

  const handleRadiusChange = (radius: number) => {
    onStateChange({ ...state, radius })
  }

  const handleTabChange = (tab: LayerType) => {
    onStateChange({ ...state, activeLayerTab: tab })
  }

  const handleLayerConfigChange = (layerId: string, config: Record<string, any>) => {
    const layer = state.layers.find(l => l.id === layerId)
    const updatedLayers = state.layers.map(l =>
      l.id === layerId ? { ...l, config: { ...l.config, ...config } } : l
    )
    onStateChange({ ...state, layers: updatedLayers })

    if (layer?.type === 'competition' && config.searchQuery && config.searchQuery !== layer.config?.searchQuery && state.center) {
      setTimeout(() => fetchCompetitionData(layerId, config.searchQuery), 100)
    }
  }

  const handleToggleLayerVisibility = (layerId: string) => {
    const updatedLayers = state.layers.map(layer =>
      layer.id === layerId ? { ...layer, visible: !layer.visible } : layer
    )
    onStateChange({ ...state, layers: updatedLayers })
  }

  const handleRemoveLayer = (layerId: string) => {
    const updatedLayers = state.layers.filter(layer => layer.id !== layerId)
    onStateChange({ ...state, layers: updatedLayers })
  }

  const handleAddLayer = (type: LayerType) => {
    const existingOfType = state.layers.find(l => l.type === type)
    if (existingOfType) {
      handleTabChange(type)
      return
    }
    const newLayer = createLayerInstance(type)
    onStateChange({
      ...state,
      layers: [...state.layers, newLayer],
      activeLayerTab: type
    })
  }

  const handleDeepCloneAnalysis = async (layerId: string) => {
    const layer = state.layers.find(l => l.id === layerId)
    if (!layer || !state.center) return

    setAnalyzingLayers(prev => ({ ...prev, [layerId]: true }))

    try {
      const response = await fetch('/api/v1/maps/deep-clone-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_business: layer.config.sourceBusiness,
          source_location: layer.config.sourceLocation || null,
          source_coordinates: layer.config.sourceLocationCoordinates || null,
          target_coordinates: {
            lat: state.center.lat,
            lng: state.center.lng
          },
          target_address: state.center.address || null,
          business_category: layer.config.businessCategory || 'restaurant',
          radius_miles: state.radius,
          include_competitors: layer.config.includeCompetitors !== false,
          include_demographics: layer.config.includeDemographics !== false
        })
      })

      if (!response.ok) {
        throw new Error('Analysis failed')
      }

      const result = await response.json()

      const updatedLayers = state.layers.map(l =>
        l.id === layerId ? { ...l, config: { ...l.config, analysisResult: result } } : l
      )
      onStateChange({ ...state, layers: updatedLayers })
    } catch (error) {
      console.error('Deep clone analysis error:', error)
      const updatedLayers = state.layers.map(l =>
        l.id === layerId ? { ...l, error: 'Analysis failed. Please try again.' } : l
      )
      onStateChange({ ...state, layers: updatedLayers })
    } finally {
      setAnalyzingLayers(prev => ({ ...prev, [layerId]: false }))
    }
  }

  const handleAiSubmit = () => {
    if (aiPromptText.trim()) {
      onAiPrompt(aiPromptText.trim())
      setAiPromptText('')
    }
  }

  const handleFindBestZones = async () => {
    if (!state.center) return
    
    setFindingZones(true)
    onStateChange({ ...state, optimalZonesLoading: true, zoneSummary: '' })
    
    try {
      const activeLayers = state.layers
        .filter(l => l.visible)
        .map(l => l.type)
      
      const demographicsLayer = state.layers.find(l => l.type === 'demographics')
      const competitionLayer = state.layers.find(l => l.type === 'competition')
      const deepCloneLayer = state.layers.find(l => l.type === 'deep_clone')
      
      const businessType = deepCloneLayer?.config?.businessCategory || 
                          competitionLayer?.config?.searchQuery || 
                          undefined
      
      let competitors: any[] = []
      if (competitionLayer?.data) {
        if (Array.isArray(competitionLayer.data)) {
          competitors = competitionLayer.data
            .map((p: any) => ({
              name: p.name,
              rating: p.rating || 0,
              latitude: p.latitude || p.lat,
              longitude: p.longitude || p.lng,
              address: p.address
            }))
            .filter((c: any) => c.latitude != null && c.longitude != null)
        } else if (competitionLayer.data.features) {
          competitors = competitionLayer.data.features
            .map((f: any) => ({
              name: f.properties?.name,
              rating: f.properties?.rating || 0,
              latitude: f.geometry?.coordinates?.[1],
              longitude: f.geometry?.coordinates?.[0],
              address: f.properties?.address
            }))
            .filter((c: any) => c.latitude != null && c.longitude != null)
        }
      }
      
      const result = await findOptimalZones({
        center: state.center,
        targetRadius: state.radius,
        analysisRadius: 3.0,
        activeLayers,
        businessType,
        demographicsData: demographicsLayer?.data,
        competitors,
        topN: 3
      })
      
      if (result.error) {
        console.error('Find zones error:', result.error)
        onStateChange({
          ...state,
          optimalZones: undefined,
          optimalZonesLoading: false,
          zoneSummary: result.error
        })
      } else {
        onStateChange({
          ...state,
          optimalZones: result.zones,
          optimalZonesLoading: false,
          zoneSummary: result.summary
        })
      }
    } catch (error) {
      console.error('Find zones error:', error)
      onStateChange({
        ...state,
        optimalZones: undefined,
        optimalZonesLoading: false,
        zoneSummary: 'Failed to analyze locations'
      })
    } finally {
      setFindingZones(false)
    }
  }

  const getLayerByType = (type: LayerType): LayerInstance | undefined => {
    return state.layers.find(l => l.type === type)
  }

  const activeTab = state.activeLayerTab === 'ai' ? defaultLayerTabs[0] : state.activeLayerTab as LayerType
  const activeLayer = getLayerByType(activeTab)
  const activeDefinition = layerRegistry[activeTab]

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg border border-stone-200">
      <div className="flex-shrink-0 p-3 border-b border-stone-200 bg-gradient-to-r from-emerald-50 to-teal-50">
        <div className="flex items-center gap-2 mb-1">
          <MapPin className="w-4 h-4 text-emerald-600" />
          <span className="text-sm font-medium text-stone-700">Target Location</span>
        </div>
        <p className="text-xs text-stone-500 mb-2">Where do you want to open your business?</p>
        
        <div className="relative mb-2">
          <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400" />
          <input
            type="text"
            value={addressInput}
            onChange={(e) => {
              setAddressInput(e.target.value)
              searchAddress(e.target.value)
            }}
            onFocus={() => addressSuggestions.length > 0 && setShowSuggestions(true)}
            placeholder="Enter target city, address, or area..."
            className="w-full pl-9 pr-10 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 bg-white"
          />
          {addressLoading && (
            <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400 animate-spin" />
          )}
          {!addressLoading && state.center && (
            <button
              onClick={() => {
                setAddressInput('')
                setAddressSuggestions([])
                onStateChange({ ...state, center: null })
              }}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-0.5 rounded hover:bg-stone-100"
              title="Clear location"
            >
              <X className="w-4 h-4 text-stone-400 hover:text-stone-600" />
            </button>
          )}
          {showSuggestions && addressSuggestions.length > 0 && (
            <div className="absolute z-20 w-full mt-1 bg-white border border-stone-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
              {addressSuggestions.map((suggestion, i) => (
                <button
                  key={i}
                  onClick={() => handleAddressSelect(suggestion)}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-stone-50 border-b border-stone-100 last:border-0"
                >
                  <span className="line-clamp-2">{suggestion.display_name}</span>
                </button>
              ))}
            </div>
          )}
        </div>
        
        {!state.center && (
          <p className="text-xs text-violet-600 mb-2 flex items-center gap-1">
            <span className="w-2 h-2 bg-violet-500 rounded-full animate-pulse"></span>
            Click on the map to set location
          </p>
        )}
        
        {state.center && (
          <p className="text-xs text-emerald-600 mb-2">
            {state.center.lat.toFixed(4)}, {state.center.lng.toFixed(4)}
          </p>
        )}
        
        <div className="flex gap-1">
          {radiusOptions.map(opt => (
            <button
              key={opt.value}
              onClick={() => handleRadiusChange(opt.value)}
              className={`flex-1 px-1 py-1.5 rounded text-xs font-medium transition-all ${
                state.radius === opt.value
                  ? 'bg-emerald-600 text-white'
                  : 'bg-white text-stone-600 hover:bg-stone-100 border border-stone-200'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
        
        {state.center && state.layers.length > 0 && (
          <div className="mt-3 pt-3 border-t border-stone-200">
            <button
              onClick={handleFindBestZones}
              disabled={findingZones}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-lg text-sm font-medium hover:from-violet-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {findingZones ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Finding optimal zones...
                </>
              ) : (
                <>
                  <Target className="w-4 h-4" />
                  Find Best 3-Mile Zones
                </>
              )}
            </button>
          </div>
        )}
      </div>

      <div className="flex-shrink-0 flex items-center gap-1.5 p-2 border-b border-stone-200 bg-stone-50 overflow-x-auto">
        {defaultLayerTabs.map(type => {
          const def = layerRegistry[type]
          const Icon = def.icon
          const layer = getLayerByType(type)
          const isActive = activeTab === type
          
          return (
            <button
              key={type}
              onClick={() => {
                if (!layer) {
                  handleAddLayer(type)
                } else {
                  handleTabChange(type)
                }
              }}
              className={`flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-violet-100 text-violet-700 ring-1 ring-violet-400'
                  : layer
                    ? 'bg-stone-100 text-stone-700 hover:bg-stone-200'
                    : 'bg-white text-stone-500 border border-dashed border-stone-300 hover:border-stone-400'
              }`}
            >
              <Icon className="w-3 h-3" />
              {def.label}
              {layer && !isActive && (
                <span className={`w-1.5 h-1.5 rounded-full ${layer.visible ? 'bg-emerald-500' : 'bg-stone-300'}`} />
              )}
            </button>
          )
        })}
      </div>

      <div className="flex-1 overflow-y-scroll overflow-x-visible p-3 pb-6 min-h-0 scrollbar-thin scrollbar-thumb-stone-300 scrollbar-track-transparent hover:scrollbar-thumb-stone-400" style={{ scrollbarWidth: 'thin', scrollbarColor: '#d6d3d1 transparent' }}>
        {activeDefinition && (
          <div className="space-y-3 pb-4">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-stone-900 text-sm">{activeDefinition.label}</h3>
                <p className="text-xs text-stone-500 mt-0.5">{activeDefinition.description}</p>
              </div>
              {activeLayer && (
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => handleToggleLayerVisibility(activeLayer.id)}
                    className="p-1 rounded hover:bg-stone-100"
                    title={activeLayer.visible ? 'Hide layer' : 'Show layer'}
                  >
                    {activeLayer.visible ? (
                      <Eye className="w-3.5 h-3.5 text-stone-600" />
                    ) : (
                      <EyeOff className="w-3.5 h-3.5 text-stone-400" />
                    )}
                  </button>
                  <button
                    onClick={() => handleRemoveLayer(activeLayer.id)}
                    className="p-1 rounded hover:bg-red-50 text-stone-400 hover:text-red-500"
                    title="Remove layer"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}
            </div>

            {activeLayer ? (
              <LayerInputRenderer
                definition={activeDefinition}
                config={activeLayer.config}
                onChange={(config: Record<string, any>) => handleLayerConfigChange(activeLayer.id, config)}
                loading={activeLayer.loading}
                onAnalyze={() => handleDeepCloneAnalysis(activeLayer.id)}
                analyzing={analyzingLayers[activeLayer.id] || false}
                targetLocation={state.center}
              />
            ) : (
              <div className="text-center py-6">
                <button
                  onClick={() => handleAddLayer(activeTab)}
                  className="px-3 py-1.5 bg-stone-100 text-stone-700 rounded-lg text-xs font-medium hover:bg-stone-200 flex items-center gap-1.5 mx-auto"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Add {activeDefinition.label} Layer
                </button>
              </div>
            )}

            {activeLayer?.error && (
              <div className="p-2 bg-red-50 border border-red-200 rounded-lg text-xs text-red-600">
                {activeLayer.error}
              </div>
            )}
          </div>
        )}

        {state.layers.length > 0 && (
          <div className="mt-4 pt-3 border-t border-stone-100">
            <p className="text-xs text-stone-400 mb-2">Active Layers</p>
            <div className="flex flex-wrap gap-1">
              {state.layers.map(layer => {
                const def = layerRegistry[layer.type]
                const Icon = def.icon
                return (
                  <div
                    key={layer.id}
                    className={`flex items-center gap-1 px-2 py-0.5 rounded text-xs group ${
                      layer.visible ? 'bg-stone-100 text-stone-700' : 'bg-stone-50 text-stone-400'
                    }`}
                  >
                    <Icon className="w-3 h-3" />
                    <span>{def.label}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleRemoveLayer(layer.id)
                      }}
                      className="ml-0.5 p-0.5 rounded hover:bg-stone-200 text-stone-400 hover:text-stone-600 transition-colors"
                      title={`Remove ${def.label} layer`}
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                )
              })}
            </div>

            <button
              onClick={() => setShowSummaryModal(true)}
              disabled={!state.center || state.layers.length === 0 || !state.layers.some(l => 
                l.config?.analysisResult || l.data
              )}
              className="mt-3 w-full flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-medium rounded-lg hover:from-indigo-700 hover:to-violet-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-sm"
            >
              <FileText className="w-4 h-4" />
              Generate Summary
            </button>
          </div>
        )}
      </div>

      <div className="flex-shrink-0 p-3 border-t border-stone-200 bg-gradient-to-r from-violet-50 to-purple-50">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="w-4 h-4 text-violet-600" />
          <span className="text-sm font-medium text-stone-700">Location Finder Assistant</span>
        </div>
        
        {aiMessage && (
          <div className={`mb-2 p-2 rounded-lg text-xs ${
            aiMessage.includes("couldn't") || aiMessage.includes("Please provide")
              ? 'bg-amber-50 border border-amber-200 text-amber-700'
              : 'bg-emerald-50 border border-emerald-200 text-emerald-700'
          }`}>
            {aiMessage}
          </div>
        )}
        
        <div className="flex gap-2">
          <input
            type="text"
            value={aiPromptText}
            onChange={(e) => setAiPromptText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleAiSubmit()}
            placeholder="e.g., Set center to Austin, show demographics..."
            className="flex-1 px-3 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500 bg-white"
          />
          <button
            onClick={handleAiSubmit}
            disabled={!aiPromptText.trim() || aiLoading}
            className="px-3 py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {aiLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {showSummaryModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full max-h-[80vh] overflow-hidden animate-in zoom-in-95 duration-200">
            <div className="bg-gradient-to-r from-indigo-600 to-violet-600 p-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-white" />
                <h2 className="text-lg font-semibold text-white">Location Analysis Summary</h2>
              </div>
              <button
                onClick={() => setShowSummaryModal(false)}
                className="p-1 hover:bg-white/20 rounded transition-colors"
              >
                <X className="w-5 h-5 text-white" />
              </button>
            </div>

            <div className="p-4 overflow-y-auto max-h-[60vh] space-y-4">
              {(() => {
                const deepCloneLayer = state.layers.find(l => l.type === 'deep_clone')
                const deepCloneResult = deepCloneLayer?.config?.analysisResult
                const competitionLayer = state.layers.find(l => l.type === 'competition')
                const demographicsLayer = state.layers.find(l => l.type === 'demographics')
                const demographicsData = demographicsLayer?.data
                const competitorCount = competitionLayer?.data?.length || deepCloneResult?.competitor_count || deepCloneResult?.three_mile_analysis?.competitor_count || 0
                const population = deepCloneResult?.three_mile_analysis?.population || demographicsData?.population
                const medianIncome = deepCloneResult?.three_mile_analysis?.median_income || demographicsData?.median_income
                const hasAnalysisData = deepCloneResult || competitionLayer?.data || demographicsData

                if (hasAnalysisData) {
                  return (
                    <div className="bg-gradient-to-br from-indigo-50 to-violet-50 rounded-xl p-4 border border-indigo-100">
                      <h3 className="font-semibold text-stone-800 mb-3 flex items-center gap-2">
                        <CheckCircle className="w-5 h-5 text-indigo-600" />
                        Analysis Overview
                      </h3>
                      <div className="grid grid-cols-2 gap-3">
                        {deepCloneResult && (
                          <div className="bg-white rounded-lg p-3 shadow-sm">
                            <div className="text-xs text-stone-500 mb-1">Clone Viability</div>
                            <div className={`text-2xl font-bold ${
                              deepCloneResult.match_score >= 75 ? 'text-emerald-600' :
                              deepCloneResult.match_score >= 50 ? 'text-amber-600' : 'text-red-600'
                            }`}>
                              {deepCloneResult.match_score}%
                            </div>
                          </div>
                        )}
                        {population && (
                          <div className="bg-white rounded-lg p-3 shadow-sm">
                            <div className="text-xs text-stone-500 mb-1">Area Population</div>
                            <div className="text-2xl font-bold text-stone-800">
                              {population.toLocaleString()}
                            </div>
                          </div>
                        )}
                        {medianIncome && (
                          <div className="bg-white rounded-lg p-3 shadow-sm">
                            <div className="text-xs text-stone-500 mb-1">Median Income</div>
                            <div className="text-2xl font-bold text-stone-800">
                              ${medianIncome.toLocaleString()}
                            </div>
                          </div>
                        )}
                        {competitorCount > 0 && (
                          <div className="bg-white rounded-lg p-3 shadow-sm">
                            <div className="text-xs text-stone-500 mb-1">Nearby Competitors</div>
                            <div className="text-2xl font-bold text-stone-800">{competitorCount}</div>
                          </div>
                        )}
                      </div>
                      {deepCloneResult?.key_factors && deepCloneResult.key_factors.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-indigo-100">
                          <div className="text-xs text-stone-500 mb-2">Key Insights</div>
                          <ul className="space-y-1">
                            {deepCloneResult.key_factors.slice(0, 3).map((factor: string, i: number) => (
                              <li key={i} className="text-sm text-stone-700 flex items-start gap-2">
                                <span className="text-indigo-500 font-bold">•</span>
                                {factor}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )
                }
                return null
              })()}

              {state.center && (
                <div className="bg-stone-50 rounded-lg p-3">
                  <div className="flex items-center gap-2 text-stone-500 mb-1">
                    <MapPin className="w-4 h-4" />
                    <span className="text-xs font-medium">Target Location</span>
                  </div>
                  <p className="text-sm text-stone-800">{state.center.address || `${state.center.lat.toFixed(4)}, ${state.center.lng.toFixed(4)}`}</p>
                  <p className="text-xs text-stone-500 mt-1">Search Radius: {state.radius} mi</p>
                </div>
              )}

              {state.layers.map(layer => {
                const def = layerRegistry[layer.type]
                const Icon = def.icon
                const deepCloneResult = layer.type === 'deep_clone' ? layer.config?.analysisResult : null

                return (
                  <div key={layer.id} className="border border-stone-200 rounded-lg overflow-hidden">
                    <div className="bg-stone-100 px-3 py-2 flex items-center gap-2">
                      <Icon className="w-4 h-4 text-stone-600" />
                      <span className="font-medium text-stone-800 text-sm">{def.label}</span>
                      {layer.visible && (
                        <span className="ml-auto text-xs bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded">Active</span>
                      )}
                    </div>
                    <div className="p-3 text-sm">
                      {layer.type === 'deep_clone' && (
                        <div className="space-y-2">
                          <p className="text-stone-600"><span className="font-medium">Business:</span> {layer.config?.sourceBusiness || 'Not set'}</p>
                          {deepCloneResult ? (
                            <div className="space-y-2">
                              <div className="flex items-center gap-2">
                                <CheckCircle className="w-4 h-4 text-emerald-500" />
                                <span className="font-semibold text-emerald-700">Match Score: {deepCloneResult.match_score}%</span>
                              </div>
                              <div className="grid grid-cols-2 gap-2 text-xs">
                                <div className="flex items-center gap-1.5">
                                  <Users className="w-3.5 h-3.5 text-stone-400" />
                                  <span>Pop: {deepCloneResult.three_mile_analysis?.population?.toLocaleString() || 'N/A'}</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                  <TrendingUp className="w-3.5 h-3.5 text-stone-400" />
                                  <span>Income: ${deepCloneResult.three_mile_analysis?.median_income?.toLocaleString() || 'N/A'}</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                  <Store className="w-3.5 h-3.5 text-stone-400" />
                                  <span>Competitors: {deepCloneResult.competitor_count ?? deepCloneResult.three_mile_analysis?.competitor_count ?? 'N/A'}</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                  <TrendingUp className="w-3.5 h-3.5 text-stone-400" />
                                  <span>Growth: {deepCloneResult.three_mile_analysis?.growth_rate != null ? `${deepCloneResult.three_mile_analysis.growth_rate}%` : 'N/A'}</span>
                                </div>
                              </div>
                              {deepCloneResult.key_factors && deepCloneResult.key_factors.length > 0 && (
                                <div className="pt-2 border-t border-stone-100">
                                  <p className="text-xs text-stone-500 mb-1">Key Factors:</p>
                                  <ul className="text-xs space-y-0.5">
                                    {deepCloneResult.key_factors.slice(0, 3).map((factor: string, i: number) => (
                                      <li key={i} className="flex items-start gap-1.5 text-stone-600">
                                        <span className="text-emerald-500">•</span>
                                        {factor}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          ) : (
                            <p className="text-xs text-stone-400 italic">Analysis not yet run</p>
                          )}
                        </div>
                      )}

                      {layer.type === 'demographics' && (
                        <div className="text-stone-600">
                          {layer.data ? (
                            <div className="grid grid-cols-2 gap-2 text-xs">
                              <div className="flex items-center gap-1.5">
                                <Users className="w-3.5 h-3.5 text-stone-400" />
                                <span>Pop: {layer.data.population?.toLocaleString() || 'N/A'}</span>
                              </div>
                              <div className="flex items-center gap-1.5">
                                <TrendingUp className="w-3.5 h-3.5 text-stone-400" />
                                <span>Income: ${layer.data.median_income?.toLocaleString() || 'N/A'}</span>
                              </div>
                              <div className="flex items-center gap-1.5">
                                <Users className="w-3.5 h-3.5 text-stone-400" />
                                <span>Households: {layer.data.households?.toLocaleString() || 'N/A'}</span>
                              </div>
                              <div className="flex items-center gap-1.5">
                                <TrendingUp className="w-3.5 h-3.5 text-stone-400" />
                                <span>Median Age: {layer.data.median_age || 'N/A'}</span>
                              </div>
                            </div>
                          ) : (
                            <p className="text-xs text-stone-400 italic">Loading demographics...</p>
                          )}
                        </div>
                      )}

                      {layer.type === 'competition' && (
                        <div className="text-stone-600">
                          <p><span className="font-medium">Business Type:</span> {layer.config?.searchQuery || 'Not set'}</p>
                          {layer.data && layer.data.length > 0 ? (
                            <div className="mt-2">
                              <p className="text-xs text-emerald-600 mb-2">{layer.data.length} competitors found</p>
                              <ul className="text-xs space-y-1 max-h-32 overflow-y-auto">
                                {layer.data.slice(0, 5).map((place: any, i: number) => (
                                  <li key={i} className="flex items-start gap-1.5">
                                    <Store className="w-3.5 h-3.5 text-stone-400 mt-0.5 flex-shrink-0" />
                                    <span className="truncate">{place.name}</span>
                                    {place.rating > 0 && (
                                      <span className="text-amber-500 ml-auto flex-shrink-0">{place.rating}★</span>
                                    )}
                                  </li>
                                ))}
                                {layer.data.length > 5 && (
                                  <li className="text-stone-400 italic">+{layer.data.length - 5} more...</li>
                                )}
                              </ul>
                            </div>
                          ) : layer.config?.searchQuery ? (
                            <p className="text-xs text-stone-400 italic mt-1">Loading competitors...</p>
                          ) : (
                            <p className="text-xs text-stone-400 italic mt-1">Select a category to find competitors</p>
                          )}
                        </div>
                      )}

                      {layer.type === 'traffic' && (
                        <div className="text-stone-600">
                          <p className="text-xs text-stone-400 italic">Traffic layer active</p>
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}

              {state.layers.length === 0 && (
                <div className="text-center py-8 text-stone-400">
                  <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No layers added yet</p>
                  <p className="text-xs mt-1">Add layers to generate a summary</p>
                </div>
              )}
            </div>

            <div className="border-t border-stone-200 p-4 bg-stone-50 flex justify-end gap-2">
              <button
                onClick={() => setShowSummaryModal(false)}
                className="px-4 py-2 text-stone-600 hover:bg-stone-100 rounded-lg text-sm font-medium transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
