import { useState, useEffect } from 'react'
import { X, FileText, TrendingUp, Lightbulb, Globe, BarChart3, Target, Loader2, CreditCard, Sparkles, ChevronDown, ChevronUp, Info, CheckCircle } from 'lucide-react'

type ReportType = 'feasibility' | 'market-analysis' | 'strategic-assessment' | 'pestle' | 'business-plan' | 'financials' | 'pitch-deck'

type ReportContext = {
  businessConcept?: string
  location?: string
  category?: string
  targetMarket?: string
  validationData?: any
  searchData?: any
  locationData?: any
  cloneData?: any
}

type ReportInputModalProps = {
  isOpen: boolean
  onClose: () => void
  reportType: ReportType
  context: ReportContext
  onSubmit: (reportType: ReportType, formData: Record<string, any>) => void
  isLoading?: boolean
}

const reportConfig: Record<ReportType, {
  name: string
  price: number
  icon: React.ComponentType<{ className?: string }>
  description: string
  color: string
}> = {
  'feasibility': {
    name: 'Feasibility Study',
    price: 0,
    icon: Target,
    description: 'Assess viability and risks for your business concept',
    color: 'green'
  },
  'market-analysis': {
    name: 'Market Analysis',
    price: 99,
    icon: TrendingUp,
    description: 'Deep market intelligence with competitor insights',
    color: 'indigo'
  },
  'strategic-assessment': {
    name: 'Strategic Assessment',
    price: 89,
    icon: Lightbulb,
    description: 'SWOT analysis and strategic positioning',
    color: 'violet'
  },
  'pestle': {
    name: 'PESTLE Analysis',
    price: 79,
    icon: Globe,
    description: 'Political, Economic, Social, Tech, Legal, Environmental scan',
    color: 'rose'
  },
  'business-plan': {
    name: 'Business Plan',
    price: 149,
    icon: FileText,
    description: 'Comprehensive business planning document',
    color: 'blue'
  },
  'financials': {
    name: 'Financial Model',
    price: 129,
    icon: BarChart3,
    description: 'Revenue projections and cost analysis',
    color: 'emerald'
  },
  'pitch-deck': {
    name: 'Pitch Deck',
    price: 79,
    icon: Target,
    description: 'Investor-ready presentation slides',
    color: 'purple'
  }
}

