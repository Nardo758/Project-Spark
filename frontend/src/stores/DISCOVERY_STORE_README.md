# Discovery Store Usage Guide

## Overview

The Discovery Store manages all state for the OppGrid Discovery Feed, including:
- Opportunity data and recommended opportunities
- Filter state with URL synchronization
- Pagination state
- Selection state for comparison (max 3)
- Loading and error states
- Optimistic updates for quick actions

## Quick Start

```tsx
import { useDiscoveryStore } from '@/stores/discoveryStore'

function DiscoveryFeed() {
  const {
    opportunities,
    loading,
    error,
    filters,
    page,
    total,
    hasMore,
    initializeFromUrl,
    setFilters,
    setPage,
    quickValidate,
  } = useDiscoveryStore()

  // Initialize on mount - loads from URL params
  useEffect(() => {
    initializeFromUrl()
  }, [initializeFromUrl])

  // Opportunities are automatically fetched when filters or page changes
  return (
    <div>
      {loading ? <Spinner /> : null}
      {error ? <ErrorBanner message={error} /> : null}
      
      {opportunities.map(opp => (
        <OpportunityCard 
          key={opp.id}
          opportunity={opp}
          onValidate={() => quickValidate(opp.id)}
        />
      ))}
      
      <Pagination 
        page={page}
        total={total}
        hasMore={hasMore}
        onNext={() => setPage(page + 1)}
        onPrev={() => setPage(page - 1)}
      />
    </div>
  )
}
```

## State Properties

### Data
- `opportunities: Opportunity[]` - Current page of opportunities
- `recommendedOpportunities: Opportunity[]` - Personalized recommendations
- `savedSearches: SavedSearch[]` - User's saved searches

### Pagination
- `page: number` - Current page (1-indexed)
- `pageSize: number` - Items per page (default: 20)
- `total: number` - Total number of opportunities matching filters
- `hasMore: boolean` - Whether there are more pages available

### Filters
- `filters: OpportunityFilters` - Current filter state
  ```ts
  {
    search?: string
    category?: string | null
    geographic_scope?: string | null
    country?: string | null
    completion_status?: string | null
    realm_type?: string | null
    min_feasibility?: number | null
    max_feasibility?: number | null
    min_validations?: number | null
    max_age_days?: number | null
    sort_by?: 'recent' | 'trending' | 'validated' | 'market' | 'feasibility' | 'recommended'
  }
  ```

### Selection (for comparison)
- `selectedOpportunityIds: number[]` - IDs of selected opportunities (max 3)

### UI State
- `loading: boolean` - Whether opportunities are being fetched
- `recommendedLoading: boolean` - Whether recommendations are loading
- `error: string | null` - Error message if any
- `view: 'grid' | 'list'` - Display mode

## Actions

### Data Fetching

#### `fetchOpportunities()`
Fetches opportunities with current filters and pagination. Automatically syncs state to URL.
```tsx
// Usually called automatically when filters/page change
// Manual call if needed:
fetchOpportunities()
```

#### `fetchRecommendedOpportunities()`
Fetches personalized recommendations (top 5 by default).
```tsx
useEffect(() => {
  fetchRecommendedOpportunities()
}, [])
```

#### `fetchSavedSearches()`
Loads user's saved searches.
```tsx
useEffect(() => {
  fetchSavedSearches()
}, [])
```

#### `loadSavedSearch(searchId: number)`
Applies a saved search's filters and fetches opportunities.
```tsx
<button onClick={() => loadSavedSearch(search.id)}>
  Load "{search.name}"
</button>
```

### Filters

#### `setFilters(filters: Partial<OpportunityFilters>)`
Updates filters and automatically fetches opportunities. Resets to page 1.
```tsx
// Single filter
setFilters({ category: 'Tech' })

// Multiple filters
setFilters({
  category: 'Tech',
  min_feasibility: 70,
  sort_by: 'recent'
})

// Clear a filter
setFilters({ category: null })
```

#### `clearFilters()`
Resets all filters to defaults and fetches opportunities.
```tsx
<button onClick={clearFilters}>Clear All Filters</button>
```

#### `initializeFromUrl()`
Loads filters and page from URL params. Call once on component mount.
```tsx
useEffect(() => {
  initializeFromUrl()
}, [])
```

### Pagination

#### `setPage(page: number)`
Navigate to a specific page.
```tsx
<button onClick={() => setPage(5)}>Go to page 5</button>
```

#### `nextPage()`
Navigate to next page (only if `hasMore` is true).
```tsx
<button onClick={nextPage} disabled={!hasMore}>Next</button>
```

#### `prevPage()`
Navigate to previous page (only if page > 1).
```tsx
<button onClick={prevPage} disabled={page === 1}>Previous</button>
```

