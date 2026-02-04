import { useState } from 'react'
import { ChevronDown, ChevronUp, Info, Car, Users, Store, TrendingUp, TrendingDown, Minus, Target, Layers } from 'lucide-react'
import type { LayerInstance } from './types'

interface MapLegendProps {
  layers: LayerInstance[]
  showOptimalZones?: boolean
  showTrends?: boolean
  trafficMode?: 'hotspot' | 'heatmap'
}

function LegendSection({ 
  title, 
  icon, 
  children,
  defaultOpen = true 
}: { 
  title: string
  icon: React.ReactNode
  children: React.ReactNode
  defaultOpen?: boolean
}) {
  const [isOpen, setIsOpen] = useState(defaultOpen)
  
  return (
    <div className="border-b border-gray-700/50 last:border-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between py-2 px-1 hover:bg-gray-700/30 transition-colors"
      >
        <div className="flex items-center gap-2">
          {icon}
          <span className="text-xs font-medium text-gray-300">{title}</span>
        </div>
        {isOpen ? (
          <ChevronUp size={14} className="text-gray-500" />
        ) : (
          <ChevronDown size={14} className="text-gray-500" />
        )}
      </button>
      {isOpen && (
        <div className="pb-2 px-1">
          {children}
        </div>
      )}
    </div>
  )
}

function ColorGradient({ 
  colors, 
  labels 
}: { 
  colors: string[]
  labels: string[] 
}) {
  return (
    <div className="space-y-1">
      <div 
        className="h-3 rounded-sm"
        style={{ 
          background: `linear-gradient(to right, ${colors.join(', ')})` 
        }}
      />
      <div className="flex justify-between text-[10px] text-gray-500">
        {labels.map((label, i) => (
          <span key={i}>{label}</span>
        ))}
      </div>
    </div>
  )
}

function LegendItem({ 
  color, 
  label, 
  shape = 'circle' 
}: { 
  color: string
  label: string
  shape?: 'circle' | 'square' | 'line'
}) {
  return (
    <div className="flex items-center gap-2 py-0.5">
      {shape === 'circle' && (
        <div 
          className="w-3 h-3 rounded-full border border-white/30"
          style={{ backgroundColor: color }}
        />
      )}
      {shape === 'square' && (
        <div 
          className="w-3 h-3 rounded-sm border border-white/30"
          style={{ backgroundColor: color }}
        />
      )}
      {shape === 'line' && (
        <div 
          className="w-4 h-0.5 rounded"
          style={{ backgroundColor: color }}
        />
      )}
      <span className="text-[11px] text-gray-400">{label}</span>
    </div>
  )
}

function TrafficLegend({ mode }: { mode: 'hotspot' | 'heatmap' }) {
  return (
    <LegendSection 
      title="Traffic / Activity" 
      icon={<Car size={14} className="text-yellow-400" />}
    >
      <div className="space-y-2">
        {mode === 'hotspot' ? (
          <>
            <div>
              <p className="text-[10px] text-gray-500 mb-1">Vitality Score (Hotspots)</p>
              <ColorGradient 
                colors={['#22c55e', '#84cc16', '#eab308', '#f97316', '#ef4444']}
                labels={['Low', 'Medium', 'High']}
              />
            </div>
            <div className="flex items-center gap-3 pt-1">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-yellow-500 border border-white/50" />
                <span className="text-[10px] text-gray-500">Small = Low</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-4 h-4 rounded-full bg-red-500 border border-white/50" />
                <span className="text-[10px] text-gray-500">Large = High</span>
              </div>
            </div>
          </>
        ) : (
          <>
            <div>
              <p className="text-[10px] text-gray-500 mb-1">Traffic Intensity (Heatmap)</p>
              <ColorGradient 
                colors={['rgba(0,0,255,0)', 'rgba(65,105,225,0.4)', 'rgba(0,255,255,0.5)', 'rgba(0,255,0,0.6)', 'rgba(255,255,0,0.7)', 'rgba(255,0,0,0.8)']}
                labels={['Low', 'Medium', 'High']}
              />
            </div>
            <LegendItem color="#f59e0b" label="Traffic data point (zoom 14+)" />
          </>
        )}
        <div className="text-[10px] text-gray-500 italic pt-1">
          Combines DOT vehicle counts + Google activity data
        </div>
      </div>
    </LegendSection>
  )
}

