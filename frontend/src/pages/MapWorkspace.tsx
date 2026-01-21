import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import {
  Send,
  Loader2,
  MapPin,
  Layers,
  MessageSquare,
  X,
  ChevronLeft,
  ChevronRight,
  Compass,
  Target,
  Building2,
  Users,
  TrendingUp,
  HelpCircle
} from 'lucide-react'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  layer?: any
  actions?: string[]
}

interface MapLayer {
  id: string
  type: string
  visible: boolean
  data: any
}

interface Viewport {
  center: [number, number]
  zoom: number
}

export default function MapWorkspace() {
  const { opportunityId } = useParams()
  const navigate = useNavigate()
  const { token } = useAuthStore()
  
  const [loading, setLoading] = useState(true)
  const [opportunity, setOpportunity] = useState<any>(null)
  
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [sending, setSending] = useState(false)
  
  const [layers, setLayers] = useState<MapLayer[]>([])
  const [viewport, setViewport] = useState<Viewport>({
    center: [-98.5795, 39.8283],
    zoom: 4
  })
  
  const [chatPanelOpen, setChatPanelOpen] = useState(true)
  const [layersPanelOpen, setLayersPanelOpen] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const mapContainerRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    if (opportunityId && token) {
      fetchOpportunity()
      fetchSession()
    } else {
      setLoading(false)
    }
  }, [opportunityId, token])
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  
  async function fetchOpportunity() {
    if (!token || !opportunityId) return
    
    try {
      const res = await fetch(`/api/v1/opportunities/${opportunityId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setOpportunity(data)
        
        if (data.location_lat && data.location_lng) {
          setViewport({
            center: [data.location_lng, data.location_lat],
            zoom: 10
          })
        }
        
        setMessages([{
          id: 'welcome',
          role: 'assistant',
          content: `Welcome to the Map Workspace for "${data.title}". I can help you analyze the location, find competitors, and explore demographics. Try asking:\n\n- "Show me competitors"\n- "What are the demographics here?"\n- "Set radius to 5 miles"`,
          timestamp: new Date()
        }])
      }
    } catch (err) {
      console.error('Failed to fetch opportunity:', err)
    } finally {
      setLoading(false)
    }
  }
  
  async function fetchSession() {
    if (!token) return
    
    try {
      const res = await fetch('/api/v1/workspace/map/session', {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        if (data.viewport) {
          setViewport(data.viewport)
        }
        if (data.layer_state) {
          setLayers(Object.values(data.layer_state))
        }
      }
    } catch (err) {
      console.error('Failed to fetch session:', err)
    }
  }
  
  async function sendMessage() {
    if (!inputValue.trim() || sending || !token) return
    
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    }
    
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setSending(true)
    
    try {
      const res = await fetch('/api/v1/workspace/map/chat', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content: userMessage.content,
          opportunity_id: opportunityId ? parseInt(opportunityId) : undefined,
          business_type: opportunity?.category,
          current_location: opportunity?.location,
          center_lat: viewport.center[1],
          center_lng: viewport.center[0]
        })
      })
      
      if (res.ok) {
        const data = await res.json()
        
        const assistantMessage: ChatMessage = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: data.message,
          timestamp: new Date(),
          layer: data.layer,
          actions: data.actions
        }
        
        setMessages(prev => [...prev, assistantMessage])
        
        if (data.layer) {
          addLayer(data.layer)
        }
        
        handleActions(data.actions)
      } else {
        setMessages(prev => [...prev, {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: 'Sorry, I encountered an error processing your request. Please try again.',
          timestamp: new Date()
        }])
      }
    } catch (err) {
      console.error('Failed to send message:', err)
      setMessages(prev => [...prev, {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Connection error. Please check your network and try again.',
        timestamp: new Date()
      }])
    } finally {
      setSending(false)
    }
  }
  
  function addLayer(layerData: any) {
    const newLayer: MapLayer = {
      id: layerData.layer_id,
      type: layerData.layer_type,
      visible: true,
      data: layerData
    }
    
    setLayers(prev => {
      const existing = prev.findIndex(l => l.id === newLayer.id)
      if (existing >= 0) {
        const updated = [...prev]
        updated[existing] = newLayer
        return updated
      }
      return [...prev, newLayer]
    })
  }
  
  function handleActions(actions: string[]) {
    if (!actions) return
    
    actions.forEach(action => {
      switch (action) {
        case 'fit_bounds':
          break
        case 'show_demographics_panel':
          setLayersPanelOpen(true)
          break
        case 'clear_layer':
          break
        default:
          break
      }
    })
  }
  
  function toggleLayerVisibility(layerId: string) {
    setLayers(prev => prev.map(layer => 
      layer.id === layerId 
        ? { ...layer, visible: !layer.visible }
        : layer
    ))
  }
  
  function removeLayer(layerId: string) {
    setLayers(prev => prev.filter(l => l.id !== layerId))
  }
  
  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }, [inputValue, sending])
  
  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-900">
        <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
      </div>
    )
  }
  
  return (
    <div className="h-screen flex flex-col bg-gray-900 text-white overflow-hidden">
      <header className="h-14 border-b border-gray-700 flex items-center justify-between px-4 bg-gray-800/50 backdrop-blur shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <MapPin className="w-5 h-5 text-purple-400" />
            <span className="font-medium truncate max-w-[300px]">
              {opportunity?.title || 'Map Workspace'}
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setLayersPanelOpen(!layersPanelOpen)}
            className={`p-2 rounded-lg transition-colors ${
              layersPanelOpen ? 'bg-purple-600' : 'hover:bg-gray-700'
            }`}
            title="Toggle layers panel"
          >
            <Layers className="w-5 h-5" />
          </button>
          <button
            onClick={() => setChatPanelOpen(!chatPanelOpen)}
            className={`p-2 rounded-lg transition-colors ${
              chatPanelOpen ? 'bg-purple-600' : 'hover:bg-gray-700'
            }`}
            title="Toggle chat panel"
          >
            <MessageSquare className="w-5 h-5" />
          </button>
        </div>
      </header>
      
      <div className="flex-1 flex overflow-hidden">
        {layersPanelOpen && (
          <div className="w-64 border-r border-gray-700 bg-gray-800/50 flex flex-col shrink-0">
            <div className="p-3 border-b border-gray-700 flex items-center justify-between">
              <span className="font-medium text-sm">Layers</span>
              <button
                onClick={() => setLayersPanelOpen(false)}
                className="p-1 hover:bg-gray-700 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              {layers.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-4">
                  No layers added yet. Use the chat to add data to the map.
                </p>
              ) : (
                layers.map(layer => (
                  <div
                    key={layer.id}
                    className="p-3 bg-gray-700/50 rounded-lg"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium capitalize">
                        {layer.id.replace(/_/g, ' ')}
                      </span>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => toggleLayerVisibility(layer.id)}
                          className={`p-1 rounded ${layer.visible ? 'text-purple-400' : 'text-gray-500'}`}
                        >
                          {layer.visible ? '👁' : '👁‍🗨'}
                        </button>
                        <button
                          onClick={() => removeLayer(layer.id)}
                          className="p-1 text-gray-400 hover:text-red-400"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                    <p className="text-xs text-gray-400">
                      {layer.data?.metadata?.count !== undefined && (
                        <span>{layer.data.metadata.count} items</span>
                      )}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
        
        <div className="flex-1 relative bg-gray-900">
          <div
            ref={mapContainerRef}
            className="absolute inset-0 flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)' }}
          >
            <div className="text-center">
              <Compass className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 mb-2">Map visualization area</p>
              <p className="text-sm text-gray-500">
                Mapbox integration pending MAPBOX_ACCESS_TOKEN
              </p>
              <div className="mt-4 flex items-center justify-center gap-4 text-sm">
                <div className="flex items-center gap-2 text-gray-500">
                  <Target className="w-4 h-4" />
                  <span>
                    {viewport.center[1].toFixed(4)}, {viewport.center[0].toFixed(4)}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-gray-500">
                  <span>Zoom: {viewport.zoom}</span>
                </div>
              </div>
            </div>
          </div>
          
          {layers.length > 0 && (
            <div className="absolute bottom-4 left-4 bg-gray-800/90 backdrop-blur rounded-lg p-3 max-w-xs">
              <div className="text-xs text-gray-400 mb-2">Active Layers</div>
              <div className="flex flex-wrap gap-2">
                {layers.filter(l => l.visible).map(layer => (
                  <span
                    key={layer.id}
                    className="px-2 py-1 bg-purple-600/30 text-purple-300 rounded text-xs"
                  >
                    {layer.id}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {chatPanelOpen && (
          <div className="w-96 border-l border-gray-700 bg-gray-800/50 flex flex-col shrink-0">
            <div className="p-3 border-b border-gray-700 flex items-center justify-between">
              <span className="font-medium text-sm">AI Assistant</span>
              <button
                onClick={() => setChatPanelOpen(false)}
                className="p-1 hover:bg-gray-700 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-3 space-y-4">
              {messages.map(message => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-lg p-3 ${
                      message.role === 'user'
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-700 text-gray-100'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    {message.layer && (
                      <div className="mt-2 pt-2 border-t border-gray-600/50">
                        <div className="flex items-center gap-2 text-xs text-gray-300">
                          <Layers className="w-3 h-3" />
                          <span>Added layer: {message.layer.layer_id}</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            
            <div className="p-3 border-t border-gray-700">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Ask about competitors, demographics..."
                  className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 placeholder-gray-400"
                  disabled={sending}
                />
                <button
                  onClick={sendMessage}
                  disabled={!inputValue.trim() || sending}
                  className="p-2 bg-purple-600 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {sending ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </button>
              </div>
              
              <div className="mt-3 flex flex-wrap gap-2">
                {['Show competitors', 'Demographics', 'Set radius 5mi'].map(suggestion => (
                  <button
                    key={suggestion}
                    onClick={() => {
                      setInputValue(suggestion)
                    }}
                    className="px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
