import { Printer, Download, Mail } from 'lucide-react'

type ReportHeaderProps = {
  reportTitle: string
  reportType: string
  projectName: string
  generatedAt: Date
  reportId: string
  userName?: string
  onPrint?: () => void
  onDownload?: () => void
  onEmail?: () => void
  showActions?: boolean
}

export default function ReportHeader({
  reportTitle,
  reportType,
  projectName,
  generatedAt,
  reportId,
  userName,
  onPrint,
  onDownload,
  onEmail,
  showActions = true
}: ReportHeaderProps) {
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="report-header bg-white border-b border-gray-200 print:border-black">
      <div className="px-6 py-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-black rounded-lg flex items-center justify-center print:bg-black">
                <span className="text-white font-bold text-sm">OG</span>
              </div>
              <div>
                <div className="font-bold text-gray-900 text-lg">OppGrid</div>
                <div className="text-xs text-gray-500">Opportunity Intelligence Platform</div>
              </div>
            </div>
          </div>
          
          {showActions && (
            <div className="flex items-center gap-2 print:hidden">
              {onPrint && (
                <button
                  onClick={onPrint}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Print Report"
                >
                  <Printer className="w-4 h-4" />
                  Print
                </button>
              )}
              {onDownload && (
                <button
                  onClick={onDownload}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Download PDF"
                >
                  <Download className="w-4 h-4" />
                  PDF
                </button>
              )}
              {onEmail && (
                <button
                  onClick={onEmail}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm bg-purple-600 text-white hover:bg-purple-700 rounded-lg transition-colors"
                  title="Send to Email"
                >
                  <Mail className="w-4 h-4" />
                  Email
                </button>
              )}
            </div>
          )}
        </div>
        
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="flex items-end justify-between">
            <div>
              <div className="text-xs font-medium text-purple-600 uppercase tracking-wide">{reportType}</div>
              <h1 className="text-xl font-bold text-gray-900 mt-1">{reportTitle}</h1>
              <div className="text-sm text-gray-600 mt-1">{projectName}</div>
            </div>
            <div className="text-right text-sm">
              <div className="text-gray-500">
                <span className="font-medium text-gray-700">Generated:</span> {formatDate(generatedAt)} at {formatTime(generatedAt)}
              </div>
              <div className="text-gray-400 text-xs mt-1">Report ID: {reportId}</div>
              {userName && <div className="text-gray-400 text-xs">Prepared for: {userName}</div>}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

type ReportFooterProps = {
  reportId: string
  pageNumber?: number
  totalPages?: number
}

export function ReportFooter({ reportId, pageNumber, totalPages }: ReportFooterProps) {
  const currentYear = new Date().getFullYear()
  
  return (
    <div className="report-footer bg-gray-50 border-t border-gray-200 px-6 py-3 print:bg-white print:border-gray-300">
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <span>&copy; {currentYear} OppGrid. All rights reserved.</span>
          <span className="text-gray-300">|</span>
          <span>Confidential Business Intelligence</span>
        </div>
        <div className="flex items-center gap-4">
          <span>Report ID: {reportId}</span>
          {pageNumber && totalPages && (
            <>
              <span className="text-gray-300">|</span>
              <span>Page {pageNumber} of {totalPages}</span>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
