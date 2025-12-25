import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '../stores/authStore'
import { 
  Search, 
  Bookmark, 
  BarChart2, 
  ClipboardList, 
  Play, 
  Rocket,
  Pause,
  Archive,
  ChevronRight,
  Check
} from 'lucide-react'

export type LifecycleState = 
  | 'discovered'
  | 'saved'
  | 'analyzing'
  | 'planning'
  | 'executing'
  | 'launched'
  | 'paused'
  | 'archived'

interface LifecycleStateInfo {
  label: string
  description: string
  color: string
  icon: React.ReactNode
  step: number
}

const LIFECYCLE_STATES: Record<LifecycleState, LifecycleStateInfo> = {
  discovered: {
    label: 'Discovered',
    description: 'Browse, preview, unlock',
    color: '#6b7280',
    icon: <Search className="w-4 h-4" />,
    step: 1
  },
  saved: {
    label: 'Saved',
    description: 'Organize, tag, notes',
    color: '#3b82f6',
    icon: <Bookmark className="w-4 h-4" />,
    step: 2
  },
  analyzing: {
    label: 'Analyzing',
    description: 'Market research, AI',
    color: '#8b5cf6',
    icon: <BarChart2 className="w-4 h-4" />,
    step: 3
  },
  planning: {
    label: 'Planning',
    description: 'Business plan, strategy',
    color: '#f59e0b',
    icon: <ClipboardList className="w-4 h-4" />,
    step: 4
  },
  executing: {
    label: 'Executing',
    description: 'Building, team, funding',
    color: '#10b981',
    icon: <Play className="w-4 h-4" />,
    step: 5
  },
  launched: {
    label: 'Launched',
    description: 'Live business',
    color: '#22c55e',
    icon: <Rocket className="w-4 h-4" />,
    step: 6
  },
  paused: {
    label: 'Paused',
    description: 'On hold',
    color: '#f97316',
    icon: <Pause className="w-4 h-4" />,
    step: 0
  },
  archived: {
    label: 'Archived',
    description: 'Completed/Closed',
    color: '#9ca3af',
    icon: <Archive className="w-4 h-4" />,
    step: 0
  }
}

const MAIN_STATES: LifecycleState[] = ['saved', 'analyzing', 'planning', 'executing', 'launched']

const ALLOWED_TRANSITIONS: Record<LifecycleState, LifecycleState[]> = {
  discovered: ['saved'],
  saved: ['analyzing', 'archived'],
  analyzing: ['planning', 'paused', 'archived'],
  planning: ['executing', 'analyzing', 'paused', 'archived'],
  executing: ['launched', 'planning', 'paused', 'archived'],
  launched: ['paused', 'archived'],
  paused: ['saved', 'analyzing', 'planning', 'executing', 'launched', 'archived'],
  archived: ['saved']
}

interface LifecycleTimelineProps {
  watchlistId: number
  currentState: LifecycleState
  stateChangedAt?: string
  onStateChange?: (newState: LifecycleState) => void
  compact?: boolean
}