function CompetitionLegend() {
  return (
    <LegendSection 
      title="Competition" 
      icon={<Store size={14} className="text-red-400" />}
    >
      <div className="space-y-1">
        <LegendItem color="#ef4444" label="Competitor location" />
        <div className="text-[10px] text-gray-500 italic pt-1">
          Each marker represents a nearby competitor
        </div>
      </div>
    </LegendSection>
  )
}

function DemographicsLegend({ displayMode }: { displayMode?: string }) {
  const modeConfig: Record<string, { fill: string; line: string; lineStyle: string; label: string }> = {
    heatmap: { fill: 'rgba(59, 130, 246, 0.25)', line: '#1d4ed8', lineStyle: 'solid', label: 'Heatmap' },
    markers: { fill: 'rgba(16, 185, 129, 0.1)', line: '#059669', lineStyle: 'dashed', label: 'Markers' },
    choropleth: { fill: 'rgba(139, 92, 246, 0.3)', line: '#6d28d9', lineStyle: 'solid', label: 'Choropleth' }
  }
  
  const mode = displayMode || 'heatmap'
  const config = modeConfig[mode] || modeConfig.heatmap
  
  return (
    <LegendSection 
      title="Demographics" 
      icon={<Users size={14} className="text-blue-400" />}
    >
      <div className="space-y-2">
        <div className="flex items-center gap-2 py-0.5">
          <div 
            className="w-6 h-4 rounded-sm border-2"
            style={{ 
              backgroundColor: config.fill, 
              borderColor: config.line,
              borderStyle: config.lineStyle as any
            }}
          />
          <span className="text-[11px] text-gray-400">Analysis radius ({config.label})</span>
        </div>
        <div className="text-[10px] text-gray-500 italic pt-1">
          Shows population, income, and employment data
        </div>
      </div>
    </LegendSection>
  )
}

function TrendLegend() {
  return (
    <LegendSection 
      title="Trend Indicators" 
      icon={<TrendingUp size={14} className="text-green-400" />}
    >
      <div className="space-y-1">
        <div className="flex items-center gap-2 py-0.5">
          <TrendingUp size={14} className="text-green-400" />
          <span className="text-[11px] text-gray-400">Growing / Positive trend</span>
        </div>
        <div className="flex items-center gap-2 py-0.5">
          <TrendingDown size={14} className="text-red-400" />
          <span className="text-[11px] text-gray-400">Declining / Negative trend</span>
        </div>
        <div className="flex items-center gap-2 py-0.5">
          <Minus size={14} className="text-gray-400" />
          <span className="text-[11px] text-gray-400">Stable / No significant change</span>
        </div>
        <div className="mt-2 pt-2 border-t border-gray-700/30">
          <p className="text-[10px] text-gray-500 font-medium mb-1">Momentum Score</p>
          <div className="flex items-center gap-2">
            <div className="px-2 py-0.5 rounded bg-green-500/20 text-[10px] text-green-400">Growing</div>
            <div className="px-2 py-0.5 rounded bg-gray-500/20 text-[10px] text-gray-400">Stable</div>
            <div className="px-2 py-0.5 rounded bg-red-500/20 text-[10px] text-red-400">Declining</div>
          </div>
        </div>
      </div>
    </LegendSection>
  )
}

