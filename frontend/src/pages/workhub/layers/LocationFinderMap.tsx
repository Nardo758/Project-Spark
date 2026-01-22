import { useEffect, useRef, useState, useCallback } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { Loader2, AlertCircle, TrendingUp, X, GripVertical } from 'lucide-react'
import type { LocationFinderState, LayerInstance } from './types'

const MAPBOX_TOKEN = (import.meta as any).env?.VITE_MAPBOX_ACCESS_TOKEN || ''

interface LocationFinderMapProps {
  state: LocationFinderState
  onLayerDataUpdate?: (layerId: string, data: any, error?: string) => void
  onCenterChange?: (center: { lat: number; lng: number; address?: string }) => void
  clickToSetEnabled?: boolean
  onClearOptimalZones?: () => void
}

export function LocationFinderMap({ state, onCenterChange, clickToSetEnabled = false, onClearOptimalZones }: LocationFinderMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<mapboxgl.Map | null>(null)
  const centerMarkerRef = useRef<mapboxgl.Marker | null>(null)
  const popupRef = useRef<mapboxgl.Popup | null>(null)
  const [mapLoaded, setMapLoaded] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [panelPosition, setPanelPosition] = useState({ x: 16, y: 16 })
  const [isDragging, setIsDragging] = useState(false)
  const dragStartRef = useRef<{ x: number; y: number; panelX: number; panelY: number } | null>(null)

  const handleDragStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    setIsDragging(true)
    dragStartRef.current = {
      x: e.clientX,
      y: e.clientY,
      panelX: panelPosition.x,
      panelY: panelPosition.y
    }
  }, [panelPosition])

  useEffect(() => {
    if (!isDragging) return

    const handleMouseMove = (e: MouseEvent) => {
      if (!dragStartRef.current) return
      const dx = e.clientX - dragStartRef.current.x
      const dy = e.clientY - dragStartRef.current.y
      setPanelPosition({
        x: Math.max(0, dragStartRef.current.panelX - dx),
        y: Math.max(0, dragStartRef.current.panelY - dy)
      })
    }

    const handleMouseUp = () => {
      setIsDragging(false)
      dragStartRef.current = null
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseup', handleMouseUp)
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging])

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return

    if (!MAPBOX_TOKEN) {
      setError('Map access token not configured')
      return
    }

    mapboxgl.accessToken = MAPBOX_TOKEN

    try {
      mapRef.current = new mapboxgl.Map({
        container: mapContainerRef.current,
        style: 'mapbox://styles/mapbox/light-v11',
        center: state.center ? [state.center.lng, state.center.lat] : [-98.5795, 39.8283],
        zoom: state.center ? 12 : 4
      })

      mapRef.current.addControl(new mapboxgl.NavigationControl(), 'top-right')

      mapRef.current.on('load', () => {
        setMapLoaded(true)
      })

      mapRef.current.on('error', (e) => {
        console.error('Map error:', e)
        setError('Error loading map')
      })
    } catch (err) {
      setError('Failed to initialize map')
      console.error(err)
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove()
        mapRef.current = null
      }
    }
  }, [])

  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return

    if (centerMarkerRef.current) {
      centerMarkerRef.current.remove()
      centerMarkerRef.current = null
    }

    if (state.center) {
      const el = document.createElement('div')
      el.className = 'center-marker'
      el.innerHTML = `
        <div style="
          width: 20px;
          height: 20px;
          background: #7c3aed;
          border: 3px solid white;
          border-radius: 50%;
          box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        "></div>
      `

      centerMarkerRef.current = new mapboxgl.Marker({ element: el })
        .setLngLat([state.center.lng, state.center.lat])
        .addTo(mapRef.current)

      mapRef.current.flyTo({
        center: [state.center.lng, state.center.lat],
        zoom: getZoomForRadius(state.radius),
        duration: 1000
      })
    }
  }, [state.center, mapLoaded])

  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return
    
    const map = mapRef.current
    
    const handleClick = async (e: mapboxgl.MapMouseEvent) => {
      if (!clickToSetEnabled || !onCenterChange) return
      
      const { lng, lat } = e.lngLat
      
      let address: string | undefined
      try {
        const response = await fetch(
          `https://api.mapbox.com/geocoding/v5/mapbox.places/${lng},${lat}.json?access_token=${MAPBOX_TOKEN}&types=address,place,locality`
        )
        const data = await response.json()
        if (data.features && data.features.length > 0) {
          address = data.features[0].place_name
        }
      } catch (err) {
        console.error('Reverse geocoding failed:', err)
      }
      
      onCenterChange({ lat, lng, address })
    }
    
    map.on('click', handleClick)
    
    const canvas = map.getCanvas()
    if (canvas) {
      canvas.style.cursor = clickToSetEnabled ? 'crosshair' : ''
    }
    
    return () => {
      map.off('click', handleClick)
      const canvas = map.getCanvas()
      if (canvas) {
        canvas.style.cursor = ''
      }
    }
  }, [clickToSetEnabled, mapLoaded, onCenterChange])

  const demographicsLayer = state.layers.find(l => l.type === 'demographics')
  const showDemographicsOverlay = demographicsLayer?.visible && demographicsLayer?.data
  const hasDemographicsLayer = !!demographicsLayer
  const demographicsDisplayMode = demographicsLayer?.config?.displayMode || 'heatmap'

  useEffect(() => {
    if (!mapRef.current || !mapLoaded || !state.center) return

    const map = mapRef.current

    if (!map.isStyleLoaded()) {
      map.once('style.load', () => {
        if (mapRef.current) {
          updateRadiusCircle(mapRef.current, state.center!, state.radius, hasDemographicsLayer, demographicsLayer?.visible, showDemographicsOverlay, demographicsDisplayMode)
        }
      })
      return
    }

    updateRadiusCircle(map, state.center, state.radius, hasDemographicsLayer, demographicsLayer?.visible, showDemographicsOverlay, demographicsDisplayMode)
  }, [state.radius, state.center, mapLoaded, hasDemographicsLayer, demographicsLayer?.visible, showDemographicsOverlay, demographicsDisplayMode])

  const updateRadiusCircle = (
    map: mapboxgl.Map, 
    center: { lat: number; lng: number }, 
    radiusMiles: number, 
    hasDemographicsLayer: boolean,
    demographicsVisible?: boolean,
    hasData?: boolean,
    displayMode?: string
  ) => {
    const sourceId = 'radius-circle'
    const shouldShow = hasDemographicsLayer ? demographicsVisible : true
    
    let fillColor = '#7c3aed'
    let fillOpacity = 0.1
    let lineColor = '#7c3aed'
    let lineStyle: number[] = [2, 2]
    
    if (hasData) {
      switch (displayMode) {
        case 'heatmap':
          fillColor = '#3b82f6'
          fillOpacity = 0.25
          lineColor = '#1d4ed8'
          lineStyle = []
          break
        case 'markers':
          fillColor = '#10b981'
          fillOpacity = 0.1
          lineColor = '#059669'
          lineStyle = [4, 4]
          break
        case 'choropleth':
          fillColor = '#8b5cf6'
          fillOpacity = 0.3
          lineColor = '#6d28d9'
          lineStyle = []
          break
        default:
          fillColor = '#3b82f6'
          fillOpacity = 0.2
          lineColor = '#3b82f6'
      }
    }

    try {
      if (map.getLayer('radius-circle-fill')) {
        map.removeLayer('radius-circle-fill')
      }
      if (map.getLayer('radius-circle-outline')) {
        map.removeLayer('radius-circle-outline')
      }
      if (map.getSource(sourceId)) {
        map.removeSource(sourceId)
      }
    } catch (e) {
    }

    if (!shouldShow) {
      map.flyTo({
        center: [center.lng, center.lat],
        zoom: getZoomForRadius(radiusMiles),
        duration: 500
      })
      return
    }

    const radiusInKm = radiusMiles * 1.60934
    const circleGeoJSON = createCircleGeoJSON(center.lng, center.lat, radiusInKm)

    map.addSource(sourceId, {
      type: 'geojson',
      data: circleGeoJSON
    })

    map.addLayer({
      id: 'radius-circle-fill',
      type: 'fill',
      source: sourceId,
      paint: {
        'fill-color': fillColor,
        'fill-opacity': fillOpacity
      }
    })

    const linePaint: any = {
      'line-color': lineColor,
      'line-width': 2
    }
    if (lineStyle.length > 0) {
      linePaint['line-dasharray'] = lineStyle
    }

    map.addLayer({
      id: 'radius-circle-outline',
      type: 'line',
      source: sourceId,
      paint: linePaint
    })

    map.flyTo({
      center: [center.lng, center.lat],
      zoom: getZoomForRadius(radiusMiles),
      duration: 500
    })
  }

  const layerDataKey = state.layers
    .map(l => `${l.id}:${l.visible}:${l.data ? 'y' : 'n'}:${l.loading ? 'l' : 's'}`)
    .join(',')

  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return

    state.layers.forEach(layer => {
      renderLayerOnMap(mapRef.current!, layer)
    })
  }, [layerDataKey, mapLoaded])

  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return

    const map = mapRef.current
    renderOptimalZones(map, state.optimalZones || [])
  }, [state.optimalZones, mapLoaded])

  const renderOptimalZones = (map: mapboxgl.Map, zones: any[]) => {
    if (!map.isStyleLoaded()) return

    for (let i = 1; i <= 5; i++) {
      const sourceId = `optimal-zone-${i}`
      const fillId = `${sourceId}-fill`
      const outlineId = `${sourceId}-outline`
      const labelId = `${sourceId}-label`
      const labelSourceId = `${sourceId}-label-source`

      if (map.getLayer(fillId)) map.removeLayer(fillId)
      if (map.getLayer(outlineId)) map.removeLayer(outlineId)
      if (map.getLayer(labelId)) map.removeLayer(labelId)
      if (map.getSource(sourceId)) map.removeSource(sourceId)
      if (map.getSource(labelSourceId)) map.removeSource(labelSourceId)
    }

    zones.forEach((zone, index) => {
      const sourceId = `optimal-zone-${index + 1}`
      const fillId = `${sourceId}-fill`
      const outlineId = `${sourceId}-outline`
      const labelId = `${sourceId}-label`

      const radiusInKm = zone.radius_miles * 1.60934
      const circleGeoJSON = createCircleGeoJSON(zone.center_lng, zone.center_lat, radiusInKm)

      map.addSource(sourceId, {
        type: 'geojson',
        data: circleGeoJSON
      })

      const opacity = 0.3 - (index * 0.08)
      const colors = ['#8b5cf6', '#a78bfa', '#c4b5fd']
      const color = colors[index] || colors[2]

      map.addLayer({
        id: fillId,
        type: 'fill',
        source: sourceId,
        paint: {
          'fill-color': color,
          'fill-opacity': opacity
        }
      })

      map.addLayer({
        id: outlineId,
        type: 'line',
        source: sourceId,
        paint: {
          'line-color': '#7c3aed',
          'line-width': 2
        }
      })

      const labelSource = `${sourceId}-label-source`
      if (map.getSource(labelSource)) map.removeSource(labelSource)

      map.addSource(labelSource, {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: [{
            type: 'Feature',
            geometry: {
              type: 'Point',
              coordinates: [zone.center_lng, zone.center_lat]
            },
            properties: {
              rank: zone.rank,
              score: zone.total_score
            }
          }]
        }
      })

      map.addLayer({
        id: labelId,
        type: 'symbol',
        source: labelSource,
        layout: {
          'text-field': ['concat', '#', ['get', 'rank'], ' (', ['get', 'score'], ')'],
          'text-size': 14,
          'text-font': ['DIN Pro Bold', 'Arial Unicode MS Bold'],
          'text-anchor': 'center'
        },
        paint: {
          'text-color': '#5b21b6',
          'text-halo-color': '#ffffff',
          'text-halo-width': 2
        }
      })
    })
  }

  const getLayerColor = (layerType: string): string => {
    switch (layerType) {
      case 'competition': return '#ef4444'
      case 'deep_clone': return '#f97316'
      case 'demographics': return '#3b82f6'
      case 'traffic': return '#22c55e'
      default: return '#7c3aed'
    }
  }

  const renderLayerOnMap = (map: mapboxgl.Map, layer: LayerInstance) => {
    if (!map.isStyleLoaded()) return
    
    const sourceId = `layer-${layer.id}`
    const pointLayerId = `${sourceId}-points`
    const fillLayerId = `${sourceId}-fill`
    const layerColor = getLayerColor(layer.type)

    const existingSource = map.getSource(sourceId) as mapboxgl.GeoJSONSource | undefined

    if (!layer.visible) {
      if (map.getLayer(pointLayerId)) {
        map.setLayoutProperty(pointLayerId, 'visibility', 'none')
      }
      if (map.getLayer(fillLayerId)) {
        map.setLayoutProperty(fillLayerId, 'visibility', 'none')
      }
      return
    }

    const geoJsonData = normalizeLayerData(layer)
    if (!geoJsonData || geoJsonData.features.length === 0) {
      if (existingSource) {
        existingSource.setData({ type: 'FeatureCollection', features: [] })
      }
      return
    }

    if (existingSource) {
      existingSource.setData(geoJsonData)
      if (map.getLayer(pointLayerId)) {
        map.setLayoutProperty(pointLayerId, 'visibility', 'visible')
      }
      if (map.getLayer(fillLayerId)) {
        map.setLayoutProperty(fillLayerId, 'visibility', 'visible')
      }
      return
    }

    map.addSource(sourceId, {
      type: 'geojson',
      data: geoJsonData
    })

    if (geoJsonData.features?.[0]?.geometry?.type === 'Point') {
      map.addLayer({
        id: pointLayerId,
        type: 'circle',
        source: sourceId,
        paint: {
          'circle-radius': 10,
          'circle-color': layerColor,
          'circle-stroke-width': 3,
          'circle-stroke-color': '#ffffff'
        }
      })

      map.on('mouseenter', pointLayerId, (e) => {
        map.getCanvas().style.cursor = 'pointer'
        
        if (e.features && e.features.length > 0) {
          const feature = e.features[0]
          const props = feature.properties || {}
          const coords = (feature.geometry as any).coordinates.slice()
          
          const name = props.name || 'Unknown Business'
          const rating = props.rating ? `${props.rating}/5` : ''
          const category = props.category || ''
          const address = props.address || ''
          
          let html = `<div style="padding: 8px; max-width: 200px;">
            <div style="font-weight: 600; color: #1f2937; margin-bottom: 4px;">${name}</div>`
          if (rating) {
            html += `<div style="font-size: 12px; color: #6b7280;">Rating: ${rating}</div>`
          }
          if (category) {
            html += `<div style="font-size: 12px; color: #6b7280;">${category}</div>`
          }
          if (address) {
            html += `<div style="font-size: 11px; color: #9ca3af; margin-top: 4px;">${address}</div>`
          }
          html += '</div>'
          
          if (popupRef.current) {
            popupRef.current.remove()
          }
          
          popupRef.current = new mapboxgl.Popup({
            closeButton: false,
            closeOnClick: false,
            offset: 15
          })
            .setLngLat(coords)
            .setHTML(html)
            .addTo(map)
        }
      })

      map.on('mouseleave', pointLayerId, () => {
        map.getCanvas().style.cursor = ''
        if (popupRef.current) {
          popupRef.current.remove()
          popupRef.current = null
        }
      })
    }
  }

  const normalizeLayerData = (layer: LayerInstance): GeoJSON.FeatureCollection | null => {
    if (!layer.data) return null

    if (layer.data.type === 'FeatureCollection') {
      return layer.data as GeoJSON.FeatureCollection
    }

    if (layer.type === 'competition' && Array.isArray(layer.data)) {
      const features: GeoJSON.Feature[] = layer.data
        .filter((place: any) => place.latitude && place.longitude)
        .map((place: any) => ({
          type: 'Feature' as const,
          geometry: {
            type: 'Point' as const,
            coordinates: [place.longitude, place.latitude]
          },
          properties: {
            name: place.name || 'Unknown Business',
            rating: place.rating || 0,
            category: layer.config?.searchQuery || '',
            address: place.address || '',
            reviews: place.reviews_count || place.reviews || 0,
            layerType: 'competition'
          }
        }))
      
      return { type: 'FeatureCollection', features }
    }

    if (layer.type === 'demographics' && layer.data && state.center) {
      return {
        type: 'FeatureCollection',
        features: []
      }
    }

    if (layer.type === 'deep_clone') {
      const analysisResult = layer.config?.analysisResult
      if (analysisResult?.competitors && Array.isArray(analysisResult.competitors)) {
        const features: GeoJSON.Feature[] = analysisResult.competitors
          .filter((c: any) => c.latitude && c.longitude)
          .map((c: any) => ({
            type: 'Feature' as const,
            geometry: {
              type: 'Point' as const,
              coordinates: [c.longitude, c.latitude]
            },
            properties: {
              name: c.name || 'Competitor',
              rating: c.rating || 0,
              category: layer.config?.businessType || '',
              address: c.address || '',
              layerType: 'deep_clone'
            }
          }))
        return { type: 'FeatureCollection', features }
      }
      return { type: 'FeatureCollection', features: [] }
    }

    if (layer.data.type === 'traffic' && layer.data.center) {
      return {
        type: 'FeatureCollection',
        features: [{
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: [layer.data.center.lng, layer.data.center.lat]
          },
          properties: {
            ...layer.data.summary,
            layerType: 'traffic'
          }
        }]
      }
    }

    return null
  }

  if (error) {
    return (
      <div className="absolute inset-0 flex items-center justify-center bg-stone-100">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-3" />
          <p className="text-stone-600">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="absolute inset-0">
      <div ref={mapContainerRef} className="w-full h-full" />
      {!mapLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-stone-100/80">
          <Loader2 className="w-8 h-8 animate-spin text-violet-600" />
        </div>
      )}
      {state.layers.some(l => l.loading) && (
        <div className="absolute top-4 left-4 bg-white px-3 py-2 rounded-lg shadow-md flex items-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin text-violet-600" />
          <span className="text-sm text-stone-600">Loading layer data...</span>
        </div>
      )}

      {/* Optimal Zones Floating Panel */}
      {(state.optimalZones && state.optimalZones.length > 0) || state.zoneSummary ? (
        <div 
          className="absolute w-80 max-h-[40vh] bg-white rounded-lg shadow-lg border border-stone-200 overflow-hidden z-20 pointer-events-auto"
          style={{ bottom: panelPosition.y, right: panelPosition.x }}
        >
          <div 
            className={`flex items-center justify-between px-3 py-2 bg-violet-50 border-b border-violet-100 ${isDragging ? 'cursor-grabbing' : 'cursor-grab'}`}
            onMouseDown={handleDragStart}
          >
            <div className="flex items-center gap-2">
              <GripVertical className="w-4 h-4 text-violet-400" />
              <div className="w-5 h-5 rounded-full bg-violet-600 flex items-center justify-center">
                <TrendingUp className="w-3 h-3 text-white" />
              </div>
              <span className="text-sm font-medium text-violet-800 select-none">
                {state.optimalZones?.length || 0} Optimal Zones
              </span>
            </div>
            <button
              onClick={(e) => { e.stopPropagation(); onClearOptimalZones?.() }}
              className="p-1 hover:bg-violet-100 rounded transition-colors"
              title="Close"
            >
              <X className="w-4 h-4 text-violet-600" />
            </button>
          </div>
          
          <div className="max-h-[calc(40vh-48px)] overflow-y-auto p-3 space-y-2">
            {state.optimalZones?.map((zone) => (
              <div 
                key={zone.id}
                className="flex items-start gap-3 p-2.5 bg-stone-50 rounded-lg border border-stone-100 hover:bg-stone-100 transition-colors"
              >
                <div className="w-7 h-7 rounded-full bg-violet-600 text-white text-sm font-bold flex items-center justify-center flex-shrink-0">
                  {zone.rank}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-semibold text-stone-800">
                      Score: {zone.total_score}/100
                    </span>
                  </div>
                  <div className="text-xs text-stone-500 space-y-0.5">
                    {zone.insights.slice(0, 2).map((insight, i) => (
                      <div key={i} className="flex items-start gap-1">
                        <span className="text-violet-400 mt-0.5">•</span>
                        <span>{insight}</span>
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2 mt-1.5 text-xs text-stone-400">
                    <span>Demo: {zone.scores.demographics}</span>
                    <span>•</span>
                    <span>Comp: {zone.scores.competition}</span>
                    <span>•</span>
                    <span>Mkt: {zone.scores.market_signals}</span>
                  </div>
                </div>
              </div>
            ))}
            
            {state.zoneSummary && (
              <div className="pt-2 border-t border-stone-100">
                <p className="text-xs text-stone-500">{state.zoneSummary}</p>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  )
}

function getZoomForRadius(radiusMiles: number): number {
  if (radiusMiles <= 0.25) return 15
  if (radiusMiles <= 0.5) return 14
  if (radiusMiles <= 1) return 13
  if (radiusMiles <= 2) return 12
  if (radiusMiles <= 5) return 11
  return 10
}

function createCircleGeoJSON(lng: number, lat: number, radiusKm: number): GeoJSON.Feature {
  const points = 64
  const coords: [number, number][] = []

  for (let i = 0; i < points; i++) {
    const angle = (i / points) * 2 * Math.PI
    const dx = radiusKm * Math.cos(angle)
    const dy = radiusKm * Math.sin(angle)

    const deltaLng = dx / (111.32 * Math.cos((lat * Math.PI) / 180))
    const deltaLat = dy / 110.574

    coords.push([lng + deltaLng, lat + deltaLat])
  }
  coords.push(coords[0])

  return {
    type: 'Feature',
    properties: {},
    geometry: {
      type: 'Polygon',
      coordinates: [coords]
    }
  }
}
