# Discovery Feed Components - Technical Specification

## 📋 Overview

This document provides detailed technical specifications for the Discovery Feed React components built for OppGrid.

---

## 🏗️ Architecture

### Component Hierarchy
```
DiscoveryFeed (Page/Container)
├── FilterBar
│   ├── SearchInput (debounced)
│   ├── CategorySelect
│   ├── FeasibilitySelect
│   ├── LocationSelect
│   ├── SortSelect
│   ├── FreshnessButtons
│   ├── ActiveFilterPills
│   └── SaveSearchButton
├── OpportunityGrid
│   ├── ViewToggle (Grid/List)
│   ├── ResultsCount
│   └── OpportunityCard[] or OpportunityCardSkeleton[]
│       ├── Header (meta, title, score)
│       ├── AccessIndicator (time-based)
│       ├── AIInsight
│       ├── Description
│       ├── MetricsGrid
│       ├── CompetitionBadges
│       ├── ViewerCount
│       └── QuickActions (hover)
│           ├── ValidateButton
│           ├── SaveButton
│           ├── AnalyzeButton
│           └── ShareButton
└── Pagination
    ├── ResultsInfo
    ├── PreviousButton
    ├── PageNumbers
    ├── NextButton
    └── PageSizeSelect (optional)
```

---

## 🎨 Design Tokens

### Colors (CSS Variables)
```css
/* Stone Scale */
--stone-50: #fafaf9;
--stone-100: #f5f5f4;
--stone-200: #e7e5e4;
--stone-300: #d6d3d1;
--stone-400: #a8a29e;
--stone-500: #78716c;
--stone-600: #57534e;
--stone-700: #44403c;
--stone-800: #292524;
--stone-900: #1c1917;

/* Semantic Colors */
--emerald-100: #d1fae5;
--emerald-600: #16a34a;
--emerald-700: #047857;

--red-50: #fef2f2;
--red-200: #fecaca;
--red-600: #dc2626;

--orange-50: #fff7ed;
--orange-200: #fed7aa;
--orange-600: #ea580c;

--yellow-50: #fef3c7;
--yellow-100: #fef9c3;
--yellow-700: #a16207;

--green-50: #f0fdf4;
--green-200: #bbf7d0;
--green-600: #16a34a;

--gray-50: #f3f4f6;
--gray-200: #d1d5db;
--gray-600: #6b7280;
```

