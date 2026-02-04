/**
 * FilterBar Component
 * 
 * Advanced filtering interface for opportunity discovery.
 * 
 * Features:
 * - Full-text search
 * - Category filtering
 * - Feasibility range
 * - Location filtering
 * - Sort options
 * - Freshness filters (HOT, FRESH, VALIDATED, ARCHIVE)
 * - Save search functionality
 * - Clear filters
 * - Active filter pills
 * 
 * @component
 */

import React, { useState, useCallback, useEffect } from 'react';
import { FilterState } from './types';

interface FilterBarProps {
  filters: FilterState;
  onFiltersChange: (filters: Partial<FilterState>) => void;
  onSaveSearch?: () => void;
  isSticky?: boolean;
  resultsCount?: number;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  onFiltersChange,
  onSaveSearch,
  isSticky = true,
  resultsCount = 0,
}) => {
  const [searchValue, setSearchValue] = useState(filters.search);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchValue !== filters.search) {
        onFiltersChange({ search: searchValue });
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchValue, filters.search, onFiltersChange]);

  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'technology', label: 'Technology' },
    { value: 'health-wellness', label: 'Health & Wellness' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'money-finance', label: 'Money & Finance' },
    { value: 'home-services', label: 'Home Services' },
    { value: 'b2b-saas', label: 'B2B SaaS' },
    { value: 'b2b-services', label: 'B2B Services' },
    { value: 'ecommerce', label: 'E-Commerce' },
    { value: 'education', label: 'Education' },
    { value: 'entertainment', label: 'Entertainment' },
    { value: 'food-beverage', label: 'Food & Beverage' },
    { value: 'real-estate', label: 'Real Estate' },
    { value: 'travel-hospitality', label: 'Travel & Hospitality' },
    { value: 'pet-tech', label: 'Pet Tech' },
    { value: 'sustainability', label: 'Sustainability' },
    { value: 'other', label: 'Other' },
  ];

  const feasibilityOptions = [
    { value: 'all', label: 'Any Feasibility' },
    { value: 'high', label: 'High (75-100)' },
    { value: 'medium', label: 'Medium (50-74)' },
    { value: 'low', label: 'Low (0-49)' },
  ];

  const locationOptions = [
    { value: 'all', label: 'All Regions' },
    { value: 'us-national', label: 'US National' },
    { value: 'global', label: 'Global' },
    { value: 'canada', label: 'Canada' },
    { value: 'uk', label: 'UK' },
    { value: 'australia', label: 'Australia' },
  ];

  const sortOptions = [
    { value: 'trending', label: 'Trending' },
    { value: 'feasibility', label: 'Highest Feasibility' },
    { value: 'validated', label: 'Most Validated' },
    { value: 'recent', label: 'Most Recent' },
    { value: 'market', label: 'Market Size' },
  ];

  const daysOldOptions = [
    { value: 'all', label: 'Any Age' },
    { value: '7', label: 'Last 7 days' },
    { value: '14', label: 'Last 14 days' },
    { value: '30', label: 'Last 30 days' },
    { value: '60', label: 'Last 60 days' },
    { value: '90', label: 'Last 90 days' },
  ];

  const hasActiveFilters = () => {
    return (
      filters.search !== '' ||
      filters.category !== 'all' ||
      filters.feasibility !== 'all' ||
      filters.location !== 'all' ||
      filters.maxDaysOld !== null ||
      filters.myAccessOnly
    );
  };

  const clearAllFilters = () => {
    setSearchValue('');
    onFiltersChange({
      search: '',
      category: 'all',
      feasibility: 'all',
      location: 'all',
      maxDaysOld: null,
      myAccessOnly: false,
    });
  };

  const getActiveFilterPills = () => {
    const pills: Array<{ label: string; onRemove: () => void }> = [];

    if (filters.search) {
      pills.push({
        label: `Search: "${filters.search}"`,
        onRemove: () => {
          setSearchValue('');
          onFiltersChange({ search: '' });
        },
      });
    }

    if (filters.category && filters.category !== 'all') {
      const categoryLabel = categories.find((c) => c.value === filters.category)?.label || filters.category;
      pills.push({
        label: categoryLabel,
        onRemove: () => onFiltersChange({ category: 'all' }),
      });
    }

    if (filters.feasibility && filters.feasibility !== 'all') {
      const feasibilityLabel = feasibilityOptions.find((f) => f.value === filters.feasibility)?.label || filters.feasibility;
      pills.push({
        label: feasibilityLabel,
        onRemove: () => onFiltersChange({ feasibility: 'all' }),
      });
    }

    if (filters.location && filters.location !== 'all') {
      const locationLabel = locationOptions.find((l) => l.value === filters.location)?.label || filters.location;
      pills.push({
        label: locationLabel,
        onRemove: () => onFiltersChange({ location: 'all' }),
      });
    }

    if (filters.maxDaysOld !== null) {
      const daysLabel = daysOldOptions.find((d) => d.value === String(filters.maxDaysOld))?.label || `Last ${filters.maxDaysOld} days`;
      pills.push({
        label: daysLabel,
        onRemove: () => onFiltersChange({ maxDaysOld: null }),
      });
    }

    if (filters.myAccessOnly) {
      pills.push({
        label: 'My Access Only',
        onRemove: () => onFiltersChange({ myAccessOnly: false }),
      });
    }

    return pills;
  };

  const activeFilterPills = getActiveFilterPills();

  return (
    <div className={`filter-bar ${isSticky ? 'sticky top-16 z-30' : ''}`}>
      {/* Main Filters Row */}
      <div className="bg-white border-b border-stone-200">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <div className="flex items-center gap-4 flex-wrap">
            {/* Search Box */}
            <div className="flex-1 min-w-[280px] relative">
              <svg
                className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-stone-400"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <circle cx="11" cy="11" r="8"/>
                <path d="m21 21-4.3-4.3"/>
              </svg>
              <input
                type="text"
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                placeholder="Search opportunities..."
                className="w-full pl-12 pr-4 py-3 border border-stone-200 rounded-lg text-sm focus:outline-none focus:border-stone-400 focus:ring-2 focus:ring-stone-100 transition-all"
              />
              {searchValue && (
                <button
                  onClick={() => {
                    setSearchValue('');
                    onFiltersChange({ search: '' });
                  }}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-600"
                  aria-label="Clear search"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              )}
            </div>

            {/* Category Filter */}
            <select
              value={filters.category || 'all'}
              onChange={(e) => onFiltersChange({ category: e.target.value })}
              className="px-4 py-3 border border-stone-200 rounded-lg text-sm bg-white focus:outline-none focus:border-stone-400 focus:ring-2 focus:ring-stone-100 appearance-none bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNzg3MTZjIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0ibTYgOSA2IDYgNi02Ii8+PC9zdmc+')] bg-no-repeat bg-[right_12px_center] pr-10"
            >
              {categories.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>

            {/* Feasibility Filter */}
            <select
              value={filters.feasibility || 'all'}
              onChange={(e) => onFiltersChange({ feasibility: e.target.value })}
              className="px-4 py-3 border border-stone-200 rounded-lg text-sm bg-white focus:outline-none focus:border-stone-400 focus:ring-2 focus:ring-stone-100 appearance-none bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNzg3MTZjIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0ibTYgOSA2IDYgNi02Ii8+PC9zdmc+')] bg-no-repeat bg-[right_12px_center] pr-10"
            >
              {feasibilityOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>

            {/* Location Filter */}
            <select
              value={filters.location || 'all'}
              onChange={(e) => onFiltersChange({ location: e.target.value })}
              className="px-4 py-3 border border-stone-200 rounded-lg text-sm bg-white focus:outline-none focus:border-stone-400 focus:ring-2 focus:ring-stone-100 appearance-none bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNzg3MTZjIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0ibTYgOSA2IDYgNi02Ii8+PC9zdmc+')] bg-no-repeat bg-[right_12px_center] pr-10"
            >
              {locationOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>

            {/* Sort */}
            <select
              value={filters.sortBy}
              onChange={(e) => onFiltersChange({ sortBy: e.target.value as FilterState['sortBy'] })}
              className="px-4 py-3 border border-stone-200 rounded-lg text-sm bg-white focus:outline-none focus:border-stone-400 focus:ring-2 focus:ring-stone-100 appearance-none bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNzg3MTZjIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0ibTYgOSA2IDYgNi02Ii8+PC9zdmc+')] bg-no-repeat bg-[right_12px_center] pr-10"
            >
              {sortOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  Sort: {opt.label}
                </option>
              ))}
            </select>

            {/* Save Search Button */}
            {onSaveSearch && (
              <button
                onClick={onSaveSearch}
                className="px-4 py-3 bg-white border border-stone-200 rounded-lg text-sm font-medium text-stone-700 hover:bg-stone-50 transition-colors flex items-center gap-2"
                title="Save this search"
              >
                <span>💾</span>
                <span className="hidden sm:inline">Save Search</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Days Old Filter Row */}
      <div className="bg-white border-b border-stone-200">
        <div className="max-w-7xl mx-auto px-8 py-3">
          <div className="flex items-center gap-4 flex-wrap">
            <span className="text-xs font-medium text-stone-500 uppercase tracking-wide">
              Filter by age:
            </span>
            <select
              value={filters.maxDaysOld !== null ? String(filters.maxDaysOld) : 'all'}
              onChange={(e) => onFiltersChange({ maxDaysOld: e.target.value === 'all' ? null : parseInt(e.target.value, 10) })}
              className="px-3 py-1.5 border border-stone-200 rounded-lg text-sm bg-white focus:outline-none focus:border-stone-400 focus:ring-2 focus:ring-stone-100 appearance-none bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNzg3MTZjIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0ibTYgOSA2IDYgNi02Ii8+PC9zdmc+')] bg-no-repeat bg-[right_8px_center] pr-8"
            >
              {daysOldOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>

            {/* My Access Toggle */}
            <label className="flex items-center gap-2 text-sm text-stone-600 cursor-pointer ml-auto">
              <input
                type="checkbox"
                checked={filters.myAccessOnly}
                onChange={(e) => onFiltersChange({ myAccessOnly: e.target.checked })}
                className="w-4 h-4 rounded border-stone-300 text-stone-900 focus:ring-stone-200"
              />
              <span>Show only my access</span>
            </label>
          </div>
        </div>
      </div>

      {/* Active Filters Pills */}
      {activeFilterPills.length > 0 && (
        <div className="bg-stone-50 border-b border-stone-200">
          <div className="max-w-7xl mx-auto px-8 py-3">
            <div className="flex items-center gap-3 flex-wrap">
              <span className="text-xs font-medium text-stone-500 uppercase tracking-wide">
                Active Filters:
              </span>
              {activeFilterPills.map((pill, index) => (
                <span
                  key={index}
                  className="inline-flex items-center gap-2 px-3 py-1 bg-white border border-stone-200 rounded-full text-sm text-stone-700"
                >
                  {pill.label}
                  <button
                    onClick={pill.onRemove}
                    className="text-stone-400 hover:text-stone-600"
                    aria-label={`Remove ${pill.label} filter`}
                  >
                    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="18" y1="6" x2="6" y2="18"/>
                      <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                  </button>
                </span>
              ))}
              {hasActiveFilters() && (
                <button
                  onClick={clearAllFilters}
                  className="text-xs font-medium text-stone-600 hover:text-stone-900 underline"
                >
                  Clear all
                </button>
              )}
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default FilterBar;
