/**
 * Pagination Component
 * 
 * Handles page navigation for opportunity lists.
 * 
 * Features:
 * - Previous/Next buttons
 * - Page number display
 * - Jump to page
 * - Responsive design
 * - Keyboard navigation
 * 
 * @component
 */

import React from 'react';
import { PaginationState } from './types';

interface PaginationProps {
  pagination: PaginationState;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
  showPageSize?: boolean;
}

export const Pagination: React.FC<PaginationProps> = ({
  pagination,
  onPageChange,
  onPageSizeChange,
  showPageSize = false,
}) => {
  const { currentPage, totalPages, totalItems, pageSize } = pagination;

  const canGoPrevious = currentPage > 1;
  const canGoNext = currentPage < totalPages;

  const handlePrevious = () => {
    if (canGoPrevious) {
      onPageChange(currentPage - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleNext = () => {
    if (canGoNext) {
      onPageChange(currentPage + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handlePageJump = (page: number) => {
    if (page >= 1 && page <= totalPages && page !== currentPage) {
      onPageChange(page);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // Generate page numbers to display
  const getPageNumbers = (): (number | 'ellipsis')[] => {
    const pages: (number | 'ellipsis')[] = [];
    const maxVisible = 7;

    if (totalPages <= maxVisible) {
      // Show all pages
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Show first, last, current, and nearby pages
      pages.push(1);

      if (currentPage > 3) {
        pages.push('ellipsis');
      }

      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (currentPage < totalPages - 2) {
        pages.push('ellipsis');
      }

      pages.push(totalPages);
    }

    return pages;
  };

  const pageNumbers = getPageNumbers();

  if (totalPages <= 1) {
    return null; // Don't show pagination if there's only one page
  }

  return (
    <div className="pagination-container">
      <div className="flex items-center justify-between flex-wrap gap-4">
        {/* Results info */}
        <div className="text-sm text-stone-600">
          Showing <strong className="text-stone-900">{Math.min((currentPage - 1) * pageSize + 1, totalItems)}</strong>
          {' '}-{' '}
          <strong className="text-stone-900">{Math.min(currentPage * pageSize, totalItems)}</strong>
          {' '}of{' '}
          <strong className="text-stone-900">{totalItems}</strong> results
        </div>

        {/* Page controls */}
        <div className="flex items-center gap-2">
          {/* Previous button */}
          <button
            onClick={handlePrevious}
            disabled={!canGoPrevious}
            className={`pagination-btn ${!canGoPrevious ? 'disabled' : ''}`}
            aria-label="Previous page"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
            <span className="hidden sm:inline">Previous</span>
          </button>

          {/* Page numbers */}
          <div className="flex items-center gap-1">
            {pageNumbers.map((page, index) => {
              if (page === 'ellipsis') {
                return (
                  <span key={`ellipsis-${index}`} className="px-2 text-stone-400">
                    ...
                  </span>
                );
              }

              return (
                <button
                  key={page}
                  onClick={() => handlePageJump(page)}
                  className={`page-number ${page === currentPage ? 'active' : ''}`}
                  aria-label={`Go to page ${page}`}
                  aria-current={page === currentPage ? 'page' : undefined}
                >
                  {page}
                </button>
              );
            })}
          </div>

          {/* Next button */}
          <button
            onClick={handleNext}
            disabled={!canGoNext}
            className={`pagination-btn ${!canGoNext ? 'disabled' : ''}`}
            aria-label="Next page"
          >
            <span className="hidden sm:inline">Next</span>
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </button>
        </div>

        {/* Page size selector */}
        {showPageSize && onPageSizeChange && (
          <select
            value={pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
            className="px-3 py-2 border border-stone-200 rounded-lg text-sm bg-white focus:outline-none focus:border-stone-400"
          >
            <option value="10">10 per page</option>
            <option value="20">20 per page</option>
            <option value="50">50 per page</option>
            <option value="100">100 per page</option>
          </select>
        )}
      </div>

      {/* Styles */}
      <style jsx>{`
        .pagination-container {
          margin-top: 3rem;
          padding-top: 2rem;
          border-top: 1px solid #e7e5e4;
        }

        .pagination-btn {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          border: 2px solid #e7e5e4;
          border-radius: 0.5rem;
          font-size: 0.875rem;
          font-weight: 500;
          color: #44403c;
          background: white;
          cursor: pointer;
          transition: all 0.2s;
        }

        .pagination-btn:hover:not(.disabled) {
          border-color: #1c1917;
          background: #fafaf9;
        }

        .pagination-btn.disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        .page-number {
          min-width: 2.5rem;
          height: 2.5rem;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          border: 2px solid transparent;
          border-radius: 0.5rem;
          font-size: 0.875rem;
          font-weight: 500;
          color: #57534e;
          background: transparent;
          cursor: pointer;
          transition: all 0.2s;
        }

        .page-number:hover {
          background: #fafaf9;
          color: #1c1917;
        }

        .page-number.active {
          border-color: #1c1917;
          background: #1c1917;
          color: white;
        }

        @media (max-width: 640px) {
          .pagination-container > div {
            justify-content: center;
          }
        }
      `}</style>
    </div>
  );
};

export default Pagination;