### Typography
```css
/* Font Families */
--font-spectral: 'Spectral', serif;
--font-inter: 'Inter', sans-serif;

/* Font Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-5xl: 3rem;      /* 48px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Spacing
```css
--spacing-1: 0.25rem;  /* 4px */
--spacing-2: 0.5rem;   /* 8px */
--spacing-3: 0.75rem;  /* 12px */
--spacing-4: 1rem;     /* 16px */
--spacing-6: 1.5rem;   /* 24px */
--spacing-8: 2rem;     /* 32px */
--spacing-12: 3rem;    /* 48px */
```

### Border Radius
```css
--radius-sm: 0.5rem;   /* 8px */
--radius-md: 1rem;     /* 16px */
--radius-lg: 1.5rem;   /* 24px */
--radius-full: 9999px;
```

---

## 🔄 State Management

### FilterState
```typescript
interface FilterState {
  search: string;           // Full-text search query
  category: string | null;  // 'all' | 'home-services' | 'health-wellness' | etc.
  feasibility: string | null; // 'all' | 'high' | 'medium' | 'low'
  location: string | null;  // 'all' | 'us-national' | 'global' | etc.
  sortBy: 'recent' | 'trending' | 'validated' | 'market' | 'feasibility' | 'recommended';
  freshness: 'all' | 'hot' | 'fresh' | 'validated' | 'archive';
  myAccessOnly: boolean;    // Show only opportunities user can access
}
```

### PaginationState
```typescript
interface PaginationState {
  currentPage: number;  // 1-indexed
  pageSize: number;     // 10, 20, 50, 100
  totalItems: number;   // Total number of results
  totalPages: number;   // Calculated: Math.ceil(totalItems / pageSize)
}
```

### ViewMode
```typescript
type ViewMode = 'grid' | 'list';
```

### UserTier
```typescript
type UserTier = 'free' | 'pro' | 'business' | 'enterprise';
```

---

## 🔐 Access Control Logic

### Time-Decay Model
Opportunities become accessible to lower tiers as they age:

| Tier       | Access Window | Days Until Unlock |
|------------|---------------|-------------------|
| Enterprise | 0 days        | Instant access    |
| Business   | 8+ days old   | 8 days            |
| Pro        | 31+ days old  | 31 days           |
| Free       | 91+ days old  | 91 days           |

### Freshness Badges
```typescript
function getFreshnessBadge(ageDays: number): FreshnessBadge {
  if (ageDays <= 7) return { icon: '🔥', label: 'HOT', color: '#dc2626', tierRequired: 'enterprise' };
  if (ageDays <= 30) return { icon: '⚡', label: 'FRESH', color: '#f97316', tierRequired: 'business' };
  if (ageDays <= 90) return { icon: '✓', label: 'VALIDATED', color: '#16a34a', tierRequired: 'pro' };
  return { icon: '📚', label: 'ARCHIVE', color: '#6b7280', tierRequired: 'free' };
}
```

### Access Check
```typescript
function canAccessOpportunity(userTier: UserTier, ageDays: number): boolean {
  const accessWindows: Record<UserTier, number> = {
    free: 91,
    pro: 31,
    business: 8,
    enterprise: 0
  };
  const minAge = accessWindows[userTier] || 91;
  return ageDays >= minAge;
}
```

---

## ⚡ Performance Optimizations

### 1. Debounced Search
```typescript
// 300ms delay to avoid excessive API calls
useEffect(() => {
  const timer = setTimeout(() => {
    if (searchValue !== filters.search) {
      onFiltersChange({ search: searchValue });
    }
  }, 300);
  return () => clearTimeout(timer);
}, [searchValue]);
```

### 2. Optimistic Updates
```typescript
// Update UI immediately, API call happens in background
const handleValidate = async (id: number) => {
  // Immediate UI update
  setValidatedIds([...validatedIds, id]);
  setOpportunities(
    opportunities.map((opp) =>
      opp.id === id
        ? { ...opp, validation_count: opp.validation_count + 1 }
        : opp
    )
  );
  
  // Background API call
  try {
    await api.validateOpportunity(id);
  } catch (error) {
    // Rollback on error
    setValidatedIds(validatedIds.filter(validatedId => validatedId !== id));
  }
};
```

### 3. Staggered Animations
```typescript
// Each card animates with 100ms delay
<div style={{ animationDelay: `${index * 0.1}s` }}>
  <OpportunityCard />
</div>
```

### 4. Lazy Loading (Future)
```typescript
// Intersection Observer for infinite scroll
const observerRef = useRef<IntersectionObserver>();
const lastCardRef = useCallback((node) => {
  if (isLoading) return;
  if (observerRef.current) observerRef.current.disconnect();
  observerRef.current = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && hasMore) {
      loadMore();
    }
  });
  if (node) observerRef.current.observe(node);
}, [isLoading, hasMore]);
```

---

## 🎭 Animations

### Hover Effects
```css
.opportunity-card {
  transition: all 0.2s ease;
}

.opportunity-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.1);
  border-color: #1c1917;
}
```

### Fade-In Animation
```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.4s ease-out forwards;
  opacity: 0;
}
```

### Quick Actions Reveal
```css
.quick-actions {
  transition: all 0.2s;
  opacity: 0;
  transform: translateY(8px);
  pointer-events: none;
}

