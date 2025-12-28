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
    <div className="report-header w-full">
      {/* Metadata Bar */}
      <div className="bg-stone-100 border-b border-stone-200 px-8 md:px-12 py-4 flex justify-between items-center print:bg-gray-100">
        <div className="flex items-center gap-3.5">
          <div 
            className="w-11 h-11 bg-stone-900 rounded-lg flex items-center justify-center shadow-sm print:bg-black"
            style={{ boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)' }}
          >
            <span className="text-white font-bold text-lg tracking-tight">OG</span>
          </div>
          <div className="flex flex-col gap-0.5">
            <div className="font-bold text-stone-900 text-[17px] tracking-tight">OppGrid</div>
            <div className="text-xs text-stone-500 font-medium">The Opportunity Intelligence Platform</div>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="flex flex-col gap-1 items-end text-right">
            <div className="text-stone-500 text-[13px]">Generated: {formatDateTime(generatedAt)}</div>
            <div className="text-stone-500 text-xs font-medium tracking-wide">Report ID: {reportId}</div>
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
      <div 
        className="bg-white px-8 md:px-12 pt-10 pb-8"
        style={{ borderBottom: '2px solid #E87F5C' }}
      >
        <div 
          className="text-[13px] font-semibold uppercase tracking-[1.5px] text-stone-400 mb-4"
          style={{ fontFamily: 'Inter, sans-serif' }}
        >
          {reportType}
        </div>
        <h1 
          className="text-4xl font-semibold text-stone-900 mb-3 leading-tight"
          style={{ fontFamily: 'Spectral, serif' }}
        >
          {reportTitle}
        </h1>
        {reportLocation && (
          <div 
            className="text-[22px] font-normal mb-4 leading-snug"
            style={{ fontFamily: 'Spectral, serif', color: '#E87F5C' }}
          >
            {reportLocation}
          </div>
        )}
        {reportSubtitle && (
          <div 
            className="text-sm text-stone-500 leading-relaxed"
            style={{ fontFamily: 'Inter, sans-serif' }}
          >
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
    <div className="report-footer bg-stone-100 border-t border-stone-200 px-8 md:px-12 py-5 print:bg-gray-100">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          <div 
            className="w-9 h-9 bg-stone-900 rounded-lg flex items-center justify-center shadow-sm print:bg-black"
            style={{ boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)' }}
          >
            <span className="text-white font-bold text-sm tracking-tight">OG</span>
          </div>
          <div className="flex flex-col gap-0.5">
            <div className="font-bold text-stone-900 text-sm tracking-tight">OppGrid</div>
            <div className="text-xs text-stone-500 italic">Transform Market Signals into Business Opportunities</div>
          </div>
        </div>
        
        <div className="flex items-center gap-4 text-xs text-stone-500">
          <span>&copy; {currentYear} OppGrid. All rights reserved.</span>
          <span className="text-stone-300">|</span>
          <span>Confidential Business Intelligence</span>
          <span className="text-stone-300">|</span>
          <span className="font-medium">Report ID: {reportId}</span>
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
