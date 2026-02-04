# Quick Start Guide - Discovery Feed Components

Get up and running in 5 minutes! 🚀

## Step 1: Install Dependencies (1 min)

```bash
npm install react-confetti lucide-react
```

## Step 2: Copy Files (1 min)

All component files are in:
```
~/clawd-workspace/projects/Project-Spark/frontend/src/components/DiscoveryFeed/
```

Ensure you have:
- ✅ `QuickActions.tsx`
- ✅ `ComparisonPanel.tsx`
- ✅ `ComparisonModal.tsx`
- ✅ `SavedSearchModal.tsx`
- ✅ `types.ts`
- ✅ `index.ts`
- ✅ `styles.css`
- ✅ `hooks/useWindowSize.ts`

## Step 3: Import Styles (30 sec)

In your main App.tsx or index.tsx:

```tsx
import '@/components/DiscoveryFeed/styles.css';
```

## Step 4: Configure Tailwind (1 min)

Update `tailwind.config.js`:

```js
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      animation: {
        'fade-in': 'fadeIn 0.2s ease-in',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        },
      },
    },
  },
}
```

## Step 5: Use Components (2 min)

### Minimal Example

```tsx
import React, { useState } from 'react';
import { QuickActions, ComparisonPanel } from '@/components/DiscoveryFeed';

function MyDiscoveryPage() {
  const [selectedOps, setSelectedOps] = useState([]);

  return (
    <div>
      {/* Add QuickActions to your opportunity cards */}
      <div className="opportunity-card">
        <h3>Cool Opportunity</h3>
        <QuickActions
          opportunityId="opp-1"
          onValidate={async (id) => console.log('Validated:', id)}
        />
      </div>

      {/* Add ComparisonPanel at bottom */}
      <ComparisonPanel
        selectedOpportunities={selectedOps}
        onRemove={(id) => setSelectedOps(prev => prev.filter(o => o.id !== id))}
        onCompare={() => console.log('Compare!')}
        onClear={() => setSelectedOps([])}
      />
    </div>
  );
}
```

## Step 6: Test It! (30 sec)

1. Start your dev server: `npm run dev`
2. Click "Validate" button → Watch confetti! 🎉
3. Select opportunities → See comparison panel appear
4. Click "Compare" → View side-by-side modal

---

## 🎯 Common Patterns

### Pattern 1: Add to Existing Opportunity Card

```tsx
// Your existing card component
<div className="opportunity-card">
  {/* Your existing content */}
  <h3>{opportunity.title}</h3>
  <p>{opportunity.description}</p>
  
  {/* Add QuickActions at the bottom */}
  <QuickActions
    opportunityId={opportunity.id}
    userValidated={opportunity.userValidated}
    isSaved={opportunity.userSaved}
    onValidate={handleValidate}
    onSave={handleSave}
  />
</div>
```

### Pattern 2: Add Comparison to Grid

```tsx
function OpportunityGrid() {
  const [selected, setSelected] = useState([]);
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <div className="grid">
        {opportunities.map(opp => (
          <Card
            key={opp.id}
            opportunity={opp}
            onSelect={() => handleSelect(opp)}
          />
        ))}
      </div>

      <ComparisonPanel
        selectedOpportunities={selected}
        onCompare={() => setShowModal(true)}
        // ... other handlers
      />

      <ComparisonModal
        opportunities={getFullOpportunityData(selected)}
        isOpen={showModal}
        onClose={() => setShowModal(false)}
      />
    </>
  );
}
```

### Pattern 3: Save Search Button

```tsx
function FilterBar() {
  const [showSaveModal, setShowSaveModal] = useState(false);

  return (
    <>
      <div className="filters">
        {/* Your filters */}
        <button onClick={() => setShowSaveModal(true)}>
          💾 Save Search
        </button>
      </div>

      <SavedSearchModal
        isOpen={showSaveModal}
        onClose={() => setShowSaveModal(false)}
        onSave={async (name, prefs) => {
          await api.saveSearch({ name, filters, prefs });
        }}
        currentFilters={activeFilters}
      />
    </>
  );
}
```

---

## 🔥 Hot Tips

1. **Confetti**: To disable confetti in tests, mock react-confetti:
   ```tsx
   jest.mock('react-confetti', () => () => null);
   ```

2. **Icons**: All icons are from `lucide-react` - easily swappable:
   ```tsx
   import { Heart } from 'lucide-react'; // Use any icon!
   ```

3. **Styling**: Override with Tailwind classes:
   ```tsx
   <QuickActions className="my-custom-class" {...props} />
   ```

4. **State**: Store comparison state in URL for sharing:
   ```tsx
   const [selected] = useQueryState('compare');
   ```

---

## 📖 Need More?

- **Full Example**: See `example.tsx` for complete integration
- **Documentation**: Read `README.md` for all props and options
- **Tests**: Check `__tests__/QuickActions.test.tsx` for testing patterns
- **Spec**: Reference `1.1.1_Discovery_Feed_Spec.md` for requirements

---

## 🐛 Troubleshooting

**Problem**: Confetti doesn't show  
**Solution**: Make sure `react-confetti` is installed and `useWindowSize` hook exists

**Problem**: Icons missing  
**Solution**: Install `lucide-react`: `npm install lucide-react`

**Problem**: Styles not working  
**Solution**: Import `styles.css` and configure Tailwind animations

**Problem**: TypeScript errors  
**Solution**: Ensure `types.ts` is in the same directory as components

---

**Ready to go!** 🚀 Start with the minimal example and build from there.
