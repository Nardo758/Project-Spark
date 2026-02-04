/**
 * OppGrid Discovery Feed - Main Page
 * Assembles all discovery components into complete feature
 */

import { useEffect } from 'react'
import '../styles/discovery-theme.css'
import {
  RecommendedSection,
  FilterBar,
  OpportunityGrid,
  Pagination,
  ComparisonPanel,
  ComparisonModal,
  SavedSearchModal,
} from '../components/DiscoveryFeed'
import { useDiscoveryStore } from '../stores/discoveryStore'

export default function Discover() {
  const {
    // State
    opportunities,
    recommendedOpportunities,
    filters,
    pagination,
    selectedOpportunityIds,
    loading,
    error,
    showComparisonModal,
    showSavedSearchModal,
    
    // Actions
    initializeFromUrl,
    setFilters,
    setPage,
    quickValidate,
    saveOpportunity,
    toggleSelection,
    setShowComparisonModal,
    setShowSavedSearchModal,
  } = useDiscoveryStore()

  // Initialize from URL on mount
  useEffect(() => {
    initializeFromUrl()
  }, [initializeFromUrl])

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation (placeholder - replace with your nav component) */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center text-white font-bold">
                O
              </div>
              <span className="text-xl font-bold text-gray-900">OppGrid</span>
            </div>
            <div className="flex items-center gap-6">
              <a href="/discover" className="text-sm font-semibold text-emerald-600">Discover</a>
              <a href="/saved" className="text-sm font-medium text-gray-600 hover:text-gray-900">Saved</a>
              <a href="/hub" className="text-sm font-medium text-gray-600 hover:text-gray-900">Hub</a>
              <a href="/experts" className="text-sm font-medium text-gray-600 hover:text-gray-900">Experts</a>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Discover Validated Opportunities
          </h1>
          <p className="text-gray-600">
            Browse real-world problems validated by the community
          </p>
        </div>

        {/* Personalized Recommendations (Compact Carousel) */}
        {recommendedOpportunities.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
                <span className="text-purple-600">✨</span>
                Recommended for You
                <span className="text-xs text-gray-500 font-normal">
                  (based on your past interactions)
                </span>
              </h2>
              <button className="text-sm text-emerald-600 hover:text-emerald-700">
                View All →
              </button>
            </div>
            <div className="flex gap-4 overflow-x-auto pb-2 hide-scrollbar">
              {recommendedOpportunities.slice(0, 5).map((opp) => (
                <div
                  key={opp.id}
                  className="min-w-[280px] bg-gradient-to-br from-purple-50 to-white border border-purple-100 rounded-lg p-4 cursor-pointer hover:border-purple-300 transition-all"
                  onClick={() => window.location.href = `/opportunity/${opp.id}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-xs font-semibold text-purple-600">{opp.category}</span>
                    <span className="text-lg font-bold text-purple-600">{opp.feasibility_score}</span>
                  </div>
                  <h3 className="font-semibold text-sm text-gray-900 mb-1 line-clamp-2">
                    {opp.title}
                  </h3>
                  <div className="flex items-center gap-3 text-xs text-gray-600">
                    <span>✅ {opp.match_score}% match</span>
                    <span>{opp.validation_count} validations</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Filters */}
        <FilterBar
          filters={filters}
          onFiltersChange={setFilters}
          onSaveSearch={() => setShowSavedSearchModal(true)}
          className="mb-8"
        />

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Opportunity Grid */}
        <OpportunityGrid
          opportunities={opportunities}
          loading={loading}
          viewMode="grid"
          onValidate={quickValidate}
          onSave={saveOpportunity}
          onSelect={toggleSelection}
          selectedIds={selectedOpportunityIds}
          className="mb-8"
        />

        {/* Pagination */}
        {opportunities.length > 0 && (
          <Pagination
            pagination={pagination}
            onPageChange={setPage}
            className="mb-16"
          />
        )}

        {/* Empty State (when no results) */}
        {!loading && opportunities.length === 0 && (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-stone-900 mb-2">
              No opportunities found
            </h3>
            <p className="text-stone-600 mb-6">
              Try adjusting your filters or search terms
            </p>
            <button
              onClick={() => setFilters({})}
              className="px-6 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
            >
              Clear All Filters
            </button>
          </div>
        )}
      </main>

      {/* Floating Comparison Panel */}
      {selectedOpportunityIds.length > 0 && (
        <ComparisonPanel
          selectedIds={selectedOpportunityIds}
          opportunities={opportunities}
          onCompare={() => setShowComparisonModal(true)}
          onRemove={(id) => toggleSelection(id)}
          onClear={() => selectedOpportunityIds.forEach(id => toggleSelection(id))}
        />
      )}

      {/* Comparison Modal */}
      {showComparisonModal && (
        <ComparisonModal
          opportunityIds={selectedOpportunityIds}
          opportunities={opportunities}
          onClose={() => setShowComparisonModal(false)}
        />
      )}

      {/* Saved Search Modal */}
      {showSavedSearchModal && (
        <SavedSearchModal
          filters={filters}
          onClose={() => setShowSavedSearchModal(false)}
          onSave={(searchData) => {
            // This will be handled by the store
            console.log('Saving search:', searchData)
            setShowSavedSearchModal(false)
          }}
        />
      )}
    </div>
  )
}
