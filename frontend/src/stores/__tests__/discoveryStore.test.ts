/**
 * EXAMPLE: Discovery Store Tests
 * 
 * This demonstrates how to test the discoveryStore.
 * Requires: @testing-library/react, vitest (or jest)
 */

import { renderHook, act, waitFor } from '@testing-library/react'
import { useDiscoveryStore } from '../discoveryStore'
import * as api from '../../services/api'

// Mock the API module
vi.mock('../../services/api')

describe('Discovery Store', () => {
  beforeEach(() => {
    // Reset store state before each test
    useDiscoveryStore.setState({
      opportunities: [],
      recommendedOpportunities: [],
      savedSearches: [],
      page: 1,
      pageSize: 20,
      total: 0,
      hasMore: false,
      filters: { sort_by: 'feasibility' },
      selectedOpportunityIds: [],
      loading: false,
      recommendedLoading: false,
      error: null,
      view: 'grid',
    })

    // Clear all mocks
    vi.clearAllMocks()
  })

  describe('Filter Management', () => {
    test('setFilters updates filter state and resets to page 1', async () => {
      const mockResponse = {
        opportunities: [],
        total: 0,
        page: 1,
        page_size: 20,
        has_more: false,
      }
      vi.mocked(api.fetchOpportunities).mockResolvedValue(mockResponse)

      const { result } = renderHook(() => useDiscoveryStore())

      // Set page to 3 first
      act(() => {
        result.current.setPage(3)
      })

      await waitFor(() => {
        expect(result.current.page).toBe(3)
      })

      // Update filter - should reset to page 1
      act(() => {
        result.current.setFilters({ category: 'Tech' })
      })

      await waitFor(() => {
        expect(result.current.filters.category).toBe('Tech')
        expect(result.current.page).toBe(1)
      })
    })

    test('clearFilters resets to default state', async () => {
      const mockResponse = {
        opportunities: [],
        total: 0,
        page: 1,
        page_size: 20,
        has_more: false,
      }
      vi.mocked(api.fetchOpportunities).mockResolvedValue(mockResponse)

      const { result } = renderHook(() => useDiscoveryStore())

      act(() => {
        result.current.setFilters({
          category: 'Tech',
          min_feasibility: 70,
          search: 'test',
        })
      })

      await waitFor(() => {
        expect(result.current.filters.category).toBe('Tech')
      })

      act(() => {
        result.current.clearFilters()
      })

      await waitFor(() => {
        expect(result.current.filters).toEqual({ sort_by: 'feasibility' })
      })
    })
  })

  describe('Pagination', () => {
    test('nextPage increments page when hasMore is true', async () => {
      const mockResponse = {
        opportunities: [],
        total: 100,
        page: 1,
        page_size: 20,
        has_more: true,
      }
      vi.mocked(api.fetchOpportunities).mockResolvedValue(mockResponse)

      const { result } = renderHook(() => useDiscoveryStore())

      // Fetch to set hasMore
      await act(async () => {
        await result.current.fetchOpportunities()
      })

      expect(result.current.hasMore).toBe(true)

      // Go to next page
      await act(async () => {
        result.current.nextPage()
      })

      await waitFor(() => {
        expect(result.current.page).toBe(2)
      })
    })

    test('nextPage does nothing when hasMore is false', async () => {
      const mockResponse = {
        opportunities: [],
        total: 20,
        page: 1,
        page_size: 20,
        has_more: false,
      }
      vi.mocked(api.fetchOpportunities).mockResolvedValue(mockResponse)

      const { result } = renderHook(() => useDiscoveryStore())

      await act(async () => {
        await result.current.fetchOpportunities()
      })

      expect(result.current.hasMore).toBe(false)

      const currentPage = result.current.page

      act(() => {
        result.current.nextPage()
      })

      expect(result.current.page).toBe(currentPage)
    })

    test('prevPage decrements page when page > 1', async () => {
      const mockResponse = {
        opportunities: [],
        total: 100,
        page: 2,
        page_size: 20,
        has_more: true,
      }
      vi.mocked(api.fetchOpportunities).mockResolvedValue(mockResponse)

      const { result } = renderHook(() => useDiscoveryStore())

      // Set to page 2
      await act(async () => {
        result.current.setPage(2)
      })

      expect(result.current.page).toBe(2)

      // Go back
      await act(async () => {
        result.current.prevPage()
      })

      await waitFor(() => {
        expect(result.current.page).toBe(1)
      })
    })
  })

  describe('Selection Management', () => {
    test('toggleSelection adds opportunity to selection', () => {
      const { result } = renderHook(() => useDiscoveryStore())

      act(() => {
        result.current.toggleSelection(1)
      })

      expect(result.current.selectedOpportunityIds).toContain(1)
    })

    test('toggleSelection removes opportunity when already selected', () => {
      const { result } = renderHook(() => useDiscoveryStore())

      act(() => {
        result.current.toggleSelection(1)
      })

      expect(result.current.selectedOpportunityIds).toContain(1)

      act(() => {
        result.current.toggleSelection(1)
      })

      expect(result.current.selectedOpportunityIds).not.toContain(1)
    })

    test('toggleSelection enforces max 3 selections', () => {
      const { result } = renderHook(() => useDiscoveryStore())

      act(() => {
        result.current.toggleSelection(1)
        result.current.toggleSelection(2)
        result.current.toggleSelection(3)
      })

      expect(result.current.selectedOpportunityIds).toHaveLength(3)

      // Try to add a 4th - should be ignored
      act(() => {
        result.current.toggleSelection(4)
      })

      expect(result.current.selectedOpportunityIds).toHaveLength(3)
      expect(result.current.selectedOpportunityIds).not.toContain(4)
    })

    test('clearSelection removes all selections', () => {
      const { result } = renderHook(() => useDiscoveryStore())

      act(() => {
        result.current.toggleSelection(1)
        result.current.toggleSelection(2)
      })

      expect(result.current.selectedOpportunityIds).toHaveLength(2)

      act(() => {
        result.current.clearSelection()
      })

      expect(result.current.selectedOpportunityIds).toHaveLength(0)
    })

    test('getSelectedOpportunities returns full objects for selected IDs', () => {
      const mockOpportunities = [
        { id: 1, title: 'Opp 1', feasibility_score: 80 },
        { id: 2, title: 'Opp 2', feasibility_score: 75 },
        { id: 3, title: 'Opp 3', feasibility_score: 70 },
      ] as any

      const { result } = renderHook(() => useDiscoveryStore())

      // Set opportunities
      act(() => {
        useDiscoveryStore.setState({ opportunities: mockOpportunities })
      })

      // Select two
      act(() => {
        result.current.toggleSelection(1)
        result.current.toggleSelection(3)
      })

      const selected = result.current.getSelectedOpportunities()

      expect(selected).toHaveLength(2)
      expect(selected[0].id).toBe(1)
      expect(selected[1].id).toBe(3)
    })
  })

  describe('Quick Validation', () => {
    test('quickValidate performs optimistic update', async () => {
      const mockOpportunities = [
        { 
          id: 1, 
          title: 'Test Opp', 
          user_validated: false, 
          validation_count: 10,
          feasibility_score: 80,
        },
      ] as any

      vi.mocked(api.quickValidateOpportunity).mockResolvedValue({
        success: true,
        validation_count: 11,
        impact_points_earned: 5,
      })

      const { result } = renderHook(() => useDiscoveryStore())

      // Set opportunities
      act(() => {
        useDiscoveryStore.setState({ opportunities: mockOpportunities })
      })

      // Validate
      await act(async () => {
        await result.current.quickValidate(1)
      })

      // Should update immediately (optimistic)
      const updatedOpp = result.current.opportunities.find(o => o.id === 1)
      expect(updatedOpp?.user_validated).toBe(true)
      expect(updatedOpp?.validation_count).toBe(11)

      // API should have been called
      expect(api.quickValidateOpportunity).toHaveBeenCalledWith(1)
    })

    test('quickValidate rolls back on error', async () => {
      const mockOpportunities = [
        { 
          id: 1, 
          title: 'Test Opp', 
          user_validated: false, 
          validation_count: 10,
          feasibility_score: 80,
        },
      ] as any

      vi.mocked(api.quickValidateOpportunity).mockRejectedValue(
        new Error('API Error')
      )

      const { result } = renderHook(() => useDiscoveryStore())

      act(() => {
        useDiscoveryStore.setState({ opportunities: mockOpportunities })
      })

      // Validate (will fail)
      await act(async () => {
        await result.current.quickValidate(1)
      })

      // Should roll back to original state
      const updatedOpp = result.current.opportunities.find(o => o.id === 1)
      expect(updatedOpp?.user_validated).toBe(false)
      expect(updatedOpp?.validation_count).toBe(10)

      // Error should be set
      expect(result.current.error).toBeTruthy()
    })
  })

  describe('API Integration', () => {
    test('fetchOpportunities calls API with correct params', async () => {
      const mockResponse = {
        opportunities: [
          { id: 1, title: 'Opp 1', feasibility_score: 80 },
        ] as any,
        total: 1,
        page: 1,
        page_size: 20,
        has_more: false,
      }

      vi.mocked(api.fetchOpportunities).mockResolvedValue(mockResponse)

      const { result } = renderHook(() => useDiscoveryStore())

      act(() => {
        result.current.setFilters({ category: 'Tech', min_feasibility: 70 })
      })

      await waitFor(() => {
        expect(api.fetchOpportunities).toHaveBeenCalledWith(
          expect.objectContaining({
            category: 'Tech',
            min_feasibility: 70,
          }),
          1,
          20
        )
      })
    })

    test('fetchOpportunities handles errors gracefully', async () => {
      vi.mocked(api.fetchOpportunities).mockRejectedValue(
        new Error('Network error')
      )

      const { result } = renderHook(() => useDiscoveryStore())

      await act(async () => {
        await result.current.fetchOpportunities()
      })

      expect(result.current.error).toBeTruthy()
      expect(result.current.loading).toBe(false)
      expect(result.current.opportunities).toEqual([])
    })

    test('fetchRecommendedOpportunities sets recommendedOpportunities', async () => {
      const mockRecommended = [
        { id: 1, title: 'Recommended 1', match_score: 95 },
        { id: 2, title: 'Recommended 2', match_score: 90 },
      ] as any

      vi.mocked(api.fetchRecommendedOpportunities).mockResolvedValue(
        mockRecommended
      )

      const { result } = renderHook(() => useDiscoveryStore())

      await act(async () => {
        await result.current.fetchRecommendedOpportunities()
      })

      expect(result.current.recommendedOpportunities).toEqual(mockRecommended)
      expect(result.current.recommendedLoading).toBe(false)
    })
  })

  describe('Saved Searches', () => {
    test('createSavedSearch adds to savedSearches array', async () => {
      const mockSavedSearch = {
        id: 1,
        name: 'My Search',
        filters: { category: 'Tech' },
        notification_prefs: { email: true },
      } as any

      vi.mocked(api.saveSearch).mockResolvedValue(mockSavedSearch)

      const { result } = renderHook(() => useDiscoveryStore())

      await act(async () => {
        await result.current.createSavedSearch('My Search', { email: true })
      })

      expect(result.current.savedSearches).toContainEqual(mockSavedSearch)
    })

    test('deleteSavedSearch removes from array', async () => {
      const mockSavedSearches = [
        { id: 1, name: 'Search 1' },
        { id: 2, name: 'Search 2' },
      ] as any

      vi.mocked(api.deleteSavedSearch).mockResolvedValue()

      const { result } = renderHook(() => useDiscoveryStore())

      act(() => {
        useDiscoveryStore.setState({ savedSearches: mockSavedSearches })
      })

      await act(async () => {
        await result.current.deleteSavedSearch(1)
      })

      expect(result.current.savedSearches).toHaveLength(1)
      expect(result.current.savedSearches[0].id).toBe(2)
    })

    test('loadSavedSearch applies filters and fetches', async () => {
      const mockSavedSearches = [
        {
          id: 1,
          name: 'Tech Search',
          filters: { category: 'Tech', min_feasibility: 70 },
        },
      ] as any

      const mockResponse = {
        opportunities: [],
        total: 0,
        page: 1,
        page_size: 20,
        has_more: false,
      }

      vi.mocked(api.fetchOpportunities).mockResolvedValue(mockResponse)

      const { result } = renderHook(() => useDiscoveryStore())

      act(() => {
        useDiscoveryStore.setState({ savedSearches: mockSavedSearches })
      })

      await act(async () => {
        await result.current.loadSavedSearch(1)
      })

      expect(result.current.filters.category).toBe('Tech')
      expect(result.current.filters.min_feasibility).toBe(70)
      expect(api.fetchOpportunities).toHaveBeenCalled()
    })
  })

  describe('UI State', () => {
    test('setView updates view mode', () => {
      const { result } = renderHook(() => useDiscoveryStore())

      expect(result.current.view).toBe('grid')

      act(() => {
        result.current.setView('list')
      })

      expect(result.current.view).toBe('list')
    })

    test('setError updates error message', () => {
      const { result } = renderHook(() => useDiscoveryStore())

      act(() => {
        result.current.setError('Test error')
      })

      expect(result.current.error).toBe('Test error')

      act(() => {
        result.current.setError(null)
      })

      expect(result.current.error).toBeNull()
    })
  })
})