.opportunity-card:hover .quick-actions {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile First */
.opportunities-grid {
  grid-template-columns: 1fr; /* Default: 1 column */
}

/* Tablet (768px+) */
@media (min-width: 768px) {
  .opportunities-grid {
    grid-template-columns: repeat(2, 1fr); /* 2 columns */
  }
}

/* Desktop (1024px+) - Keep 2 columns for better readability */
@media (min-width: 1024px) {
  .opportunities-grid {
    grid-template-columns: repeat(2, 1fr); /* Still 2 columns */
  }
}
```

---

## 🧪 Testing Guidelines

### Unit Tests
```typescript
// OpportunityCard.test.tsx
describe('OpportunityCard', () => {
  it('displays opportunity title', () => {
    render(<OpportunityCard opportunity={mockOpportunity} />);
    expect(screen.getByText(mockOpportunity.title)).toBeInTheDocument();
  });

  it('shows HOT badge for opportunities < 7 days old', () => {
    const recentOpp = { ...mockOpportunity, created_at: new Date().toISOString() };
    render(<OpportunityCard opportunity={recentOpp} />);
    expect(screen.getByText('HOT')).toBeInTheDocument();
  });

  it('calls onValidate when validate button clicked', () => {
    const handleValidate = jest.fn();
    render(<OpportunityCard opportunity={mockOpportunity} onValidate={handleValidate} />);
    fireEvent.click(screen.getByText('✓ Validate'));
    expect(handleValidate).toHaveBeenCalledWith(mockOpportunity.id);
  });
});
```

### Integration Tests
```typescript
// DiscoveryFeed.test.tsx
describe('DiscoveryFeed', () => {
  it('fetches and displays opportunities on mount', async () => {
    render(<DiscoveryFeed />);
    await waitFor(() => {
      expect(screen.getByText('Showing 20 opportunities')).toBeInTheDocument();
    });
  });

  it('filters opportunities when search is entered', async () => {
    render(<DiscoveryFeed />);
    fireEvent.change(screen.getByPlaceholderText('Search opportunities...'), {
      target: { value: 'freelance' }
    });
    await waitFor(() => {
      expect(mockApi.getOpportunities).toHaveBeenCalledWith(
        expect.objectContaining({ search: 'freelance' })
      );
    }, { timeout: 500 }); // Account for debounce
  });
});
```

---

## 🔌 API Integration

### Expected API Response Format
```typescript
// GET /api/opportunities
{
  "opportunities": [
    {
      "id": 1,
      "title": "Freelance invoicing is a nightmare",
      "description": "...",
      "category": "b2b-saas",
      "validation_count": 445,
      "growth_rate": 18,
      "severity": 4,
      "market_size": "$100M-$500M",
      "geographic_scope": "international",
      "created_at": "2024-01-15T10:30:00Z",
      "ai_generated_title": "AI-Powered Invoicing for Freelancers",
      "ai_problem_statement": "...",
      "ai_summary": "High-potential opportunity...",
      "ai_opportunity_score": 85,
      "ai_competition_level": "medium",
      "ai_market_size_estimate": "$250M",
      "user_validated": false,
      "match_score": 92
    }
  ],
  "total": 432,
  "page": 1,
  "page_size": 20,
  "has_more": true
}
```

---

## 📦 Dependencies

### Required
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.3.0"
  }
}
```

### Optional (Recommended)
```json
{
  "dependencies": {
    "zustand": "^4.4.0",          // State management
    "@tanstack/react-query": "^5.0.0",  // Server state
    "framer-motion": "^10.16.0"   // Advanced animations
  }
}
```

---

## 🚀 Deployment Checklist

- [ ] Tailwind CSS configured and purging unused styles
- [ ] Fonts (Spectral, Inter) loaded in HTML head
- [ ] API endpoints configured (production URLs)
- [ ] Error boundaries implemented
- [ ] Loading states tested
- [ ] Mobile responsiveness verified on real devices
- [ ] Accessibility audit passed (WCAG 2.1 AA)
- [ ] Performance audit (Lighthouse score > 90)
- [ ] Analytics events tracked
- [ ] SEO meta tags added

---

## 📊 Analytics Events

### Recommended Tracking
```typescript
// Filter applied
track('discovery_filter_applied', {
  filter_type: 'category',
  filter_value: 'b2b-saas'
});

// Opportunity validated
track('opportunity_validated', {
  opportunity_id: 123,
  source: 'quick_action', // 'quick_action' | 'detail_page'
  user_tier: 'pro'
});

// Search performed
track('discovery_search', {
  query: 'freelance',
  results_count: 45
});

// Page viewed
track('discovery_page_view', {
  page: 2,
  filters_active: 3,
  view_mode: 'grid'
});
```

---

**Last Updated:** 2024-01-15  
**Version:** 1.0.0  
**Maintainer:** OppGrid Team
