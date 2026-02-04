// Opportunity types for the Discovery Feed

export interface Opportunity {
  id: number
  title: string
  description: string
  category?: string
  geographic_scope?: string
  country?: string
  feasibility_score: number
  validation_count: number
  growth_rate?: number
  market_size?: string
  status: string
  created_at: string
  updated_at: string
  
  // Personalization fields
  match_score?: number
  user_validated?: boolean
  match_reasons?: MatchReason[]
  social_proof?: SocialProof
}

export interface MatchReason {
  type: 'skills' | 'category' | 'location' | 'feasibility' | 'validation'
  label: string
  score: number
  description: string
}

export interface SocialProof {
  similar_users_validated: number
  similar_users_text?: string
  expert_validation_count?: number
  trending_indicator?: boolean
}

export interface RecommendedOpportunitiesResponse {
  opportunities: Opportunity[]
  total: number
  personalization_metadata?: {
    user_interests: string[]
    recommendation_strategy: string
  }
}
