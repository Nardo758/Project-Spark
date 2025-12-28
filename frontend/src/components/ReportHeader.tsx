import { Printer, Download, Mail } from 'lucide-react'

type ReportHeaderProps = {
  reportType: string
  reportTitle: string
  reportLocation?: string
  reportSubtitle?: string
  generatedAt: Date
  reportId: string
  onPrint?: () => void
  onDownload?: () => void
  onEmail?: () => void
  showActions?: boolean
}

export default function ReportHeader({
  reportType,
  reportTitle,
  reportLocation,
  reportSubtitle,
  generatedAt,
  reportId,
  onPrint,
  onDownload,
  onEmail,
  showActions = true
}: ReportHeaderProps) {
  const formatDateTime = (date: Date) => {
    const dateStr = date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
    const timeStr = date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
    return `${dateStr} at ${timeStr}`
  }

  return (
    <div className="report-header w-full font-sans">
      {/* Metadata Bar */}
      <div className="metadata-bar bg-stone-100 border-b border-stone-200 px-6 py-4 flex flex-wrap justify-between items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-stone-900 rounded-lg flex items-center justify-center flex-shrink-0">
            <span className="text-white font-bold text-base tracking-tight">OG</span>
          </div>
          <div className="flex flex-col">
            <div className="font-bold text-stone-900 text-base tracking-tight">OppGrid</div>
            <div className="text-xs text-stone-500 font-medium">The Opportunity Intelligence Platform</div>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex flex-col gap-0.5 items-end text-right">
            <div className="text-stone-600 text-sm">Generated: {formatDateTime(generatedAt)}</div>
            <div className="text-stone-500 text-xs font-medium">Report ID: {reportId}</div>
          </div>
          
          {showActions && (
            <div className="flex items-center gap-1.5 print:hidden">
              {onPrint && (
                <button
                  onClick={onPrint}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm text-stone-600 hover:text-stone-900 hover:bg-stone-200 rounded-lg transition-colors"
                  title="Print Report"
                >
                  <Printer className="w-4 h-4" />
                  Print
                </button>
              )}
              {onDownload && (
                <button
                  onClick={onDownload}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm text-stone-600 hover:text-stone-900 hover:bg-stone-200 rounded-lg transition-colors"
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
      </div>
      
      {/* Main Header */}
      <div className="main-header-content bg-white px-6 pt-8 pb-6 border-b-2 border-orange-400">
        <div className="text-xs font-semibold uppercase tracking-widest text-stone-400 mb-3">
          {reportType}
        </div>
        <h1 className="text-2xl md:text-3xl font-bold text-stone-900 mb-2 leading-tight">
          {reportTitle}
        </h1>
        {reportLocation && (
          <div className="text-lg md:text-xl font-medium text-orange-500 mb-3">
            {reportLocation}
          </div>
        )}
        {reportSubtitle && (
          <div className="text-sm text-stone-500">
            {reportSubtitle}
          </div>
        )}
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
    <div className="report-footer bg-stone-100 border-t border-stone-200 px-6 py-4 font-sans">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-stone-900 rounded-lg flex items-center justify-center flex-shrink-0">
            <span className="text-white font-bold text-xs tracking-tight">OG</span>
          </div>
          <div className="flex flex-col">
            <div className="font-bold text-stone-900 text-sm tracking-tight">OppGrid</div>
            <div className="text-xs text-stone-500 italic">Transform Market Signals into Business Opportunities</div>
          </div>
        </div>
        
        <div className="flex flex-wrap items-center gap-3 text-xs text-stone-500">
          <span>&copy; {currentYear} OppGrid</span>
          <span className="text-stone-300">|</span>
          <span>Confidential</span>
          <span className="text-stone-300">|</span>
          <span className="font-medium">{reportId}</span>
          {pageNumber && totalPages && (
            <>
              <span className="text-stone-300">|</span>
              <span>Page {pageNumber} of {totalPages}</span>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