### Selection (for comparison)

#### `toggleSelection(opportunityId: number)`
Toggles opportunity selection. Max 3 can be selected.
```tsx
<Checkbox
  checked={selectedOpportunityIds.includes(opp.id)}
  onChange={() => toggleSelection(opp.id)}
/>
```

#### `clearSelection()`
Clears all selections.
```tsx
<button onClick={clearSelection}>Clear Selection</button>
```

#### `getSelectedOpportunities()`
Returns full Opportunity objects for selected IDs.
```tsx
const selectedOpps = getSelectedOpportunities()
<ComparisonModal opportunities={selectedOpps} />
```

### Quick Actions

#### `quickValidate(opportunityId: number)`
Validates or unvalidates an opportunity with optimistic update.
```tsx
<button 
  onClick={() => quickValidate(opp.id)}
  className={opp.user_validated ? 'validated' : ''}
>
  {opp.user_validated ? '✓ Validated' : 'Validate'}
</button>
```

Features:
- Optimistic update - UI updates immediately
- Automatic rollback on error
- Updates validation count in real-time

#### `toggleSave(opportunityId: number)`
Saves or unsaves an opportunity.
```tsx
<button onClick={() => toggleSave(opp.id)}>
  {opp.user_saved ? '💾 Saved' : 'Save'}
</button>
```

### Saved Searches

#### `createSavedSearch(name: string, notificationPrefs: NotificationPreferences)`
Creates a new saved search with current filters.
```tsx
const handleSaveSearch = async () => {
  try {
    await createSavedSearch('High-Potential Tech', {
      email: true,
      email_frequency: 'daily',
      push: false,
      slack: false,
    })
    alert('Search saved!')
  } catch (error) {
    alert('Failed to save search')
  }
}
```

#### `deleteSavedSearch(searchId: number)`
Deletes a saved search.
```tsx
<button onClick={() => deleteSavedSearch(search.id)}>Delete</button>
```

### UI State

#### `setView(view: 'grid' | 'list')`
Changes display mode.
```tsx
<button onClick={() => setView('grid')}>Grid View</button>
<button onClick={() => setView('list')}>List View</button>
```

#### `setError(error: string | null)`
Sets or clears error message.
```tsx
setError('Something went wrong')
setError(null) // Clear error
```

## Example Components

### Filter Bar Component
```tsx
import { useDiscoveryStore } from '@/stores/discoveryStore'

function FilterBar() {
  const { filters, setFilters, clearFilters } = useDiscoveryStore()

  return (
    <div className="filter-bar">
      <input
        type="text"
        placeholder="Search opportunities..."
        value={filters.search || ''}
        onChange={(e) => setFilters({ search: e.target.value })}
      />
      
      <select
        value={filters.category || ''}
        onChange={(e) => setFilters({ category: e.target.value || null })}
      >
        <option value="">All Categories</option>
        <option value="Tech">Tech</option>
        <option value="Health">Health</option>
        <option value="Finance">Finance</option>
      </select>
      
      <select
        value={filters.sort_by || 'feasibility'}
        onChange={(e) => setFilters({ sort_by: e.target.value as any })}
      >
        <option value="feasibility">Highest Feasibility</option>
        <option value="recent">Most Recent</option>
        <option value="trending">Trending</option>
        <option value="validated">Most Validated</option>
      </select>
      
      <button onClick={clearFilters}>Clear Filters</button>
    </div>
  )
}
```

### Opportunity Card Component
```tsx
import { useDiscoveryStore } from '@/stores/discoveryStore'
import { Opportunity } from '@/types/opportunity'

interface OpportunityCardProps {
  opportunity: Opportunity
}

function OpportunityCard({ opportunity }: OpportunityCardProps) {
  const { 
    quickValidate, 
    toggleSelection, 
    selectedOpportunityIds 
  } = useDiscoveryStore()

  const isSelected = selectedOpportunityIds.includes(opportunity.id)

  return (
    <div className="opportunity-card">
      <input
        type="checkbox"
        checked={isSelected}
        onChange={() => toggleSelection(opportunity.id)}
        title="Select for comparison"
      />
      
      <h3>{opportunity.title}</h3>
      <p>{opportunity.description}</p>
      
      <div className="metrics">
        <span>Feasibility: {opportunity.feasibility_score}</span>
        <span>Validations: {opportunity.validation_count}</span>
        {opportunity.match_score && (
          <span>Match: {opportunity.match_score}%</span>
        )}
      </div>
      
      <button
        onClick={() => quickValidate(opportunity.id)}
        className={opportunity.user_validated ? 'validated' : ''}
      >
        {opportunity.user_validated ? '✓ Validated' : 'Validate'}
      </button>
    </div>
  )
}
```

