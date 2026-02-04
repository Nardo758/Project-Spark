# Discovery Feed Personalization - Architecture

## Component Hierarchy

```
RecommendedSection (Container)
│
├── Header
│   ├── Title + Icon
│   └── "View All" Link
│
├── Carousel Container
│   ├── Left Navigation Button
│   ├── Opportunity Cards (3 visible)
│   │   │
│   │   ├── OpportunityCard #1
│   │   │   ├── MatchScoreBadge
│   │   │   ├── Category Tag
│   │   │   ├── Title + Description
│   │   │   ├── Match Reasons
│   │   │   ├── Metrics (feasibility, validations, growth)
│   │   │   ├── SocialProof (compact mode)
│   │   │   └── Quick Validate Button
│   │   │
│   │   ├── OpportunityCard #2
│   │   │   └── (same structure)
│   │   │
│   │   └── OpportunityCard #3
│   │       └── (same structure)
│   │
│   └── Right Navigation Button
│
└── Pagination Dots
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     User Authenticates                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          RecommendedSection Component Mounts                │
│              (useEffect triggers on mount)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           fetchRecommendedOpportunities(token)              │
│                 (opportunityApi.ts)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│      GET /api/opportunities/recommended?limit=6             │
│            Authorization: Bearer {token}                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend Calculates Match Scores                │
│          (User profile + past validations + ML)             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          Returns Array of Opportunity Objects               │
│       (with match_score, match_reasons, etc.)               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           enrichOpportunity() (Frontend)                    │
│      Calculates match reasons if not provided               │
│      Formats social proof text                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         setOpportunities(enriched) → State Update           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Component Renders Carousel                     │
│           (3 cards visible, navigation arrows)              │
└─────────────────────────────────────────────────────────────┘
```

## Validation Flow

```
User Clicks "Quick Validate" Button
          │
          ▼
handleQuickValidate(opportunityId)
          │
          ├─── Add ID to validatingIds set (UI shows "Validating...")
          │
          ▼
quickValidateOpportunity(opportunityId, token)
          │
          ▼
POST /api/validations { opportunity_id: 123 }
          │
          ├─── Success ✓
          │    │
          │    ├─── Update local state (optimistic)
          │    │    - user_validated: true
          │    │    - validation_count: +1
          │    │
          │    ├─── Call onValidate callback (optional)
          │    │
          │    └─── Remove from validatingIds set
          │
          └─── Error ✗
               │
               ├─── Log error (console)
               │
               └─── Remove from validatingIds set (reset UI)
```

## State Management

### Component State (useState)

```typescript
// In RecommendedSection.tsx
const [opportunities, setOpportunities] = useState<Opportunity[]>([])
const [loading, setLoading] = useState(true)
const [currentIndex, setCurrentIndex] = useState(0)
const [validatingIds, setValidatingIds] = useState<Set<number>>(new Set())
```

### Global State (Zustand)

```typescript
// From authStore.ts
const { token, isAuthenticated, user } = useAuthStore()

// Used for:
// - Authentication check (show/hide component)
// - API requests (Bearer token)
// - User profile data (personalization)
```

### Derived State

```typescript
// Calculated from state
const canScrollLeft = currentIndex > 0
const canScrollRight = currentIndex < opportunities.length - 3
const visibleOpportunities = opportunities.slice(currentIndex, currentIndex + 3)
```

## API Contracts

### Request: Get Recommendations

```http
GET /api/opportunities/recommended?limit=10
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response: Opportunities Array

```typescript
type Response = Opportunity[]

interface Opportunity {
  // Core fields
  id: number
  title: string
  description: string
  category?: string
  feasibility_score: number
  validation_count: number
  
  // Personalization fields
  match_score?: number              // 0-100 (calculated by backend)
  category_match_score?: number     // 0-100 (optional, for debugging)
  skills_alignment_score?: number   // 0-100 (optional, for debugging)
  
  // Social proof
  similar_users_validated?: number  // Count of similar users
  expert_validations?: number       // Count of expert validations
  
  // User state
  user_validated?: boolean          // Has current user validated this?
  
