/**
 * Discovery Feed State Management Store
 * Manages opportunities, filters, pagination, selection, and API integration
 */

import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import {
  Opportunity,
  OpportunityFilters,
  SavedSearch,
  SavedSearchCreate,
} from '../types/opportunity'
import {
  fetchOpportunities,
  fetchRecommendedOpportunities,
  quickValidateOpportunity,
  unvalidateOpportunity,
  saveSearch,
  fetchSavedSearches,
  deleteSavedSearch,
  loadSavedSearch,
  saveOpportunity,
  unsaveOpportunity,
} from '../services/api'
import {
  syncFiltersToUrl,
  getFiltersFromUrl,
} from '../utils/urlParams'

interface DiscoveryState {
  // Data
  opportunities: Opportunity[]
  recommendedOpportunities: Opportunity[]
  savedSearches: SavedSearch[]
  
  // Pagination
  page: number
  pageSize: number
  total: number
  hasMore: boolean
  
  // Filters
  filters: OpportunityFilters
  
  // Selection (for comparison - max 3)
  selectedOpportunityIds: number[]
  
  // UI State
  loading: boolean
  recommendedLoading: boolean
  error: string | null
  view: 'grid' | 'list'
  
  // Actions - Data Fetching
  fetchOpportunities: () => Promise<void>
  fetchRecommendedOpportunities: () => Promise<void>
  fetchSavedSearches: () => Promise<void>
  loadSavedSearch: (searchId: number) => Promise<void>
  
  // Actions - Filters
  setFilters: (filters: Partial<OpportunityFilters>) => void
  clearFilters: () => void
  initializeFromUrl: () => void
  
  // Actions - Pagination
  setPage: (page: number) => void
  nextPage: () => void
  prevPage: () => void
  
  // Actions - Selection (for comparison)
  toggleSelection: (opportunityId: number) => void
  clearSelection: () => void
  getSelectedOpportunities: () => Opportunity[]
  
  // Actions - Quick Actions
  quickValidate: (opportunityId: number) => Promise<void>
  toggleSave: (opportunityId: number) => Promise<void>
  
  // Actions - Saved Searches
  createSavedSearch: (name: string, notificationPrefs: SavedSearchCreate['notification_prefs']) => Promise<void>
  deleteSavedSearch: (searchId: number) => Promise<void>
  
  // Actions - UI
  setView: (view: 'grid' | 'list') => void
  setError: (error: string | null) => void
}

const DEFAULT_FILTERS: OpportunityFilters = {
  sort_by: 'feasibility',
}

