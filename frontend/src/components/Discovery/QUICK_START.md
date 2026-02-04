# Quick Start Guide - Discovery Feed Components

Get up and running with the OppGrid Discovery Feed components in 5 minutes.

---

## 🚀 Installation

### 1. Prerequisites
Ensure you have these installed:
```bash
node >= 16.0.0
npm >= 8.0.0
```

### 2. Install Dependencies
```bash
cd ~/clawd-workspace/projects/Project-Spark/frontend

# Install React and TypeScript
npm install react react-dom
npm install -D @types/react @types/react-dom typescript

# Install Tailwind CSS (if not already installed)
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 3. Configure Tailwind
Update `tailwind.config.js`:
```javascript
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        stone: {
          50: '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
          500: '#78716c',
          600: '#57534e',
          700: '#44403c',
          800: '#292524',
          900: '#1c1917',
        },
        emerald: {
          100: '#d1fae5',
          600: '#16a34a',
          700: '#047857',
        },
      },
      fontFamily: {
        spectral: ['Spectral', 'serif'],
        inter: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
```

### 4. Add Fonts
In your `index.html` or layout component:
```html
<link href="https://fonts.googleapis.com/css2?family=Spectral:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
```

---

## 📦 Component Structure

All components are in:
```
~/clawd-workspace/projects/Project-Spark/frontend/src/components/Discovery/
├── types.ts                     # TypeScript interfaces
├── OpportunityCard.tsx          # Main card component
├── OpportunityCardSkeleton.tsx  # Loading skeleton
├── OpportunityGrid.tsx          # Grid container
├── FilterBar.tsx                # Filters interface
├── Pagination.tsx               # Page navigation
├── index.ts                     # Exports
├── Example.tsx                  # Full working example
├── README.md                    # Documentation
├── COMPONENT_SPEC.md            # Technical spec
└── QUICK_START.md               # This file
```

---

## 🎯 Basic Usage

### Minimal Example
```tsx
import React, { useState } from 'react';
import { OpportunityCard } from './components/Discovery';

function App() {
  const mockOpportunity = {
    id: 1,
    title: "Freelance invoicing is a nightmare",
    description: "Managing invoices, payments, and taxes takes 15% of my billable time.",
    category: "b2b-saas",
    validation_count: 445,
    growth_rate: 18,
    severity: 4,
    market_size: "$100M-$500M",
    created_at: new Date().toISOString(),
  };

  return (
    <div className="p-8 bg-stone-50 min-h-screen">
      <OpportunityCard
        opportunity={mockOpportunity}
        userTier="free"
        onValidate={(id) => console.log('Validated:', id)}
      />
    </div>
  );
}

export default App;
```

### Full Discovery Feed
See `Example.tsx` for a complete, production-ready implementation.

---

## 🔧 Configuration

### API Integration
Create an API helper:
```typescript
// api/opportunities.ts
export const opportunitiesApi = {
  async getAll(filters: FilterState, pagination: PaginationState) {
    const response = await fetch('/api/opportunities', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...filters,
        skip: (pagination.currentPage - 1) * pagination.pageSize,
        limit: pagination.pageSize,
      }),
    });
    return response.json();
  },

  async validate(id: number) {
    return fetch(`/api/opportunities/${id}/validate`, { method: 'POST' });
  },

  async save(id: number) {
    return fetch(`/api/opportunities/${id}/save`, { method: 'POST' });
  },
};
```

### State Management (Optional)
Using Zustand:
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
    const data = await opportunitiesApi.getAll(get().filters, get().pagination);
    set({ opportunities: data.opportunities });
  },
}));
```

---

## ✅ Verification

### 1. Run Development Server
```bash
npm run dev
```

### 2. Check Components Load
Navigate to `http://localhost:3000` and verify:
- [ ] Opportunity cards render
- [ ] Hover states work
- [ ] Filters update results
- [ ] Pagination works
- [ ] Mobile responsive

### 3. Test Interactions
- [ ] Click "Validate" button
- [ ] Toggle grid/list view
- [ ] Apply filters
- [ ] Change pages
- [ ] Search for opportunities

---

## 🐛 Common Issues

### Issue: "Cannot find module '@/components/Discovery'"
**Solution:** Update your `tsconfig.json`:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

### Issue: Tailwind styles not applying
**Solution:** 
1. Ensure `tailwind.config.js` has correct `content` paths
2. Run `npm run build` to regenerate CSS
3. Check that Tailwind directives are in your main CSS file:
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

### Issue: Fonts not loading
**Solution:** Add fonts to `<head>` in `index.html`:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Spectral:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
```

### Issue: TypeScript errors
**Solution:**
```bash
# Install type definitions
npm install -D @types/node

# Clear TypeScript cache
rm -rf node_modules/.cache
```

---

## 📚 Next Steps

1. **Read the docs**: Check out `README.md` for detailed component documentation
2. **Review the example**: Study `Example.tsx` for best practices
3. **Customize styles**: Modify Tailwind config to match your brand
4. **Add analytics**: Track user interactions (see `COMPONENT_SPEC.md`)
5. **Optimize performance**: Implement lazy loading and caching

---

## 🆘 Need Help?

- **Documentation**: `README.md` (user guide)
- **Technical Spec**: `COMPONENT_SPEC.md` (deep dive)
- **Example Code**: `Example.tsx` (copy-paste ready)
- **Spec Reference**: `~/clawd-workspace/projects/Project-Spark/specs/1.1.1_Discovery_Feed_Spec.md`

---

## 🎉 You're Ready!

The components are production-ready and fully documented. Start by copying `Example.tsx` and customizing it to your needs.

**Happy coding! 🚀**
