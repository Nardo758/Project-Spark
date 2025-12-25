interface BrainData {
  brainName?: string | null
  matchScore?: number
  tokensUsed?: number
  estimatedCostUsd?: number
  isEnabled?: boolean
}

export async function fetchActiveBrain(token: string): Promise<BrainData | null> {
  try {
    const response = await fetch('/api/v1/ai-engine/brain/active', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })
    if (!response.ok) {
      return null
    }
    return response.json()
  } catch {
    return null
  }
}