export default function ReportInputModal({ isOpen, onClose, reportType, context, onSubmit, isLoading }: ReportInputModalProps) {
  const [formData, setFormData] = useState<Record<string, any>>({})
  const [showAdvanced, setShowAdvanced] = useState(false)
  
  const config = reportConfig[reportType]
  const Icon = config.icon

  useEffect(() => {
    if (isOpen && context) {
      setFormData({
        businessConcept: context.businessConcept || '',
        location: context.location || '',
        category: context.category || '',
        targetMarket: context.targetMarket || '',
        ...getDefaultFieldsForType(reportType)
      })
    }
  }, [isOpen, context, reportType])

  const getDefaultFieldsForType = (type: ReportType): Record<string, any> => {
    switch (type) {
      case 'feasibility':
        return { startupBudget: '', timeline: '6 months' }
      case 'market-analysis':
        return { serviceRadius: '10 miles', demographics: '', priceRange: '', competitors: '' }
      case 'strategic-assessment':
        return { businessSituation: 'startup', goals: '', planningHorizon: '1 year', challenges: '' }
      case 'pestle':
        return { businessScale: 'local', launchTimeline: '', regulatoryConcerns: '' }
      case 'business-plan':
        return { 
          products: '', valueProposition: '', customerSegments: '', 
          businessModel: 'B2C', revenueStreams: '', locationType: 'physical',
          initialCapital: '', fundingNeeds: '', founderBackground: '', keyRoles: '',
          launchTarget: '', milestones: ''
        }
      case 'financials':
        return {
          revenueModel: '', pricingStructure: '', customerVolume: '',
          startupCosts: '', monthlyFixedCosts: '', variableCosts: '',
          growthAssumptions: '', projectionYears: '3', breakevenGoal: ''
        }
      case 'pitch-deck':
        return {
          fundingAmount: '', useOfFunds: '', founderBio: '', advisors: '',
          traction: '', tamSamSom: '', investorType: 'angel'
        }
      default:
        return {}
    }
  }

  const handleFieldChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = () => {
    onSubmit(reportType, formData)
  }

  if (!isOpen) return null

  const renderCommonFields = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Business Concept <span className="text-red-500">*</span>
        </label>
        <textarea
          value={formData.businessConcept || ''}
          onChange={(e) => handleFieldChange('businessConcept', e.target.value)}
          placeholder="Describe your business idea in 1-2 sentences..."
          className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
          rows={3}
        />
        <p className="text-xs text-gray-500 mt-1">e.g., "Mobile coffee cart serving specialty drinks in downtown Seattle"</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Geographic Location <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.location || ''}
            onChange={(e) => handleFieldChange('location', e.target.value)}
            placeholder="City, state or zip code"
            className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Industry/Category
          </label>
          <input
            type="text"
            value={formData.category || ''}
            onChange={(e) => handleFieldChange('category', e.target.value)}
            placeholder="e.g., Food & Beverage, Tech, Healthcare"
            className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Target Market
        </label>
        <input
          type="text"
          value={formData.targetMarket || ''}
          onChange={(e) => handleFieldChange('targetMarket', e.target.value)}
          placeholder="Who are your customers?"
          className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        />
        <p className="text-xs text-gray-500 mt-1">e.g., "Young professionals aged 25-40, health-conscious consumers"</p>
      </div>
    </div>
  )

  const renderTypeSpecificFields = () => {
    switch (reportType) {
      case 'feasibility':
        return (
          <div className="space-y-4 mt-4 pt-4 border-t border-gray-100">
            <h4 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <Info className="w-4 h-4 text-gray-400" />
              Feasibility-Specific Inputs
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Estimated Startup Budget
                </label>
                <input
                  type="text"
                  value={formData.startupBudget || ''}
                  onChange={(e) => handleFieldChange('startupBudget', e.target.value)}
                  placeholder="e.g., $50,000"
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Desired Timeline
                </label>
                <select
                  value={formData.timeline || '6 months'}
                  onChange={(e) => handleFieldChange('timeline', e.target.value)}
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="3 months">3 months</option>
                  <option value="6 months">6 months</option>
                  <option value="1 year">1 year</option>
                  <option value="2+ years">2+ years</option>
                </select>
              </div>
            </div>
          </div>
        )

      case 'market-analysis':
        return (
          <div className="space-y-4 mt-4 pt-4 border-t border-gray-100">
            <h4 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-indigo-500" />
              Market Analysis Inputs
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Service Radius
                </label>
                <select
                  value={formData.serviceRadius || '10 miles'}
                  onChange={(e) => handleFieldChange('serviceRadius', e.target.value)}
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="5 miles">5 miles</option>
                  <option value="10 miles">10 miles</option>
                  <option value="25 miles">25 miles</option>
                  <option value="50 miles">50 miles</option>
                  <option value="statewide">Statewide</option>
                  <option value="national">National</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Price Point Range
                </label>
                <input
                  type="text"
                  value={formData.priceRange || ''}
                  onChange={(e) => handleFieldChange('priceRange', e.target.value)}
                  placeholder="e.g., $10-25 per item"
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Target Demographics
              </label>
              <input
                type="text"
                value={formData.demographics || ''}
                onChange={(e) => handleFieldChange('demographics', e.target.value)}
                placeholder="Age, income level, lifestyle..."
                className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Specific Competitors to Benchmark <span className="text-gray-400">(optional)</span>
              </label>
              <input
                type="text"
                value={formData.competitors || ''}
                onChange={(e) => handleFieldChange('competitors', e.target.value)}
                placeholder="e.g., Starbucks, Blue Bottle, local cafes"
                className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
        )

      case 'strategic-assessment':
        return (
          <div className="space-y-4 mt-4 pt-4 border-t border-gray-100">
            <h4 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-violet-500" />
              Strategic Assessment Inputs
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Business Situation
                </label>
                <select
                  value={formData.businessSituation || 'startup'}
                  onChange={(e) => handleFieldChange('businessSituation', e.target.value)}
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="startup">New Startup</option>
                  <option value="early-stage">Early Stage (0-2 years)</option>
                  <option value="growth">Growth Stage (2-5 years)</option>
                  <option value="established">Established Business (5+ years)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Planning Horizon
                </label>
                <select
                  value={formData.planningHorizon || '1 year'}
                  onChange={(e) => handleFieldChange('planningHorizon', e.target.value)}
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="1 year">1-year strategy</option>
                  <option value="3 years">3-year strategy</option>
                  <option value="5 years">5-year strategy</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Business Goals
              </label>
              <textarea
                value={formData.goals || ''}
                onChange={(e) => handleFieldChange('goals', e.target.value)}
                placeholder="Growth targets, market position, expansion plans..."
                className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
                rows={2}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Key Challenges or Concerns
              </label>
              <textarea
                value={formData.challenges || ''}
                onChange={(e) => handleFieldChange('challenges', e.target.value)}
                placeholder="What obstacles are you facing?"
                className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
                rows={2}
              />
            </div>
          </div>
        )

      case 'pestle':
        return (
          <div className="space-y-4 mt-4 pt-4 border-t border-gray-100">
            <h4 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <Globe className="w-4 h-4 text-rose-500" />
              PESTLE Analysis Inputs
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Business Scale
                </label>
                <select
                  value={formData.businessScale || 'local'}
                  onChange={(e) => handleFieldChange('businessScale', e.target.value)}
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="local">Local Store</option>
                  <option value="regional">Regional Chain</option>
                  <option value="national">National Business</option>
                  <option value="international">International</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Launch Timeline
                </label>
                <input
                  type="text"
                  value={formData.launchTimeline || ''}
                  onChange={(e) => handleFieldChange('launchTimeline', e.target.value)}
                  placeholder="e.g., Q2 2025"
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Known Regulatory/Environmental Concerns <span className="text-gray-400">(optional)</span>
              </label>
              <textarea
                value={formData.regulatoryConcerns || ''}
                onChange={(e) => handleFieldChange('regulatoryConcerns', e.target.value)}
                placeholder="Any specific regulations, permits, or environmental factors you're aware of..."
                className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
                rows={2}
              />
            </div>
          </div>
        )

      case 'business-plan':
        return (
          <div className="space-y-4 mt-4 pt-4 border-t border-gray-100">
            <h4 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-500" />
              Business Plan Inputs
            </h4>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Products/Services Offered
              </label>
              <textarea
                value={formData.products || ''}
                onChange={(e) => handleFieldChange('products', e.target.value)}
                placeholder="What will you sell or provide?"
                className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
                rows={2}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Unique Value Proposition
              </label>
              <textarea
                value={formData.valueProposition || ''}
                onChange={(e) => handleFieldChange('valueProposition', e.target.value)}
                placeholder="What makes you different from competitors?"
                className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
                rows={2}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Business Model
                </label>
                <select
                  value={formData.businessModel || 'B2C'}
                  onChange={(e) => handleFieldChange('businessModel', e.target.value)}
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="B2C">B2C (Business to Consumer)</option>
                  <option value="B2B">B2B (Business to Business)</option>
                  <option value="marketplace">Marketplace</option>
                  <option value="subscription">Subscription</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location Type
                </label>
                <select
                  value={formData.locationType || 'physical'}
                  onChange={(e) => handleFieldChange('locationType', e.target.value)}
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="physical">Physical Location</option>
                  <option value="online">Online Only</option>
                  <option value="hybrid">Hybrid (Both)</option>
                </select>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-700"
            >
              {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              {showAdvanced ? 'Hide' : 'Show'} Additional Fields
            </button>

            {showAdvanced && (
              <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Revenue Streams
                  </label>
                  <input
                    type="text"
                    value={formData.revenueStreams || ''}
                    onChange={(e) => handleFieldChange('revenueStreams', e.target.value)}
                    placeholder="How will you make money?"
                    className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Initial Capital Available
                    </label>
                    <input
                      type="text"
                      value={formData.initialCapital || ''}
                      onChange={(e) => handleFieldChange('initialCapital', e.target.value)}
                      placeholder="e.g., $100,000"
                      className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Funding Needs
                    </label>
                    <input
                      type="text"
                      value={formData.fundingNeeds || ''}
                      onChange={(e) => handleFieldChange('fundingNeeds', e.target.value)}
                      placeholder="e.g., $500,000"
                      className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Founder Background
                  </label>
                  <textarea
                    value={formData.founderBackground || ''}
                    onChange={(e) => handleFieldChange('founderBackground', e.target.value)}
                    placeholder="Relevant experience, skills, previous ventures..."
                    className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
                    rows={2}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Launch Target & Milestones
                  </label>
                  <input
                    type="text"
                    value={formData.launchTarget || ''}
                    onChange={(e) => handleFieldChange('launchTarget', e.target.value)}
                    placeholder="e.g., Launch Q3 2025, 100 customers by year 1"
                    className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
              </div>
            )}
          </div>
        )

      case 'financials':
        return (
          <div className="space-y-4 mt-4 pt-4 border-t border-gray-100">
            <h4 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-emerald-500" />
              Financial Model Inputs
            </h4>

            <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg">
              <p className="text-sm text-emerald-800">
                <strong>Tip:</strong> More specific inputs = more accurate projections. Estimates are fine if you're unsure.
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Revenue Model
              </label>
              <input
                type="text"
                value={formData.revenueModel || ''}
                onChange={(e) => handleFieldChange('revenueModel', e.target.value)}
                placeholder="e.g., Per-unit sales, monthly subscription, service fees"
                className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Pricing Structure
                </label>
                <input
                  type="text"
                  value={formData.pricingStructure || ''}
                  onChange={(e) => handleFieldChange('pricingStructure', e.target.value)}
                  placeholder="e.g., $15/item, $99/month"
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Expected Customer Volume
                </label>
                <input
                  type="text"
                  value={formData.customerVolume || ''}
                  onChange={(e) => handleFieldChange('customerVolume', e.target.value)}
                  placeholder="e.g., 50 customers/day"
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Startup Costs
                </label>
                <input
                  type="text"
                  value={formData.startupCosts || ''}
                  onChange={(e) => handleFieldChange('startupCosts', e.target.value)}
                  placeholder="e.g., $75,000"
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Monthly Fixed Costs
                </label>
                <input
                  type="text"
                  value={formData.monthlyFixedCosts || ''}
                  onChange={(e) => handleFieldChange('monthlyFixedCosts', e.target.value)}
                  placeholder="e.g., $8,000"
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Variable Costs
                </label>
                <input
                  type="text"
                  value={formData.variableCosts || ''}
                  onChange={(e) => handleFieldChange('variableCosts', e.target.value)}
                  placeholder="e.g., $5/unit"
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Projection Years
                </label>
                <select
                  value={formData.projectionYears || '3'}
                  onChange={(e) => handleFieldChange('projectionYears', e.target.value)}
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="1">1 Year</option>
                  <option value="3">3 Years</option>
                  <option value="5">5 Years</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Growth Assumptions
                </label>
                <input
                  type="text"
                  value={formData.growthAssumptions || ''}
                  onChange={(e) => handleFieldChange('growthAssumptions', e.target.value)}
                  placeholder="e.g., 10% monthly growth"
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>
          </div>
        )

      case 'pitch-deck':
        return (
          <div className="space-y-4 mt-4 pt-4 border-t border-gray-100">
            <h4 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <Target className="w-4 h-4 text-purple-500" />
              Pitch Deck Inputs
            </h4>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Funding Amount Seeking
                </label>
                <input
                  type="text"
                  value={formData.fundingAmount || ''}
                  onChange={(e) => handleFieldChange('fundingAmount', e.target.value)}
                  placeholder="e.g., $500,000"
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Target Investor Type
                </label>
                <select
                  value={formData.investorType || 'angel'}
                  onChange={(e) => handleFieldChange('investorType', e.target.value)}
                  className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="angel">Angel Investors</option>
                  <option value="vc">Venture Capital</option>
                  <option value="strategic">Strategic Partner</option>
                  <option value="crowd">Crowdfunding</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Use of Funds
              </label>
              <textarea
                value={formData.useOfFunds || ''}
                onChange={(e) => handleFieldChange('useOfFunds', e.target.value)}
                placeholder="How will you allocate the investment? e.g., 40% product development, 30% marketing..."
                className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
                rows={2}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Founder Bio & Experience
              </label>
              <textarea
                value={formData.founderBio || ''}
                onChange={(e) => handleFieldChange('founderBio', e.target.value)}
                placeholder="Relevant experience, previous exits, industry expertise..."
                className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
                rows={2}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Traction to Date
              </label>
              <textarea
                value={formData.traction || ''}
                onChange={(e) => handleFieldChange('traction', e.target.value)}
                placeholder="Current customers, revenue, partnerships, waitlist size..."
                className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
                rows={2}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Market Size (TAM/SAM/SOM) <span className="text-gray-400">(optional)</span>
              </label>
              <input
                type="text"
                value={formData.tamSamSom || ''}
                onChange={(e) => handleFieldChange('tamSamSom', e.target.value)}
                placeholder="e.g., $50B TAM, $5B SAM, $500M SOM"
                className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
        )

      default:
        return null
    }
  }

  const isFormValid = () => {
    return formData.businessConcept?.trim() && formData.location?.trim()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className={`p-6 bg-gradient-to-r from-${config.color}-50 to-${config.color}-100 border-b border-${config.color}-200`}>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-3 bg-${config.color}-100 rounded-xl`}>
                <Icon className={`w-6 h-6 text-${config.color}-600`} />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">{config.name}</h2>
                <p className="text-sm text-gray-600">{config.description}</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-white/50 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="mt-4 flex items-center gap-2">
            {config.price === 0 ? (
              <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-bold">FREE</span>
            ) : (
              <span className="px-3 py-1 bg-white/80 text-gray-900 rounded-full text-sm font-bold">${config.price}</span>
            )}
            <span className="text-sm text-gray-500">• AI-generated report in minutes</span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {context.businessConcept && (
            <div className="mb-4 p-3 bg-indigo-50 border border-indigo-100 rounded-lg flex items-start gap-2">
              <CheckCircle className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-indigo-900">Pre-filled from your analysis</p>
                <p className="text-xs text-indigo-700 mt-0.5">We've captured context from your session. Review and add any additional details.</p>
              </div>
            </div>
          )}

          {renderCommonFields()}
          {renderTypeSpecificFields()}
        </div>

        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-500">
              <span className="text-red-500">*</span> Required fields
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={onClose}
                className="px-4 py-2 text-gray-700 hover:text-gray-900 font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                disabled={isLoading || !isFormValid()}
                className={`px-6 py-3 bg-gradient-to-r from-${config.color}-600 to-${config.color}-700 text-white font-semibold rounded-lg hover:from-${config.color}-700 hover:to-${config.color}-800 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg`}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Processing...
                  </>
                ) : config.price === 0 ? (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate FREE Report
                  </>
                ) : (
                  <>
                    <CreditCard className="w-4 h-4" />
                    Continue to Payment (${config.price})
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
