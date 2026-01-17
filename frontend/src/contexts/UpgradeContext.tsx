import { createContext, useContext, useState, ReactNode } from 'react'
import UpgradeModal from '../components/UpgradeModal'

type UpgradeContext = 'opportunity' | 'report' | 'analysis' | 'general'

interface UpgradeContextValue {
  showUpgradeModal: (context?: UpgradeContext, feature?: string) => void
}

const UpgradeCtx = createContext<UpgradeContextValue | null>(null)

export function UpgradeProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false)
  const [context, setContext] = useState<UpgradeContext>('general')
  const [feature, setFeature] = useState<string | undefined>()

  function showUpgradeModal(ctx?: UpgradeContext, feat?: string) {
    setContext(ctx || 'general')
    setFeature(feat)
    setIsOpen(true)
  }

  function closeModal() {
    setIsOpen(false)
  }

  return (
    <UpgradeCtx.Provider value={{ showUpgradeModal }}>
      {children}
      <UpgradeModal
        isOpen={isOpen}
        onClose={closeModal}
        context={context}
        feature={feature}
      />
    </UpgradeCtx.Provider>
  )
}

export function useUpgrade() {
  const ctx = useContext(UpgradeCtx)
  if (!ctx) {
    throw new Error('useUpgrade must be used within UpgradeProvider')
  }
  return ctx
}
