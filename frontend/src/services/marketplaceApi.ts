export type MarketplaceLead = {
  id: number
  public_id: string
  public_title: string
  anonymized_summary: string
  industry?: string | null
  deal_size_range?: string | null
  location?: string | null
  revenue_range?: string | null
  status: string
  lead_price_cents: number
  quality_score: number
  views_count: number
  purchase_count: number
  published_at?: string | null
  expires_at?: string | null
}

export type MarketplaceLeadListResponse = {
  leads: MarketplaceLead[]
  total: number
  page: number
  page_size: number
}

export type MarketplaceLeadDetail = MarketplaceLead & {
  opportunity_id?: number | null
  full_data_json?: string | null
  has_purchased: boolean
}

export async function fetchMarketplaceLeads(params: Record<string, string | number | undefined>) {
  const qp = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === '') continue
    qp.set(k, String(v))
  }
  const res = await fetch(`/api/v1/marketplace/leads?${qp.toString()}`)
  if (!res.ok) throw new Error('Failed to load leads')
  return (await res.json()) as MarketplaceLeadListResponse
}

export async function fetchMarketplaceLead(leadId: number) {
  const res = await fetch(`/api/v1/marketplace/leads/${leadId}`)
  if (!res.ok) throw new Error('Failed to load lead')
  return (await res.json()) as MarketplaceLeadDetail
}

