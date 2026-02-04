/**
 * Type definitions for Discovery Feed components
 */

export interface Opportunity {
  id: number;
  title: string;
  description?: string;
  category?: string;
  validation_count?: number;
  growth_rate?: number;
  severity?: number;
  feasibility_score?: number;
  market_size?: string;
  geographic_scope?: string;
  city?: string;
  region?: string;
  country?: string;
  created_at: string;
  ai_generated_title?: string;
  ai_problem_statement?: string;
  ai_summary?: string;
  ai_opportunity_score?: number;
  ai_competition_level?: 'low' | 'medium' | 'high';
  ai_market_size_estimate?: string;
  ai_analyzed?: boolean;
  status?: string;
  moderation_status?: string;
  user_validated?: boolean;
  match_score?: number;
}

export interface FilterState {
  search: string;
  category: string | null;
  feasibility: string | null;
  location: string | null;
  sortBy: 'recent' | 'trending' | 'validated' | 'market' | 'feasibility' | 'recommended';
  maxDaysOld: number | null;
  myAccessOnly: boolean;
}

export interface PaginationState {
  currentPage: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
}

export type ViewMode = 'grid' | 'list';

export type UserTier = 'free' | 'pro' | 'business' | 'enterprise';

export interface FreshnessBadge {
  icon: string;
  label: string;
  color: string;
  tierRequired: UserTier;
}