  // Other
  growth_rate?: number              // Percentage (e.g., 18 = +18%)
  created_at: string                // ISO timestamp
}
```

### Request: Quick Validate

```http
POST /api/validations
Authorization: Bearer {token}
Content-Type: application/json

{
  "opportunity_id": 123
}
```

### Response: Validation Success

```json
{
  "success": true,
  "validation_id": 456,
  "points_earned": 5
}
```

## Component Dependencies

### External Dependencies

```typescript
// React ecosystem
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

// Icons (lucide-react)
import { 
  ChevronLeft, 
  ChevronRight, 
  ArrowRight, 
  Sparkles, 
  TrendingUp, 
  CheckCircle,
  Users,
  Award
} from 'lucide-react'

// Internal stores
import { useAuthStore } from '../../stores/authStore'

// Internal services
import { 
  fetchRecommendedOpportunities, 
  quickValidateOpportunity 
} from '../../services/opportunityApi'

// Internal types
import type { Opportunity, SocialProof, MatchReason } from '../../types/opportunity'
```

### Component Dependencies

```
RecommendedSection
├── MatchScoreBadge (child component)
└── SocialProof (child component)

MatchScoreBadge
└── (no dependencies, pure presentational)

SocialProof
└── (no dependencies, pure presentational)
```

## Styling Architecture

### Tailwind Utility Classes

All components use Tailwind CSS utility classes for styling:

```css
/* Layout */
.container, .grid, .flex, .space-y-*, .gap-*

/* Spacing */
.p-*, .px-*, .py-*, .m-*, .mx-*, .my-*

/* Colors */
.bg-{color}-{shade}, .text-{color}-{shade}, .border-{color}-{shade}

/* Typography */
.text-{size}, .font-{weight}, .line-clamp-{n}

