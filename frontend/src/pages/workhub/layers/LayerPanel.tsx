import { useState } from 'react'
import { Sparkles, Plus, X, Eye, EyeOff, ChevronRight } from 'lucide-react'
import { layerRegistry, defaultLayerTabs, createLayerInstance } from './registry'
import type { LayerType, LayerInstance, LocationFinderState } from './types'
import { LayerInputRenderer } from './LayerInputRenderer'

interface LayerPanelProps {
  state: LocationFinderState
  onStateChange: (state: LocationFinderState) => void
  onAiPrompt: (prompt: string) => void
  aiLoading?: boolean
  aiMessage?: string | null
}

export function LayerPanel({ state, onStateChange, onAiPrompt, aiLoading, aiMessage }: LayerPanelProps) {
  const [aiPromptText, setAiPromptText] = useState('')

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
    ? getLayerByType(state.activeLayerTab)
    : null

  const activeDefinition = state.activeLayerTab !== 'ai'
    ? layerRegistry[state.activeLayerTab]
    : null

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg border border-stone-200 overflow-hidden">
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
                  {activeLayer.type !== 'center_point' && (
                    <button
                      onClick={() => handleRemoveLayer(activeLayer.id)}
                      className="p-1.5 rounded-lg hover:bg-red-50 text-stone-400 hover:text-red-500"
                      title="Remove layer"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
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
