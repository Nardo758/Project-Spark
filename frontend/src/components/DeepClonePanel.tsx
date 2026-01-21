import { useState, memo } from 'react'
import { X, Search, MapPin, Loader2, Plus, Trash2 } from 'lucide-react'

interface DeepClonePanelProps {
  isOpen: boolean
  onClose: () => void
  opportunity?: any
  onAnalyze: (targets: Array<{name: string, lat: number, lng: number}>) => void
  isAnalyzing?: boolean
}

function DeepClonePanel({
  isOpen,
  onClose,
  opportunity,
  onAnalyze,
  isAnalyzing = false
}: DeepClonePanelProps) {
  const [businessType, setBusinessType] = useState('')
  const [targetInput, setTargetInput] = useState('')
  const [targets, setTargets] = useState<Array<{name: string, lat: number, lng: number}>>([])
  const [isGeocoding, setIsGeocoding] = useState(false)

  if (!isOpen) return null

  async function addTarget() {
    if (!targetInput.trim() || isGeocoding) return

    setIsGeocoding(true)
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(targetInput)}&limit=1`
      )
      if (res.ok) {
        const data = await res.json()
        if (data.length > 0) {
          const loc = data[0]
          const newTarget = {
            name: loc.display_name.split(',').slice(0, 2).join(',').trim(),
            lat: parseFloat(loc.lat),
            lng: parseFloat(loc.lon)
          }
          setTargets(prev => [...prev, newTarget])
          setTargetInput('')
        }
      }
    } catch (err) {
      console.error('Failed to geocode:', err)
    } finally {
      setIsGeocoding(false)
    }
  }

  function removeTarget(index: number) {
    setTargets(prev => prev.filter((_, i) => i !== index))
  }

  function handleAnalyze() {
    if (targets.length === 0) return
    onAnalyze(targets)
  }

  return (
    <div className="w-80 border-r border-gray-700 bg-gray-800/50 flex flex-col shrink-0">
      <div className="p-3 border-b border-gray-700 flex items-center justify-between">
        <span className="font-medium text-sm flex items-center gap-2">
          <MapPin className="w-4 h-4 text-blue-400" />
          Deep Clone
        </span>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-700 rounded"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div>
          <label className="block text-xs text-gray-400 mb-2">Business Model</label>
          <input
            type="text"
            value={businessType || opportunity?.category || ''}
            onChange={(e) => setBusinessType(e.target.value)}
            placeholder="e.g., Coffee Shop, Gym, Restaurant"
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-sm focus:outline-none focus:border-purple-500"
          />
          <p className="text-xs text-gray-500 mt-1">
            {opportunity?.title ? `Based on: ${opportunity.title}` : 'Enter business type to clone'}
          </p>
        </div>

        <div>
          <label className="block text-xs text-gray-400 mb-2">Target Locations</label>
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={targetInput}
              onChange={(e) => setTargetInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') addTarget()
              }}
              placeholder="City name or ZIP code"
              className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-sm focus:outline-none focus:border-purple-500"
            />
            <button
              onClick={addTarget}
              disabled={isGeocoding || !targetInput.trim()}
              className="px-3 py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg"
            >
              {isGeocoding ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Plus className="w-4 h-4" />
              )}
            </button>
          </div>

          <div className="space-y-2 max-h-40 overflow-y-auto">
            {targets.map((target, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-gray-700/50 rounded-lg"
              >
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <MapPin className="w-3 h-3 text-blue-400 shrink-0" />
                  <span className="text-sm truncate">{target.name}</span>
                </div>
                <button
                  onClick={() => removeTarget(index)}
                  className="p-1 text-gray-400 hover:text-red-400 shrink-0"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>

          {targets.length === 0 && (
            <p className="text-xs text-gray-500 text-center py-4">
              Add cities or ZIP codes to compare
            </p>
          )}
        </div>
      </div>

      <div className="p-4 border-t border-gray-700">
        <button
          onClick={handleAnalyze}
          disabled={targets.length === 0 || isAnalyzing}
          className="w-full py-2 px-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-medium text-sm flex items-center justify-center gap-2"
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Search className="w-4 h-4" />
              Analyze {targets.length} Location{targets.length !== 1 ? 's' : ''}
            </>
          )}
        </button>
      </div>
    </div>
  )
}

export default memo(DeepClonePanel)
