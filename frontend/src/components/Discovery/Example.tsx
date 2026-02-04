/**
 * Example Discovery Feed Implementation
 * 
 * Complete working example showing how to use all Discovery components together.
 * This can be used as a template or reference implementation.
 */

import React, { useState, useEffect } from 'react';
import {
  OpportunityGrid,
  FilterBar,
  Pagination,
  FilterState,
  PaginationState,
  Opportunity,
  ViewMode,
  UserTier,
} from './index';

// Example API functions (replace with your actual API calls)
const api = {
  async getOpportunities(params: any): Promise<{ opportunities: Opportunity[]; total: number }> {
    // Replace with actual API call
    const response = await fetch('/api/opportunities', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    return response.json();
  },

  async validateOpportunity(id: number): Promise<void> {
    await fetch(`/api/opportunities/${id}/validate`, { method: 'POST' });
  },

  async saveOpportunity(id: number): Promise<void> {
    await fetch(`/api/opportunities/${id}/save`, { method: 'POST' });
  },

  async analyzeOpportunity(id: number): Promise<void> {
    await fetch(`/api/opportunities/${id}/analyze`, { method: 'POST' });
  },
};

export const DiscoveryFeedExample: React.FC = () => {
  // State
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [userTier, setUserTier] = useState<UserTier>('free'); // Get from auth context
  const [validatedIds, setValidatedIds] = useState<number[]>([]);
  const [savedIds, setSavedIds] = useState<number[]>([]);

  const [filters, setFilters] = useState<FilterState>({
    search: '',
    category: 'all',
    feasibility: 'all',
    location: 'all',
    sortBy: 'trending',
    freshness: 'all',
    myAccessOnly: false,
  });

  const [pagination, setPagination] = useState<PaginationState>({
    currentPage: 1,
    pageSize: 20,
    totalItems: 0,
    totalPages: 0,
  });

  // Fetch opportunities when filters or page changes
  useEffect(() => {
    fetchOpportunities();
  }, [filters, pagination.currentPage, pagination.pageSize]);

  const fetchOpportunities = async () => {
    setIsLoading(true);
    try {
      const params = {
        search: filters.search || undefined,
        category: filters.category !== 'all' ? filters.category : undefined,
        feasibility: filters.feasibility !== 'all' ? filters.feasibility : undefined,
        location: filters.location !== 'all' ? filters.location : undefined,
        sortBy: filters.sortBy,
        freshness: filters.freshness !== 'all' ? filters.freshness : undefined,
        myAccessOnly: filters.myAccessOnly,
        skip: (pagination.currentPage - 1) * pagination.pageSize,
        limit: pagination.pageSize,
      };

      const data = await api.getOpportunities(params);

      setOpportunities(data.opportunities);
      setPagination((prev) => ({
        ...prev,
        totalItems: data.total,
        totalPages: Math.ceil(data.total / prev.pageSize),
      }));
    } catch (error) {
      console.error('Failed to fetch opportunities:', error);
      // TODO: Show error toast/notification
    } finally {
      setIsLoading(false);
    }
  };

  // Quick validation handler
  const handleValidate = async (id: number) => {
    try {
      await api.validateOpportunity(id);

      // Optimistic update
      setValidatedIds([...validatedIds, id]);
      setOpportunities(
        opportunities.map((opp) =>
          opp.id === id
            ? {
                ...opp,
                validation_count: (opp.validation_count || 0) + 1,
                user_validated: true,
              }
            : opp
        )
      );

      // TODO: Show success message/confetti animation
      console.log('✓ Validated opportunity', id);
    } catch (error) {
      console.error('Failed to validate:', error);
      // TODO: Show error toast
    }
  };

  // Save opportunity handler
  const handleSave = async (id: number) => {
    try {
      const isSaved = savedIds.includes(id);

      if (isSaved) {
        // Unsave
        setSavedIds(savedIds.filter((savedId) => savedId !== id));
      } else {
        // Save
        await api.saveOpportunity(id);
        setSavedIds([...savedIds, id]);
      }

      console.log(isSaved ? '💾 Unsaved opportunity' : '💾 Saved opportunity', id);
    } catch (error) {
      console.error('Failed to save:', error);
    }
  };

  // Analyze opportunity handler
  const handleAnalyze = async (id: number) => {
    try {
      await api.analyzeOpportunity(id);
      console.log('🤖 AI analyzing opportunity', id);
      // TODO: Navigate to analysis page or show modal
    } catch (error) {
      console.error('Failed to analyze:', error);
    }
  };

  // Share opportunity handler
  const handleShare = (id: number) => {
    const url = `${window.location.origin}/opportunity.html?id=${id}`;

    if (navigator.share) {
      navigator
        .share({
          title: 'Check out this opportunity on OppGrid',
          url,
        })
        .then(() => console.log('Shared successfully'))
        .catch((err) => console.log('Share failed:', err));
    } else {
      // Fallback: Copy to clipboard
      navigator.clipboard.writeText(url);
      console.log('↗ Link copied to clipboard');
      // TODO: Show toast notification
    }
  };

  // Save search handler
  const handleSaveSearch = () => {
    // TODO: Show modal to name and save search
    console.log('💾 Save search with filters:', filters);
    // Example implementation:
    // showModal({
    //   title: 'Save This Search',
    //   content: <SaveSearchForm filters={filters} />,
    // });
  };

  // Handle filters change
  const handleFiltersChange = (newFilters: Partial<FilterState>) => {
    setFilters({ ...filters, ...newFilters });
    // Reset to page 1 when filters change
    setPagination({ ...pagination, currentPage: 1 });
  };

  // Handle page change
  const handlePageChange = (page: number) => {
    setPagination({ ...pagination, currentPage: page });
  };

  // Handle page size change
  const handlePageSizeChange = (pageSize: number) => {
    setPagination({
      ...pagination,
      pageSize,
      currentPage: 1, // Reset to first page
      totalPages: Math.ceil(pagination.totalItems / pageSize),
    });
  };

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Page Header */}
      <header className="bg-white border-b border-stone-200 py-12 px-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="font-spectral text-5xl font-bold text-stone-900 mb-4">
            Discover Validated Opportunities
          </h1>
          <p className="text-xl text-stone-600 max-w-3xl leading-relaxed">
            Browse market opportunities backed by real consumer insights. Each idea is
            AI-analyzed, validated, and ready to explore.
          </p>
        </div>
      </header>

      {/* Filter Bar */}
      <FilterBar
        filters={filters}
        onFiltersChange={handleFiltersChange}
        onSaveSearch={handleSaveSearch}
        isSticky={true}
        resultsCount={pagination.totalItems}
      />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-8 py-12">
        {/* Opportunities Grid */}
        <OpportunityGrid
          opportunities={opportunities}
          viewMode={viewMode}
          onViewModeChange={setViewMode}
          isLoading={isLoading}
          userTier={userTier}
          onValidate={handleValidate}
          onSave={handleSave}
          onAnalyze={handleAnalyze}
          onShare={handleShare}
          validatedIds={validatedIds}
          savedIds={savedIds}
          emptyMessage={
            filters.search
              ? `No opportunities found for "${filters.search}". Try adjusting your filters.`
              : 'No opportunities found. Be the first to submit one!'
          }
        />

        {/* Pagination */}
        {!isLoading && opportunities.length > 0 && (
          <Pagination
            pagination={pagination}
            onPageChange={handlePageChange}
            onPageSizeChange={handlePageSizeChange}
            showPageSize={true}
          />
        )}
      </main>

      {/* Floating Action Button */}
      <a
        href="/idea-generator.html"
        className="fixed bottom-6 right-6 bg-stone-900 text-white px-6 py-4 rounded-full font-semibold text-sm flex items-center gap-2 shadow-2xl hover:bg-stone-800 transition-all hover:-translate-y-1 z-50"
      >
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
        </svg>
        Generate Idea
      </a>

      {/* Global Styles */}
      <style jsx global>{`
        .font-spectral {
          font-family: 'Spectral', serif;
        }

        @media (max-width: 768px) {
          h1 {
            font-size: 2.5rem !important;
          }

          .max-w-7xl {
            padding-left: 1rem;
            padding-right: 1rem;
          }
        }
      `}</style>
    </div>
  );
};

export default DiscoveryFeedExample;
