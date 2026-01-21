import { useState, useCallback, useRef, useEffect } from 'react'
import { Search, MapPin, Loader2 } from 'lucide-react'
import type { LayerDefinition, LayerInputField } from './types'

function useDebounce<T extends (...args: any[]) => any>(fn: T, delay: number) {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)
  
  const debouncedFn = useCallback((...args: Parameters<T>) => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    timeoutRef.current = setTimeout(() => fn(...args), delay)
  }, [fn, delay])
  
  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    }
  }, [])
  
  return debouncedFn
}

interface LayerInputRendererProps {
  definition: LayerDefinition
  config: Record<string, any>
  onChange: (config: Record<string, any>) => void
  loading?: boolean
}

const radiusOptions = [
  { value: 0.25, label: '0.25 mi' },
  { value: 0.5, label: '0.5 mi' },
  { value: 1, label: '1 mi' },
  { value: 2, label: '2 mi' },
  { value: 5, label: '5 mi' },
  { value: 10, label: '10 mi' }
]

export function LayerInputRenderer({ definition, config, onChange, loading }: LayerInputRendererProps) {
  const [addressSuggestions, setAddressSuggestions] = useState<any[]>([])
  const [addressLoading, setAddressLoading] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)

  const doAddressSearch = useCallback(async (query: string) => {
    if (query.length < 3) {
      setAddressSuggestions([])
      return
    }
    
    setAddressLoading(true)
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&countrycodes=us`
      )
      const data = await response.json()
      setAddressSuggestions(data)
      setShowSuggestions(true)
    } catch (error) {
      console.error('Address search error:', error)
    } finally {
      setAddressLoading(false)
    }
  }, [])

  const searchAddress = useDebounce(doAddressSearch, 300)

  const handleAddressSelect = (suggestion: any) => {
    onChange({
      address: suggestion.display_name,
      coordinates: {
        lat: parseFloat(suggestion.lat),
        lng: parseFloat(suggestion.lon)
      }
    })
    setShowSuggestions(false)
    setAddressSuggestions([])
  }

  const renderInput = (field: LayerInputField) => {
    const value = config[field.key]

    switch (field.type) {
      case 'address':
        return (
          <div className="relative">
            <div className="relative">
              <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400" />
              <input
                type="text"
                value={value || ''}
                onChange={(e) => {
                  onChange({ [field.key]: e.target.value, coordinates: null })
                  searchAddress(e.target.value)
                }}
                onFocus={() => addressSuggestions.length > 0 && setShowSuggestions(true)}
                placeholder={field.placeholder}
                className="w-full pl-9 pr-10 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
              />
              {addressLoading && (
                <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400 animate-spin" />
              )}
            </div>
            {showSuggestions && addressSuggestions.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-stone-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                {addressSuggestions.map((suggestion, i) => (
                  <button
                    key={i}
                    onClick={() => handleAddressSelect(suggestion)}
                    className="w-full text-left px-3 py-2 text-sm hover:bg-stone-50 border-b border-stone-100 last:border-0"
                  >
                    <span className="line-clamp-2">{suggestion.display_name}</span>
                  </button>
                ))}
              </div>
            )}
            {config.coordinates && (
              <p className="mt-1 text-xs text-emerald-600">
                Location set: {config.coordinates.lat.toFixed(4)}, {config.coordinates.lng.toFixed(4)}
              </p>
            )}
          </div>
        )

      case 'radius':
        return (
          <div className="space-y-2">
            <div className="flex gap-1">
              {radiusOptions.map(opt => (
                <button
                  key={opt.value}
                  onClick={() => onChange({ [field.key]: opt.value })}
                  className={`flex-1 px-2 py-1.5 rounded text-xs font-medium transition-all ${
                    value === opt.value
                      ? 'bg-violet-600 text-white'
                      : 'bg-stone-100 text-stone-600 hover:bg-stone-200'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        )

      case 'text':
        return (
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400" />
            <input
              type="text"
              value={value || ''}
              onChange={(e) => onChange({ [field.key]: e.target.value })}
              placeholder={field.placeholder}
              className="w-full pl-9 pr-3 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
            />
          </div>
        )

      case 'select':
        return (
          <select
            value={value || field.defaultValue}
            onChange={(e) => onChange({ [field.key]: e.target.value })}
            className="w-full px-3 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500 bg-white"
          >
            {field.options?.map(opt => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        )

      case 'toggle':
        return (
          <button
            onClick={() => onChange({ [field.key]: !value })}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              value ? 'bg-violet-600' : 'bg-stone-200'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                value ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        )

      case 'number':
        return (
          <input
            type="number"
            value={value || ''}
            onChange={(e) => onChange({ [field.key]: parseFloat(e.target.value) || 0 })}
            placeholder={field.placeholder}
            className="w-full px-3 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
          />
        )

      default:
        return null
    }
  }

  return (
    <div className="space-y-4">
      {definition.inputs.map(field => (
        <div key={field.key} className={field.type === 'toggle' ? 'flex items-center justify-between' : ''}>
          <label className="block text-sm font-medium text-stone-700 mb-1">
            {field.label}
            {field.required && <span className="text-red-500 ml-0.5">*</span>}
          </label>
          {renderInput(field)}
        </div>
      ))}

      {loading && (
        <div className="flex items-center justify-center py-4">
          <Loader2 className="w-5 h-5 text-violet-600 animate-spin" />
          <span className="ml-2 text-sm text-stone-500">Loading layer data...</span>
        </div>
      )}
    </div>
  )
}
