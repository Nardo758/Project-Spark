import { useState, useCallback, useRef, useEffect } from 'react'
import { Sparkles, Plus, X, Eye, EyeOff, ChevronRight, MapPin, Loader2 } from 'lucide-react'
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

  const handleTabChange = (tab: LayerType | 'ai') => {
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
    const remainingTypes = updatedLayers.map(l => l.type)
    const newActiveTab = remainingTypes.length > 0 ? remainingTypes[0] : 'ai'
    onStateChange({ ...state, layers: updatedLayers, activeLayerTab: newActiveTab })
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

  const handleAiSubmit = () => {
    if (aiPromptText.trim()) {
      onAiPrompt(aiPromptText.trim())
      setAiPromptText('')
    }
  }

  const getLayerByType = (type: LayerType): LayerInstance | undefined => {
    return state.layers.find(l => l.type === type)
  }

  const activeLayer = state.activeLayerTab !== 'ai' 
    ? getLayerByType(state.activeLayerTab as LayerType)
    : null

  const activeDefinition = state.activeLayerTab !== 'ai'
    ? layerRegistry[state.activeLayerTab as LayerType]
    : null

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg border border-stone-200 overflow-hidden">
      <div className="p-3 border-b border-stone-200 bg-gradient-to-r from-violet-50 to-purple-50">
        <div className="flex items-center gap-2 mb-2">
          <MapPin className="w-4 h-4 text-violet-600" />
          <span className="text-sm font-medium text-stone-700">Center Point</span>
        </div>
        
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
            placeholder="Enter address, city, or landmark..."
            className="w-full pl-9 pr-10 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500 bg-white"
          />
          {addressLoading && (
            <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400 animate-spin" />
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
              className={`flex-1 px-2 py-1.5 rounded text-xs font-medium transition-all ${
                state.radius === opt.value
                  ? 'bg-violet-600 text-white'
                  : 'bg-white text-stone-600 hover:bg-stone-100 border border-stone-200'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-2 p-3 border-b border-stone-200 bg-stone-50 overflow-x-auto">
        {defaultLayerTabs.map(type => {
          const def = layerRegistry[type]
          const Icon = def.icon
          const layer = getLayerByType(type)
          const isActive = state.activeLayerTab === type
          
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
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                isActive
                  ? `bg-${def.color}-100 text-${def.color}-700 ring-2 ring-${def.color}-500`
                  : layer
                    ? 'bg-stone-100 text-stone-700 hover:bg-stone-200'
                    : 'bg-white text-stone-500 border border-dashed border-stone-300 hover:border-stone-400'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {def.label}
              {layer && !isActive && (
                <span className={`w-1.5 h-1.5 rounded-full ${layer.visible ? 'bg-emerald-500' : 'bg-stone-300'}`} />
              )}
            </button>
          )
        })}
        
        <button
          onClick={() => handleTabChange('ai')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
            state.activeLayerTab === 'ai'
              ? 'bg-violet-100 text-violet-700 ring-2 ring-violet-500'
              : 'bg-gradient-to-r from-violet-50 to-purple-50 text-violet-600 hover:from-violet-100 hover:to-purple-100'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          AI
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {state.activeLayerTab === 'ai' ? (
          <div className="space-y-4">
            <div className="text-center py-4">
              <div className="w-12 h-12 bg-gradient-to-br from-violet-100 to-purple-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                <Sparkles className="w-6 h-6 text-violet-600" />
              </div>
              <h3 className="font-semibold text-stone-900 mb-1">AI Layer Assistant</h3>
              <p className="text-xs text-stone-500">
                Describe what you want to see on the map
              </p>
            </div>

            <div className="space-y-2">
              <textarea
                value={aiPromptText}
                onChange={(e) => setAiPromptText(e.target.value)}
                placeholder="e.g., Show me coffee shops within 2 miles, add demographics data, find competitors for a pizza restaurant..."
                className="w-full px-3 py-2 border border-stone-200 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                rows={3}
              />
              <button
                onClick={handleAiSubmit}
                disabled={!aiPromptText.trim() || aiLoading}
                className="w-full px-4 py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {aiLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Apply with AI
                  </>
                )}
              </button>
              {aiMessage && (
                <div className={`p-3 rounded-lg text-sm ${
                  aiMessage.includes("couldn't") || aiMessage.includes("Please provide")
                    ? 'bg-amber-50 border border-amber-200 text-amber-700'
                    : 'bg-emerald-50 border border-emerald-200 text-emerald-700'
                }`}>
                  {aiMessage}
                </div>
              )}
            </div>

            <div className="pt-4 border-t border-stone-100">
              <p className="text-xs text-stone-400 mb-2">Try asking:</p>
              <div className="space-y-1">
                {[
                  'Set center to downtown Austin with 1 mile radius',
                  'Show demographics for this area',
                  'Find all coffee shops nearby',
                  'Clone Starbucks business model here'
                ].map((suggestion, i) => (
                  <button
                    key={i}
                    onClick={() => setAiPromptText(suggestion)}
                    className="w-full text-left px-2 py-1.5 text-xs text-stone-600 hover:bg-stone-50 rounded"
                  >
                    <ChevronRight className="w-3 h-3 inline mr-1 text-stone-400" />
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : activeDefinition ? (
          <div className="space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-stone-900">{activeDefinition.label}</h3>
                <p className="text-xs text-stone-500 mt-0.5">{activeDefinition.description}</p>
              </div>
              {activeLayer && (
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => handleToggleLayerVisibility(activeLayer.id)}
                    className="p-1.5 rounded-lg hover:bg-stone-100"
                    title={activeLayer.visible ? 'Hide layer' : 'Show layer'}
                  >
                    {activeLayer.visible ? (
                      <Eye className="w-4 h-4 text-stone-600" />
                    ) : (
                      <EyeOff className="w-4 h-4 text-stone-400" />
                    )}
                  </button>
                  <button
                    onClick={() => handleRemoveLayer(activeLayer.id)}
                    className="p-1.5 rounded-lg hover:bg-red-50 text-stone-400 hover:text-red-500"
                    title="Remove layer"
                  >
                    <X className="w-4 h-4" />
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
              />
            ) : (
              <div className="text-center py-8">
                <button
                  onClick={() => handleAddLayer(state.activeLayerTab as LayerType)}
                  className="px-4 py-2 bg-stone-100 text-stone-700 rounded-lg text-sm font-medium hover:bg-stone-200 flex items-center gap-2 mx-auto"
                >
                  <Plus className="w-4 h-4" />
                  Add {activeDefinition.label} Layer
                </button>
              </div>
            )}

            {activeLayer?.error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
                {activeLayer.error}
              </div>
            )}
          </div>
        ) : null}
      </div>

      {state.layers.length > 0 && state.activeLayerTab !== 'ai' && (
        <div className="p-3 border-t border-stone-200 bg-stone-50">
          <p className="text-xs text-stone-500 mb-2">Active Layers</p>
          <div className="flex flex-wrap gap-1">
            {state.layers.map(layer => {
              const def = layerRegistry[layer.type]
              const Icon = def.icon
              return (
                <div
                  key={layer.id}
                  className={`flex items-center gap-1 px-2 py-1 rounded text-xs ${
                    layer.visible ? 'bg-white border border-stone-200' : 'bg-stone-100 text-stone-400'
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
  )
}
