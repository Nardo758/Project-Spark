export type DeepSeekAnalyzeResponse = {
  match_score: number
  reasoning: string
  tokens_used: number
  estimated_cost_usd: number
}

export async function deepSeekAnalyze(token: string, opportunityId: number): Promise<DeepSeekAnalyzeResponse> {
  const res = await fetch('/api/v1/deepseek/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ opportunity_id: opportunityId, analysis_type: 'quick_match' }),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data?.detail || 'DeepSeek analysis failed')
  return data as DeepSeekAnalyzeResponse
}

