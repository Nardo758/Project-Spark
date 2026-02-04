import React from 'react';
import { X, GitCompare } from 'lucide-react';

interface SelectedOpportunity {
  id: string;
  title: string;
}

interface ComparisonPanelProps {
  selectedOpportunities: SelectedOpportunity[];
  maxSelection?: number;
  onRemove: (id: string) => void;
  onCompare: () => void;
  onClear: () => void;
}

export const ComparisonPanel: React.FC<ComparisonPanelProps> = ({
  selectedOpportunities,
  maxSelection = 3,
  onRemove,
  onCompare,
  onClear
}) => {
  if (selectedOpportunities.length === 0) return null;

  const canCompare = selectedOpportunities.length >= 2;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t-2 border-gray-300 shadow-2xl animate-slide-up">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Left side - Selected opportunities */}
          <div className="flex items-center gap-4 flex-1">
            <div className="flex items-center gap-2">
              <GitCompare className="w-5 h-5 text-gray-700" />
              <span className="font-semibold text-gray-900">
                Compare Selected ({selectedOpportunities.length}/{maxSelection})
              </span>
            </div>

            {/* Selected opportunity chips */}
            <div className="flex gap-2 flex-wrap">
              {selectedOpportunities.map((opp) => (
                <div
                  key={opp.id}
                  className="flex items-center gap-2 px-3 py-1.5 bg-blue-100 text-blue-800 
                             rounded-full text-sm font-medium border border-blue-300"
                >
                  <span className="truncate max-w-[200px]">{opp.title}</span>
                  <button
                    onClick={() => onRemove(opp.id)}
                    className="hover:bg-blue-200 rounded-full p-0.5 transition-colors"
                    aria-label={`Remove ${opp.title}`}
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Right side - Actions */}
          <div className="flex items-center gap-3">
            {!canCompare && (
              <p className="text-sm text-gray-500 mr-2">
                Select at least 2 opportunities to compare
              </p>
            )}
            
            <button
              onClick={onClear}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 
                         rounded-lg transition-colors"
            >
              Clear All
            </button>

            <button
              onClick={onCompare}
              disabled={!canCompare}
              className={`
                flex items-center gap-2 px-6 py-2 rounded-lg text-sm font-semibold
                transition-all duration-200
                ${canCompare 
                  ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-md hover:shadow-lg' 
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }
              `}
            >
              <GitCompare className="w-4 h-4" />
              Compare
            </button>
          </div>
        </div>

        {/* Progress indicator */}
        {selectedOpportunities.length < maxSelection && (
          <div className="mt-3">
            <div className="w-full bg-gray-200 rounded-full h-1.5">
              <div
                className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${(selectedOpportunities.length / maxSelection) * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ComparisonPanel;
