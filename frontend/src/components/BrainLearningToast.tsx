import { useEffect, useState } from 'react'
import { Brain } from 'lucide-react'
import { useBrainStore } from '../stores/brainStore'

export default function BrainLearningToast() {
  const message = useBrainStore((s) => s.lastLearningMessage)
  const dismiss = useBrainStore((s) => s.dismissLearningMessage)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (!message) return
    setVisible(true)
    const id = window.setTimeout(() => {
      setVisible(false)
      window.setTimeout(() => dismiss(), 300)
    }, 2800)
    return () => window.clearTimeout(id)
  }, [message, dismiss])

  if (!message) return null

  return (
    <div
      className={`fixed bottom-6 right-6 z-50 max-w-sm transition-all ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'}`}
      role="status"
      aria-live="polite"
    >
      <div className="bg-white border border-gray-200 shadow-xl rounded-2xl px-4 py-3 flex items-start gap-3">
        <div className="w-9 h-9 rounded-xl bg-purple-100 flex items-center justify-center flex-shrink-0">
          <Brain className="w-5 h-5 text-purple-700" />
        </div>
        <div className="text-sm text-gray-800">
          <div className="font-semibold text-gray-900">DeepSeek Brain updated</div>
          <div className="mt-0.5">{message}</div>
        </div>
      </div>
    </div>
  )
}