export const useDiscoveryStore = create<DiscoveryState>()(
  devtools(
    (set, get) => ({
      // Initial State
      opportunities: [],
      recommendedOpportunities: [],
      savedSearches: [],
      page: 1,
      pageSize: 20,
      total: 0,
      hasMore: false,
      filters: DEFAULT_FILTERS,
      selectedOpportunityIds: [],
      loading: false,
      recommendedLoading: false,
      error: null,
      view: 'grid',

      // Fetch opportunities with current filters and pagination
      fetchOpportunities: async () => {
        set({ loading: true, error: null })
        
        try {
          const { filters, page, pageSize } = get()
          const response = await fetchOpportunities(filters, page, pageSize)
          
          set({
            opportunities: response.opportunities,
            total: response.total,
            hasMore: response.has_more,
            loading: false,
          })
          
          // Sync to URL
          syncFiltersToUrl(filters, page)
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to fetch opportunities'
          set({ 
            loading: false, 
            error: errorMessage,
            opportunities: [],
          })
        }
      },

      // Fetch personalized recommendations
      fetchRecommendedOpportunities: async () => {
        set({ recommendedLoading: true })
        
        try {
          const recommended = await fetchRecommendedOpportunities(5)
          set({
            recommendedOpportunities: recommended,
            recommendedLoading: false,
          })
        } catch (error) {
          console.error('Failed to fetch recommendations:', error)
          set({ 
            recommendedLoading: false,
            recommendedOpportunities: [],
          })
        }
      },

      // Fetch user's saved searches
      fetchSavedSearches: async () => {
        try {
          const searches = await fetchSavedSearches()
          set({ savedSearches: searches })
        } catch (error) {
          console.error('Failed to fetch saved searches:', error)
        }
      },

      // Load opportunities from a saved search
      loadSavedSearch: async (searchId: number) => {
        set({ loading: true, error: null })
        
        try {
          const { savedSearches } = get()
          const savedSearch = savedSearches.find(s => s.id === searchId)
          
          if (!savedSearch) {
            throw new Error('Saved search not found')
          }
          
          // Update filters and reset to page 1
          set({
            filters: savedSearch.filters,
            page: 1,
          })
          
          // Fetch opportunities with the saved filters
          await get().fetchOpportunities()
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to load saved search'
          set({ 
            loading: false, 
            error: errorMessage,
          })
        }
      },

      // Update filters (partial update) and reset to page 1
      setFilters: (newFilters: Partial<OpportunityFilters>) => {
        set((state) => ({
          filters: { ...state.filters, ...newFilters },
          page: 1, // Reset to first page when filters change
        }))
        
        // Auto-fetch with new filters
        get().fetchOpportunities()
      },

      // Clear all filters back to defaults
      clearFilters: () => {
        set({
          filters: DEFAULT_FILTERS,
          page: 1,
        })
        
        get().fetchOpportunities()
      },

      // Initialize filters and page from URL params
      initializeFromUrl: () => {
        const { filters, page } = getFiltersFromUrl()
        set({
          filters,
          page,
        })
        
        // Fetch opportunities with URL filters
        get().fetchOpportunities()
        
        // Also fetch recommendations and saved searches
        get().fetchRecommendedOpportunities()
        get().fetchSavedSearches()
      },

      // Set specific page
      setPage: (page: number) => {
        set({ page })
        get().fetchOpportunities()
      },

      // Go to next page
      nextPage: () => {
        const { page, hasMore } = get()
        if (hasMore) {
          get().setPage(page + 1)
        }
      },

      // Go to previous page
      prevPage: () => {
        const { page } = get()
        if (page > 1) {
          get().setPage(page - 1)
        }
      },

      // Toggle opportunity selection for comparison (max 3)
      toggleSelection: (opportunityId: number) => {
        set((state) => {
          const isSelected = state.selectedOpportunityIds.includes(opportunityId)
          
          if (isSelected) {
            // Deselect
            return {
              selectedOpportunityIds: state.selectedOpportunityIds.filter(
                id => id !== opportunityId
              ),
            }
          } else {
            // Select (max 3)
            if (state.selectedOpportunityIds.length >= 3) {
              // Already at max - could show a toast here
              console.warn('Maximum 3 opportunities can be selected for comparison')
              return state
            }
            
            return {
              selectedOpportunityIds: [...state.selectedOpportunityIds, opportunityId],
            }
          }
        })
      },

      // Clear all selections
      clearSelection: () => {
        set({ selectedOpportunityIds: [] })
      },

      // Get full opportunity objects for selected IDs
      getSelectedOpportunities: () => {
        const { opportunities, selectedOpportunityIds } = get()
        return opportunities.filter(opp => selectedOpportunityIds.includes(opp.id))
      },

      // Quick validate with optimistic update
      quickValidate: async (opportunityId: number) => {
        // Optimistic update - immediately update UI
        set((state) => ({
          opportunities: state.opportunities.map(opp =>
            opp.id === opportunityId
              ? {
                  ...opp,
                  user_validated: !opp.user_validated,
                  validation_count: opp.user_validated 
                    ? opp.validation_count - 1 
                    : opp.validation_count + 1,
                }
              : opp
          ),
          recommendedOpportunities: state.recommendedOpportunities.map(opp =>
            opp.id === opportunityId
              ? {
                  ...opp,
                  user_validated: !opp.user_validated,
                  validation_count: opp.user_validated 
                    ? opp.validation_count - 1 
                    : opp.validation_count + 1,
                }
              : opp
          ),
        }))
        
        try {
          const opportunity = get().opportunities.find(opp => opp.id === opportunityId)
          
          if (opportunity?.user_validated) {
            // Was just validated - call API
            await quickValidateOpportunity(opportunityId)
          } else {
            // Was just unvalidated - call API
            await unvalidateOpportunity(opportunityId)
          }
        } catch (error) {
          console.error('Validation failed:', error)
          
          // Rollback optimistic update on error
          set((state) => ({
            opportunities: state.opportunities.map(opp =>
              opp.id === opportunityId
                ? {
                    ...opp,
                    user_validated: !opp.user_validated,
                    validation_count: opp.user_validated 
                      ? opp.validation_count - 1 
                      : opp.validation_count + 1,
                  }
                : opp
            ),
            recommendedOpportunities: state.recommendedOpportunities.map(opp =>
              opp.id === opportunityId
                ? {
                    ...opp,
                    user_validated: !opp.user_validated,
                    validation_count: opp.user_validated 
                      ? opp.validation_count - 1 
                      : opp.validation_count + 1,
                  }
                : opp
            ),
          }))
          
          // Show error
          set({ error: 'Failed to validate opportunity. Please try again.' })
        }
      },

      // Toggle save/bookmark with optimistic update
      toggleSave: async (opportunityId: number) => {
        // TODO: Add user_saved field to Opportunity type when backend implements it
        // For now, just call the API
        try {
          const opportunity = get().opportunities.find(opp => opp.id === opportunityId)
          
          // This assumes backend will add a user_saved field
          // For now, we just call save/unsave
          if ((opportunity as any)?.user_saved) {
            await unsaveOpportunity(opportunityId)
          } else {
            await saveOpportunity(opportunityId)
          }
          
          // Refresh opportunities to get updated state
          await get().fetchOpportunities()
        } catch (error) {
          console.error('Failed to save/unsave opportunity:', error)
          set({ error: 'Failed to save opportunity. Please try again.' })
        }
      },

      // Create a new saved search
      createSavedSearch: async (
        name: string,
        notificationPrefs: SavedSearchCreate['notification_prefs']
      ) => {
        try {
          const { filters } = get()
          const searchData: SavedSearchCreate = {
            name,
            filters,
            notification_prefs: notificationPrefs,
          }
          
          const newSearch = await saveSearch(searchData)
          
          set((state) => ({
            savedSearches: [...state.savedSearches, newSearch],
          }))
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to save search'
          set({ error: errorMessage })
          throw error
        }
      },

      // Delete a saved search
      deleteSavedSearch: async (searchId: number) => {
        try {
          await deleteSavedSearch(searchId)
          
          set((state) => ({
            savedSearches: state.savedSearches.filter(s => s.id !== searchId),
          }))
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to delete search'
          set({ error: errorMessage })
          throw error
        }
      },

      // Set view mode (grid or list)
      setView: (view: 'grid' | 'list') => {
        set({ view })
      },

      // Set error message
      setError: (error: string | null) => {
        set({ error })
      },
    }),
    { name: 'DiscoveryStore' }
  )
)
