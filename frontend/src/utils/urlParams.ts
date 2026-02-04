/**
 * URL Parameter Synchronization Utility
 * Persists filter state to URL params for shareable links and back-button support
 */

import { OpportunityFilters } from '../types/opportunity'

/**
 * Serialize filters to URL search params
 */
export function filtersToUrlParams(filters: OpportunityFilters): URLSearchParams {
  const params = new URLSearchParams()

  // Only add non-null/non-empty values to URL
  if (filters.search) params.set('search', filters.search)
  if (filters.category) params.set('category', filters.category)
  if (filters.geographic_scope) params.set('geo_scope', filters.geographic_scope)
  if (filters.country) params.set('country', filters.country)
  if (filters.completion_status) params.set('completion', filters.completion_status)
  if (filters.realm_type) params.set('realm', filters.realm_type)
  if (filters.min_feasibility !== null && filters.min_feasibility !== undefined) {
    params.set('min_feas', filters.min_feasibility.toString())
  }
  if (filters.max_feasibility !== null && filters.max_feasibility !== undefined) {
    params.set('max_feas', filters.max_feasibility.toString())
  }
  if (filters.min_validations !== null && filters.min_validations !== undefined) {
    params.set('min_val', filters.min_validations.toString())
  }
  if (filters.max_age_days !== null && filters.max_age_days !== undefined) {
    params.set('max_age', filters.max_age_days.toString())
  }
  if (filters.sort_by && filters.sort_by !== 'feasibility') {
    // Only include sort_by if it's not the default
    params.set('sort', filters.sort_by)
  }

  return params
}

/**
 * Parse URL search params to filters object
 */
export function urlParamsToFilters(searchParams: URLSearchParams): OpportunityFilters {
  const filters: OpportunityFilters = {
    sort_by: 'feasibility', // default
  }

  const search = searchParams.get('search')
  if (search) filters.search = search

  const category = searchParams.get('category')
  if (category) filters.category = category

  const geoScope = searchParams.get('geo_scope')
  if (geoScope) filters.geographic_scope = geoScope

  const country = searchParams.get('country')
  if (country) filters.country = country

  const completion = searchParams.get('completion')
  if (completion) filters.completion_status = completion

  const realm = searchParams.get('realm')
  if (realm) filters.realm_type = realm

  const minFeas = searchParams.get('min_feas')
  if (minFeas) {
    const parsed = parseInt(minFeas, 10)
    if (!isNaN(parsed)) filters.min_feasibility = parsed
  }

  const maxFeas = searchParams.get('max_feas')
  if (maxFeas) {
    const parsed = parseInt(maxFeas, 10)
    if (!isNaN(parsed)) filters.max_feasibility = parsed
  }

  const minVal = searchParams.get('min_val')
  if (minVal) {
    const parsed = parseInt(minVal, 10)
    if (!isNaN(parsed)) filters.min_validations = parsed
  }

  const maxAge = searchParams.get('max_age')
  if (maxAge) {
    const parsed = parseInt(maxAge, 10)
    if (!isNaN(parsed)) filters.max_age_days = parsed
  }

  const sort = searchParams.get('sort')
  if (sort) {
    const validSorts = ['recent', 'trending', 'validated', 'market', 'feasibility', 'recommended']
    if (validSorts.includes(sort)) {
      filters.sort_by = sort as OpportunityFilters['sort_by']
    }
  }

  return filters
}

/**
 * Update browser URL without triggering navigation
 */
export function syncFiltersToUrl(filters: OpportunityFilters, page?: number): void {
  const params = filtersToUrlParams(filters)
  
  // Add page if not 1
  if (page && page > 1) {
    params.set('page', page.toString())
  }

  const newUrl = params.toString() 
    ? `${window.location.pathname}?${params.toString()}`
    : window.location.pathname

  // Use pushState to update URL without page reload
  window.history.pushState({}, '', newUrl)
}

/**
 * Get current filters from URL on page load
 */
export function getFiltersFromUrl(): { filters: OpportunityFilters; page: number } {
  const searchParams = new URLSearchParams(window.location.search)
  const filters = urlParamsToFilters(searchParams)
  
  const pageParam = searchParams.get('page')
  const page = pageParam ? parseInt(pageParam, 10) : 1

  return {
    filters,
    page: isNaN(page) ? 1 : page,
  }
}

/**
 * Build shareable URL with current filters
 */
export function buildShareableUrl(filters: OpportunityFilters, page?: number): string {
  const params = filtersToUrlParams(filters)
  
  if (page && page > 1) {
    params.set('page', page.toString())
  }

  const baseUrl = typeof window !== 'undefined' 
    ? `${window.location.origin}/discover`
    : '/discover'

  return params.toString() 
    ? `${baseUrl}?${params.toString()}`
    : baseUrl
}
