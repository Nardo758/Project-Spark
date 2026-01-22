import { TrendingUp, TrendingDown, Minus, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import { TrendSummary, TrendIndicator } from './types'

interface TrendIndicatorsProps {
  trends: TrendSummary
}

function TrendArrow({ direction, size = 16 }: { direction: 'up' | 'down' | 'stable'; size?: number }) {
  if (direction === 'up') {
    return <TrendingUp className="text-green-400" size={size} />
  } else if (direction === 'down') {
    return <TrendingDown className="text-red-400" size={size} />
  }
  return <Minus className="text-gray-400" size={size} />
}

function TrendBadge({ trend }: { trend: TrendIndicator }) {
  const colorClass = trend.direction === 'up' 
    ? 'text-green-400' 
    : trend.direction === 'down' 
      ? 'text-red-400' 
      : 'text-gray-400'
  
  const sign = trend.change_percent > 0 ? '+' : ''
  
  return (
    <div className="flex items-center gap-1.5">
      <TrendArrow direction={trend.direction} size={14} />
      <span className={`text-sm font-medium ${colorClass}`}>
        {sign}{trend.change_percent.toFixed(1)}%
      </span>
    </div>
  )
}

function TrendRow({ trend }: { trend: TrendIndicator }) {
  return (
    <div className="flex items-center justify-between py-1.5 px-2 hover:bg-gray-700/30 rounded">
      <div className="flex flex-col">
        <span className="text-sm text-gray-300">{trend.metric_name}</span>
        <span className="text-xs text-gray-500">{trend.period} period</span>
      </div>
      <TrendBadge trend={trend} />
    </div>
  )
}

function TrendCategory({ 
  title, 
  trends, 
  icon 
}: { 
  title: string
  trends: Record<string, TrendIndicator>
  icon: React.ReactNode 
}) {
  const trendList = Object.values(trends)
  if (trendList.length === 0) return null
  
  return (
    <div className="mb-3">
      <div className="flex items-center gap-2 mb-1.5 px-2">
        {icon}
        <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">{title}</span>
      </div>
      <div className="space-y-0.5">
        {trendList.map((trend) => (
          <TrendRow key={trend.metric_name} trend={trend} />
        ))}
      </div>
    </div>
  )
}

function MomentumIndicator({ momentum, score }: { momentum: string; score: number }) {
  const colorClass = momentum === 'growing' 
    ? 'bg-green-500/20 text-green-400 border-green-500/30' 
    : momentum === 'declining' 
      ? 'bg-red-500/20 text-red-400 border-red-500/30' 
      : 'bg-gray-500/20 text-gray-400 border-gray-500/30'
  
  const Icon = momentum === 'growing' 
    ? TrendingUp 
    : momentum === 'declining' 
      ? TrendingDown 
      : Minus
  
  return (
    <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${colorClass}`}>
      <Icon size={18} />
      <div>
        <div className="text-sm font-medium capitalize">{momentum}</div>
        <div className="text-xs opacity-70">
          Momentum: {score > 0 ? '+' : ''}{score.toFixed(1)}
        </div>
      </div>
    </div>
  )
}

export default function TrendIndicators({ trends }: TrendIndicatorsProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  
  return (
    <div className="bg-gray-800/60 rounded-lg border border-gray-700/50">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 hover:bg-gray-700/30 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <TrendingUp size={16} className="text-blue-400" />
            <span className="text-sm font-medium text-gray-200">Trend Indicators</span>
          </div>
          <MomentumIndicator momentum={trends.overall_momentum} score={trends.momentum_score} />
        </div>
        {isExpanded ? (
          <ChevronUp size={18} className="text-gray-400" />
        ) : (
          <ChevronDown size={18} className="text-gray-400" />
        )}
      </button>
      
      {isExpanded && (
        <div className="px-3 pb-3 border-t border-gray-700/50 pt-3">
          <TrendCategory 
            title="Traffic Trends" 
            trends={trends.traffic_trends}
            icon={<div className="w-2 h-2 rounded-full bg-blue-400" />}
          />
          <TrendCategory 
            title="Competition Trends" 
            trends={trends.competition_trends}
            icon={<div className="w-2 h-2 rounded-full bg-orange-400" />}
          />
          <TrendCategory 
            title="Demographic Trends" 
            trends={trends.demographic_trends}
            icon={<div className="w-2 h-2 rounded-full bg-purple-400" />}
          />
          <TrendCategory 
            title="Vitality Trends" 
            trends={trends.vitality_trends}
            icon={<div className="w-2 h-2 rounded-full bg-green-400" />}
          />
          
          <div className="mt-3 pt-3 border-t border-gray-700/30">
            <div className="text-xs text-gray-500 px-2">
              Trends compare current values to historical baselines. 
              Traffic uses 90-day averages, demographics use year-over-year Census data.
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
