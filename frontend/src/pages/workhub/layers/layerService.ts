import type { LayerType, LayerInstance, LocationFinderState, OptimalZone, FindOptimalZonesResponse } from './types'

const API_BASE = '/api/v1'

export interface LayerFetchParams {
  center: { lat: number; lng: number }
  radius: number
  config: Record<string, any>
}

export async function fetchLayerData(
  layerType: LayerType,
  params: LayerFetchParams
): Promise<{ data: any; error?: string }> {
  try {
    switch (layerType) {
      case 'deep_clone':
        return await fetchDeepCloneData(params)
      case 'demographics':
        return await fetchDemographicsData(params)
      case 'competition':
        return await fetchCompetitionData(params)
      case 'traffic':
        return await fetchTrafficData(params)
      default:
        return { data: null, error: `Unknown layer type: ${layerType}` }
    }
  } catch (error) {
    console.error(`Error fetching ${layerType} layer data:`, error)
    return { data: null, error: error instanceof Error ? error.message : 'Failed to fetch layer data' }
  }
}

async function fetchDeepCloneData(params: LayerFetchParams): Promise<{ data: any; error?: string }> {
  const { center, radius, config } = params
  const businessCategory = config.businessCategory
  
  if (!businessCategory) {
    return {
      data: {
        type: 'FeatureCollection',
        features: [],
        metadata: { count: 0, layerType: 'deep_clone', awaiting_category: true }
      }
    }
  }
  
  const response = await fetch(`${API_BASE}/maps/places/nearby`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      lat: center.lat,
      lng: center.lng,
      radius_miles: radius,
      business_type: businessCategory,
      limit: 20
    })
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    return { data: null, error: errorData.detail || 'Failed to fetch nearby businesses' }
  }

  const data = await response.json()
  
  const features = (data.places || []).map((place: any) => ({
    type: 'Feature',
    geometry: {
      type: 'Point',
      coordinates: [place.lng || place.longitude, place.lat || place.latitude]
    },
    properties: {
      id: place.id || place.place_id,
      name: place.name,
      rating: place.rating,
      reviews: place.user_ratings_total || place.review_count,
      address: place.address || place.formatted_address,
      type: 'deep_clone'
    }
  }))

  return {
    data: {
      type: 'FeatureCollection',
      features,
      metadata: { count: features.length, layerType: 'deep_clone' }
    }
  }
}

async function fetchDemographicsData(params: LayerFetchParams): Promise<{ data: any; error?: string }> {
  const { center, radius, config } = params
  const metrics = config.metrics || ['population', 'income']
  
  const response = await fetch(`${API_BASE}/maps/demographics`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      lat: center.lat,
      lng: center.lng,
      radius_miles: radius,
      metrics
    })
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    return { data: null, error: errorData.detail || 'Failed to fetch demographics' }
  }

  const data = await response.json()
  
  return {
    data: {
      type: 'demographics',
      summary: data,
      metadata: { layerType: 'demographics' }
    }
  }
}

async function fetchCompetitionData(params: LayerFetchParams): Promise<{ data: any; error?: string }> {
  const { center, radius, config } = params
  const category = config.category || config.searchQuery || 'business'
  
  const response = await fetch(`${API_BASE}/maps/places/nearby`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      lat: center.lat,
      lng: center.lng,
      radius_miles: radius,
      business_type: category,
      limit: 30
    })
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    return { data: null, error: errorData.detail || 'Failed to fetch competition data' }
  }

  const data = await response.json()
  
  const features = (data.places || []).map((place: any) => ({
    type: 'Feature',
    geometry: {
      type: 'Point',
      coordinates: [place.lng || place.longitude, place.lat || place.latitude]
    },
    properties: {
      id: place.id || place.place_id,
      name: place.name,
      rating: place.rating,
      reviews: place.user_ratings_total || place.review_count,
      address: place.address || place.formatted_address,
      type: 'competition'
    }
  }))

  return {
    data: {
      type: 'FeatureCollection',
      features,
      metadata: { count: features.length, layerType: 'competition' }
    }
  }
}

