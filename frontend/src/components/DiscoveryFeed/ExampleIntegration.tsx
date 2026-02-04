/**
 * Example Integration - Discovery Feed with Personalization
 * 
 * This file demonstrates how to integrate the personalization components
 * into your Discover page. Copy this pattern into your actual page.
 */

import { useState } from 'react'
import { RecommendedSection, MatchScoreBadge, SocialProof } from './index'
import type { Opportunity } from '../../types/opportunity'

// Example: Full Discover Page with Personalization
export function DiscoverPageExample() {
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleOpportunityValidated = (opportunityId: number) => {
    console.log('✅ Opportunity validated:', opportunityId)
    
    // Optional: Show success toast
    // toast.success('Opportunity validated successfully!')
    
    // Optional: Refresh main feed to update counts
    setRefreshTrigger(prev => prev + 1)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Page Header */}
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Discover Opportunities
          </h1>
          <p className="text-lg text-gray-600">
            Find validated business opportunities matched to your profile
          </p>
        </header>

        {/* Personalized Recommendations Section */}
        <RecommendedSection 
          limit={9}
          onValidate={handleOpportunityValidated}
        />

        {/* Main Discovery Feed */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          {/* Filters, sorting, grid, etc. */}
          <MainDiscoveryFeed key={refreshTrigger} />
        </div>
      </div>
    </div>
  )
}

// Example: Using MatchScoreBadge standalone in opportunity cards
export function OpportunityCardWithBadge({ opportunity }: { opportunity: Opportunity }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      {/* Match Score at Top */}
      {opportunity.match_score !== undefined && (
        <div className="mb-3">
          <MatchScoreBadge 
            score={opportunity.match_score} 
            size="sm"
            showLabel={false}
          />
        </div>
      )}

      {/* Opportunity Content */}
      <h3 className="font-bold text-lg mb-2">{opportunity.title}</h3>
      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
        {opportunity.description}
      </p>

      {/* Match Reasons */}
      {opportunity.match_reasons && opportunity.match_reasons.length > 0 && (
        <div className="bg-purple-50 border border-purple-100 rounded-lg p-3 mb-3">
          <p className="text-xs font-semibold text-purple-900 mb-1">
            Why this matches:
          </p>
          <ul className="space-y-1">
            {opportunity.match_reasons.map((reason, idx) => (
              <li key={idx} className="text-xs text-purple-700 flex items-start gap-1">
                <span>•</span>
                <span>{reason.description}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Social Proof */}
      {opportunity.social_proof && (
        <div className="mb-4">
          <SocialProof 
            socialProof={opportunity.social_proof} 
            compact={true}
          />
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2">
        <button className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors">
          View Details
        </button>
        <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
          Save
        </button>
      </div>
    </div>
  )
}

// Example: Grid showing multiple opportunities with match scores
export function PersonalizedOpportunityGrid({ opportunities }: { opportunities: Opportunity[] }) {
  // Sort by match score (highest first)
  const sortedOpportunities = [...opportunities].sort((a, b) => 
    (b.match_score || 0) - (a.match_score || 0)
  )

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {sortedOpportunities.map(opportunity => (
        <OpportunityCardWithBadge 
          key={opportunity.id} 
          opportunity={opportunity}
        />
      ))}
    </div>
  )
}

// Example: Showing different badge sizes
export function BadgeSizeExamples() {
  return (
    <div className="space-y-4 p-8 bg-gray-50">
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Small Badge (for cards)</h3>
        <MatchScoreBadge score={92} size="sm" />
      </div>
      
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Medium Badge (default)</h3>
        <MatchScoreBadge score={78} size="md" />
      </div>
      
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Large Badge (hero sections)</h3>
        <MatchScoreBadge score={65} size="lg" />
      </div>
      
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Without label (compact mode)</h3>
        <MatchScoreBadge score={88} showLabel={false} />
      </div>
    </div>
  )
}

// Example: Social Proof Variations
export function SocialProofExamples() {
  const fullProof = {
    similar_users_validated: 12,
    similar_users_text: "12 users like you validated this",
    expert_validation_count: 3,
    trending_indicator: true
  }

  const minimalProof = {
    similar_users_validated: 5,
    similar_users_text: "5 users like you validated this"
  }

  return (
    <div className="space-y-6 p-8 bg-gray-50">
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Full Social Proof (normal mode)</h3>
        <SocialProof socialProof={fullProof} compact={false} />
      </div>
      
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Compact Social Proof (for cards)</h3>
        <SocialProof socialProof={fullProof} compact={true} />
      </div>
      
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Minimal Social Proof</h3>
        <SocialProof socialProof={minimalProof} compact={false} />
      </div>
    </div>
  )
}

// Placeholder component for main feed
function MainDiscoveryFeed() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900">All Opportunities</h2>
        <div className="flex gap-2">
          {/* Filter buttons, sort dropdown, etc. */}
        </div>
      </div>
      <div className="text-gray-500 text-center py-12">
        Your main opportunity feed goes here...
      </div>
    </div>
  )
}

// Export all examples
export default {
  DiscoverPageExample,
  OpportunityCardWithBadge,
  PersonalizedOpportunityGrid,
  BadgeSizeExamples,
  SocialProofExamples
}
