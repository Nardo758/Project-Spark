import { useState, useCallback, useRef, useEffect } from 'react'
import { Sparkles, Plus, X, Eye, EyeOff, MapPin, Loader2, Send } from 'lucide-react'
import { layerRegistry, defaultLayerTabs, createLayerInstance } from './registry'
import type { LayerType, LayerInstance, LocationFinderState } from './types'
import { LayerInputRenderer } from './LayerInputRenderer'

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

  useEffect(() => {
    if (state.center?.address) {
      setAddressInput(state.center.address)
    } else if (!state.center) {
      setAddressInput('')
    }
  }, [state.center])

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
    const updatedLayers = state.layers.map(layer =>
      layer.id === layerId ? { ...layer, config: { ...layer.config, ...config } } : layer
    )
    onStateChange({ ...state, layers: updatedLayers })
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
      const response = await fetch('/api/maps/deep-clone-analysis', {
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
                    className={`flex items-center gap-1 px-2 py-0.5 rounded text-xs ${
                      layer.visible ? 'bg-stone-100 text-stone-700' : 'bg-stone-50 text-stone-400'
                    }`}
                  >
                    <Icon className="w-3 h-3" />
                    <span>{def.label}</span>
                  </div>
                )
              })}
            </div>
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
    </div>
  )
}
