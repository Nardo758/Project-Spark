# Discovery Feed - Personalization Components

This directory contains React components for the OppGrid Discovery Feed personalization features, implementing the specifications from `1.1.1_Discovery_Feed_Spec.md`.

## 📦 Components

### 1. **RecommendedSection** - Main Container Component
The carousel section showing personalized opportunity recommendations.

**Features:**
- Fetches from `/api/opportunities/recommended` endpoint
- Displays 3 cards at a time in a carousel layout
- Responsive navigation (left/right arrows)
- Quick validation without leaving the page
- Match score badges and reasoning
- Social proof indicators
- Auto-refresh on user authentication

**Usage:**
```tsx
import { RecommendedSection } from './components/DiscoveryFeed'

function DiscoverPage() {
  return (
    <div>
      <RecommendedSection 
        limit={6} 
        onValidate={(oppId) => console.log('Validated:', oppId)}
      />
      {/* Rest of discover feed */}
    </div>
  )
}
```

**Props:**
- `limit?: number` - Number of recommendations to fetch (default: 6)
- `onValidate?: (opportunityId: number) => void` - Callback when user validates an opportunity

---

### 2. **MatchScoreBadge** - Match Score UI Component
Color-coded badge showing match percentage (0-100%).

**Color Scheme:**
- 🟢 **90-100%**: Green (excellent match)
- 🟡 **70-89%**: Amber (good match)
- ⚪ **0-69%**: Gray (decent match)

**Usage:**
```tsx
import { MatchScoreBadge } from './components/DiscoveryFeed'

<MatchScoreBadge score={92} size="md" showIcon showLabel />
```

**Props:**
- `score: number` - Match percentage (0-100)
- `size?: 'sm' | 'md' | 'lg'` - Badge size (default: 'md')
- `showIcon?: boolean` - Show sparkle icon (default: true)
- `showLabel?: boolean` - Show "match" label (default: true)

**Features:**
- Hover effects with scale animation
- Pulse animation for excellent matches (90%+)
- Accessible tooltips
- Responsive sizing

---

### 3. **SocialProof** - Social Validation Indicators
Displays social validation metrics like similar user validations and trending status.

**Usage:**
```tsx
import { SocialProof } from './components/DiscoveryFeed'

const socialProof = {
  similar_users_validated: 5,
  similar_users_text: "5 users like you validated this",
  expert_validation_count: 2,
  trending_indicator: true
}

<SocialProof socialProof={socialProof} compact={false} />
```

**Props:**
- `socialProof: SocialProofType` - Social proof data object
- `compact?: boolean` - Compact mode (icons only) vs full mode (default: false)

**SocialProofType Structure:**
```typescript
interface SocialProof {
  similar_users_validated: number
  similar_users_text?: string
  expert_validation_count?: number
  trending_indicator?: boolean
}
```

---

## 🔧 Integration Guide

### Step 1: Import Types
```typescript
import type { Opportunity, SocialProof } from '../../types/opportunity'
```

### Step 2: Use in Discovery Page
```tsx
import { RecommendedSection } from '../../components/DiscoveryFeed'

function DiscoverPage() {
  const handleValidate = (opportunityId: number) => {
    // Optional: Refresh main feed or show toast
    console.log('Opportunity validated:', opportunityId)
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Personalized Recommendations at Top */}
      <RecommendedSection limit={9} onValidate={handleValidate} />
      
      {/* Main Discovery Feed */}
      <FilterBar />
      <OpportunityGrid />
    </div>
  )
}
```

### Step 3: Standalone Usage of Sub-Components
You can use `MatchScoreBadge` and `SocialProof` independently in other components:

```tsx
import { MatchScoreBadge, SocialProof } from '../../components/DiscoveryFeed'

function OpportunityCard({ opportunity }) {
  return (
    <div className="card">
      <MatchScoreBadge score={opportunity.match_score} />
      <h3>{opportunity.title}</h3>
      <SocialProof socialProof={opportunity.social_proof} compact />
    </div>
  )
}
```

---

## 🔌 API Integration

### Required Backend Endpoint
The `RecommendedSection` component expects this endpoint:

**GET** `/api/opportunities/recommended?limit={number}`

**Headers:**
```
Authorization: Bearer {token}
```

**Response Format:**
```json
[
  {
    "id": 123,
    "title": "Freelance invoicing is a nightmare",
    "description": "...",
    "category": "Work & Productivity",
    "feasibility_score": 82,
    "validation_count": 445,
    "growth_rate": 18,
    "match_score": 92,
    "category_match_score": 88,
    "skills_alignment_score": 95,
    "similar_users_validated": 5,
    "expert_validations": 2,
    "user_validated": false
  }
]
```

### Quick Validation Endpoint
**POST** `/api/validations`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Body:**
```json
{
  "opportunity_id": 123
}
```

**Response:**
```json
{
  "success": true,
  "validation_id": 456
}
```

---

## 🎨 Styling

All components use **Tailwind CSS** classes and follow the existing design system:

