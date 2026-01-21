import { useState } from 'react'
import { Copy, MapPin, Search, Loader2, ChevronRight } from 'lucide-react'

type DeepCloneInputPanelProps = {
  onAnalyze: (sourceBusiness: string, targetLocation: string, coords: { lat: number; lng: number }) => void
  isAnalyzing?: boolean
}

export default function DeepCloneInputPanel({ onAnalyze, isAnalyzing = false }: DeepCloneInputPanelProps) {
  const [sourceBusiness, setSourceBusiness] = useState('')
  const [targetLocation, setTargetLocation] = useState('')
  const [geocoding, setGeocoding] = useState(false)
  const [geocodeError, setGeocodeError] = useState('')
  const [previewCoords, setPreviewCoords] = useState<{ lat: number; lng: number } | null>(null)

  const handleLocationChange = async (value: string) => {
    setTargetLocation(value)
    setGeocodeError('')
    setPreviewCoords(null)

    if (value.length < 3) return

    setGeocoding(true)
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(value)}&countrycodes=us&limit=1`,
        { headers: { 'User-Agent': 'OppGrid/1.0' } }
      )
      const data = await response.json()
      if (data && data.length > 0) {
        setPreviewCoords({ lat: parseFloat(data[0].lat), lng: parseFloat(data[0].lon) })
      }
    } catch {
      // Silent fail for preview
    } finally {
      setGeocoding(false)
    }
  }

  const handleAnalyze = async () => {
    if (!sourceBusiness.trim() || !targetLocation.trim()) return

    setGeocoding(true)
    setGeocodeError('')

    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(targetLocation)}&countrycodes=us&limit=1`,
        { headers: { 'User-Agent': 'OppGrid/1.0' } }
      )
      const data = await response.json()
      
      if (!data || data.length === 0) {
        setGeocodeError('Location not found. Try a city name or zip code.')
        return
      }

      const coords = { lat: parseFloat(data[0].lat), lng: parseFloat(data[0].lon) }
      onAnalyze(sourceBusiness.trim(), targetLocation.trim(), coords)
    } catch {
      setGeocodeError('Failed to geocode location. Please try again.')
    } finally {
      setGeocoding(false)
    }
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
              <Copy className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-stone-900 mb-2">Deep Clone</h2>
            <p className="text-stone-600">
              Clone a successful business model to a new location. We'll analyze demographics, 
              competition, and market fit to help you validate the opportunity.
            </p>
          </div>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-2">
                <Search className="w-4 h-4 inline mr-1" />
                Source Business
              </label>
              <input
                type="text"
                value={sourceBusiness}
                onChange={(e) => setSourceBusiness(e.target.value)}
                placeholder="e.g., Crumbl Cookies, Planet Fitness, The UPS Store"
                className="w-full px-4 py-3 border border-stone-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="mt-1 text-xs text-stone-500">
                Enter the name of a successful franchise or business model you want to clone
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-stone-700 mb-2">
                <MapPin className="w-4 h-4 inline mr-1" />
                Target Location
              </label>
              <input
                type="text"
                value={targetLocation}
                onChange={(e) => handleLocationChange(e.target.value)}
                placeholder="e.g., Austin, TX or 78701"
                className="w-full px-4 py-3 border border-stone-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              {geocoding && (
                <p className="mt-1 text-xs text-stone-500 flex items-center gap-1">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  Finding location...
                </p>
              )}
              {geocodeError && (
                <p className="mt-1 text-xs text-red-600">{geocodeError}</p>
              )}
              {previewCoords && !geocoding && (
                <p className="mt-1 text-xs text-emerald-600">
                  Location found: {previewCoords.lat.toFixed(4)}, {previewCoords.lng.toFixed(4)}
                </p>
              )}
            </div>

            {previewCoords && (
              <div className="bg-stone-100 rounded-xl p-4 h-48 flex items-center justify-center">
                <div className="text-center text-stone-500">
                  <MapPin className="w-8 h-8 mx-auto mb-2" />
                  <p className="text-sm">Map preview</p>
                  <p className="text-xs">{targetLocation}</p>
                </div>
              </div>
            )}

            <button
              onClick={handleAnalyze}
              disabled={!sourceBusiness.trim() || !targetLocation.trim() || geocoding || isAnalyzing}
              className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  Analyze Location
                  <ChevronRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
