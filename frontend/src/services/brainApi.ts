export type BrainResponse = {
  id: number
  name: string
  focus_tags: string[]
  match_score: number
  knowledge_items: number
  tokens_used: number
  estimated_cost_usd: number
}

export async function fetchActiveBrain(token: string): Promise<BrainResponse> {
  const res = await fetch('/api/v1/brains/active', {
    headers: { Authorization: `Bearer ${token}` },
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data?.detail || 'Failed to load brain')
  return data as BrainResponse
}

export async function upsertBrain(
  token: string,
  input: { name: string; focus_tags: string[] },
): Promise<BrainResponse> {
  const res = await fetch('/api/v1/brains/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(input),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data?.detail || 'Failed to create brain')
  return data as BrainResponse
}

export async function saveOpportunityToBrain(token: string, opportunityId: number): Promise<BrainResponse> {
  const res = await fetch('/api/v1/brains/save-opportunity', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ opportunity_id: opportunityId }),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data?.detail || 'Failed to save to brain')
  return data as BrainResponse
}

