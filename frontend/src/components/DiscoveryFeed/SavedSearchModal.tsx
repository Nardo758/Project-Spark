import React, { useState } from 'react';
import { X, Save, Mail, Bell, MessageSquare, Check } from 'lucide-react';

interface NotificationPreferences {
  email: boolean;
  emailFrequency?: 'instant' | 'daily';
  push: boolean;
  slack: boolean;
}

interface SavedSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (name: string, notificationPrefs: NotificationPreferences) => Promise<void>;
  currentFilters?: Record<string, any>;
  suggestedName?: string;
}

export const SavedSearchModal: React.FC<SavedSearchModalProps> = ({
  isOpen,
  onClose,
  onSave,
  currentFilters = {},
  suggestedName = ''
}) => {
  const [searchName, setSearchName] = useState(suggestedName);
  const [notificationPrefs, setNotificationPrefs] = useState<NotificationPreferences>({
    email: false,
    emailFrequency: 'daily',
    push: false,
    slack: false
  });
  const [isSaving, setIsSaving] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSave = async () => {
    if (!searchName.trim()) {
      setError('Please enter a name for this search');
      return;
    }

    try {
      setIsSaving(true);
      setError('');
      await onSave(searchName.trim(), notificationPrefs);
      
      // Show success message
      setShowSuccess(true);
      setTimeout(() => {
        setShowSuccess(false);
        onClose();
        // Reset form
        setSearchName('');
        setNotificationPrefs({
          email: false,
          emailFrequency: 'daily',
          push: false,
          slack: false
        });
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save search');
    } finally {
      setIsSaving(false);
    }
  };

  const handleClose = () => {
    if (!isSaving) {
      onClose();
      setError('');
      setShowSuccess(false);
    }
  };

  const toggleNotification = (type: keyof NotificationPreferences) => {
    setNotificationPrefs(prev => ({
      ...prev,
      [type]: !prev[type]
    }));
  };

  const setEmailFrequency = (frequency: 'instant' | 'daily') => {
    setNotificationPrefs(prev => ({
      ...prev,
      emailFrequency: frequency
    }));
  };

  // Generate filter summary
  const getFilterSummary = () => {
    const filters = [];
    if (currentFilters.category) filters.push(`Category: ${currentFilters.category}`);
    if (currentFilters.feasibility) filters.push(`Feasibility: ${currentFilters.feasibility}`);
    if (currentFilters.location) filters.push(`Location: ${currentFilters.location}`);
    if (currentFilters.search) filters.push(`Search: "${currentFilters.search}"`);
    return filters.length > 0 ? filters.join(' • ') : 'No filters applied';
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4 animate-fade-in">
      <div className="bg-white rounded-xl shadow-2xl max-w-md w-full overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-purple-600 to-blue-600 text-white">
          <div className="flex items-center gap-3">
            <Save className="w-6 h-6" />
            <h2 className="text-xl font-bold">Save This Search</h2>
          </div>
          <button
            onClick={handleClose}
            disabled={isSaving}
            className="hover:bg-purple-700 rounded-full p-2 transition-colors disabled:opacity-50"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Success Message */}
        {showSuccess && (
          <div className="bg-green-50 border-b border-green-200 px-6 py-4">
            <div className="flex items-center gap-3 text-green-800">
              <Check className="w-5 h-5" />
              <p className="font-semibold">Search saved successfully!</p>
            </div>
          </div>
        )}

        {/* Content */}
        <div className="px-6 py-6 space-y-6">
          {/* Current Filters Summary */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm font-semibold text-blue-900 mb-2">Current Filters:</p>
            <p className="text-sm text-blue-700">{getFilterSummary()}</p>
          </div>

          {/* Search Name Input */}
          <div>
            <label htmlFor="searchName" className="block text-sm font-semibold text-gray-700 mb-2">
              Search Name <span className="text-red-500">*</span>
            </label>
            <input
              id="searchName"
              type="text"
              value={searchName}
              onChange={(e) => setSearchName(e.target.value)}
              placeholder="e.g., High-Potential Tech Opportunities"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 
                         focus:ring-blue-500 focus:border-blue-500 outline-none"
              disabled={isSaving}
            />
            {error && (
              <p className="text-sm text-red-600 mt-1">{error}</p>
            )}
          </div>

          {/* Notification Preferences */}
          <div>
            <p className="text-sm font-semibold text-gray-700 mb-3">
              Notify me when new opportunities match:
            </p>

            <div className="space-y-3">
              {/* Email Notification */}
              <div className="border border-gray-200 rounded-lg p-4">
                <label className="flex items-start gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={notificationPrefs.email}
                    onChange={() => toggleNotification('email')}
                    className="mt-1 w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    disabled={isSaving}
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Mail className="w-4 h-4 text-gray-600" />
                      <span className="font-medium text-gray-900">Email</span>
                    </div>
                    
                    {notificationPrefs.email && (
                      <div className="mt-2 ml-1 space-x-3">
                        <label className="inline-flex items-center">
                          <input
                            type="radio"
                            name="emailFrequency"
                            checked={notificationPrefs.emailFrequency === 'daily'}
                            onChange={() => setEmailFrequency('daily')}
                            className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                            disabled={isSaving}
                          />
                          <span className="ml-2 text-sm text-gray-700">Daily digest</span>
                        </label>
                        <label className="inline-flex items-center">
                          <input
                            type="radio"
                            name="emailFrequency"
                            checked={notificationPrefs.emailFrequency === 'instant'}
                            onChange={() => setEmailFrequency('instant')}
                            className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                            disabled={isSaving}
                          />
                          <span className="ml-2 text-sm text-gray-700">Instant</span>
                        </label>
                      </div>
                    )}
                  </div>
                </label>
              </div>

              {/* Push Notification */}
              <label className="flex items-start gap-3 cursor-pointer border border-gray-200 rounded-lg p-4">
                <input
                  type="checkbox"
                  checked={notificationPrefs.push}
                  onChange={() => toggleNotification('push')}
                  className="mt-1 w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  disabled={isSaving}
                />
                <div className="flex items-center gap-2">
                  <Bell className="w-4 h-4 text-gray-600" />
                  <span className="font-medium text-gray-900">Push Notification</span>
                  <span className="text-xs text-gray-500">(Instant)</span>
                </div>
              </label>

              {/* Slack Notification */}
              <label className="flex items-start gap-3 cursor-pointer border border-gray-200 rounded-lg p-4">
                <input
                  type="checkbox"
                  checked={notificationPrefs.slack}
                  onChange={() => toggleNotification('slack')}
                  className="mt-1 w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  disabled={isSaving}
                />
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-gray-600" />
                  <span className="font-medium text-gray-900">Slack Message</span>
                  {!notificationPrefs.slack && (
                    <span className="text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full">
                      Premium
                    </span>
                  )}
                </div>
              </label>
            </div>

            {!notificationPrefs.email && !notificationPrefs.push && !notificationPrefs.slack && (
              <p className="text-sm text-amber-600 mt-3 flex items-center gap-2">
                <Bell className="w-4 h-4" />
                Select at least one notification method to stay updated
              </p>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-200 bg-gray-50">
          <button
            onClick={handleClose}
            disabled={isSaving}
            className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 
                       rounded-lg transition-colors disabled:opacity-50"
          >
            Cancel
          </button>

          <button
            onClick={handleSave}
            disabled={isSaving || !searchName.trim()}
            className="flex items-center gap-2 px-6 py-2 text-sm font-semibold bg-blue-600 
                       text-white hover:bg-blue-700 rounded-lg transition-colors
                       disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Save Search
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SavedSearchModal;
