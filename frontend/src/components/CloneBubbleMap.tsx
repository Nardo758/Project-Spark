import { useEffect, useRef, Component, ReactNode } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

interface MatchingLocation {
  name: string
  city: string
  state: string
  lat: number
  lng: number
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

function MapController({ locations, selectedLocation }: { 
  locations: MatchingLocation[]
  selectedLocation: MatchingLocation | null 
}) {
  const map = useMap()
  
  useEffect(() => {
    if (selectedLocation) {
      map.flyTo([selectedLocation.lat, selectedLocation.lng], 12, { duration: 0.5 })
    } else if (locations.length > 0) {
      const bounds = L.latLngBounds(locations.map(loc => [loc.lat, loc.lng]))
      map.fitBounds(bounds, { padding: [50, 50] })
    }
  }, [locations, selectedLocation, map])
  
  return null
}

function getScoreColor(score: number): string {
  if (score >= 80) return '#10b981'
  if (score >= 60) return '#f59e0b'
  return '#6b7280'
}

function getBubbleRadius(score: number): number {
  const minRadius = 15
  const maxRadius = 35
  return minRadius + ((score / 100) * (maxRadius - minRadius))
}

export default function CloneBubbleMap({ locations, selectedLocation, onSelectLocation }: CloneBubbleMapProps) {
  if (!locations || locations.length === 0) {
    return (
      <div className="w-full h-[400px] bg-gray-100 rounded-lg flex items-center justify-center">
        <p className="text-gray-500">No matching locations to display</p>
      </div>
    )
  }

  const center: [number, number] = locations.length > 0 
    ? [locations[0].lat, locations[0].lng]
    : [39.8283, -98.5795]

  return (
    <MapErrorBoundary>
      <div className="relative">
        <div className="absolute top-3 left-3 z-[1000] bg-white rounded-lg shadow-md p-3">
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
        
        <MapContainer
          center={center}
          zoom={10}
          style={{ height: '400px', width: '100%' }}
          scrollWheelZoom={true}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          <MapController locations={locations} selectedLocation={selectedLocation} />
          
          {locations.map((loc, i) => (
            <CircleMarker
              key={`${loc.name}-${i}`}
              center={[loc.lat, loc.lng]}
              radius={getBubbleRadius(loc.similarity_score)}
              pathOptions={{
                fillColor: getScoreColor(loc.similarity_score),
                fillOpacity: selectedLocation?.name === loc.name ? 0.9 : 0.6,
                color: selectedLocation?.name === loc.name ? '#7c3aed' : getScoreColor(loc.similarity_score),
                weight: selectedLocation?.name === loc.name ? 3 : 1,
              }}
              eventHandlers={{
                click: () => onSelectLocation(loc),
              }}
            >
              <Popup>
                <div className="min-w-[200px] p-2">
                  <h3 className="font-semibold text-gray-900 text-base">{loc.name}</h3>
                  <p className="text-sm text-gray-500 mb-2">{loc.city}, {loc.state}</p>
                  
                  <div className={`inline-flex items-center px-2 py-1 rounded-full text-sm font-bold mb-3 ${
                    loc.similarity_score >= 80 ? 'bg-green-100 text-green-700' :
                    loc.similarity_score >= 60 ? 'bg-yellow-100 text-yellow-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {loc.similarity_score}% Match
                  </div>
                  
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Demographics:</span>
                      <span className="font-medium">{loc.demographics_match}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Competition:</span>
                      <span className="font-medium">{loc.competition_match}%</span>
                    </div>
                    {loc.population && (
                      <div className="flex justify-between">
                        <span className="text-gray-500">Population:</span>
                        <span className="font-medium">{loc.population.toLocaleString()}</span>
                      </div>
                    )}
                    {loc.median_income && (
                      <div className="flex justify-between">
                        <span className="text-gray-500">Income:</span>
                        <span className="font-medium">${loc.median_income.toLocaleString()}</span>
                      </div>
                    )}
                  </div>
                  
                  {loc.key_factors.length > 0 && (
                    <div className="mt-3 pt-2 border-t border-gray-200">
                      <div className="flex flex-wrap gap-1">
                        {loc.key_factors.slice(0, 3).map((factor, j) => (
                          <span key={j} className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs">
                            {factor}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
    </MapErrorBoundary>
  )
}
