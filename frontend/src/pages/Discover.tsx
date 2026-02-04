/**
 * OppGrid Discovery Feed - Main Page
 * Assembles all discovery components into complete feature
 */

import { useEffect } from 'react'
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
    <div className="min-h-screen bg-stone-50">
      {/* Navigation (placeholder - replace with your nav component) */}
      <nav className="bg-white border-b border-stone-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-stone-900 rounded-lg flex items-center justify-center text-white font-bold">
                O
              </div>
              <span className="text-xl font-bold text-stone-900">OppGrid</span>
            </div>
            <div className="flex items-center gap-6">
              <a href="/discover" className="text-sm font-semibold text-stone-900">Discover</a>
              <a href="/saved" className="text-sm font-medium text-stone-600 hover:text-stone-900">Saved</a>
              <a href="/hub" className="text-sm font-medium text-stone-600 hover:text-stone-900">Hub</a>
              <a href="/experts" className="text-sm font-medium text-stone-600 hover:text-stone-900">Experts</a>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Hero Section */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-stone-900 mb-2">
            Discover Validated Opportunities
          </h1>
          <p className="text-lg text-stone-600">
            Browse real-world problems validated by the community
          </p>
        </div>

        {/* Personalized Recommendations */}
        <RecommendedSection
          opportunities={recommendedOpportunities}
          loading={loading}
          onValidate={quickValidate}
          onSave={saveOpportunity}
          className="mb-12"
        />

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
              className="px-6 py-2 bg-stone-900 text-white rounded-lg hover:bg-stone-800 transition-colors"
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
