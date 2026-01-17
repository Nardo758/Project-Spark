import type { Tier } from '../constants/pricing'

export type ContentState = 'preview' | 'locked' | 'unlocked' | 'purchased'

export type LockReason = 
  | 'not_authenticated'
  | 'tier_required'
  | 'slot_limit'
  | 'exclusive_cap'
  | 'payment_required'

export interface FreshnessBadge {
  label: string
  icon: string
  color: string
  tier_required: string
  description: string
}

export interface AccessInfo {
  age_days: number
  days_until_unlock: number
  is_accessible: boolean
  working_on_count?: number
  is_unlocked: boolean
  can_pay_to_unlock: boolean
  unlock_price?: number | null
  user_tier?: Tier | string | null
  content_state?: ContentState | string | null
  freshness_badge?: FreshnessBadge | null
}

export interface OpportunityAccessSnapshot {
  opportunity_id: number
  is_locked: boolean
  lock_reason?: LockReason | null
  required_tier?: Tier | null
  can_unlock: boolean
  unlock_price?: number | null
  working_on_count?: number
  exclusive_cap?: number
  user_has_slot: boolean
  content_state: ContentState
}

export interface PaywallConfig {
  is_locked: boolean
  lock_reason: LockReason | null
  required_tier: Tier | null
  unlock_action: 'login' | 'upgrade' | 'purchase' | 'claim_slot' | null
  unlock_price: number | null
  cta_text: string
  cta_description: string
}

export function getPaywallConfig(access: OpportunityAccessSnapshot, isAuthenticated: boolean): PaywallConfig {
  if (!isAuthenticated) {
    return {
      is_locked: true,
      lock_reason: 'not_authenticated',
      required_tier: null,
      unlock_action: 'login',
      unlock_price: null,
      cta_text: 'Sign in to access',
      cta_description: 'Create an account or sign in to view this opportunity.',
    }
  }

  if (!access.is_locked) {
    return {
      is_locked: false,
      lock_reason: null,
      required_tier: null,
      unlock_action: null,
      unlock_price: null,
      cta_text: '',
      cta_description: '',
    }
  }

  if (access.lock_reason === 'tier_required' && access.required_tier) {
    return {
      is_locked: true,
      lock_reason: 'tier_required',
      required_tier: access.required_tier,
      unlock_action: 'upgrade',
      unlock_price: null,
      cta_text: `Upgrade to ${access.required_tier}`,
      cta_description: `This feature requires ${access.required_tier} tier or higher.`,
    }
  }

  if (access.lock_reason === 'slot_limit') {
    return {
      is_locked: true,
      lock_reason: 'slot_limit',
      required_tier: null,
      unlock_action: 'purchase',
      unlock_price: access.unlock_price ?? null,
      cta_text: access.unlock_price ? `Unlock for $${access.unlock_price}` : 'Purchase slot',
      cta_description: 'You\'ve reached your monthly slot limit. Purchase additional slots to continue.',
    }
  }

  if (access.lock_reason === 'exclusive_cap') {
    return {
      is_locked: true,
      lock_reason: 'exclusive_cap',
      required_tier: null,
      unlock_action: null,
      unlock_price: null,
      cta_text: 'Opportunity unavailable',
      cta_description: `This opportunity has reached its exclusivity cap (${access.exclusive_cap} users).`,
    }
  }

  if (access.can_unlock && access.unlock_price) {
    return {
      is_locked: true,
      lock_reason: 'payment_required',
      required_tier: null,
      unlock_action: 'purchase',
      unlock_price: access.unlock_price,
      cta_text: `Unlock for $${access.unlock_price}`,
      cta_description: 'Purchase access to view full opportunity details.',
    }
  }

  return {
    is_locked: true,
    lock_reason: null,
    required_tier: null,
    unlock_action: 'claim_slot',
    unlock_price: null,
    cta_text: 'Claim this opportunity',
    cta_description: 'Use one of your monthly slots to access this opportunity.',
  }
}