async function fetchTrafficData(params: LayerFetchParams): Promise<{ data: any; error?: string }> {
  const { center, radius, config } = params
  
  const radiusMeters = Math.round(radius * 1609.34)
  const forceRefresh = config.forceRefresh || false
  
  try {
    const response = await fetch(`${API_BASE}/foot-traffic/collect-and-analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        latitude: center.lat,
        longitude: center.lng,
        radius_meters: radiusMeters,
        force_refresh: forceRefresh
      })
    })
    
    if (!response.ok) {
      if (response.status === 401) {
        return {
          data: {
            type: 'traffic',
            requiresAuth: true,
            summary: null,
            metadata: { layerType: 'traffic', source: 'unavailable' }
          },
          error: 'Authentication required for foot traffic data'
        }
      }
      const errorData = await response.json().catch(() => ({}))
      return { data: null, error: errorData.detail || 'Failed to fetch foot traffic data' }
    }

    const data = await response.json()
    
    const peakHour = data.peak_hour
    let peakTimeFormatted = null
    if (peakHour !== null && peakHour !== undefined) {
      const hour12 = peakHour % 12 || 12
      const ampm = peakHour < 12 ? 'AM' : 'PM'
      peakTimeFormatted = `${hour12}:00 ${ampm}`
    }
    
    let heatmapData = null
    if (data.total_locations_sampled > 0) {
      try {
        const heatmapResponse = await fetch(`${API_BASE}/foot-traffic/heatmap`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            latitude: center.lat,
            longitude: center.lng,
            radius_meters: radiusMeters
          })
        })
        if (heatmapResponse.ok) {
          heatmapData = await heatmapResponse.json()
        }
      } catch (e) {
        console.warn('Failed to fetch heatmap data:', e)
      }
    }
    
    return {
      data: {
        type: 'traffic',
        summary: {
          vitalityScore: data.area_vitality_score || 0,
          businessDensityScore: data.business_density_score || 0,
          trafficConsistency: data.traffic_consistency || 0,
          peakDay: data.peak_day,
          peakHour: peakTimeFormatted,
          peakTrafficScore: data.peak_traffic_score || 0,
          totalLocationsSampled: data.total_locations_sampled || 0,
          dominantPlaceTypes: data.dominant_place_types || {},
          avgPopularTimes: data.avg_popular_times || {},
          currentAvgPopularity: data.current_avg_popularity,
          message: data.message,
          fromCache: data.from_cache,
          freshCollection: data.fresh_collection
        },
        heatmap: heatmapData,
        center: { lat: center.lat, lng: center.lng },
        radius,
        metadata: { 
          layerType: 'traffic', 
          source: data.from_cache ? 'cached' : 'fresh',
          generatedAt: data.generated_at
        }
      }
    }
  } catch (error) {
    console.error('Error fetching foot traffic:', error)
    return { 
      data: null, 
      error: error instanceof Error ? error.message : 'Failed to fetch foot traffic data' 
    }
  }
}

export function shouldRefetchLayer(
  layer: LayerInstance,
  prevState: LocationFinderState | null,
  newState: LocationFinderState
): boolean {
  if (!newState.center) return false
  if (!layer.visible) return false
  
  if (!layer.data && !layer.loading && !layer.error) {
    return true
  }
  
  if (prevState?.center && newState.center) {
    const centerChanged = 
      prevState.center.lat !== newState.center.lat ||
      prevState.center.lng !== newState.center.lng
    
    if (centerChanged) return true
  }
  
  if (prevState?.radius !== newState.radius && layer.data) {
    return true
  }
  
  const prevLayer = prevState?.layers.find(l => l.id === layer.id)
  if (prevLayer) {
    if (layer.type === 'deep_clone') {
      const prevCategory = prevLayer.config?.businessCategory
      const newCategory = layer.config?.businessCategory
      if (prevCategory !== newCategory && newCategory) {
        return true
      }
    }
    
    if (layer.type === 'competition') {
      const prevCategory = prevLayer.config?.category || prevLayer.config?.searchQuery
      const newCategory = layer.config?.category || layer.config?.searchQuery
      if (prevCategory !== newCategory && newCategory) {
        return true
      }
    }
  }
  
  return false
}

export interface FindOptimalZonesParams {
  center: { lat: number; lng: number }
  targetRadius: number
  analysisRadius?: number
  activeLayers: string[]
  businessType?: string
  demographicsData?: any
  competitors?: any[]
  topN?: number
}

export async function findOptimalZones(
  params: FindOptimalZonesParams
): Promise<{ zones: OptimalZone[]; summary: string; error?: string }> {
  try {
    const response = await fetch(`${API_BASE}/maps/find-optimal-zones`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        center_lat: params.center.lat,
        center_lng: params.center.lng,
        target_radius_miles: params.targetRadius,
        analysis_radius_miles: params.analysisRadius || 3.0,
        active_layers: params.activeLayers,
        business_type: params.businessType,
        demographics_data: params.demographicsData,
        competitors: params.competitors,
        top_n: params.topN || 3
      })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return { zones: [], summary: '', error: errorData.detail || 'Failed to find optimal zones' }
    }

    const data: FindOptimalZonesResponse = await response.json()
    
    return {
      zones: data.zones,
      summary: data.analysis_summary
    }
  } catch (error) {
    console.error('Error finding optimal zones:', error)
    return {
      zones: [],
      summary: '',
      error: error instanceof Error ? error.message : 'Failed to analyze locations'
    }
  }
}
