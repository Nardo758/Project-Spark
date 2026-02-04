import React from 'react';
import { X, TrendingUp, CheckCircle, Target, DollarSign, MapPin, Clock, Trophy } from 'lucide-react';

interface OpportunityMetrics {
  id: string;
  title: string;
  description: string;
  category: string;
  feasibilityScore: number;
  validationCount: number;
  growthRate: number;
  marketSize: string;
  geographicScope: string;
  ageInDays: number;
}

interface ComparisonModalProps {
  opportunities: OpportunityMetrics[];
  isOpen: boolean;
  onClose: () => void;
  onViewDetails?: (id: string) => void;
  onExportPDF?: () => void;
}

export const ComparisonModal: React.FC<ComparisonModalProps> = ({
  opportunities,
  isOpen,
  onClose,
  onViewDetails,
  onExportPDF
}) => {
  if (!isOpen) return null;

  // Determine winner (highest overall score)
  const calculateScore = (opp: OpportunityMetrics) => {
    return (opp.feasibilityScore * 0.5) + 
           (Math.min(opp.validationCount / 10, 50) * 0.3) + 
           (Math.min(opp.growthRate * 2, 50) * 0.2);
  };

  const winnerIndex = opportunities.reduce((maxIdx, opp, idx, arr) => 
    calculateScore(opp) > calculateScore(arr[maxIdx]) ? idx : maxIdx, 0
  );

  const MetricRow = ({ label, icon: Icon, values }: { 
    label: string; 
    icon: React.ElementType; 
    values: (string | number)[] 
  }) => (
    <div className="border-b border-gray-200 last:border-0">
      <div className="flex items-center gap-2 px-4 py-3 bg-gray-50 font-semibold text-gray-700">
        <Icon className="w-4 h-4" />
        {label}
      </div>
      <div className="grid grid-cols-3 divide-x divide-gray-200">
        {values.map((value, idx) => {
          const isWinner = idx === winnerIndex;
          return (
            <div
              key={idx}
              className={`px-4 py-4 text-center ${isWinner ? 'bg-green-50' : 'bg-white'}`}
            >
              <span className={`text-lg font-bold ${isWinner ? 'text-green-700' : 'text-gray-900'}`}>
                {value}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4 animate-fade-in">
      <div className="bg-white rounded-xl shadow-2xl max-w-7xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-blue-700 text-white">
          <div className="flex items-center gap-3">
            <Trophy className="w-6 h-6" />
            <h2 className="text-2xl font-bold">Opportunity Comparison</h2>
          </div>
          <button
            onClick={onClose}
            className="hover:bg-blue-800 rounded-full p-2 transition-colors"
            aria-label="Close modal"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto">
          {/* Opportunity Titles */}
          <div className="grid grid-cols-3 divide-x divide-gray-300 bg-gray-100 sticky top-0 z-10">
            {opportunities.map((opp, idx) => (
              <div
                key={opp.id}
                className={`px-6 py-4 ${idx === winnerIndex ? 'bg-green-100' : ''}`}
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <h3 className="font-bold text-lg text-gray-900 line-clamp-2">
                    {opp.title}
                  </h3>
                  {idx === winnerIndex && (
                    <Trophy className="w-5 h-5 text-yellow-500 flex-shrink-0" />
                  )}
                </div>
                <p className="text-sm text-gray-600 line-clamp-2">{opp.description}</p>
                <div className="mt-2">
                  <span className="inline-block px-2 py-1 text-xs font-semibold bg-blue-100 text-blue-700 rounded">
                    {opp.category}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Metrics Comparison */}
          <div className="divide-y divide-gray-200">
            <MetricRow
              label="Feasibility Score"
              icon={Target}
              values={opportunities.map(opp => opp.feasibilityScore)}
            />

            <MetricRow
              label="Validations"
              icon={CheckCircle}
              values={opportunities.map(opp => opp.validationCount)}
            />

            <MetricRow
              label="Growth Rate (7d)"
              icon={TrendingUp}
              values={opportunities.map(opp => `+${opp.growthRate}%`)}
            />

            <MetricRow
              label="Market Size"
              icon={DollarSign}
              values={opportunities.map(opp => opp.marketSize)}
            />

            <MetricRow
              label="Geographic Scope"
              icon={MapPin}
              values={opportunities.map(opp => opp.geographicScope)}
            />

            <MetricRow
              label="Age (Days)"
              icon={Clock}
              values={opportunities.map(opp => opp.ageInDays)}
            />
          </div>

          {/* Winner Banner */}
          <div className="bg-gradient-to-r from-yellow-50 to-green-50 border-t-2 border-yellow-400 px-6 py-4">
            <div className="flex items-center gap-3">
              <Trophy className="w-6 h-6 text-yellow-600" />
              <div>
                <p className="font-bold text-green-800 text-lg">
                  Highest Overall Score: {opportunities[winnerIndex].title}
                </p>
                <p className="text-sm text-gray-600">
                  Based on weighted analysis of feasibility, validations, and growth rate
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 
                       rounded-lg transition-colors"
          >
            Close
          </button>

          <div className="flex gap-3">
            {onExportPDF && (
              <button
                onClick={onExportPDF}
                className="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 
                           hover:bg-gray-100 rounded-lg transition-colors"
              >
                Export as PDF
              </button>
            )}

            <div className="flex gap-2">
              {opportunities.map((opp) => (
                <button
                  key={opp.id}
                  onClick={() => onViewDetails && onViewDetails(opp.id)}
                  className="px-4 py-2 text-sm font-medium bg-blue-600 text-white 
                             hover:bg-blue-700 rounded-lg transition-colors"
                >
                  View #{opportunities.indexOf(opp) + 1}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComparisonModal;
