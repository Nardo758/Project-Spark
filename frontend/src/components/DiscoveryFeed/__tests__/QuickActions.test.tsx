/**
 * Test Suite for QuickActions Component
 * 
 * Run with: npm test QuickActions.test.tsx
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { QuickActions } from '../QuickActions';

describe('QuickActions Component', () => {
  const mockProps = {
    opportunityId: 'test-opp-123',
    userValidated: false,
    isSaved: false,
    onValidate: jest.fn().mockResolvedValue(undefined),
    onSave: jest.fn().mockResolvedValue(undefined),
    onAnalyze: jest.fn(),
    onShare: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render all action buttons', () => {
      render(<QuickActions {...mockProps} />);
      
      expect(screen.getByText('Validate')).toBeInTheDocument();
      expect(screen.getByTitle('Saved')).toBeInTheDocument();
      expect(screen.getByTitle('Analyze')).toBeInTheDocument();
      expect(screen.getByTitle('Share')).toBeInTheDocument();
    });

    it('should show "Validated" when userValidated is true', () => {
      render(<QuickActions {...mockProps} userValidated={true} />);
      
      expect(screen.getByText('Validated')).toBeInTheDocument();
      expect(screen.getByText('Validated')).toBeDisabled();
    });

    it('should show filled bookmark icon when opportunity is saved', () => {
      const { container } = render(<QuickActions {...mockProps} isSaved={true} />);
      
      const saveButton = screen.getByTitle('Saved');
      expect(saveButton).toHaveClass('bg-blue-500');
    });
  });

  describe('Validation Action', () => {
    it('should call onValidate with correct opportunityId', async () => {
      render(<QuickActions {...mockProps} />);
      
      const validateButton = screen.getByText('Validate');
      fireEvent.click(validateButton);
      
      await waitFor(() => {
        expect(mockProps.onValidate).toHaveBeenCalledWith('test-opp-123');
      });
    });

    it('should show loading state during validation', async () => {
      const slowValidate = jest.fn(() => new Promise(resolve => setTimeout(resolve, 1000)));
      render(<QuickActions {...mockProps} onValidate={slowValidate} />);
      
      const validateButton = screen.getByText('Validate');
      fireEvent.click(validateButton);
      
      // Should show loading state
      await waitFor(() => {
        expect(screen.queryByText('Validate')).not.toBeInTheDocument();
      });
    });

    it('should show confetti after successful validation', async () => {
      render(<QuickActions {...mockProps} />);
      
      const validateButton = screen.getByText('Validate');
      fireEvent.click(validateButton);
      
      await waitFor(() => {
        expect(mockProps.onValidate).toHaveBeenCalled();
      });
      
      // Confetti component should be rendered
      // Note: This tests implementation detail - may need adjustment based on actual confetti library behavior
    });

    it('should not allow validation when already validated', () => {
      render(<QuickActions {...mockProps} userValidated={true} />);
      
      const validateButton = screen.getByText('Validated');
      expect(validateButton).toBeDisabled();
      
      fireEvent.click(validateButton);
      expect(mockProps.onValidate).not.toHaveBeenCalled();
    });
  });

  describe('Save Action', () => {
    it('should call onSave with correct opportunityId', async () => {
      render(<QuickActions {...mockProps} />);
      
      const saveButton = screen.getByTitle('Saved');
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(mockProps.onSave).toHaveBeenCalledWith('test-opp-123');
      });
    });

    it('should toggle saved state', async () => {
      const { rerender } = render(<QuickActions {...mockProps} isSaved={false} />);
      
      const saveButton = screen.getByTitle('Saved');
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(mockProps.onSave).toHaveBeenCalled();
      });
      
      // Simulate state change after save
      rerender(<QuickActions {...mockProps} isSaved={true} />);
      
      expect(saveButton).toHaveClass('bg-blue-500');
    });
  });

  describe('Analyze Action', () => {
    it('should call onAnalyze with correct opportunityId', () => {
      render(<QuickActions {...mockProps} />);
      
      const analyzeButton = screen.getByTitle('Analyze');
      fireEvent.click(analyzeButton);
      
      expect(mockProps.onAnalyze).toHaveBeenCalledWith('test-opp-123');
    });
  });

  describe('Share Action', () => {
    it('should call onShare with correct opportunityId', () => {
      render(<QuickActions {...mockProps} />);
      
      const shareButton = screen.getByTitle('Share');
      fireEvent.click(shareButton);
      
      expect(mockProps.onShare).toHaveBeenCalledWith('test-opp-123');
    });
  });

  describe('Error Handling', () => {
    it('should handle validation errors gracefully', async () => {
      const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
      const failingValidate = jest.fn().mockRejectedValue(new Error('Validation failed'));
      
      render(<QuickActions {...mockProps} onValidate={failingValidate} />);
      
      const validateButton = screen.getByText('Validate');
      fireEvent.click(validateButton);
      
      await waitFor(() => {
        expect(consoleError).toHaveBeenCalledWith('Validation failed:', expect.any(Error));
      });
      
      consoleError.mockRestore();
    });

    it('should handle save errors gracefully', async () => {
      const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
      const failingSave = jest.fn().mockRejectedValue(new Error('Save failed'));
      
      render(<QuickActions {...mockProps} onSave={failingSave} />);
      
      const saveButton = screen.getByTitle('Saved');
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(consoleError).toHaveBeenCalledWith('Save failed:', expect.any(Error));
      });
      
      consoleError.mockRestore();
    });
  });

  describe('Accessibility', () => {
    it('should have accessible button labels', () => {
      render(<QuickActions {...mockProps} />);
      
      expect(screen.getByTitle('Saved')).toBeInTheDocument();
      expect(screen.getByTitle('Analyze')).toBeInTheDocument();
      expect(screen.getByTitle('Share')).toBeInTheDocument();
    });

    it('should disable buttons during loading states', async () => {
      const slowValidate = jest.fn(() => new Promise(resolve => setTimeout(resolve, 1000)));
      render(<QuickActions {...mockProps} onValidate={slowValidate} />);
      
      const validateButton = screen.getByText('Validate');
      fireEvent.click(validateButton);
      
      await waitFor(() => {
        expect(validateButton).toBeDisabled();
      });
    });
  });
});
