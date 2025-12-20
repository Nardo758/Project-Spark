import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type BrainEventType = 'create_brain' | 'save_opportunity' | 'answer_question' | 'generate_report' | 'upload_knowledge'

export type BrainEvent = {
  id: string
  type: BrainEventType
  message: string
  deltaScore: number
  createdAt: number
}

type BrainState = {
  isEnabled: boolean
  brainName: string | null
  focusTags: string[]
  matchScore: number
  knowledgeItems: number
  tokensUsed: number
  estimatedCostUsd: number
  lastTrainedAt: number | null
  lastLearningMessage: string | null
  timeline: BrainEvent[]

  setEnabled: (enabled: boolean) => void
  hydrateFromServer: (input: {
    name: string
    focus_tags: string[]
    match_score: number
    knowledge_items: number
    tokens_used: number
    estimated_cost_usd: number
  }) => void

  // UI-only feedback helpers (server updates happen via API calls)
  noteLearning: (message: string, deltaScore?: number) => void
  dismissLearningMessage: () => void
}

function clamp01To100(n: number) {
  return Math.max(0, Math.min(100, Math.round(n)))
}

function makeId() {
  return `${Date.now()}_${Math.random().toString(16).slice(2)}`
}

function pushTimeline(state: BrainState, event: Omit<BrainEvent, 'id' | 'createdAt'>): BrainEvent[] {
  const next: BrainEvent = { id: makeId(), createdAt: Date.now(), ...event }
  return [next, ...(state.timeline || [])].slice(0, 20)
}

export const useBrainStore = create<BrainState>()(
  persist(
    (set) => ({
      isEnabled: true,
      brainName: null,
      focusTags: [],
      matchScore: 0,
      knowledgeItems: 0,
      tokensUsed: 0,
      estimatedCostUsd: 0,
      lastTrainedAt: null,
      lastLearningMessage: null,
      timeline: [],

      setEnabled: (enabled) => set({ isEnabled: enabled }),

      hydrateFromServer: (input) => {
        set((s) => ({
          brainName: input.name,
          focusTags: input.focus_tags ?? [],
          matchScore: clamp01To100(input.match_score ?? s.matchScore),
          knowledgeItems: Math.max(0, input.knowledge_items ?? s.knowledgeItems),
          tokensUsed: Math.max(0, input.tokens_used ?? s.tokensUsed),
          estimatedCostUsd: Math.max(0, input.estimated_cost_usd ?? s.estimatedCostUsd),
        }))
      },

      noteLearning: (message, deltaScore = 0) => {
        set((s) => ({
          lastTrainedAt: Date.now(),
          lastLearningMessage: message,
          timeline: pushTimeline(s, {
            type: 'answer_question',
            deltaScore,
            message,
          }),
        }))
      },

      dismissLearningMessage: () => set({ lastLearningMessage: null }),
    }),
    {
      name: 'oppgrid_brain_store_v1',
      partialize: (s) => ({
        isEnabled: s.isEnabled,
        brainName: s.brainName,
        focusTags: s.focusTags,
        matchScore: s.matchScore,
        knowledgeItems: s.knowledgeItems,
        tokensUsed: s.tokensUsed,
        estimatedCostUsd: s.estimatedCostUsd,
        lastTrainedAt: s.lastTrainedAt,
        timeline: s.timeline,
      }),
    },
  ),
)

