import { useEffect, useRef, useState, Component, ReactNode } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

interface MatchingLocation {
  name: string
  city: string
  state: string
  lat: number
  lng: number
  address?: string
  similarity_score: number
  demographics_match: number
  competition_match: number
  population?: number
  median_income?: number
  competition_count?: number
  key_factors: string[]
}

interface CloneBubbleMapProps {
  locations: MatchingLocation[]
  selectedLocation: MatchingLocation | null
  onSelectLocation: (loc: MatchingLocation) => void
}

interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

class MapErrorBoundary extends Component<{ children: ReactNode; fallback?: ReactNode }, ErrorBoundaryState> {
  constructor(props: { children: ReactNode; fallback?: ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="w-full h-[400px] bg-gray-100 rounded-lg flex items-center justify-center">
          <div className="text-center p-6">
            <div className="text-4xl mb-4">🗺️</div>
            <p className="text-gray-600 mb-2">Map temporarily unavailable</p>
            <p className="text-sm text-gray-500">The results are displayed below</p>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

function MapFallback() {
  return (
    <div className="w-full h-[400px] bg-gray-100 rounded-lg flex items-center justify-center">
      <div className="text-center p-6">
        <div className="text-4xl mb-4">🗺️</div>
        <p className="text-gray-600 mb-2">Map not available</p>
        <p className="text-sm text-gray-500">Results are displayed in the cards below</p>
      </div>
    </div>
  )
}

function getScoreColor(score: number): string {
  if (score >= 80) return '#10b981'
  if (score >= 60) return '#f59e0b'
  return '#6b7280'
}

function CloneBubbleMapInner({ locations, selectedLocation, onSelectLocation }: CloneBubbleMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<mapboxgl.Map | null>(null)
  const markersRef = useRef<{ marker: mapboxgl.Marker; element: HTMLDivElement; location: MatchingLocation }[]>([])
  const [hasToken, setHasToken] = useState(true)

  useEffect(() => {
    if (!mapContainer.current || locations.length === 0) return

    const accessToken = (import.meta as any).env?.VITE_MAPBOX_ACCESS_TOKEN
    if (!accessToken) {
      console.warn('Mapbox access token not configured')
      setHasToken(false)
      return
    }
    mapboxgl.accessToken = accessToken

    const center: [number, number] = [locations[0].lng, locations[0].lat]

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/light-v11',
      center: center,
      zoom: 10,
    })

    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right')

    map.current.on('load', () => {
      locations.forEach((loc) => {
        const color = getScoreColor(loc.similarity_score)
        const size = 20 + (loc.similarity_score / 100) * 30
        
        const el = document.createElement('div')
        el.className = 'clone-marker'
        el.style.width = `${size}px`
        el.style.height = `${size}px`
        el.style.borderRadius = '50%'
        el.style.backgroundColor = color
        el.style.opacity = '0.45'
        el.style.border = `2px solid ${color}`
        el.style.cursor = 'pointer'
        el.style.transition = 'all 0.2s ease'
        el.style.boxShadow = '0 2px 6px rgba(0,0,0,0.15)'
        
        el.addEventListener('mouseenter', () => {
          el.style.transform = 'scale(1.1)'
        })
        el.addEventListener('mouseleave', () => {
          el.style.transform = 'scale(1)'
        })
        el.addEventListener('click', () => {
          onSelectLocation(loc)
        })

        const popupContent = `
          <div style="min-width: 200px; padding: 8px;">
            <h3 style="font-weight: 600; color: #111; font-size: 14px; margin-bottom: 4px;">${loc.name}</h3>
            ${loc.address ? `<p style="color: #888; font-size: 11px; margin-bottom: 6px;">${loc.address}</p>` : ''}
            <p style="color: #666; font-size: 12px; margin-bottom: 8px;">${loc.city}, ${loc.state}</p>
            <div style="display: inline-block; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600; background: ${
              loc.similarity_score >= 80 ? '#d1fae5' : loc.similarity_score >= 60 ? '#fef3c7' : '#f3f4f6'
            }; color: ${
              loc.similarity_score >= 80 ? '#065f46' : loc.similarity_score >= 60 ? '#92400e' : '#374151'
            };">
              ${loc.similarity_score}% Match
            </div>
            <div style="margin-top: 8px; font-size: 11px; color: #666;">
              <div>Demographics: ${loc.demographics_match}%</div>
              <div>Competition: ${loc.competition_match}%</div>
              ${loc.population ? `<div>Population: ${loc.population.toLocaleString()}</div>` : ''}
              ${loc.median_income ? `<div>Income: $${loc.median_income.toLocaleString()}</div>` : ''}
            </div>
          </div>
        `

        const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(popupContent)

        const marker = new mapboxgl.Marker({ element: el })
          .setLngLat([loc.lng, loc.lat])
          .setPopup(popup)
          .addTo(map.current!)

        markersRef.current.push({ marker, element: el, location: loc })
      })

      if (locations.length > 1) {
        const bounds = new mapboxgl.LngLatBounds()
        locations.forEach(loc => bounds.extend([loc.lng, loc.lat]))
        map.current?.fitBounds(bounds, { padding: 60 })
      }
    })

    return () => {
      markersRef.current.forEach(({ marker }) => marker.remove())
      markersRef.current = []
      map.current?.remove()
    }
  }, [locations])

  useEffect(() => {
    markersRef.current.forEach(({ element, location }) => {
      const isSelected = selectedLocation?.name === location.name
      const color = getScoreColor(location.similarity_score)
      
      element.style.opacity = isSelected ? '0.6' : '0.45'
      element.style.border = isSelected ? '3px solid #7c3aed' : `2px solid ${color}`
      element.style.boxShadow = isSelected ? '0 0 10px rgba(124, 58, 237, 0.4)' : '0 2px 6px rgba(0,0,0,0.15)'
    })

    if (selectedLocation && map.current) {
      map.current.flyTo({
        center: [selectedLocation.lng, selectedLocation.lat],
        zoom: 12,
        duration: 500
      })
    }
  }, [selectedLocation])

  if (!hasToken) {
    return <MapFallback />
  }

  if (!locations || locations.length === 0) {
    return (
      <div className="w-full h-[400px] bg-gray-100 rounded-lg flex items-center justify-center">
        <p className="text-gray-500">No matching locations to display</p>
      </div>
    )
  }

  return (
    <div className="relative">
      <div className="absolute top-3 left-3 z-10 bg-white rounded-lg shadow-md p-3">
        <h4 className="text-sm font-semibold text-gray-900 mb-2">Match Score</h4>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span>80%+ (High Match)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
            <span>60-79% (Medium)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-gray-500"></div>
            <span>&lt;60% (Lower)</span>
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-2">Bubble size = match strength</p>
      </div>
      
      <div ref={mapContainer} style={{ height: '400px', width: '100%', borderRadius: '8px' }} />
    </div>
  )
}

export default function CloneBubbleMap(props: CloneBubbleMapProps) {
  return (
    <MapErrorBoundary>
      <CloneBubbleMapInner {...props} />
    </MapErrorBoundary>
  )
}
