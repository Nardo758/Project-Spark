import { useEffect, useRef, useState } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { Loader2, AlertCircle } from 'lucide-react'
import type { LocationFinderState, LayerInstance } from './types'
import { layerRegistry } from './registry'

const MAPBOX_TOKEN = (import.meta as any).env?.VITE_MAPBOX_ACCESS_TOKEN || ''

interface LocationFinderMapProps {
  state: LocationFinderState
  onLayerDataUpdate?: (layerId: string, data: any, error?: string) => void
  onCenterChange?: (center: { lat: number; lng: number; address?: string }) => void
}

export function LocationFinderMap({ state, onCenterChange }: LocationFinderMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<mapboxgl.Map | null>(null)
  const centerMarkerRef = useRef<mapboxgl.Marker | null>(null)
  const popupRef = useRef<mapboxgl.Popup | null>(null)
  const [mapLoaded, setMapLoaded] = useState(false)
  const [error, setError] = useState<string | null>(null)

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
    if (!mapRef.current || !mapLoaded || !state.center) return

    const map = mapRef.current

    if (!map.isStyleLoaded()) {
      map.once('style.load', () => {
        if (mapRef.current) {
          addRadiusCircle(mapRef.current, state.center!, state.radius)
        }
      })
      return
    }

    addRadiusCircle(map, state.center, state.radius)
  }, [state.radius, state.center, mapLoaded])

  const addRadiusCircle = (map: mapboxgl.Map, center: { lat: number; lng: number }, radiusMiles: number) => {
    const sourceId = 'radius-circle'

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
        'fill-color': '#7c3aed',
        'fill-opacity': 0.1
      }
    })

    map.addLayer({
      id: 'radius-circle-outline',
      type: 'line',
      source: sourceId,
      paint: {
        'line-color': '#7c3aed',
        'line-width': 2,
        'line-dasharray': [2, 2]
      }
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

  const renderLayerOnMap = (map: mapboxgl.Map, layer: LayerInstance) => {
    if (!map.isStyleLoaded()) return
    
    const sourceId = `layer-${layer.id}`
    const def = layerRegistry[layer.type]
    const pointLayerId = `${sourceId}-points`
    const fillLayerId = `${sourceId}-fill`

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

    if (!layer.data) return

    const geoJsonData = normalizeLayerData(layer)
    if (!geoJsonData || geoJsonData.features.length === 0) return

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
          'circle-radius': 8,
          'circle-color': def.color,
          'circle-stroke-width': 2,
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

    if (layer.data.type === 'demographics' && state.center) {
      return {
        type: 'FeatureCollection',
        features: [{
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: [state.center.lng, state.center.lat]
          },
          properties: {
            ...layer.data.summary,
            layerType: 'demographics'
          }
        }]
      }
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