function OptimalZonesLegend() {
  return (
    <LegendSection 
      title="Optimal Zones" 
      icon={<Target size={14} className="text-violet-400" />}
    >
      <div className="space-y-1">
        <div className="flex items-center gap-2 py-0.5">
          <div className="w-5 h-5 rounded-full bg-violet-600 flex items-center justify-center text-[10px] text-white font-bold border-2 border-white">
            1
          </div>
          <span className="text-[11px] text-gray-400">Best zone (highest score)</span>
        </div>
        <div className="flex items-center gap-2 py-0.5">
          <div className="w-5 h-5 rounded-full bg-violet-500 flex items-center justify-center text-[10px] text-white font-bold border-2 border-white">
            2
          </div>
          <span className="text-[11px] text-gray-400">Second best zone</span>
        </div>
        <div className="flex items-center gap-2 py-0.5">
          <div className="w-5 h-5 rounded-full bg-violet-400 flex items-center justify-center text-[10px] text-white font-bold border-2 border-white">
            3
          </div>
          <span className="text-[11px] text-gray-400">Third best zone</span>
        </div>
        <div className="mt-1 text-[10px] text-gray-500 italic">
          Zones ranked by weighted score across all metrics
        </div>
      </div>
    </LegendSection>
  )
}

export default function MapLegend({ layers, showOptimalZones, showTrends, trafficMode = 'hotspot' }: MapLegendProps) {
  const [isExpanded, setIsExpanded] = useState(true)
  
  const footTrafficLayer = layers.find(l => l.type === 'foot_traffic' && l.visible)
  const hasFootTraffic = !!footTrafficLayer
  const driveByTrafficLayer = layers.find(l => l.type === 'drive_by_traffic' && l.visible)
  const hasDriveByTraffic = !!driveByTrafficLayer
  const actualTrafficMode: 'hotspot' | 'heatmap' = footTrafficLayer?.data?.hotspots?.length > 0 || 
    footTrafficLayer?.data?.features?.[0]?.properties?.vitalityScore !== undefined 
      ? 'hotspot' 
      : 'heatmap'
  
  const competitionLayer = layers.find(l => l.type === 'competition' && l.visible)
  const hasCompetition = !!competitionLayer
  
  const demographicsLayer = layers.find(l => l.type === 'demographics' && l.visible)
  const hasDemographics = !!demographicsLayer
  const demographicsDisplayMode = demographicsLayer?.config?.displayMode || 'heatmap'
  
  const hasDeepClone = layers.some(l => l.type === 'deep_clone' && l.visible)
  
  const hasAnyVisibleLayer = hasFootTraffic || hasDriveByTraffic || hasCompetition || hasDemographics || hasDeepClone || showOptimalZones || showTrends
  
  if (!hasAnyVisibleLayer) return null
  
  return (
    <div className="absolute bottom-4 left-4 z-10">
      <div className="bg-gray-900/95 backdrop-blur-sm rounded-lg shadow-xl border border-gray-700/50 overflow-hidden max-w-[220px]">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between px-3 py-2 hover:bg-gray-700/30 transition-colors"
        >
          <div className="flex items-center gap-2">
            <Layers size={14} className="text-gray-400" />
            <span className="text-xs font-medium text-gray-200">Map Legend</span>
          </div>
          {isExpanded ? (
            <ChevronDown size={14} className="text-gray-500" />
          ) : (
            <ChevronUp size={14} className="text-gray-500" />
          )}
        </button>
        
        {isExpanded && (
          <div className="px-2 max-h-[400px] overflow-y-auto">
            {hasFootTraffic && <TrafficLegend mode={actualTrafficMode} />}
            {hasDriveByTraffic && <TrafficLegend mode="heatmap" />}
            {hasCompetition && <CompetitionLegend />}
            {(hasDemographics || hasDeepClone) && <DemographicsLegend displayMode={demographicsDisplayMode} />}
            {showTrends && <TrendLegend />}
            {showOptimalZones && <OptimalZonesLegend />}
            
            <div className="py-2 px-1 text-[10px] text-gray-600 flex items-center gap-1">
              <Info size={10} />
              <span>Click legend sections to expand/collapse</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
