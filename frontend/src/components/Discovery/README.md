# Discovery Feed Components

React + TypeScript components for the OppGrid Discovery Feed, matching the Stone color palette design aesthetic.

## 📦 Components

### 1. **OpportunityCard**
Enhanced opportunity card with hover states, quick actions, and time-based access control.

**Features:**
- Hover animations and elevation effects
- Quick action buttons (Validate, Save, Analyze, Share)
- Time-decay access indicators (HOT 🔥, FRESH ⚡, VALIDATED ✓, ARCHIVE 📚)
- AI-powered insights and scoring
- Competition level badges
- Viewer count display
- Mobile responsive

**Props:**
```typescript
interface OpportunityCardProps {
  opportunity: Opportunity;
  userTier?: UserTier; // 'free' | 'pro' | 'business' | 'enterprise'
  onValidate?: (id: number) => void;
  onSave?: (id: number) => void;
  onAnalyze?: (id: number) => void;
  onShare?: (id: number) => void;
  isValidated?: boolean;
  isSaved?: boolean;
}
```

**Usage:**
```tsx
import { OpportunityCard } from '@/components/Discovery';

<OpportunityCard
  opportunity={opportunityData}
  userTier="pro"
  onValidate={(id) => handleValidate(id)}
  onSave={(id) => handleSave(id)}
  isValidated={false}
  isSaved={true}
/>
```

---

### 2. **OpportunityGrid**
Container for displaying opportunities in grid or list view with loading states.

**Features:**
- Grid/List view toggle
- Responsive layout (1 column mobile, 2 columns desktop)
- Loading skeletons
- Empty state with CTA
- Staggered fade-in animations

**Props:**
```typescript
interface OpportunityGridProps {
  opportunities: Opportunity[];
  viewMode?: ViewMode; // 'grid' | 'list'
  onViewModeChange?: (mode: ViewMode) => void;
  isLoading?: boolean;
  userTier?: UserTier;
  onValidate?: (id: number) => void;
  onSave?: (id: number) => void;
  onAnalyze?: (id: number) => void;
  onShare?: (id: number) => void;
  validatedIds?: number[];
  savedIds?: number[];
  emptyMessage?: string;
}
```

**Usage:**
```tsx
import { OpportunityGrid } from '@/components/Discovery';

<OpportunityGrid
  opportunities={opportunities}
  viewMode="grid"
  onViewModeChange={setViewMode}
  isLoading={isLoading}
  userTier="free"
  onValidate={handleValidate}
  validatedIds={[1, 2, 3]}
/>
```

---

### 3. **FilterBar**
Advanced filtering interface with search, category, feasibility, location, and freshness filters.

**Features:**
- Full-text search with debouncing (300ms)
- Category dropdown
- Feasibility range filter
- Location filter
- Sort options (Trending, Feasibility, Validated, Recent, Market Size)
- Freshness filters (HOT, FRESH, VALIDATED, ARCHIVE)
- "My Access Only" toggle
- Active filter pills with remove buttons
- Clear all filters
- Save search button
- Sticky positioning option

**Props:**
```typescript
interface FilterBarProps {
  filters: FilterState;
  onFiltersChange: (filters: Partial<FilterState>) => void;
  onSaveSearch?: () => void;
  isSticky?: boolean;
  resultsCount?: number;
}
```

**Usage:**
```tsx
import { FilterBar } from '@/components/Discovery';

const [filters, setFilters] = useState<FilterState>({
  search: '',
  category: 'all',
  feasibility: 'all',
  location: 'all',
  sortBy: 'trending',
  freshness: 'all',
  myAccessOnly: false,
});

<FilterBar
  filters={filters}
  onFiltersChange={(newFilters) => setFilters({ ...filters, ...newFilters })}
  onSaveSearch={handleSaveSearch}
  isSticky={true}
  resultsCount={432}
/>
```

---

### 4. **Pagination**
Page navigation component with previous/next buttons and page numbers.

**Features:**
- Previous/Next buttons with disabled states
- Smart page number display (shows first, last, current, and nearby pages)
- Ellipsis for large page ranges
- Results count display
- Optional page size selector
- Keyboard accessible
- Auto-scroll to top on page change