- **Primary Color:** Purple (`purple-600`, `purple-700`)
- **Success/Match:** Green (`green-600`, `green-700`)
- **Warning/Good Match:** Amber (`amber-600`, `amber-700`)
- **Neutral:** Gray (`gray-600`, etc.)

### Dark Mode Support
Currently not implemented. To add dark mode:

1. Add `dark:` prefixes to color classes
2. Update gradient backgrounds for dark theme
3. Test readability of all text colors

---

## 📊 State Management

The components use **Zustand** for authentication state:

```typescript
import { useAuthStore } from '../../stores/authStore'

const { token, isAuthenticated, user } = useAuthStore()
```

### Local State
- `RecommendedSection`: Manages opportunities, loading, carousel position, validation state
- `MatchScoreBadge`: Stateless presentational component
- `SocialProof`: Stateless presentational component

---

## 🧪 Testing Recommendations

### Unit Tests
```typescript
// MatchScoreBadge.test.tsx
test('renders green badge for 90+ score', () => {
  render(<MatchScoreBadge score={92} />)
  expect(screen.getByText('92%')).toHaveClass('text-green-700')
})

test('renders amber badge for 70-89 score', () => {
  render(<MatchScoreBadge score={75} />)
  expect(screen.getByText('75%')).toHaveClass('text-amber-700')
})

test('renders gray badge for <70 score', () => {
  render(<MatchScoreBadge score={65} />)
  expect(screen.getByText('65%')).toHaveClass('text-gray-600')
})
```

### Integration Tests
```typescript
// RecommendedSection.test.tsx
test('fetches and displays recommendations', async () => {
  const mockOpportunities = [/* ... */]
  jest.spyOn(api, 'fetchRecommendedOpportunities').mockResolvedValue(mockOpportunities)
  
  render(<RecommendedSection />)
  
  await waitFor(() => {
    expect(screen.getByText('Recommended for You')).toBeInTheDocument()
    expect(screen.getByText(mockOpportunities[0].title)).toBeInTheDocument()
  })
})
```

---

## 🚀 Performance Optimizations

1. **Lazy Loading:** Only fetch recommendations when user is authenticated
2. **Debounced Validation:** Prevent rapid-fire validation clicks
3. **Optimistic Updates:** Update UI immediately, rollback on error
4. **Pagination:** Carousel loads 6-9 opportunities, shows 3 at a time

### Future Improvements
- [ ] Add skeleton loaders during fetch
- [ ] Implement virtualization for large carousels
- [ ] Cache recommendations for 5 minutes
- [ ] Add error boundaries for graceful failures

---

## 🐛 Known Issues & Limitations

1. **Match Score Calculation:** Currently uses placeholder logic on frontend. Backend should calculate this based on:
   - User profile data
   - Past validations
   - Category interests
   - Skills alignment

2. **Social Proof Data:** Backend needs to implement:
   - Similar users detection algorithm
   - Expert validation tracking
   - Trending calculation

3. **Mobile Carousel:** Works but could be improved with touch/swipe gestures

---

## 📝 Future Enhancements

### Phase 2 (ML Personalization)
- [ ] Replace placeholder match score with ML model
- [ ] Add A/B testing framework for recommendation algorithms
- [ ] Implement collaborative filtering
- [ ] Track click-through rates and optimize ranking

### Phase 3 (Advanced Features)
- [ ] "Why this recommendation?" modal with detailed reasoning
- [ ] "Not interested" feedback button
- [ ] Save recommendations for later
- [ ] Email digest of weekly recommendations

---

## 📚 Related Files

- **Spec:** `~/clawd-workspace/projects/Project-Spark/specs/1.1.1_Discovery_Feed_Spec.md`
- **Types:** `frontend/src/types/opportunity.ts`
- **API Service:** `frontend/src/services/opportunityApi.ts`
- **Auth Store:** `frontend/src/stores/authStore.ts`

---

## 🤝 Contributing

When modifying these components:

1. **Maintain consistency** with existing design patterns
2. **Update types** in `opportunity.ts` if adding new fields
3. **Test with real data** from backend
4. **Add prop types** for new props
5. **Update this README** with changes

---

## 💡 Example Implementation

Complete example integrating all components:

```tsx
import { useState } from 'react'
import { RecommendedSection, MatchScoreBadge, SocialProof } from './components/DiscoveryFeed'

export default function DiscoverPage() {
  const [refreshKey, setRefreshKey] = useState(0)

  const handleValidation = (opportunityId: number) => {
    console.log('Validated opportunity:', opportunityId)
    // Optionally refresh main feed
    setRefreshKey(prev => prev + 1)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Discover Opportunities
          </h1>
          <p className="text-gray-600">
            Explore validated business opportunities tailored to your interests
          </p>
        </div>

        {/* Personalized Recommendations */}
        <RecommendedSection 
          limit={9} 
          onValidate={handleValidation}
        />

        {/* Main Feed */}
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <FilterBar />
          <OpportunityGrid key={refreshKey} />
        </div>
      </div>
    </div>
  )
}
```

---

**Built with ❤️ for OppGrid Discovery Feed v1.1.1**
