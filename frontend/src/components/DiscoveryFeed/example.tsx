/**
 * Example: Full Discovery Feed Integration
 * 
 * This example demonstrates how to integrate all Discovery Feed components
 * together in a real application.
 */

import React, { useState, useEffect } from 'react';
import {
  QuickActions,
  ComparisonPanel,
  ComparisonModal,
  SavedSearchModal,
  Opportunity,
  NotificationPreferences,
  ComparisonMetrics
} from './index';

// Mock API functions (replace with real API calls)
const api = {
  validateOpportunity: async (id: string) => {
    console.log('Validating opportunity:', id);
    return new Promise(resolve => setTimeout(resolve, 500));
  },
  
  saveOpportunity: async (id: string) => {
    console.log('Saving opportunity:', id);
    return new Promise(resolve => setTimeout(resolve, 300));
  },
  
  saveSearch: async (data: { name: string; filters: any; notificationPrefs: NotificationPreferences }) => {
    console.log('Saving search:', data);
    return new Promise(resolve => setTimeout(resolve, 500));
  }
};

// Mock opportunities data
const mockOpportunities: Opportunity[] = [
  {
    id: 'opp-1',
    title: 'AI-Powered Invoice Management',
    description: 'Freelancers spend 15% of billable time on invoicing and payment tracking',
    category: 'Productivity',
    feasibilityScore: 82,
    validationCount: 445,
    growthRate: 18,
    marketSize: '$100M-$500M',
    geographicScope: 'International',
    ageInDays: 45,
    createdAt: '2024-01-15T10:00:00Z',
    userValidated: false,
    userSaved: false,
    matchScore: 92
  },
  {
    id: 'opp-2',
    title: 'Remote Team Schedule Coordinator',
    description: 'Coordinating meetings across time zones is a daily headache for distributed teams',
    category: 'Collaboration',
    feasibilityScore: 76,
    validationCount: 312,
    growthRate: 12,
    marketSize: '$50M-$100M',
    geographicScope: 'International',
    ageInDays: 32,
    createdAt: '2024-01-28T14:30:00Z',
    userValidated: false,
    userSaved: false,
    matchScore: 88
  },
  {
    id: 'opp-3',
    title: 'Local Service Provider Marketplace',
    description: 'Finding reliable local contractors is hit-or-miss with current platforms',
    category: 'Marketplace',
    feasibilityScore: 69,
    validationCount: 189,
    growthRate: 5,
    marketSize: '$500M+',
    geographicScope: 'Local',
    ageInDays: 67,
    createdAt: '2023-12-20T09:15:00Z',
    userValidated: true,
    userSaved: true,
    matchScore: 75
  }
];