**Props:**
```typescript
interface PaginationProps {
  pagination: PaginationState;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
  showPageSize?: boolean;
}
```

**Usage:**
```tsx
import { Pagination } from '@/components/Discovery';

const [pagination, setPagination] = useState<PaginationState>({
  currentPage: 1,
  pageSize: 20,
  totalItems: 432,
  totalPages: 22,
});

<Pagination
  pagination={pagination}
  onPageChange={(page) => setPagination({ ...pagination, currentPage: page })}
  onPageSizeChange={(size) => setPagination({ ...pagination, pageSize: size, currentPage: 1 })}
  showPageSize={true}
/>
```

---

### 5. **OpportunityCardSkeleton**
Loading skeleton for OpportunityCard.

**Usage:**
```tsx
import { OpportunityCardSkeleton } from '@/components/Discovery';

{isLoading && (
  <div className="grid grid-cols-2 gap-6">
    <OpportunityCardSkeleton />
    <OpportunityCardSkeleton />
    <OpportunityCardSkeleton />
  </div>
)}
```

---

## 🎨 Design System

### Color Palette (Stone Theme)
```css
--stone-50: #fafaf9
--stone-100: #f5f5f4
--stone-200: #e7e5e4
--stone-300: #d6d3d1
--stone-400: #a8a29e
--stone-500: #78716c
--stone-600: #57534e
--stone-700: #44403c
--stone-800: #292524
--stone-900: #1c1917

--emerald-100: #d1fae5
--emerald-600: #16a34a
--emerald-700: #047857
```

### Typography
- **Headings:** Spectral (serif) - elegant, professional
- **Body:** Inter (sans-serif) - clean, readable

### Spacing
- Cards: 1.5rem padding, 1rem border-radius
- Grid gap: 1.5rem
- Section spacing: 3rem

---

## 🔧 Implementation Example

### Full Discovery Feed Page
```tsx
import React, { useState, useEffect } from 'react';
import {
  OpportunityGrid,
  FilterBar,
  Pagination,
  FilterState,
  PaginationState,
  Opportunity,
  ViewMode,
} from '@/components/Discovery';

export const DiscoveryFeed: React.FC = () => {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
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

  useEffect(() => {
    fetchOpportunities();
  }, [filters, pagination.currentPage]);

  const fetchOpportunities = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/opportunities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...filters,
          skip: (pagination.currentPage - 1) * pagination.pageSize,
          limit: pagination.pageSize,
        }),
      });
      const data = await response.json();
      setOpportunities(data.opportunities);
      setPagination({
        ...pagination,
        totalItems: data.total,
        totalPages: Math.ceil(data.total / pagination.pageSize),
      });
    } catch (error) {
      console.error('Failed to fetch opportunities:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleValidate = async (id: number) => {
    try {
      await fetch(`/api/opportunities/${id}/validate`, { method: 'POST' });
      setValidatedIds([...validatedIds, id]);
      // Optimistic update
      setOpportunities(
        opportunities.map((opp) =>
          opp.id === id
            ? { ...opp, validation_count: opp.validation_count + 1, user_validated: true }
            : opp
        )
      );
    } catch (error) {
      console.error('Failed to validate:', error);
    }
  };

  const handleSave = async (id: number) => {
    try {
      await fetch(`/api/opportunities/${id}/save`, { method: 'POST' });
      setSavedIds([...savedIds, id]);
    } catch (error) {
      console.error('Failed to save:', error);
    }
  };

  const handleSaveSearch = () => {
    // Implement save search modal
    console.log('Save search with filters:', filters);
  };

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Header */}
      <div className="bg-white border-b border-stone-200 py-12">
        <div className="max-w-7xl mx-auto px-8">
          <h1 className="font-spectral text-5xl font-bold text-stone-900 mb-4">
            Discover Validated Opportunities
          </h1>
          <p className="text-xl text-stone-600 max-w-3xl">
            Browse market opportunities backed by real consumer insights. Each idea is
            AI-analyzed, validated, and ready to explore.
          </p>
        </div>
      </div>

      {/* Filters */}
      <FilterBar
        filters={filters}
        onFiltersChange={(newFilters) => {
          setFilters({ ...filters, ...newFilters });
          setPagination({ ...pagination, currentPage: 1 }); // Reset to page 1
        }}
        onSaveSearch={handleSaveSearch}
        isSticky={true}
        resultsCount={pagination.totalItems}
      />

      {/* Opportunities Grid */}
      <div className="max-w-7xl mx-auto px-8 py-12">
        <OpportunityGrid
          opportunities={opportunities}
          viewMode={viewMode}
          onViewModeChange={setViewMode}
          isLoading={isLoading}
          userTier="pro"
          onValidate={handleValidate}
          onSave={handleSave}
          onAnalyze={(id) => console.log('Analyze:', id)}
          onShare={(id) => console.log('Share:', id)}
          validatedIds={validatedIds}
          savedIds={savedIds}
        />

        {/* Pagination */}
        <Pagination
          pagination={pagination}
          onPageChange={(page) => setPagination({ ...pagination, currentPage: page })}
          onPageSizeChange={(size) =>
            setPagination({ ...pagination, pageSize: size, currentPage: 1 })
          }
          showPageSize={true}
        />
      </div>
    </div>
  );
};
```

