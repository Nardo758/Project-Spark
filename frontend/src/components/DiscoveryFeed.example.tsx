/**
 * EXAMPLE: Complete Discovery Feed Component
 * 
 * This is a reference implementation showing how to use the discoveryStore.
 * Copy and adapt this for your actual implementation.
 */

import { useEffect } from 'react'
import { useDiscoveryStore } from '../stores/discoveryStore'

export function DiscoveryFeedExample() {
  const {
    // Data
    opportunities,
    recommendedOpportunities,
    
    // Pagination
    page,
    total,
    hasMore,
    
    // Filters
    filters,
    
    // Selection
    selectedOpportunityIds,
    getSelectedOpportunities,
    
    // UI State
    loading,
    recommendedLoading,
    error,
    view,
    
    // Actions
    initializeFromUrl,
    setFilters,
    clearFilters,
    setPage,
    nextPage,
    prevPage,
    toggleSelection,
    clearSelection,
    quickValidate,
    setView,
  } = useDiscoveryStore()

  // Initialize on mount - loads filters from URL
  useEffect(() => {
    initializeFromUrl()
  }, [initializeFromUrl])

  return (
    <div className="discovery-feed">
      {/* Header */}
      <header className="feed-header">
        <h1>Discover Opportunities</h1>
        
        {/* View Toggle */}
        <div className="view-toggle">
          <button
            onClick={() => setView('grid')}
            className={view === 'grid' ? 'active' : ''}
          >
            Grid
          </button>
          <button
            onClick={() => setView('list')}
            className={view === 'list' ? 'active' : ''}
          >
            List
          </button>
        </div>
      </header>

      {/* Recommended Section */}
      {recommendedOpportunities.length > 0 && (
        <section className="recommended-section">
          <h2>💡 Recommended for You</h2>
          
          {recommendedLoading ? (
            <div>Loading recommendations...</div>
          ) : (
            <div className="recommended-grid">
              {recommendedOpportunities.map(opp => (
                <OpportunityCardMini
                  key={opp.id}
                  opportunity={opp}
                  onValidate={() => quickValidate(opp.id)}
                />
              ))}
            </div>
          )}
        </section>
      )}

      {/* Filter Bar */}
      <section className="filter-bar">
        <div className="filters">
          {/* Search */}
          <input
            type="text"
            placeholder="Search opportunities..."
            value={filters.search || ''}
            onChange={(e) => setFilters({ search: e.target.value })}
            className="search-input"
          />

          {/* Category Filter */}
          <select
            value={filters.category || ''}
            onChange={(e) => setFilters({ category: e.target.value || null })}
          >
            <option value="">All Categories</option>
            <option value="Tech">Tech</option>
            <option value="Health">Health</option>
            <option value="Finance">Finance</option>
            <option value="Education">Education</option>
            <option value="Sustainability">Sustainability</option>
          </select>

          {/* Feasibility Range */}
          <div className="range-filter">
            <label>Min Feasibility:</label>
            <input
              type="number"
              min="0"
              max="100"
              value={filters.min_feasibility || ''}
              onChange={(e) => setFilters({ 
                min_feasibility: e.target.value ? parseInt(e.target.value) : null 
              })}
              placeholder="0"
            />
          </div>

          {/* Sort */}
          <select
            value={filters.sort_by || 'feasibility'}
            onChange={(e) => setFilters({ sort_by: e.target.value as any })}
          >
            <option value="feasibility">Highest Feasibility</option>
            <option value="recent">Most Recent</option>
            <option value="trending">Trending</option>
            <option value="validated">Most Validated</option>
            <option value="recommended">Recommended</option>
          </select>

          {/* Clear Filters */}
          <button onClick={clearFilters} className="btn-secondary">
            Clear All
          </button>
        </div>

        {/* Active Filters Display */}
        <div className="active-filters">
          {filters.search && (
            <span className="filter-tag">
              Search: "{filters.search}"
              <button onClick={() => setFilters({ search: '' })}>×</button>
            </span>
          )}
          {filters.category && (
            <span className="filter-tag">
              Category: {filters.category}
              <button onClick={() => setFilters({ category: null })}>×</button>
            </span>
          )}
          {filters.min_feasibility && (
            <span className="filter-tag">
              Min Feasibility: {filters.min_feasibility}
              <button onClick={() => setFilters({ min_feasibility: null })}>×</button>
            </span>
          )}
        </div>
      </section>

      {/* Error Display */}
      {error && (
        <div className="error-banner">
          <span>⚠️ {error}</span>
          <button onClick={() => useDiscoveryStore.getState().setError(null)}>
            Dismiss
          </button>
        </div>
      )}

      {/* Results Count */}
      <div className="results-info">
        <span>{total} opportunities found</span>
        {loading && <span className="loading-indicator">Loading...</span>}
      </div>

      {/* Opportunities Grid/List */}
      <section className={`opportunities ${view}`}>
        {loading && opportunities.length === 0 ? (
          // Initial loading state
          <div className="loading-state">
            <div className="spinner" />
            <p>Loading opportunities...</p>
          </div>
        ) : opportunities.length === 0 ? (
          // No results
          <div className="empty-state">
            <p>No opportunities found matching your filters.</p>
            <button onClick={clearFilters}>Clear Filters</button>
          </div>
        ) : (
          // Opportunities list
          opportunities.map(opp => (
            <OpportunityCard
              key={opp.id}
              opportunity={opp}
              isSelected={selectedOpportunityIds.includes(opp.id)}
              onToggleSelection={() => toggleSelection(opp.id)}
              onValidate={() => quickValidate(opp.id)}
            />
          ))
        )}
      </section>

      {/* Pagination */}
      {opportunities.length > 0 && (
        <section className="pagination">
          <button
            onClick={prevPage}
            disabled={page === 1}
            className="btn-secondary"
          >
            ← Previous
          </button>

          <span className="page-info">
            Page {page} of {Math.ceil(total / 20)}
          </span>

          <button
            onClick={nextPage}
            disabled={!hasMore}
            className="btn-secondary"
          >
            Next →
          </button>
        </section>
      )}

      {/* Comparison Panel (Floating) */}
      {selectedOpportunityIds.length > 0 && (
        <div className="comparison-panel">
          <div className="panel-content">
            <h4>Compare Selected ({selectedOpportunityIds.length}/3)</h4>
            
            <div className="selected-items">
              {getSelectedOpportunities().map(opp => (
                <span key={opp.id} className="selected-item">
                  {opp.title}
                </span>
              ))}
            </div>

            <div className="panel-actions">
              <button
                onClick={() => {
                  const selected = getSelectedOpportunities()
                  console.log('Open comparison modal with:', selected)
                  // TODO: Open ComparisonModal
                }}
                disabled={selectedOpportunityIds.length < 2}
                className="btn-primary"
              >
                Compare →
              </button>
              
              <button onClick={clearSelection} className="btn-secondary">
                Clear
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * Opportunity Card Component
 */
interface OpportunityCardProps {
  opportunity: any
  isSelected: boolean
  onToggleSelection: () => void
  onValidate: () => void
}

function OpportunityCard({ 
  opportunity, 
  isSelected, 
  onToggleSelection, 
  onValidate 
}: OpportunityCardProps) {
  return (
    <div className={`opportunity-card ${isSelected ? 'selected' : ''}`}>
      {/* Selection Checkbox */}
      <div className="card-header">
        <input
          type="checkbox"
          checked={isSelected}
          onChange={onToggleSelection}
          title="Select for comparison"
        />
        <span className="category-badge">{opportunity.category}</span>
      </div>

      {/* Content */}
      <div className="card-content">
        <h3>{opportunity.title}</h3>
        <p className="description">{opportunity.description}</p>

        {/* Metrics */}
        <div className="metrics">
          <div className="metric">
            <span className="label">Feasibility</span>
            <span className={`value score-${Math.floor(opportunity.feasibility_score / 20)}`}>
              {opportunity.feasibility_score}
            </span>
          </div>

          <div className="metric">
            <span className="label">Validations</span>
            <span className="value">{opportunity.validation_count}</span>
          </div>

          {opportunity.match_score && (
            <div className="metric">
              <span className="label">Match</span>
              <span className="value">{opportunity.match_score}%</span>
            </div>
          )}

          {opportunity.growth_rate && (
            <div className="metric">
              <span className="label">Growth</span>
              <span className="value positive">+{opportunity.growth_rate}%</span>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="card-actions">
          <button
            onClick={onValidate}
            className={`btn-validate ${opportunity.user_validated ? 'validated' : ''}`}
          >
            {opportunity.user_validated ? '✓ Validated' : 'Validate'}
          </button>

          <button className="btn-secondary">💾 Save</button>
          <button className="btn-secondary">🤖 Analyze</button>
          <button className="btn-secondary">↗ Share</button>
        </div>

        {/* Additional Info */}
        {opportunity.user_validated && (
          <div className="user-feedback">
            ✓ You validated this opportunity
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Mini Card for Recommended Section
 */
interface OpportunityCardMiniProps {
  opportunity: any
  onValidate: () => void
}

function OpportunityCardMini({ opportunity, onValidate }: OpportunityCardMiniProps) {
  return (
    <div className="opportunity-card-mini">
      <div className="match-score">
        {opportunity.match_score}% match
      </div>
      
      <h4>{opportunity.title}</h4>
      
      <div className="metrics-mini">
        <span>⚡ {opportunity.feasibility_score}</span>
        <span>👥 {opportunity.validation_count}</span>
      </div>

      <button
        onClick={onValidate}
        className={`btn-validate ${opportunity.user_validated ? 'validated' : ''}`}
      >
        {opportunity.user_validated ? '✓' : 'Validate'}
      </button>
    </div>
  )
}

/**
 * Example CSS (paste into your stylesheet)
 */
const exampleStyles = `
.discovery-feed {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.feed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.view-toggle button {
  padding: 0.5rem 1rem;
  margin-left: 0.5rem;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
}

.view-toggle button.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.recommended-section {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.recommended-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.filter-bar {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

.filters {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 250px;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.opportunities.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.opportunities.list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.opportunity-card {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.2s;
}

.opportunity-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: #007bff;
}

.opportunity-card.selected {
  border-color: #28a745;
  background: #f0fff4;
}

.metrics {
  display: flex;
  gap: 1rem;
  margin: 1rem 0;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.btn-validate {
  padding: 0.5rem 1rem;
  border: 2px solid #007bff;
  background: white;
  color: #007bff;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-validate:hover {
  background: #007bff;
  color: white;
}

.btn-validate.validated {
  background: #28a745;
  color: white;
  border-color: #28a745;
}

.comparison-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  box-shadow: 0 -4px 12px rgba(0,0,0,0.1);
  padding: 1rem;
  z-index: 1000;
}

.panel-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.selected-items {
  display: flex;
  gap: 0.5rem;
  flex: 1;
}

.selected-item {
  background: #e3f2fd;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  margin-top: 2rem;
  padding: 2rem 0;
}

.error-banner {
  background: #fff3cd;
  border: 1px solid #ffc107;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #666;
}

.loading-state {
  text-align: center;
  padding: 4rem 2rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}
`
