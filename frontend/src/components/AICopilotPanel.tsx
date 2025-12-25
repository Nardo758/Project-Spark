import { useState, useRef, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '../stores/authStore'
import { useLocation } from 'react-router-dom'
import { 
  MessageCircle, 
  X, 
  Send, 
  Trash2, 
  Sparkles,
  ChevronDown,
  Bot,
  User as UserIcon,
  Lightbulb
} from 'lucide-react'

interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  page_context?: string
  opportunity_id?: number
  created_at: string
}

interface Suggestion {
  id: number
  suggestion_type: string
  content: string
  page_context?: string
  opportunity_id?: number
}

function getPageContext(pathname: string): string {
  if (pathname.includes('/opportunity/') && pathname.includes('/hub')) return 'hub'
  if (pathname.includes('/opportunity/')) return 'opportunity_detail'
  if (pathname.includes('/saved')) return 'saved'
  if (pathname.includes('/discover') || pathname === '/') return 'feed'
  if (pathname.includes('/consultant')) return 'consultant'
  if (pathname.includes('/experts')) return 'experts'
  if (pathname.includes('/network')) return 'network'
  if (pathname.includes('/profile')) return 'profile'
  return 'general'
}

function extractOpportunityId(pathname: string): number | undefined {
  const match = pathname.match(/\/opportunity\/(\d+)/)
  return match ? parseInt(match[1], 10) : undefined
}

export function AICopilotPanel() {
  const [isOpen, setIsOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [isMinimized, setIsMinimized] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  
  const { token, isAuthenticated } = useAuthStore()
  const location = useLocation()
  const queryClient = useQueryClient()

  const pageContext = getPageContext(location.pathname)
  const opportunityId = extractOpportunityId(location.pathname)

  const { data: chatHistory = [], isLoading: historyLoading } = useQuery<ChatMessage[]>({
    queryKey: ['copilot-history'],
    queryFn: async () => {
      const res = await fetch('/api/v1/copilot/history?limit=50', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) return []
      return res.json()
    },
    enabled: isAuthenticated && isOpen
  })

  const { data: suggestions = [] } = useQuery<Suggestion[]>({
    queryKey: ['copilot-suggestions', pageContext, opportunityId],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (pageContext) params.append('page_context', pageContext)
      if (opportunityId) params.append('opportunity_id', String(opportunityId))
      const res = await fetch(`/api/v1/copilot/suggestions?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) return []
      return res.json()
    },
    enabled: isAuthenticated,
    staleTime: 60000
  })

  const chatMutation = useMutation({
    mutationFn: async (userMessage: string) => {
      const res = await fetch('/api/v1/copilot/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: userMessage,
          page_context: pageContext,
          opportunity_id: opportunityId
        })
      })
      if (!res.ok) throw new Error('Failed to send message')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['copilot-history'] })
      setMessage('')
    }
  })

  const clearMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/v1/copilot/history', {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) throw new Error('Failed to clear history')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['copilot-history'] })
    }
  })

  const dismissSuggestionMutation = useMutation({
    mutationFn: async (suggestionId: number) => {
      const res = await fetch(`/api/v1/copilot/suggestions/${suggestionId}/dismiss`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) throw new Error('Failed to dismiss suggestion')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['copilot-suggestions'] })
    }
  })

  useEffect(() => {
    if (messagesEndRef.current && isOpen) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [chatHistory, isOpen])

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  const handleSend = () => {
    if (!message.trim() || chatMutation.isPending) return
    chatMutation.mutate(message.trim())
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (!isAuthenticated) return null

  return (
    <>
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 bg-stone-900 text-white rounded-full shadow-lg hover:bg-stone-800 transition-all flex items-center justify-center z-50"
          title="Open AI Copilot"
        >
          <MessageCircle className="w-6 h-6" />
          {suggestions.length > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-amber-500 text-white text-xs rounded-full flex items-center justify-center">
              {suggestions.length}
            </span>
          )}
        </button>
      )}

      {isOpen && (
        <div className={`fixed bottom-6 right-6 w-96 bg-white rounded-xl shadow-2xl border border-gray-200 z-50 flex flex-col transition-all ${isMinimized ? 'h-14' : 'h-[500px]'}`}>
          <div 
            className="flex items-center justify-between px-4 py-3 bg-stone-900 text-white rounded-t-xl cursor-pointer"
            onClick={() => setIsMinimized(!isMinimized)}
          >
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-400" />
              <span className="font-semibold">AI Copilot</span>
              <span className="text-xs text-stone-400 capitalize">({pageContext})</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setIsMinimized(!isMinimized)
                }}
                className="p-1 hover:bg-stone-800 rounded"
              >
                <ChevronDown className={`w-4 h-4 transition-transform ${isMinimized ? 'rotate-180' : ''}`} />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setIsOpen(false)
                }}
                className="p-1 hover:bg-stone-800 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              {suggestions.length > 0 && (
                <div className="px-3 py-2 bg-amber-50 border-b border-amber-100">
                  <div className="flex items-center gap-1 text-xs text-amber-700 mb-1">
                    <Lightbulb className="w-3 h-3" />
                    <span>Suggestions</span>
                  </div>
                  {suggestions.slice(0, 2).map(suggestion => (
                    <div key={suggestion.id} className="text-xs text-amber-800 bg-white rounded px-2 py-1 mb-1 flex items-start justify-between">
                      <span className="flex-1">{suggestion.content}</span>
                      <button
                        onClick={() => dismissSuggestionMutation.mutate(suggestion.id)}
                        className="text-amber-500 hover:text-amber-700 ml-1"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex-1 overflow-y-auto p-3 space-y-3">
                {historyLoading ? (
                  <div className="text-center text-gray-400 text-sm py-4">Loading...</div>
                ) : chatHistory.length === 0 ? (
                  <div className="text-center text-gray-400 text-sm py-8">
                    <Bot className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                    <p>Hi! I'm your AI Copilot.</p>
                    <p className="text-xs mt-1">Ask me anything about opportunities, validation, or building your business.</p>
                  </div>
                ) : (
                  chatHistory.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[85%] rounded-lg px-3 py-2 ${
                        msg.role === 'user'
                          ? 'bg-stone-900 text-white'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        <div className="flex items-start gap-2">
                          {msg.role === 'assistant' && (
                            <Bot className="w-4 h-4 mt-0.5 text-stone-600 flex-shrink-0" />
                          )}
                          <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                          {msg.role === 'user' && (
                            <UserIcon className="w-4 h-4 mt-0.5 text-stone-300 flex-shrink-0" />
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>

              <div className="p-3 border-t border-gray-100">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => clearMutation.mutate()}
                    disabled={clearMutation.isPending || chatHistory.length === 0}
                    className="p-2 text-gray-400 hover:text-red-500 disabled:opacity-50"
                    title="Clear history"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                  <input
                    ref={inputRef}
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask anything..."
                    className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-stone-500"
                    disabled={chatMutation.isPending}
                  />
                  <button
                    onClick={handleSend}
                    disabled={!message.trim() || chatMutation.isPending}
                    className="p-2 bg-stone-900 text-white rounded-lg hover:bg-stone-800 disabled:opacity-50"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </>
  )
}