export function LifecycleTimeline({ 
  watchlistId, 
  currentState, 
  stateChangedAt,
  onStateChange,
  compact = false
}: LifecycleTimelineProps) {
  const [showTransitionMenu, setShowTransitionMenu] = useState(false)
  const [transitionReason, setTransitionReason] = useState('')
  const [selectedTransition, setSelectedTransition] = useState<LifecycleState | null>(null)
  const queryClient = useQueryClient()
  const { token } = useAuthStore()

  const transitionMutation = useMutation({
    mutationFn: async ({ newState, reason }: { newState: LifecycleState, reason?: string }) => {
      const res = await fetch(`/api/v1/workhub/lifecycle/watchlist/${watchlistId}/transition`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        credentials: 'include',
        body: JSON.stringify({ new_state: newState, reason })
      })
      if (!res.ok) {
        const error = await res.json()
        throw new Error(error.detail || 'Failed to transition')
      }
      return res.json()
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'], exact: false })
      queryClient.invalidateQueries({ queryKey: ['lifecycle'], exact: false })
      setShowTransitionMenu(false)
      setSelectedTransition(null)
      setTransitionReason('')
      onStateChange?.(data.new_state)
    }
  })

  const allowedTransitions = ALLOWED_TRANSITIONS[currentState] || []
  const currentInfo = LIFECYCLE_STATES[currentState]
  const currentStep = currentInfo.step

  const handleTransition = (newState: LifecycleState) => {
    if (newState === 'paused' || newState === 'archived') {
      setSelectedTransition(newState)
    } else {
      transitionMutation.mutate({ newState })
    }
  }

  const confirmTransition = () => {
    if (selectedTransition) {
      transitionMutation.mutate({ 
        newState: selectedTransition, 
        reason: transitionReason || undefined 
      })
    }
  }

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <div 
          className="flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium text-white"
          style={{ backgroundColor: currentInfo.color }}
        >
          {currentInfo.icon}
          <span>{currentInfo.label}</span>
        </div>
        {allowedTransitions.length > 0 && (
          <div className="relative">
            <button
              onClick={() => setShowTransitionMenu(!showTransitionMenu)}
              className="p-1 rounded hover:bg-gray-100 text-gray-500"
              title="Change state"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
            {showTransitionMenu && (
              <div className="absolute left-0 top-full mt-1 bg-white rounded-lg shadow-lg border z-50 min-w-[160px]">
                {allowedTransitions.map(state => {
                  const info = LIFECYCLE_STATES[state]
                  return (
                    <button
                      key={state}
                      onClick={() => handleTransition(state)}
                      className="w-full flex items-center gap-2 px-3 py-2 hover:bg-gray-50 text-left text-sm"
                      disabled={transitionMutation.isPending}
                    >
                      <span style={{ color: info.color }}>{info.icon}</span>
                      <span>{info.label}</span>
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl border p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">Opportunity Journey</h3>
        {stateChangedAt && (
          <span className="text-xs text-gray-500">
            Updated {new Date(stateChangedAt).toLocaleDateString()}
          </span>
        )}
      </div>

      <div className="flex items-center justify-between mb-6">
        {MAIN_STATES.map((state, index) => {
          const info = LIFECYCLE_STATES[state]
          const isActive = state === currentState
          const isPast = info.step < currentStep
          const isFuture = info.step > currentStep

          return (
            <div key={state} className="flex items-center">
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                    isActive
                      ? 'ring-2 ring-offset-2'
                      : isPast
                      ? 'bg-opacity-100'
                      : 'bg-gray-200 text-gray-400'
                  }`}
                  style={{
                    backgroundColor: isActive || isPast ? info.color : undefined,
                    color: isActive || isPast ? 'white' : undefined,
                    ringColor: isActive ? info.color : undefined
                  }}
                >
                  {isPast ? <Check className="w-5 h-5" /> : info.icon}
                </div>
                <span
                  className={`mt-2 text-xs font-medium ${
                    isActive ? 'text-gray-900' : isPast ? 'text-gray-600' : 'text-gray-400'
                  }`}
                >
                  {info.label}
                </span>
              </div>
              {index < MAIN_STATES.length - 1 && (
                <div
                  className={`w-12 h-0.5 mx-2 ${
                    isPast ? 'bg-green-500' : 'bg-gray-200'
                  }`}
                />
              )}
            </div>
          )
        })}
      </div>

      {(currentState === 'paused' || currentState === 'archived') && (
        <div 
          className="flex items-center gap-2 px-3 py-2 rounded-lg mb-4"
          style={{ backgroundColor: `${currentInfo.color}15` }}
        >
          <span style={{ color: currentInfo.color }}>{currentInfo.icon}</span>
          <span className="text-sm font-medium" style={{ color: currentInfo.color }}>
            {currentInfo.label}
          </span>
          <span className="text-sm text-gray-600">- {currentInfo.description}</span>
        </div>
      )}

      {allowedTransitions.length > 0 && (
        <div className="border-t pt-4">
          <p className="text-sm text-gray-600 mb-3">Move to next stage:</p>
          <div className="flex flex-wrap gap-2">
            {allowedTransitions.map(state => {
              const info = LIFECYCLE_STATES[state]
              return (
                <button
                  key={state}
                  onClick={() => handleTransition(state)}
                  disabled={transitionMutation.isPending}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-sm font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
                  style={{ borderColor: info.color, color: info.color }}
                >
                  {info.icon}
                  <span>{info.label}</span>
                </button>
              )
            })}
          </div>
        </div>
      )}

      {selectedTransition && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
            <h4 className="font-semibold text-lg mb-2">
              {selectedTransition === 'paused' ? 'Pause Opportunity' : 'Archive Opportunity'}
            </h4>
            <p className="text-gray-600 text-sm mb-4">
              {selectedTransition === 'paused'
                ? "You can resume this opportunity anytime. Add a note about why you're pausing."
                : "Archive this opportunity when it's completed or no longer relevant."}
            </p>
            <textarea
              value={transitionReason}
              onChange={(e) => setTransitionReason(e.target.value)}
              placeholder={selectedTransition === 'paused' ? 'Why are you pausing?' : 'Reason for archiving...'}
              className="w-full px-3 py-2 border rounded-lg text-sm mb-4"
              rows={3}
            />
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => {
                  setSelectedTransition(null)
                  setTransitionReason('')
                }}
                className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={confirmTransition}
                disabled={transitionMutation.isPending}
                className="px-4 py-2 text-sm text-white rounded-lg disabled:opacity-50"
                style={{ backgroundColor: LIFECYCLE_STATES[selectedTransition].color }}
              >
                {transitionMutation.isPending ? 'Saving...' : 'Confirm'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export function LifecycleStateBadge({ state }: { state: LifecycleState }) {
  const info = LIFECYCLE_STATES[state]
  return (
    <div 
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium text-white"
      style={{ backgroundColor: info.color }}
    >
      {info.icon}
      <span>{info.label}</span>
    </div>
  )
}

export { LIFECYCLE_STATES, ALLOWED_TRANSITIONS }
