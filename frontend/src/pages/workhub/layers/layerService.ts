import type { LayerType, LayerInstance, LocationFinderState } from './types'

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
  const businessType = config.businessType || 'restaurant'
  
  const response = await fetch(`${API_BASE}/maps/places/nearby`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      lat: center.lat,
      lng: center.lng,
      radius_miles: radius,
      business_type: businessType,
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
  const category = config.category || 'business'
  
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
  const { center, radius } = params
  
  return {
    data: {
      type: 'traffic',
      summary: {
        estimatedFootTraffic: 'Medium-High',
        peakHours: ['12:00 PM - 1:00 PM', '5:00 PM - 7:00 PM'],
        weekdayAverage: Math.floor(Math.random() * 5000) + 2000,
        weekendAverage: Math.floor(Math.random() * 8000) + 3000,
        nearbyPOIs: ['Shopping Center', 'Transit Stop', 'Office Park']
      },
      center: { lat: center.lat, lng: center.lng },
      radius,
      metadata: { layerType: 'traffic', source: 'estimated' }
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
  
  return false
}
