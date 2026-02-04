/**
 * OpportunityCardSkeleton Component
 * 
 * Loading skeleton for OpportunityCard.
 * Provides visual feedback while data is being fetched.
 * 
 * @component
 */

import React from 'react';

export const OpportunityCardSkeleton: React.FC = () => {
  return (
    <div className="opportunity-card-skeleton animate-pulse">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <div className="h-5 w-20 bg-stone-200 rounded"></div>
            <div className="h-5 w-24 bg-stone-200 rounded"></div>
          </div>
          <div className="h-6 w-3/4 bg-stone-300 rounded mb-1"></div>
        </div>
        <div className="ml-4">
          <div className="h-12 w-16 bg-emerald-100 rounded-2xl"></div>
        </div>
      </div>

      {/* Description */}
      <div className="space-y-2 mb-4">
        <div className="h-4 bg-stone-200 rounded w-full"></div>
        <div className="h-4 bg-stone-200 rounded w-5/6"></div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-stone-50 rounded-lg p-3">
            <div className="h-3 w-16 bg-stone-200 rounded mb-2"></div>
            <div className="h-5 w-12 bg-stone-300 rounded"></div>
          </div>
        ))}
      </div>

      {/* Tags */}
      <div className="flex gap-2 mb-4">
        <div className="h-6 w-32 bg-stone-200 rounded-xl"></div>
        <div className="h-6 w-24 bg-stone-200 rounded-xl"></div>
      </div>

      {/* Viewer Count */}
      <div className="h-4 w-48 bg-stone-200 rounded mb-4"></div>

      {/* CTA */}
      <div className="h-4 w-32 bg-stone-200 rounded"></div>

      <style jsx>{`
        .opportunity-card-skeleton {
          background: white;
          border-radius: 1rem;
          border: 2px solid #e7e5e4;
          padding: 1.5rem;
        }

        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }

        .animate-pulse {
          animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
      `}</style>
    </div>
  );
};

export default OpportunityCardSkeleton;