### Comparison Panel Component
```tsx
import { useDiscoveryStore } from '@/stores/discoveryStore'

function ComparisonPanel() {
  const { 
    selectedOpportunityIds, 
    getSelectedOpportunities, 
    clearSelection 
  } = useDiscoveryStore()

  if (selectedOpportunityIds.length === 0) return null

  const selected = getSelectedOpportunities()

  return (
    <div className="comparison-panel">
      <h4>Compare Selected ({selectedOpportunityIds.length}/3)</h4>
      
      {selected.map(opp => (
        <span key={opp.id} className="selected-item">
          {opp.title}
        </span>
      ))}
      
      <button 
        onClick={() => {/* Open comparison modal */}}
        disabled={selectedOpportunityIds.length < 2}
      >
        Compare
      </button>
      
      <button onClick={clearSelection}>Clear</button>
    </div>
  )
}
```

## URL Synchronization

Filters are automatically synced to URL params:
- `?search=freelance` → `filters.search = 'freelance'`
- `?category=Tech&min_feas=70` → `filters.category = 'Tech', filters.min_feasibility = 70`
- `?page=3` → `page = 3`

This enables:
- ✅ Shareable URLs
- ✅ Browser back/forward button support
- ✅ Bookmark-able filtered views

### URL Parameter Mapping
| Filter | URL Param | Example |
|--------|-----------|---------|
| search | `search` | `?search=freelance` |
| category | `category` | `?category=Tech` |
| geographic_scope | `geo_scope` | `?geo_scope=local` |
| country | `country` | `?country=US` |
| completion_status | `completion` | `?completion=active` |
| realm_type | `realm` | `?realm=digital` |
| min_feasibility | `min_feas` | `?min_feas=70` |
| max_feasibility | `max_feas` | `?max_feas=90` |
| min_validations | `min_val` | `?min_val=100` |
| max_age_days | `max_age` | `?max_age=30` |
| sort_by | `sort` | `?sort=recent` |
| page | `page` | `?page=3` |

## Best Practices

1. **Initialize on mount**: Always call `initializeFromUrl()` once when the component mounts
2. **Use optimistic updates**: `quickValidate` already does this - UI updates immediately
3. **Handle errors**: Display `error` state to users
4. **Loading states**: Show spinners when `loading` is true
5. **Selection limits**: The store enforces max 3 selections automatically
6. **Filter reset**: Changing filters automatically resets to page 1
7. **URL sharing**: Users can share URLs with filters - they persist across sessions

## TypeScript Support

All types are fully typed with TypeScript. Import types as needed:

```tsx
import type { 
  Opportunity, 
  OpportunityFilters, 
  SavedSearch 
} from '@/types/opportunity'
```

## Testing

Example test setup:
```tsx
import { renderHook, act } from '@testing-library/react'
import { useDiscoveryStore } from '@/stores/discoveryStore'

test('filters update and trigger fetch', async () => {
  const { result } = renderHook(() => useDiscoveryStore())
  
  await act(async () => {
    result.current.setFilters({ category: 'Tech' })
  })
  
  expect(result.current.filters.category).toBe('Tech')
  expect(result.current.page).toBe(1) // Reset to page 1
})
```

## Performance Considerations

- **Debounce search input**: The `setFilters` action triggers immediate fetch. Consider debouncing search input:
  ```tsx
  const debouncedSetSearch = useMemo(
    () => debounce((value: string) => setFilters({ search: value }), 300),
    [setFilters]
  )
  ```

- **Memoize selectors**: Use `useMemo` for derived data:
  ```tsx
  const filteredCount = useMemo(() => 
    opportunities.filter(opp => opp.feasibility_score > 70).length,
    [opportunities]
  )
  ```

- **Lazy load recommendations**: Only fetch when "Recommended" section is visible

## Migration Guide (from legacy HTML)

If migrating from static HTML to React with this store:

1. Replace filter form submission with `setFilters`:
   ```tsx
   // Before
   <form action="/discover" method="GET">
     <select name="category">...</select>
     <button type="submit">Filter</button>
   </form>
   
   // After
   <select onChange={(e) => setFilters({ category: e.target.value })}>
     ...
   </select>
   ```

2. Replace pagination links with `setPage`:
   ```tsx
   // Before
   <a href="/discover?page=2">Next</a>
   
   // After
   <button onClick={() => setPage(2)}>Next</button>
   ```

3. Replace validation forms with `quickValidate`:
   ```tsx
   // Before
   <form action="/api/validate" method="POST">
     <input type="hidden" name="opp_id" value={opp.id} />
     <button type="submit">Validate</button>
   </form>
   
   // After
   <button onClick={() => quickValidate(opp.id)}>Validate</button>
   ```
