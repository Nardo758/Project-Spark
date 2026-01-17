import { useState } from 'react'
import { X, Zap, Lock, TrendingUp, FileText, Users, Loader2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { useInlinePayment } from '../hooks/useInlinePayment'
import { type Tier } from '../constants/pricing'
import PayPerUnlockModal from './PayPerUnlockModal'

interface UpgradeModalProps {
  isOpen: boolean
  onClose: () => void
  feature?: string
  context?: 'opportunity' | 'report' | 'analysis' | 'general'
}

const contextMessages = {
  opportunity: {
    title: 'Unlock Full Opportunity Access',
    description: 'Get complete market data, competitor analysis, and actionable insights for this opportunity.',
    icon: TrendingUp,
  },
  report: {
    title: 'Unlock AI-Generated Reports',
    description: 'Access detailed business reports including marketing plans, financial projections, and go-to-market strategies.',
    icon: FileText,
  },
  analysis: {
    title: 'Unlock Advanced Analysis',
    description: 'Get in-depth market research, demographic data, and location intelligence for your business idea.',
    icon: Zap,
  },
  general: {
    title: 'Upgrade Your Plan',
    description: 'Unlock premium features to accelerate your business journey.',
    icon: Lock,
  },
}

const benefits = [
  { icon: TrendingUp, text: 'Full access to opportunity data and insights' },
  { icon: FileText, text: 'AI-generated business reports and analysis' },
  { icon: Users, text: 'Expert marketplace and consultation access' },
  { icon: Zap, text: 'Priority processing and faster results' },
]

const individualPlans = [
  { tier: 'starter', name: 'Starter', price: '$20/mo', slots: 1 },
  { tier: 'growth', name: 'Growth', price: '$50/mo', slots: 3, popular: true },
  { tier: 'pro', name: 'Pro', price: '$99/mo', slots: 5 },
]

const businessPlans = [
  { tier: 'team', name: 'Team', price: '$250/mo', slots: 5, seats: 3 },
  { tier: 'business', name: 'Business', price: '$750/mo', slots: 15, seats: 10 },
  { tier: 'enterprise', name: 'Enterprise', price: '$2,500+/mo', slots: 30, seats: 'Unlimited' },
]

export default function UpgradeModal({ isOpen, onClose, feature, context = 'general' }: UpgradeModalProps) {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()
  
  const { 
    state: paymentState, 
    startCheckout, 
    closePaymentModal, 
    handlePaymentConfirmed 
  } = useInlinePayment(() => {
    onClose()
  })
  
  if (!isOpen && !paymentState.paymentModalOpen) return null

  const contextInfo = contextMessages[context]
  const ContextIcon = contextInfo.icon

  function handlePlanSelect(tier: string) {
    if (isAuthenticated) {
      startCheckout(tier as Tier)
    } else {
      onClose()
      navigate(`/signup?plan=${tier}`)
    }
  }

  function handleViewAllPlans() {
    onClose()
    navigate('/pricing')
  }

  if (paymentState.paymentModalOpen && paymentState.publishableKey && paymentState.clientSecret) {
    return (
      <PayPerUnlockModal
        publishableKey={paymentState.publishableKey}
        clientSecret={paymentState.clientSecret}
        amountLabel={paymentState.priceLabel || ''}
        title={`Subscribe to ${paymentState.selectedTier?.charAt(0).toUpperCase()}${paymentState.selectedTier?.slice(1) || ''}`}
        contextLabel="Subscription"
        confirmLabel={`Subscribe ${paymentState.priceLabel}`}
        footnote="Your subscription will begin immediately after payment."
        onClose={() => {
          closePaymentModal()
        }}
        onConfirmed={handlePaymentConfirmed}
      />
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="w-full max-w-lg bg-white rounded-2xl shadow-2xl overflow-hidden">
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 p-6 text-white relative">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-1 hover:bg-white/20 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-white/20 rounded-lg">
              <ContextIcon className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold">{contextInfo.title}</h2>
          </div>
          <p className="text-white/90 text-sm">
            {contextInfo.description}
          </p>
          {feature && (
            <p className="mt-2 text-sm text-white/70">
              Feature: {feature}
            </p>
          )}
        </div>

        <div className="p-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">What you'll get:</h3>
          <div className="space-y-2 mb-6">
            {benefits.map((benefit, i) => (
              <div key={i} className="flex items-center gap-3 text-sm text-gray-700">
                <benefit.icon className="w-4 h-4 text-purple-600 shrink-0" />
                <span>{benefit.text}</span>
              </div>
            ))}
          </div>

          {paymentState.error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {paymentState.error}
            </div>
          )}

          <h3 className="text-sm font-semibold text-gray-900 mb-3">Individual Plans:</h3>
          <div className="grid grid-cols-3 gap-3 mb-4">
            {individualPlans.map((plan) => (
              <button
                key={plan.tier}
                onClick={() => handlePlanSelect(plan.tier)}
                disabled={paymentState.isLoading}
                className={`p-3 rounded-xl border-2 text-center transition-all hover:border-purple-500 hover:bg-purple-50 disabled:opacity-50 disabled:cursor-not-allowed ${
                  plan.popular ? 'border-purple-500 bg-purple-50' : 'border-gray-200'
                }`}
              >
                {paymentState.isLoading && paymentState.selectedTier === plan.tier ? (
                  <Loader2 className="w-5 h-5 animate-spin mx-auto text-purple-600" />
                ) : (
                  <>
                    {plan.popular && (
                      <span className="text-[10px] font-bold text-purple-600 uppercase">Popular</span>
                    )}
                    <div className="font-semibold text-gray-900">{plan.name}</div>
                    <div className="text-sm text-gray-600">{plan.price}</div>
                    <div className="text-xs text-gray-500 mt-1">{plan.slots} slot{plan.slots > 1 ? 's' : ''}</div>
                  </>
                )}
              </button>
            ))}
          </div>

          <h3 className="text-sm font-semibold text-gray-900 mb-3">Business Plans:</h3>
          <div className="grid grid-cols-3 gap-3 mb-4">
            {businessPlans.map((plan) => (
              <button
                key={plan.tier}
                onClick={() => handlePlanSelect(plan.tier)}
                disabled={paymentState.isLoading}
                className="p-3 rounded-xl border-2 border-gray-200 text-center transition-all hover:border-indigo-500 hover:bg-indigo-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {paymentState.isLoading && paymentState.selectedTier === plan.tier ? (
                  <Loader2 className="w-5 h-5 animate-spin mx-auto text-indigo-600" />
                ) : (
                  <>
                    <div className="font-semibold text-gray-900">{plan.name}</div>
                    <div className="text-sm text-gray-600">{plan.price}</div>
                    <div className="text-xs text-gray-500 mt-1">{plan.slots} slots • {plan.seats} seats</div>
                  </>
                )}
              </button>
            ))}
          </div>

          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 py-2.5 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Maybe later
            </button>
            <button
              onClick={handleViewAllPlans}
              className="flex-1 py-2.5 text-gray-500 hover:text-gray-700 text-sm transition-colors"
            >
              Compare plan details
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export function useUpgradeModal() {
  const [isOpen, setIsOpen] = useState(false)
  const [context, setContext] = useState<UpgradeModalProps['context']>('general')
  const [feature, setFeature] = useState<string | undefined>()

  function openUpgradeModal(ctx?: UpgradeModalProps['context'], feat?: string) {
    setContext(ctx || 'general')
    setFeature(feat)
    setIsOpen(true)
  }

  function closeUpgradeModal() {
    setIsOpen(false)
  }

  return {
    isOpen,
    context,
    feature,
    openUpgradeModal,
    closeUpgradeModal,
  }
}
