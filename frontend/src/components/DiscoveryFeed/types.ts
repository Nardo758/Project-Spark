/**
 * Types and interfaces for Discovery Feed components
 */

export interface Opportunity {
  id: string;
  title: string;
  description: string;
  category: string;
  feasibilityScore: number;
  validationCount: number;
  growthRate: number;
  marketSize: string;
  geographicScope: string;
  ageInDays: number;
  createdAt: string;
  userValidated?: boolean;
  userSaved?: boolean;
  matchScore?: number;
}

export interface NotificationPreferences {
  email: boolean;
  emailFrequency?: 'instant' | 'daily';
  push: boolean;
  slack: boolean;
}

export interface SavedSearch {
  id: string;
  name: string;
  filters: Record<string, any>;
  notificationPrefs: NotificationPreferences;
  createdAt: string;
  lastNotifiedAt?: string;
}

export interface DiscoveryFilters {
  search?: string;
  category?: string;
  feasibility?: string;
  location?: string;
  sortBy?: 'recent' | 'trending' | 'validated' | 'market' | 'feasibility' | 'recommended';
  minFeasibility?: number;
  maxFeasibility?: number;
  minValidations?: number;
  maxAgeDays?: number;
}

export interface ComparisonMetrics {
  id: string;
  title: string;
  description: string;
  category: string;
  feasibilityScore: number;
  validationCount: number;
  growthRate: number;
  marketSize: string;
  geographicScope: string;
  ageInDays: number;
}
