/**
 * OpportunityCard Component
 * 
 * Enhanced opportunity card with hover states, quick actions, and time-based access control.
 * 
 * Features:
 * - Hover animations and elevation
 * - Quick action buttons (Validate, Save, Analyze, Share)
 * - Time-decay access indicators (HOT, FRESH, VALIDATED, ARCHIVE)
 * - AI-powered insights and scoring
 * - Mobile responsive design
 * 
 * @component
 */

import React, { useState } from 'react';
import { Opportunity, UserTier, FreshnessBadge } from './types';

interface OpportunityCardProps {
  opportunity: Opportunity;
  userTier?: UserTier;
  onValidate?: (id: number) => void;
  onSave?: (id: number) => void;
  onAnalyze?: (id: number) => void;
  onShare?: (id: number) => void;
  isValidated?: boolean;
  isSaved?: boolean;
}

export const OpportunityCard: React.FC<OpportunityCardProps> = ({
  opportunity,
  userTier = 'free',
  onValidate,
  onSave,
  onAnalyze,
  onShare,
  isValidated = false,
  isSaved = false,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  // Calculate opportunity age
  const getOpportunityAgeDays = (): number => {
    const createdAt = opportunity.created_at ? new Date(opportunity.created_at) : new Date();
    const now = new Date();
    return Math.floor((now.getTime() - createdAt.getTime()) / (1000 * 60 * 60 * 24));
  };

  const ageDays = getOpportunityAgeDays();

  // Determine freshness badge
  const getFreshnessBadge = (): FreshnessBadge => {
    if (ageDays <= 7) {
      return { icon: '🔥', label: 'HOT', color: '#dc2626', tierRequired: 'enterprise' };
    } else if (ageDays <= 30) {
      return { icon: '⚡', label: 'FRESH', color: '#f97316', tierRequired: 'business' };
    } else if (ageDays <= 90) {
      return { icon: '✓', label: 'VALIDATED', color: '#16a34a', tierRequired: 'pro' };
    } else {
      return { icon: '📚', label: 'ARCHIVE', color: '#6b7280', tierRequired: 'free' };
    }
  };

  const freshnessBadge = getFreshnessBadge();

  // Access control logic
  const canAccessOpportunity = (): boolean => {
    const accessWindows: Record<UserTier, number> = {
      free: 91,
      pro: 31,
      business: 8,
      enterprise: 0
    };
    const minAge = accessWindows[userTier] || 91;
    return ageDays >= minAge;
  };

  const getDaysUntilUnlock = (): number => {
    const accessWindows: Record<UserTier, number> = {
      free: 91,
      pro: 31,
      business: 8,
      enterprise: 0
    };
    const minAge = accessWindows[userTier] || 91;
    return Math.max(0, minAge - ageDays);
  };

  const isAccessible = canAccessOpportunity();
  const daysUntilUnlock = getDaysUntilUnlock();
  const canPayToUnlock = ageDays >= 91 && userTier === 'free';

  // UI helpers
  const formatNumber = (num: number): string => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
    }
    return num.toString();
  };

  const generateViewerCount = (): number => {
    return 12 + (opportunity.id * 7) % 89;
  };

  const isTrending = (opportunity.growth_rate || 0) > 20;
  const aiScore = opportunity.ai_opportunity_score || Math.min(100, Math.round(50 + ((opportunity.validation_count || 0) / 10) + (opportunity.growth_rate || 0)));
  const competitionLevel = opportunity.ai_competition_level || 'medium';
  const viewerCount = generateViewerCount();

  const getRegionLabel = (): string => {
    if (opportunity.geographic_scope === 'online') return 'Online';
    if (opportunity.geographic_scope === 'international') return 'Global';
    if (opportunity.city) return opportunity.city;
    if (opportunity.region) return opportunity.region;
    if (opportunity.country) return opportunity.country;
    return opportunity.geographic_scope || 'N/A';
  };

  const handleCardClick = (e: React.MouseEvent) => {
    // Prevent navigation if clicking on action buttons
    if ((e.target as HTMLElement).closest('.quick-actions')) {
      e.preventDefault();
      return;
    }
    window.location.href = `/opportunity.html?id=${opportunity.id}`;
  };

  return (
    <div
      className="opportunity-card group"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleCardClick}
      role="article"
      aria-label={`Opportunity: ${opportunity.ai_generated_title || opportunity.title}`}
    >
      {/* Card Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          {/* Meta badges */}
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span className="text-xs font-semibold uppercase tracking-wider text-stone-500">
              {opportunity.category}
            </span>
            
            {/* Freshness Badge */}
            <span
              className="inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-semibold"
              style={{
                background: `${freshnessBadge.color}15`,
                color: freshnessBadge.color,
                border: `1px solid ${freshnessBadge.color}30`
              }}
            >
              <span>{freshnessBadge.icon}</span>
              <span>{freshnessBadge.label}</span>
              <span>· {ageDays}d</span>
            </span>

            {/* Trending Badge */}
            {isTrending && (
              <span className="inline-flex items-center gap-1 bg-stone-200 text-stone-700 px-2 py-1 rounded-xl text-xs font-semibold">
                <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
                  <polyline points="16 7 22 7 22 13"/>
                </svg>
                Trending
              </span>
            )}
          </div>

          {/* Title */}
          <h3 className="font-spectral text-xl font-bold text-stone-900 mb-1 group-hover:text-stone-800 transition-colors">
            {opportunity.ai_generated_title || opportunity.title}
          </h3>
        </div>

        {/* AI Score Badge */}
        <div className="text-center ml-4">
          <div className="bg-emerald-100 text-emerald-700 px-3 py-2 rounded-2xl mb-1">
            <span className="font-spectral text-2xl font-bold">{aiScore}</span>
          </div>
          <div className="text-xs text-stone-500">Score</div>
        </div>
      </div>

      {/* Access Indicator */}
      {!isAccessible && !canPayToUnlock && (
        <div className="bg-stone-100 rounded-lg p-3 mb-3 flex items-center gap-2 text-sm">
          <span className="text-base">⏰</span>
          <span className="text-stone-600">
            {daysUntilUnlock > 0 ? (
              <>
                Unlocks for you in <strong className="text-stone-800">{daysUntilUnlock} days</strong>
              </>
            ) : (
              '✨ Available to you now'
            )}
          </span>
        </div>
      )}

      {canPayToUnlock && (
        <div className="bg-gradient-to-r from-yellow-50 to-yellow-100 rounded-lg p-3 mb-3 flex items-center justify-between text-sm">
          <span className="text-stone-600">
            <span className="text-base">🔓</span> Unlock for <strong className="text-amber-700">$15</strong>
          </span>
          <span className="text-stone-500 text-xs">or upgrade to Pro</span>
        </div>
      )}

      {/* AI Summary */}
      {opportunity.ai_summary && (
        <div className="bg-stone-100 rounded-lg p-3 mb-3">
          <div className="text-xs font-semibold uppercase tracking-wide text-stone-600 mb-1">
            AI Insight:
          </div>
          <p className="text-sm text-stone-700 leading-relaxed">
            {opportunity.ai_summary}
          </p>
        </div>
      )}

      {/* Description */}
      <p className="text-sm text-stone-700 leading-relaxed mb-4">
        {(opportunity.ai_problem_statement || opportunity.description).substring(0, 120)}
        {(opportunity.ai_problem_statement || opportunity.description).length > 120 ? '...' : ''}
      </p>

      {/* Metrics Grid */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        <div className="bg-stone-50 rounded-lg p-3">
          <div className="text-xs text-stone-500 mb-1 flex items-center gap-1">
            <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 12l2 2 4-4"/>
              <circle cx="12" cy="12" r="10"/>
            </svg>
            Validations
          </div>
          <div className="font-spectral text-lg font-bold text-stone-900">
            {formatNumber(opportunity.validation_count || 0)}
          </div>
        </div>

        <div className="bg-stone-50 rounded-lg p-3">
          <div className="text-xs text-stone-500 mb-1 flex items-center gap-1">
            <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            Market
          </div>
          <div className="font-spectral text-lg font-bold text-stone-900">
            {opportunity.ai_market_size_estimate || opportunity.market_size || 'TBD'}
          </div>
        </div>

        <div className="bg-stone-50 rounded-lg p-3">
          <div className="text-xs text-stone-500 mb-1 flex items-center gap-1">
            <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
            Growth
          </div>
          <div className="font-spectral text-lg font-bold text-emerald-600">
            +{opportunity.growth_rate || 0}%
          </div>
        </div>

        <div className="bg-stone-50 rounded-lg p-3">
          <div className="text-xs text-stone-500 mb-1 flex items-center gap-1">
            <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
            Region
          </div>
          <div className="font-spectral text-base font-bold text-stone-900 truncate">
            {getRegionLabel()}
          </div>
        </div>
      </div>

      {/* Competition & Severity */}
      <div className="flex flex-wrap gap-2 mb-4">
        <span
          className={`inline-flex items-center gap-1 px-3 py-1 rounded-xl text-xs font-medium ${
            competitionLevel === 'low'
              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
              : competitionLevel === 'high'
              ? 'bg-red-50 text-red-700 border border-red-200'
              : 'bg-yellow-50 text-yellow-700 border border-yellow-200'
          }`}
        >
          {competitionLevel.charAt(0).toUpperCase() + competitionLevel.slice(1)} Competition
        </span>
        <span className="bg-stone-100 text-stone-700 px-3 py-1 rounded-xl text-xs">
          Severity: {opportunity.severity}/5
        </span>
      </div>

      {/* Viewer Count */}
      <div className="flex items-center gap-2 text-xs text-stone-500 mb-4">
        <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
        <span className="font-medium text-stone-700">{viewerCount} people</span>
        <span>viewed this week</span>
      </div>

      {/* Quick Actions - Show on Hover */}
      <div
        className={`quick-actions transition-all duration-200 ${
          isHovered ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2 pointer-events-none'
        }`}
      >
        <div className="flex items-center gap-2 p-3 bg-stone-50 rounded-lg border border-stone-200">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onValidate?.(opportunity.id);
            }}
            disabled={isValidated}
            className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              isValidated
                ? 'bg-emerald-100 text-emerald-700 cursor-default'
                : 'bg-white text-stone-700 hover:bg-stone-100 border border-stone-200'
            }`}
          >
            {isValidated ? '✓ Validated' : '✓ Validate'}
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onSave?.(opportunity.id);
            }}
            className={`p-2 rounded-md transition-colors ${
              isSaved
                ? 'bg-violet-100 text-violet-700'
                : 'bg-white text-stone-600 hover:bg-stone-100 border border-stone-200'
            }`}
            title={isSaved ? 'Saved' : 'Save'}
          >
            {isSaved ? '💾' : '💾'}
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onAnalyze?.(opportunity.id);
            }}
            className="p-2 bg-white text-stone-600 hover:bg-stone-100 border border-stone-200 rounded-md transition-colors"
            title="AI Analyze"
          >
            🤖
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onShare?.(opportunity.id);
            }}
            className="p-2 bg-white text-stone-600 hover:bg-stone-100 border border-stone-200 rounded-md transition-colors"
            title="Share"
          >
            ↗
          </button>
        </div>
      </div>

      {/* CTA */}
      <div className="flex items-center gap-2 text-sm font-medium text-stone-900 mt-4">
        <span>
          {isAccessible || userTier !== 'free'
            ? 'View full analysis'
            : canPayToUnlock
            ? '🔓 Unlock for $15'
            : 'Preview opportunity'}
        </span>
        <svg
          className="w-4 h-4 transition-transform group-hover:translate-x-1"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path d="M7 17 17 7"/>
          <path d="M7 7h10v10"/>
        </svg>
      </div>

      {/* Styles */}
      <style jsx>{`
        .opportunity-card {
          background: white;
          border-radius: 1rem;
          border: 2px solid #e7e5e4;
          padding: 1.5rem;
          text-decoration: none;
          color: inherit;
          transition: all 0.2s;
          display: block;
          cursor: pointer;
        }

        .opportunity-card:hover {
          border-color: #1c1917;
          box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.1);
          transform: translateY(-2px);
        }

        .font-spectral {
          font-family: 'Spectral', serif;
        }
      `}</style>
    </div>
  );
};

export default OpportunityCard;
