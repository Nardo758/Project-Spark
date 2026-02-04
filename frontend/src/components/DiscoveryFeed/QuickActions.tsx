import React, { useState } from 'react';
import ReactConfetti from 'react-confetti';
import { useWindowSize } from '@/hooks/useWindowSize';
import { 
  CheckCircle, 
  Bookmark, 
  Brain, 
  Share2,
  Loader2 
} from 'lucide-react';

interface QuickActionsProps {
  opportunityId: string;
  userValidated?: boolean;
  onValidate?: (id: string) => Promise<void>;
  onSave?: (id: string) => Promise<void>;
  onAnalyze?: (id: string) => void;
  onShare?: (id: string) => void;
  isSaved?: boolean;
}

export const QuickActions: React.FC<QuickActionsProps> = ({
  opportunityId,
  userValidated = false,
  onValidate,
  onSave,
  onAnalyze,
  onShare,
  isSaved = false
}) => {
  const [isValidating, setIsValidating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showConfetti, setShowConfetti] = useState(false);
  const [validated, setValidated] = useState(userValidated);
  const [saved, setSaved] = useState(isSaved);
  const { width, height } = useWindowSize();

  const handleValidate = async () => {
    if (validated || !onValidate) return;
    
    try {
      setIsValidating(true);
      await onValidate(opportunityId);
      setValidated(true);
      
      // Trigger confetti animation
      setShowConfetti(true);
      setTimeout(() => setShowConfetti(false), 3000);
    } catch (error) {
      console.error('Validation failed:', error);
    } finally {
      setIsValidating(false);
    }
  };

  const handleSave = async () => {
    if (!onSave) return;
    
    try {
      setIsSaving(true);
      await onSave(opportunityId);
      setSaved(!saved);
    } catch (error) {
      console.error('Save failed:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleAnalyze = () => {
    if (onAnalyze) {
      onAnalyze(opportunityId);
    }
  };

  const handleShare = () => {
    if (onShare) {
      onShare(opportunityId);
    }
  };

  return (
    <>
      {showConfetti && (
        <ReactConfetti
          width={width}
          height={height}
          recycle={false}
          numberOfPieces={200}
          gravity={0.3}
        />
      )}
      
      <div className="quick-actions flex gap-2 p-3 border-t border-gray-200 bg-gray-50">
        {/* Validate Button */}
        <button
          onClick={handleValidate}
          disabled={validated || isValidating}
          className={`
            flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg
            text-sm font-medium transition-all duration-200
            ${validated 
              ? 'bg-green-500 text-white cursor-not-allowed' 
              : 'bg-white border-2 border-green-500 text-green-600 hover:bg-green-50'
            }
          `}
        >
          {isValidating ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <CheckCircle className="w-4 h-4" />
          )}
          <span>{validated ? 'Validated' : 'Validate'}</span>
        </button>

        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={isSaving}
          className={`
            flex items-center justify-center gap-2 px-4 py-2 rounded-lg
            text-sm font-medium transition-all duration-200
            ${saved 
              ? 'bg-blue-500 text-white' 
              : 'bg-white border-2 border-gray-300 text-gray-700 hover:bg-gray-50'
            }
          `}
          title={saved ? 'Saved' : 'Save'}
        >
          {isSaving ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Bookmark className={`w-4 h-4 ${saved ? 'fill-current' : ''}`} />
          )}
        </button>

        {/* Analyze Button */}
        <button
          onClick={handleAnalyze}
          className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg
                     text-sm font-medium bg-white border-2 border-gray-300 text-gray-700 
                     hover:bg-gray-50 transition-all duration-200"
          title="Analyze"
        >
          <Brain className="w-4 h-4" />
        </button>

        {/* Share Button */}
        <button
          onClick={handleShare}
          className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg
                     text-sm font-medium bg-white border-2 border-gray-300 text-gray-700 
                     hover:bg-gray-50 transition-all duration-200"
          title="Share"
        >
          <Share2 className="w-4 h-4" />
        </button>
      </div>
    </>
  );
};

export default QuickActions;
