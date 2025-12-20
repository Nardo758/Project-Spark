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
  createBrain: (input: { brainName: string; focusTags: string[] }) => void
  quickTrain: () => void
  saveOpportunity: (input: { opportunityId: number; category?: string | null; title?: string | null }) => void
  answerDailyQuestion: (input: { topic: string }) => void
  dismissLearningMessage: () => void
}

function clamp01To100(n: number) {
  return Math.max(0, Math.min(100, Math.round(n)))
}

function estimateCostUsd(tokens: number) {
  // UI-only estimate: DeepSeek is very cost-effective; this is intentionally conservative.
  // Adjust once backend returns real token/cost usage.
  const usdPer1kTokens = 0.001
  return (tokens / 1000) * usdPer1kTokens
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

      createBrain: ({ brainName, focusTags }) => {
        const base = 42
        const tokens = 1200
        set((s) => ({
          brainName,
          focusTags,
          matchScore: clamp01To100(Math.max(s.matchScore, base)),
          knowledgeItems: Math.max(s.knowledgeItems, 0),
          tokensUsed: s.tokensUsed + tokens,
          estimatedCostUsd: estimateCostUsd(s.tokensUsed + tokens),
          lastTrainedAt: Date.now(),
          lastLearningMessage: 'DeepSeek Brain is live — it will learn from every interaction.',
          timeline: pushTimeline(s, {
            type: 'create_brain',
            deltaScore: Math.max(0, base - s.matchScore),
            message: `Created brain “${brainName}”`,
          }),
        }))
      },

      quickTrain: () => {
        const inc = 3
        const tokens = 450
        set((s) => ({
          matchScore: clamp01To100(s.matchScore + inc),
          tokensUsed: s.tokensUsed + tokens,
          estimatedCostUsd: estimateCostUsd(s.tokensUsed + tokens),
          lastTrainedAt: Date.now(),
          lastLearningMessage: `+${inc}%: DeepSeek updated your brain (quick train)`,
          timeline: pushTimeline(s, { type: 'answer_question', deltaScore: inc, message: 'Quick training session completed' }),
        }))
      },

      saveOpportunity: ({ opportunityId, category, title }) => {
        const inc = 5
        const tokens = 800
        set((s) => ({
          matchScore: clamp01To100(s.matchScore + inc),
          knowledgeItems: s.knowledgeItems + 1,
          tokensUsed: s.tokensUsed + tokens,
          estimatedCostUsd: estimateCostUsd(s.tokensUsed + tokens),
          lastTrainedAt: Date.now(),
          lastLearningMessage: `+${inc}%: Saved ${category ? category + ' ' : ''}opportunity${title ? ` (“${title}”)` : ''}`,
          timeline: pushTimeline(s, {
            type: 'save_opportunity',
            deltaScore: inc,
            message: `Saved opportunity #${opportunityId}${category ? ` (${category})` : ''}`,
          }),
        }))
      },

      answerDailyQuestion: ({ topic }) => {
        const inc = 4
        const tokens = 650
        set((s) => ({
          matchScore: clamp01To100(s.matchScore + inc),
          tokensUsed: s.tokensUsed + tokens,
          estimatedCostUsd: estimateCostUsd(s.tokensUsed + tokens),
          lastTrainedAt: Date.now(),
          lastLearningMessage: `+${inc}%: DeepSeek learned more about ${topic}`,
          timeline: pushTimeline(s, { type: 'answer_question', deltaScore: inc, message: `Answered daily question: ${topic}` }),
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

