import { create } from 'zustand'

interface BrainState {
  brainName: string | null
  matchScore: number
  tokensUsed: number
  estimatedCostUsd: number
  isEnabled: boolean
  hydrateFromServer: (data: BrainData | null) => void
}

interface BrainData {
  brainName?: string | null
  matchScore?: number
  tokensUsed?: number
  estimatedCostUsd?: number
  isEnabled?: boolean
}

export const useBrainStore = create<BrainState>((set) => ({
  brainName: null,
  matchScore: 0,
  tokensUsed: 0,
  estimatedCostUsd: 0,
  isEnabled: false,
  hydrateFromServer: (data: BrainData | null) => {
    if (!data) return
    set({
      brainName: data.brainName ?? null,
      matchScore: data.matchScore ?? 0,
      tokensUsed: data.tokensUsed ?? 0,
      estimatedCostUsd: data.estimatedCostUsd ?? 0,
      isEnabled: data.isEnabled ?? false,
    })
  },
}))
