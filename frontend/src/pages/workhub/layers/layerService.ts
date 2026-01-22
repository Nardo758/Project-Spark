import type { LayerType, LayerInstance, LocationFinderState, OptimalZone, FindOptimalZonesResponse } from './types'
import { useAuthStore } from '../../../stores/authStore'

const API_BASE = '/api/v1'

function getAuthHeaders(): Record<string, string> {
  const token = useAuthStore.getState().token
  if (token) {
    return { Authorization: `Bearer ${token}` }
  }
  return {}
}

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

function generateHotspotGrid(center: { lat: number; lng: number }, radiusMiles: number): { lat: number; lng: number }[] {
  if (radiusMiles <= 3.1) {
    return [center]
  }
  
  const points: { lat: number; lng: number }[] = []
  const gridSize = 3
  const effectiveRadius = radiusMiles * 0.7
  
  for (let row = 0; row < gridSize; row++) {
    for (let col = 0; col < gridSize; col++) {
      const xOffset = (col - 1) * (effectiveRadius * 2 / (gridSize - 1))
      const yOffset = (row - 1) * (effectiveRadius * 2 / (gridSize - 1))
      
      const latOffset = yOffset / 69
      const lngOffset = xOffset / (69 * Math.cos(center.lat * Math.PI / 180))
      
      const distance = Math.sqrt(xOffset * xOffset + yOffset * yOffset)
      if (distance <= radiusMiles) {
        points.push({
          lat: center.lat + latOffset,
          lng: center.lng + lngOffset
        })
      }
    }
  }
  
  return points
}

async function fetchSingleHotspot(
  point: { lat: number; lng: number },
  forceRefresh: boolean
): Promise<{ point: { lat: number; lng: number }; data: any; error?: string }> {
  const HOTSPOT_RADIUS_METERS = 2500
  
  try {
    const response = await fetch(`${API_BASE}/foot-traffic/collect-and-analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      credentials: 'include',
      body: JSON.stringify({
        latitude: point.lat,
        longitude: point.lng,
        radius_meters: HOTSPOT_RADIUS_METERS,
        force_refresh: forceRefresh
      })
    })
    
    if (!response.ok) {
      if (response.status === 401) {
        return { point, data: null, error: 'Authentication required' }
      }
      return { point, data: null, error: 'Failed to fetch' }
    }
    
    const data = await response.json()
    return { point, data }
  } catch (error) {
    return { point, data: null, error: 'Network error' }
  }
}

async function fetchTrafficData(params: LayerFetchParams): Promise<{ data: any; error?: string }> {
  const { center, radius, config } = params
  const forceRefresh = config.forceRefresh || false
  const radiusMiles = radius
  
  try {
    const hotspotPoints = generateHotspotGrid(center, radiusMiles)
    const isMultiHotspot = hotspotPoints.length > 1
    
    const hotspotResults = await Promise.all(
      hotspotPoints.map(point => fetchSingleHotspot(point, forceRefresh))
    )
    
    const validResults = hotspotResults.filter(r => r.data && !r.error)
    
    if (validResults.length === 0) {
      const firstError = hotspotResults.find(r => r.error)
      if (firstError?.error === 'Authentication required') {
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
      return { data: null, error: 'Failed to fetch foot traffic data from any location' }
    }
    
    const hotspots = validResults.map(result => {
      const data = result.data
      const peakHour = data.peak_hour
      let peakTimeFormatted = null
      if (peakHour !== null && peakHour !== undefined) {
        const hour12 = peakHour % 12 || 12
        const ampm = peakHour < 12 ? 'AM' : 'PM'
        peakTimeFormatted = `${hour12}:00 ${ampm}`
      }
      
      // Include drive-by traffic data from DOT
      const driveByTraffic = data.drive_by_traffic || {}
      
      return {
        lat: result.point.lat,
        lng: result.point.lng,
        vitalityScore: data.area_vitality_score || 0,
        businessDensityScore: data.business_density_score || 0,
        trafficConsistency: data.traffic_consistency || 0,
        peakDay: data.peak_day,
        peakHour: peakTimeFormatted,
        totalLocationsSampled: data.total_locations_sampled || 0,
        avgDailyTraffic: data.avg_daily_traffic || 0,
        dominantPlaceTypes: data.dominant_place_types || {},
        intensity: Math.min(100, (data.area_vitality_score || 0)),
        driveByTrafficMonthly: driveByTraffic.monthly_estimate || 0,
        driveByTrafficDaily: driveByTraffic.daily_average || 0,
        driveBySource: driveByTraffic.source || 'unavailable'
      }
    })
    
    const avgVitality = hotspots.reduce((sum, h) => sum + h.vitalityScore, 0) / hotspots.length
    const avgDensity = hotspots.reduce((sum, h) => sum + h.businessDensityScore, 0) / hotspots.length
    const totalSampled = hotspots.reduce((sum, h) => sum + h.totalLocationsSampled, 0)
    const bestHotspot = hotspots.reduce((best, h) => h.vitalityScore > best.vitalityScore ? h : best, hotspots[0])
    const totalDriveByMonthly = hotspots.reduce((sum, h) => sum + (h.driveByTrafficMonthly || 0), 0)
    
    return {
      data: {
        type: 'traffic',
        isMultiHotspot,
        hotspots,
        summary: {
          vitalityScore: Math.round(avgVitality),
          businessDensityScore: Math.round(avgDensity),
          trafficConsistency: bestHotspot.trafficConsistency || 0,
          peakDay: bestHotspot.peakDay,
          peakHour: bestHotspot.peakHour,
          peakTrafficScore: bestHotspot.vitalityScore,
          totalLocationsSampled: totalSampled,
          hotspotCount: hotspots.length,
          driveByTrafficMonthly: totalDriveByMonthly,
          driveBySource: bestHotspot.driveBySource || 'unavailable',
          bestHotspot: {
            lat: bestHotspot.lat,
            lng: bestHotspot.lng,
            vitalityScore: bestHotspot.vitalityScore,
            driveByTrafficMonthly: bestHotspot.driveByTrafficMonthly || 0
          },
          message: isMultiHotspot 
            ? `Analyzed ${hotspots.length} hotspots across ${radiusMiles} mile radius`
            : `Analyzed area within ${radiusMiles} mile radius`
        },
        heatmap: null,
        center: { lat: center.lat, lng: center.lng },
        radius,
        metadata: { 
          layerType: 'traffic', 
          source: 'hotspots',
          hotspotsAnalyzed: hotspots.length
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
    const response = await fetch(`${API_BASE}/maps/find-optimal-zones-enhanced`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        center_lat: params.center.lat,
        center_lng: params.center.lng,
        target_radius_miles: params.targetRadius,
        analysis_radius_miles: params.analysisRadius || 3.0,
        business_type: params.businessType,
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