---

## 🚀 Quick Start

### Installation
```bash
# Components are already created in:
# ~/clawd-workspace/projects/Project-Spark/frontend/src/components/Discovery/

# Install dependencies (if not already installed):
npm install react react-dom
npm install -D @types/react @types/react-dom typescript
```

### Import Components
```tsx
import {
  OpportunityCard,
  OpportunityGrid,
  FilterBar,
  Pagination,
  OpportunityCardSkeleton,
} from '@/components/Discovery';
```

---

## 📱 Mobile Responsive

All components are mobile-responsive:
- **OpportunityCard**: Stacks metrics vertically on small screens
- **OpportunityGrid**: Switches to single column on mobile
- **FilterBar**: Wraps filters into rows on narrow screens
- **Pagination**: Hides text labels on mobile, shows icons only

---

## ♿ Accessibility

- Semantic HTML (article, button, nav, etc.)
- ARIA labels and roles
- Keyboard navigation support
- Focus states on all interactive elements
- Screen reader friendly

---

## 🎯 Performance

- **Debounced search**: 300ms delay to reduce API calls
- **Optimistic updates**: UI updates instantly for validations
- **Lazy animations**: Staggered fade-in for cards
- **Loading skeletons**: Instant visual feedback

---

## 🔄 State Management Recommendations

These components are **state-agnostic** and work with:
- **React useState** (simple apps)
- **Zustand** (recommended, as per spec)
- **Redux/Redux Toolkit**
- **Context API**
- **TanStack Query (React Query)** for server state

Example with Zustand (from spec):
```typescript
// stores/discoveryStore.ts
import { create } from 'zustand';

export const useDiscoveryStore = create((set, get) => ({
  opportunities: [],
  filters: {
    search: '',
    category: 'all',
    sortBy: 'trending',
  },
  setFilters: (newFilters) => set((state) => ({
    filters: { ...state.filters, ...newFilters },
  })),
  fetchOpportunities: async () => {
    // Implementation
  },
}));
```

---

## 📝 Notes

- **Tailwind CSS**: These components use Tailwind utility classes. Ensure Tailwind is configured in your project.
- **Custom CSS**: Some components use `<style jsx>` for scoped styles. If using Next.js, ensure `styled-jsx` is enabled.
- **Fonts**: Import Spectral and Inter fonts in your app:
  ```html
  <link href="https://fonts.googleapis.com/css2?family=Spectral:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
  ```

---

## 🐛 Troubleshooting

### Issue: Styles not applying
- Ensure Tailwind CSS is configured and compiled
- Check that `tailwind.config.js` includes the components directory in `content: []`

### Issue: TypeScript errors
- Ensure all type definitions are imported from `./types.ts`
- Install `@types/react` and `@types/react-dom`

### Issue: Animations not working
- Ensure `@keyframes` CSS is properly scoped
- Check browser support for CSS animations

---

## 📚 Further Reading

- [Discovery Feed Spec](~/clawd-workspace/projects/Project-Spark/specs/1.1.1_Discovery_Feed_Spec.md)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)

---

**Built with ❤️ for OppGrid - The Opportunity Intelligence Platform**
