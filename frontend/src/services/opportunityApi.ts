import type { Opportunity, RecommendedOpportunitiesResponse, MatchReason, SocialProof } from '../types/opportunity'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

/**
 * Fetch personalized opportunity recommendations
 */
export async function fetchRecommendedOpportunities(
  token: string,
  limit: number = 10
): Promise<Opportunity[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/opportunities/recommended?limit=${limit}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      console.error('Failed to fetch recommended opportunities:', response.statusText)
      return []
    }

    const data = await response.json()
    
    // The API returns an array of opportunities
    const opportunities = Array.isArray(data) ? data : data.opportunities || []
    
    // Enrich with match reasons and social proof
    return opportunities.map(enrichOpportunity)
  } catch (error) {
    console.error('Error fetching recommended opportunities:', error)
    return []
  }
}

/**
 * Enrich opportunity data with calculated match reasons
 */
function enrichOpportunity(opp: any): Opportunity {
  const matchScore = opp.match_score || 50
  
  // Calculate match reasons based on available data
  const matchReasons: MatchReason[] = []
  
  if (opp.category_match_score) {
    matchReasons.push({
      type: 'category',
      label: 'Category Interest',
      score: opp.category_match_score,
      description: `${opp.category_match_score}% match with your interests`
    })
  }
  
  if (opp.skills_alignment_score) {
    matchReasons.push({
      type: 'skills',
      label: 'Skills Alignment',
      score: opp.skills_alignment_score,
      description: `${opp.skills_alignment_score}% skills alignment`
    })
  }
  
  if (opp.feasibility_score >= 75) {
    matchReasons.push({
      type: 'feasibility',
      label: 'High Feasibility',
      score: opp.feasibility_score,
      description: `${opp.feasibility_score}% feasibility score`
    })
  }
  
  if (opp.growth_rate && opp.growth_rate > 10) {
    matchReasons.push({
      type: 'validation',
      label: 'Trending',
      score: Math.min(opp.growth_rate * 5, 100),
      description: `+${opp.growth_rate}% validation growth`
    })
  }
  
  // Calculate social proof
  const socialProof: SocialProof = {
    similar_users_validated: opp.similar_users_validated || 0,
    expert_validation_count: opp.expert_validations || 0,
    trending_indicator: opp.growth_rate && opp.growth_rate > 15
  }
  
  // Generate social proof text
  if (socialProof.similar_users_validated > 0) {
    socialProof.similar_users_text = `${socialProof.similar_users_validated} user${socialProof.similar_users_validated > 1 ? 's' : ''} like you validated this`
  }
  
  return {
    ...opp,
    match_score: matchScore,
    match_reasons: matchReasons,
    social_proof: socialProof
  }
}

/**
 * Quick validate an opportunity (from card, without navigating)
 */
export async function quickValidateOpportunity(
  opportunityId: number,
  token: string
): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/validations`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ opportunity_id: opportunityId })
    })

    return response.ok
  } catch (error) {
    console.error('Error validating opportunity:', error)
    return false
  }
}