/* Effects */
.rounded-{size}, .shadow-{size}, .hover:*, .transition-*
```

### Color Palette

```typescript
// Match Score Badges
const matchColors = {
  excellent: { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200' },
  good: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
  decent: { bg: 'bg-gray-50', text: 'text-gray-600', border: 'border-gray-200' }
}

// Primary Actions
const primary = 'bg-purple-600 hover:bg-purple-700 text-white'

// Social Proof Types
const socialProofColors = {
  users: { bg: 'bg-blue-50', text: 'text-blue-800', icon: 'text-blue-600' },
  experts: { bg: 'bg-purple-50', text: 'text-purple-800', icon: 'text-purple-600' },
  trending: { bg: 'bg-orange-50', text: 'text-orange-800', icon: 'text-orange-600' }
}
```

## Performance Considerations

### Optimizations Implemented

1. **Conditional Rendering**
   ```typescript
   // Don't render for unauthenticated users
   if (!isAuthenticated) return null
   
   // Don't render social proof if no data
   if (!hasSocialProof) return null
   ```

2. **Lazy Evaluation**
   ```typescript
   // Only calculate visible opportunities
   const visibleOpportunities = opportunities.slice(currentIndex, currentIndex + 3)
   ```

3. **Optimistic Updates**
   ```typescript
   // Update UI immediately, before API response
   setOpportunities(prev => prev.map(opp => 
     opp.id === opportunityId 
       ? { ...opp, user_validated: true }
       : opp
   ))
   ```

4. **Debouncing State**
   ```typescript
   // Prevent rapid-fire validation clicks
   if (validatingIds.has(opportunityId)) return
   ```

### Future Optimizations

1. **Memoization**
   ```typescript
   const MemoizedMatchBadge = memo(MatchScoreBadge)
   const MemoizedSocialProof = memo(SocialProof)
   ```

2. **Virtualization**
   ```typescript
   // For large carousels (>20 items)
   import { useVirtualizer } from '@tanstack/react-virtual'
   ```

3. **Image Lazy Loading**
   ```tsx
   <img loading="lazy" src={opportunity.image} />
   ```

4. **Code Splitting**
   ```typescript
   const RecommendedSection = lazy(() => import('./RecommendedSection'))
   ```

## Testing Strategy

### Unit Tests (Jest + React Testing Library)

```typescript
// MatchScoreBadge.test.tsx
describe('MatchScoreBadge', () => {
  test('renders green for excellent match (90%+)', () => {
    render(<MatchScoreBadge score={92} />)
    expect(screen.getByText('92%')).toHaveClass('text-green-700')
  })
  
  test('renders amber for good match (70-89%)', () => {
    render(<MatchScoreBadge score={75} />)
    expect(screen.getByText('75%')).toHaveClass('text-amber-700')
  })
  
  test('shows pulse animation for excellent match', () => {
    const { container } = render(<MatchScoreBadge score={95} />)
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument()
  })
})
```

### Integration Tests

```typescript
// RecommendedSection.test.tsx
describe('RecommendedSection', () => {
  test('fetches and displays recommendations', async () => {
    const mockOpps = [/* mock data */]
    jest.spyOn(api, 'fetchRecommendedOpportunities').mockResolvedValue(mockOpps)
    
    render(<RecommendedSection />)
    
    await waitFor(() => {
      expect(screen.getByText('Recommended for You')).toBeInTheDocument()
      expect(screen.getByText(mockOpps[0].title)).toBeInTheDocument()
    })
  })
  
  test('handles quick validation', async () => {
    const onValidate = jest.fn()
    render(<RecommendedSection onValidate={onValidate} />)
    
    const validateBtn = await screen.findByText('Quick Validate')
    fireEvent.click(validateBtn)
    
    await waitFor(() => {
      expect(screen.getByText('Validated')).toBeInTheDocument()
      expect(onValidate).toHaveBeenCalledWith(expect.any(Number))
    })
  })
})
```

### E2E Tests (Playwright)

```typescript
// discover-personalization.spec.ts
test('personalized recommendations flow', async ({ page }) => {
  await page.goto('/login')
  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="password"]', 'password123')
  await page.click('button[type="submit"]')
  
  await page.goto('/discover')
  
  // Verify recommendations section
  await expect(page.locator('text=Recommended for You')).toBeVisible()
  
  // Verify match score badges
  const badges = page.locator('[data-testid="match-score-badge"]')
  await expect(badges).toHaveCount(3)
  
  // Test carousel navigation
  await page.click('[aria-label="Next"]')
  await expect(page.locator('text=Opportunity #4')).toBeVisible()
  
  // Test quick validation
  await page.click('button:has-text("Quick Validate")')
  await expect(page.locator('button:has-text("Validated")')).toBeVisible()
})
```

## Error Handling

### API Error Scenarios

```typescript
// In opportunityApi.ts
try {
  const response = await fetch(url, options)
  
  if (!response.ok) {
    console.error('API error:', response.statusText)
    return [] // Return empty array (graceful degradation)
  }
  
  return await response.json()
} catch (error) {
  console.error('Network error:', error)
  return [] // Return empty array (graceful degradation)
}
```

### Component Error Boundaries

```tsx
// Future enhancement: Add error boundary
<ErrorBoundary fallback={<EmptyState />}>
  <RecommendedSection />
</ErrorBoundary>
```

## Accessibility (a11y)

### Semantic HTML

```tsx
// Use semantic elements
<nav aria-label="Recommended opportunities carousel">
  <button aria-label="Previous recommendations">
  <button aria-label="Next recommendations">
</nav>
```

### Keyboard Navigation

```tsx
// All interactive elements are keyboard accessible
<button 
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
  tabIndex={0}
>
```

### Screen Reader Support

```tsx
// Descriptive labels and ARIA attributes
<div role="region" aria-label="Personalized recommendations">
  <h2 id="recommendations-heading">Recommended for You</h2>
  <div aria-labelledby="recommendations-heading">
```

## Browser Support

### Supported Browsers
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

### Polyfills Required
- None (all features use modern but widely-supported APIs)

### Progressive Enhancement
- Base functionality works without JavaScript (SSR-ready)
- Enhanced interactivity with JavaScript
- Graceful degradation for older browsers

---

**Architecture Version:** 1.0  
**Last Updated:** February 3, 2026  
**Maintainer:** OppGrid Team