export const DiscoveryFeedExample: React.FC = () => {
  // State management
  const [opportunities, setOpportunities] = useState<Opportunity[]>(mockOpportunities);
  const [selectedForComparison, setSelectedForComparison] = useState<{ id: string; title: string }[]>([]);
  const [showComparisonModal, setShowComparisonModal] = useState(false);
  const [showSaveSearchModal, setShowSaveSearchModal] = useState(false);
  const [currentFilters, setCurrentFilters] = useState({
    category: 'Tech',
    feasibility: 'High',
    location: 'All'
  });

  // Handlers for QuickActions
  const handleValidate = async (id: string) => {
    await api.validateOpportunity(id);
    
    // Optimistic update
    setOpportunities(prev => prev.map(opp => 
      opp.id === id 
        ? { ...opp, userValidated: true, validationCount: opp.validationCount + 1 }
        : opp
    ));
  };

  const handleSave = async (id: string) => {
    await api.saveOpportunity(id);
    
    // Toggle saved state
    setOpportunities(prev => prev.map(opp =>
      opp.id === id
        ? { ...opp, userSaved: !opp.userSaved }
        : opp
    ));
  };

  const handleAnalyze = (id: string) => {
    console.log('Analyzing opportunity:', id);
    // Navigate to analysis page or open analysis modal
  };

  const handleShare = (id: string) => {
    console.log('Sharing opportunity:', id);
    // Open share modal or copy link
    if (navigator.share) {
      navigator.share({
        title: opportunities.find(o => o.id === id)?.title,
        url: `${window.location.origin}/opportunity/${id}`
      });
    }
  };

  // Handlers for comparison
  const handleSelectForComparison = (opportunity: Opportunity) => {
    setSelectedForComparison(prev => {
      const isSelected = prev.some(o => o.id === opportunity.id);
      
      if (isSelected) {
        return prev.filter(o => o.id !== opportunity.id);
      } else if (prev.length < 3) {
        return [...prev, { id: opportunity.id, title: opportunity.title }];
      }
      
      return prev; // Max 3 reached
    });
  };

  const handleRemoveFromComparison = (id: string) => {
    setSelectedForComparison(prev => prev.filter(o => o.id !== id));
  };

  const handleCompare = () => {
    setShowComparisonModal(true);
  };

  const handleClearComparison = () => {
    setSelectedForComparison([]);
  };

  const handleViewDetails = (id: string) => {
    console.log('Viewing details for:', id);
    // Navigate to opportunity detail page
    window.location.href = `/opportunity/${id}`;
  };

  const handleExportPDF = () => {
    console.log('Exporting comparison as PDF');
    // Implement PDF export logic
  };

  // Handler for saved search
  const handleSaveSearch = async (name: string, notificationPrefs: NotificationPreferences) => {
    await api.saveSearch({
      name,
      filters: currentFilters,
      notificationPrefs
    });
    
    console.log('Search saved successfully!');
  };

  // Get full opportunity data for comparison
  const comparisonOpportunities: ComparisonMetrics[] = opportunities
    .filter(opp => selectedForComparison.some(s => s.id === opp.id))
    .map(opp => ({
      id: opp.id,
      title: opp.title,
      description: opp.description,
      category: opp.category,
      feasibilityScore: opp.feasibilityScore,
      validationCount: opp.validationCount,
      growthRate: opp.growthRate,
      marketSize: opp.marketSize,
      geographicScope: opp.geographicScope,
      ageInDays: opp.ageInDays
    }));

  return (
    <div className="discovery-feed-example min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 mb-6">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900">Discover Opportunities</h1>
            <button
              onClick={() => setShowSaveSearchModal(true)}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 
                         transition-colors font-medium"
            >
              💾 Save Search
            </button>
          </div>
        </div>
      </header>

      {/* Opportunities Grid */}
      <main className="container mx-auto px-4 pb-24">
        <div className="mb-4 text-sm text-gray-600">
          {opportunities.length} opportunities found
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {opportunities.map(opportunity => {
            const isSelected = selectedForComparison.some(o => o.id === opportunity.id);
            
            return (
              <div
                key={opportunity.id}
                className={`
                  bg-white rounded-lg shadow-md overflow-hidden transition-all duration-200
                  hover:shadow-xl hover:-translate-y-1
                  ${isSelected ? 'ring-2 ring-blue-500' : ''}
                `}
              >
                {/* Selection checkbox */}
                <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => handleSelectForComparison(opportunity)}
                      disabled={!isSelected && selectedForComparison.length >= 3}
                      className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-600">
                      {isSelected ? 'Selected for comparison' : 'Select to compare'}
                    </span>
                  </label>
                  
                  {opportunity.matchScore && (
                    <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded">
                      {opportunity.matchScore}% match
                    </span>
                  )}
                </div>

                {/* Card content */}
                <div className="p-6">
                  <div className="mb-2">
                    <span className="inline-block px-2 py-1 text-xs font-semibold bg-blue-100 text-blue-700 rounded">
                      {opportunity.category}
                    </span>
                  </div>

                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {opportunity.title}
                  </h3>

                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                    {opportunity.description}
                  </p>

                  {/* Feasibility score */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-semibold text-gray-700">Feasibility</span>
                      <span className={`text-sm font-bold ${
                        opportunity.feasibilityScore >= 75 ? 'text-green-600' :
                        opportunity.feasibilityScore >= 60 ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {opportunity.feasibilityScore}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          opportunity.feasibilityScore >= 75 ? 'bg-green-500' :
                          opportunity.feasibilityScore >= 60 ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}
                        style={{ width: `${opportunity.feasibilityScore}%` }}
                      />
                    </div>
                  </div>

                  {/* Metrics */}
                  <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                    <span>📊 {opportunity.validationCount} validations</span>
                    <span>🔥 +{opportunity.growthRate}% (7d)</span>
                  </div>

                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span>💰 {opportunity.marketSize}</span>
                    <span>•</span>
                    <span>🌍 {opportunity.geographicScope}</span>
                  </div>
                </div>

                {/* Quick Actions */}
                <QuickActions
                  opportunityId={opportunity.id}
                  userValidated={opportunity.userValidated}
                  isSaved={opportunity.userSaved}
                  onValidate={handleValidate}
                  onSave={handleSave}
                  onAnalyze={handleAnalyze}
                  onShare={handleShare}
                />
              </div>
            );
          })}
        </div>
      </main>

      {/* Comparison Panel (floating) */}
      <ComparisonPanel
        selectedOpportunities={selectedForComparison}
        maxSelection={3}
        onRemove={handleRemoveFromComparison}
        onCompare={handleCompare}
        onClear={handleClearComparison}
      />

      {/* Comparison Modal */}
      <ComparisonModal
        opportunities={comparisonOpportunities}
        isOpen={showComparisonModal}
        onClose={() => setShowComparisonModal(false)}
        onViewDetails={handleViewDetails}
        onExportPDF={handleExportPDF}
      />

      {/* Save Search Modal */}
      <SavedSearchModal
        isOpen={showSaveSearchModal}
        onClose={() => setShowSaveSearchModal(false)}
        onSave={handleSaveSearch}
        currentFilters={currentFilters}
        suggestedName="High-Potential Tech Opportunities"
      />
    </div>
  );
};

export default DiscoveryFeedExample;
