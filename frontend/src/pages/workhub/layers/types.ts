import { LucideIcon } from 'lucide-react'

export type LayerType = 
  | 'deep_clone'
  | 'demographics'
  | 'competition'
  | 'foot_traffic'
  | 'drive_by_traffic'
  | 'custom'

export interface LayerInputField {
  key: string
  label: string
  type: 'text' | 'number' | 'select' | 'toggle' | 'radius' | 'address' | 'combobox'
  placeholder?: string
  options?: { value: string; label: string }[]
  defaultValue?: any
  required?: boolean
}

export interface LayerDefinition {
  type: LayerType
  label: string
  description: string
  icon: LucideIcon
  inputs: LayerInputField[]
  aiKeywords: string[]
  defaultConfig: Record<string, any>
  color: string
}

export interface LayerInstance {
  id: string
  type: LayerType
  config: Record<string, any>
  visible: boolean
  loading: boolean
  data: any | null
  error: string | null
}

export interface LayerAction {
  action: 'add_layer' | 'update_layer' | 'remove_layer' | 'toggle_layer' | 'set_center' | 'set_radius'
  layerType?: LayerType
  layerId?: string
  config?: Record<string, any>
  center?: { lat: number; lng: number }
  radius?: number
}

export interface LocationFinderState {
  center: { lat: number; lng: number; address?: string } | null
  radius: number
  layers: LayerInstance[]
  activeLayerTab: LayerType | 'ai'
  optimalZones?: OptimalZone[]
  optimalZonesLoading?: boolean
  zoneSummary?: string
}

export interface ZoneMetrics {
  total_population: number
  population_growth: number
  median_income: number
  median_age: number
  total_competitors: number
  drive_by_traffic_monthly: number
  foot_traffic_monthly: number
}

export interface DerivedMetricValue {
  name: string
  raw_value: number
  normalized_value: number
  category: 'market' | 'traffic' | 'economic' | 'demographics'
  description: string
  is_higher_better: boolean
}

export interface DerivedMetrics {
  metrics: {
    competition_per_capita: DerivedMetricValue
    revenue_potential_per_competitor: DerivedMetricValue
    traffic_per_competitor: DerivedMetricValue
    foot_to_vehicle_ratio: DerivedMetricValue
    traffic_density: DerivedMetricValue
    customer_conversion_potential: DerivedMetricValue
    purchasing_power_index: DerivedMetricValue
    growth_momentum: DerivedMetricValue
    market_opportunity_score: DerivedMetricValue
    working_age_ratio: DerivedMetricValue
    income_per_traffic: DerivedMetricValue
  }
  category_scores: {
    market: number
    traffic: number
    economic: number
    demographics: number
  }
  overall_score: number
}

export interface OptimalZone {
  id: string
  center_lat: number
  center_lng: number
  radius_miles: number
  total_score: number
  scores?: {
    demographics: number
    competition: number
    market_signals: number
  }
  metrics?: ZoneMetrics
  component_scores?: {
    population: number
    growth: number
    income: number
    age: number
    competition: number
    foot_traffic: number
    drive_by_traffic: number
  }
  derived_metrics?: DerivedMetrics
  category_scores?: {
    market: number
    traffic: number
    economic: number
    demographics: number
  }
  trends?: TrendSummary
  insights: string[]
  rank: number
}

export interface FindOptimalZonesResponse {
  zones: OptimalZone[]
  analysis_summary: string
  center_lat: number
  center_lng: number
  target_radius_miles: number
}

export interface TrendIndicator {
  metric_name: string
  direction: 'up' | 'down' | 'stable'
  change_percent: number
  current_value: number
  previous_value: number
  confidence: number
  period: string
  data_source: string
}

export interface TrendSummary {
  traffic_trends: Record<string, TrendIndicator>
  competition_trends: Record<string, TrendIndicator>
  demographic_trends: Record<string, TrendIndicator>
  vitality_trends: Record<string, TrendIndicator>
  overall_momentum: 'growing' | 'stable' | 'declining'
  momentum_score: number
}
