import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { X, Download, FileText, Lock, Loader2, CheckCircle } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

type ReportLayer = 'layer1' | 'layer2' | 'layer3'

type GeneratedReport = {
  id: number
  opportunity_id: number
  report_type: string
  content: string
  created_at: string
}

type ReportViewerProps = {
  opportunityId: number
  opportunityTitle: string
  userTier: string
  isOpen: boolean
  onClose: () => void
  initialLayer?: ReportLayer
  hasUnlockedAccess?: boolean
}

const layerConfig = {
  layer1: {
    title: 'Problem Overview',
    description: 'Executive summary, problem analysis, market snapshot, and validation signals',
    tier: 'Pro',
    price: '$15 one-time or Pro subscription',
    color: 'violet',
  },
  layer2: {
    title: 'Deep Dive Analysis',
    description: 'TAM/SAM/SOM analysis, demographics, competitive landscape, and geographic insights',
    tier: 'Business',
    price: 'Business subscription required',
    color: 'blue',
  },
  layer3: {
    title: 'Execution Package',
    description: 'Full business plan, go-to-market strategy, financial projections, and 90-day roadmap',
    tier: 'Business/Enterprise',
    price: 'Business (5/month) or Enterprise (unlimited)',
    color: 'emerald',
  },
}

export default function ReportViewer({ 
  opportunityId, 
  opportunityTitle, 
  userTier, 
  isOpen, 
  onClose,
  initialLayer = 'layer1',
  hasUnlockedAccess = false
}: ReportViewerProps) {
  const { token } = useAuthStore()
  const [selectedLayer, setSelectedLayer] = useState<ReportLayer>(initialLayer)
  const [generatedReport, setGeneratedReport] = useState<GeneratedReport | null>(null)
  const [error, setError] = useState<string | null>(null)

  const tierLevel = (tier: string): number => {
    const levels: Record<string, number> = { free: 0, pro: 1, business: 2, enterprise: 3 }
    return levels[tier.toLowerCase()] ?? 0
  }

  const canAccessLayer = (layer: ReportLayer): boolean => {
    const userLevel = tierLevel(userTier)
    if (layer === 'layer1') return userLevel >= 1 || hasUnlockedAccess
    if (layer === 'layer2') return userLevel >= 2
    if (layer === 'layer3') return userLevel >= 2
    return false
  }

  const generateMutation = useMutation({
    mutationFn: async (layer: ReportLayer) => {
      const res = await fetch(`/api/v1/reports/opportunity/${opportunityId}/${layer}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}` 
        },
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail?.message || data.detail || 'Failed to generate report')
      }
      const report = data.report
      return {
        id: report.id,
        opportunity_id: opportunityId,
        report_type: layer,
        content: report.content,
        created_at: report.created_at,
      } as GeneratedReport
    },
    onSuccess: (data) => {
      setGeneratedReport(data)
      setError(null)
    },
    onError: (err: Error) => {
      setError(err.message)
      setGeneratedReport(null)
    },
  })

  const existingReportQuery = useQuery({
    queryKey: ['report', opportunityId, selectedLayer],
    enabled: isOpen && canAccessLayer(selectedLayer),
    queryFn: async () => {
      const reportTypeMap: Record<ReportLayer, string> = {
        layer1: 'LAYER_1_OVERVIEW',
        layer2: 'LAYER_2_DEEP_DIVE',
        layer3: 'LAYER_3_EXECUTION',
      }
      const res = await fetch(`/api/v1/reports/?opportunity_id=${opportunityId}&report_type=${reportTypeMap[selectedLayer]}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) return null
      const data = await res.json()
      return data.reports?.length > 0 ? data.reports[0] : null
    },
  })

  const handleGenerate = () => {
    setError(null)
    generateMutation.mutate(selectedLayer)
  }

  const handleDownloadPDF = () => {
    const reportContent = generatedReport?.content || existingReportQuery.data?.content
    if (!reportContent) return

    const printWindow = window.open('', '_blank')
    if (printWindow) {
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>${opportunityTitle} - ${layerConfig[selectedLayer].title}</title>
          <style>
            body { font-family: system-ui, -apple-system, sans-serif; padding: 40px; max-width: 900px; margin: 0 auto; }
            h1, h2, h3 { color: #1a1a1a; }
            h1 { border-bottom: 2px solid #7c3aed; padding-bottom: 10px; }
            h2 { color: #7c3aed; margin-top: 30px; }
            p { line-height: 1.6; color: #374151; }
            ul, ol { color: #374151; }
            .section { margin-bottom: 30px; }
            @media print { body { padding: 20px; } }
          </style>
        </head>
        <body>
          ${reportContent}
        </body>
        </html>
      `)
      printWindow.document.close()
      printWindow.print()
    }
  }

  if (!isOpen) return null

  const config = layerConfig[selectedLayer]
  const hasAccess = canAccessLayer(selectedLayer)
  const existingReport = existingReportQuery.data
  const displayReport = generatedReport || existingReport

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between p-6 border-b border-stone-200">
          <div>
            <h2 className="text-xl font-bold text-stone-900">Generate Report</h2>
            <p className="text-sm text-stone-500">{opportunityTitle}</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-stone-100 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex border-b border-stone-200">
          {(['layer1', 'layer2', 'layer3'] as ReportLayer[]).map((layer) => {
            const cfg = layerConfig[layer]
            const hasLayerAccess = canAccessLayer(layer)
            return (
              <button
                key={layer}
                onClick={() => {
                  setSelectedLayer(layer)
                  setGeneratedReport(null)
                  setError(null)
                }}
                className={`flex-1 py-4 px-6 text-sm font-medium transition-all relative ${
                  selectedLayer === layer 
                    ? `text-${cfg.color}-600 border-b-2 border-${cfg.color}-600 bg-${cfg.color}-50` 
                    : 'text-stone-600 hover:bg-stone-50'
                }`}
              >
                <div className="flex items-center justify-center gap-2">
                  {!hasLayerAccess && <Lock className="w-4 h-4" />}
                  <span>{cfg.title}</span>
                </div>
                <div className="text-xs text-stone-400 mt-1">{cfg.tier}</div>
              </button>
            )
          })}
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {!hasAccess ? (
            <div className="text-center py-12">
              <Lock className="w-16 h-16 text-stone-300 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-stone-900 mb-2">Upgrade Required</h3>
              <p className="text-stone-600 mb-4">{config.description}</p>
              <p className="text-sm text-stone-500 mb-6">{config.price}</p>
              <a 
                href="/pricing" 
                className={`inline-flex items-center gap-2 bg-${config.color}-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-${config.color}-700`}
              >
                Upgrade to {config.tier}
              </a>
            </div>
          ) : displayReport ? (
            <div>
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2 text-emerald-600">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-medium">Report Ready</span>
                </div>
                <button 
                  onClick={handleDownloadPDF}
                  className="flex items-center gap-2 bg-stone-900 text-white px-4 py-2 rounded-lg font-medium hover:bg-stone-800"
                >
                  <Download className="w-4 h-4" />
                  Download PDF
                </button>
              </div>
              <div 
                className="prose prose-stone max-w-none bg-stone-50 rounded-xl p-8 border border-stone-200"
                dangerouslySetInnerHTML={{ __html: displayReport.content }}
              />
            </div>
          ) : (
            <div className="text-center py-12">
              <FileText className="w-16 h-16 text-stone-300 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-stone-900 mb-2">{config.title}</h3>
              <p className="text-stone-600 mb-6 max-w-md mx-auto">{config.description}</p>
              
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 max-w-md mx-auto">
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              )}

              <button 
                onClick={handleGenerate}
                disabled={generateMutation.isPending}
                className={`inline-flex items-center gap-2 bg-${config.color}-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-${config.color}-700 disabled:opacity-50`}
              >
                {generateMutation.isPending ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <FileText className="w-5 h-5" />
                    Generate {config.title}
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
