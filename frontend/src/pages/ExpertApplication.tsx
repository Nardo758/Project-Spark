import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { 
  ArrowLeft,
  User,
  Briefcase,
  MapPin,
  DollarSign,
  CheckCircle,
  Loader2,
  Save,
  Award,
  BookOpen,
  Clock
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

interface LinkedInData {
  name: string
  email: string
  picture?: string
}

const categoryOptions = [
  { value: 'business_consultant', label: 'Business Consultant' },
  { value: 'technical_advisor', label: 'Technical Advisor' },
  { value: 'industry_specialist', label: 'Industry Specialist' },
  { value: 'growth_marketing', label: 'Growth & Marketing' },
  { value: 'financial_advisor', label: 'Financial Advisor' },
  { value: 'legal_compliance', label: 'Legal & Compliance' },
]

const specializationOptions = [
  { value: 'strategy_planning', label: 'Strategy & Planning' },
  { value: 'market_analysis', label: 'Market Analysis' },
  { value: 'business_model_design', label: 'Business Model Design' },
  { value: 'go_to_market', label: 'Go-To-Market Strategy' },
  { value: 'software_architecture', label: 'Software Architecture' },
  { value: 'product_development', label: 'Product Development' },
  { value: 'technical_due_diligence', label: 'Technical Due Diligence' },
  { value: 'fintech', label: 'FinTech' },
  { value: 'healthtech', label: 'HealthTech' },
  { value: 'saas', label: 'SaaS' },
  { value: 'marketplace', label: 'Marketplace' },
  { value: 'customer_acquisition', label: 'Customer Acquisition' },
  { value: 'brand_strategy', label: 'Brand Strategy' },
  { value: 'financial_modeling', label: 'Financial Modeling' },
  { value: 'fundraising', label: 'Fundraising' },
]

const industryOptions = [
  { value: 'technology', label: 'Technology' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'finance', label: 'Finance & Banking' },
  { value: 'ecommerce', label: 'E-commerce & Retail' },
  { value: 'manufacturing', label: 'Manufacturing' },
  { value: 'real_estate', label: 'Real Estate' },
  { value: 'education', label: 'Education' },
  { value: 'media', label: 'Media & Entertainment' },
  { value: 'energy', label: 'Energy & Utilities' },
  { value: 'food_beverage', label: 'Food & Beverage' },
]

export default function ExpertApplication() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { user, isAuthenticated, token, setToken } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [linkedInData, setLinkedInData] = useState<LinkedInData | null>(null)

  const [formData, setFormData] = useState({
    headline: '',
    bio: '',
    location: '',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    primary_category: '',
    specializations: [] as string[],
    industries: [] as string[],
    years_experience: '',
    education: '',
    certifications: '',
    hourly_rate: '',
    availability: 'available',
    skills: [] as string[],
    skillInput: '',
  })

  useEffect(() => {
    const code = searchParams.get('code')
    const name = searchParams.get('name')
    const email = searchParams.get('email')
    const picture = searchParams.get('picture')
    const error = searchParams.get('error')

    if (error) {
      setErrorMessage(decodeURIComponent(error))
      return
    }

    if (code) {
      setIsLoading(true)
      const redeemCode = async () => {
        try {
          const response = await fetch(`/api/v1/auth/linkedin/redeem?code=${code}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
          })
          
          if (!response.ok) {
            const data = await response.json()
            setErrorMessage(data.detail || 'Authentication failed. Please try again.')
            setIsLoading(false)
            return
          }
          
          const data = await response.json()
          const authToken = data.access_token
          
          localStorage.setItem('token', authToken)
          setToken(authToken)
          
          setLinkedInData({
            name: name ? decodeURIComponent(name) : data.user?.name || '',
            email: email ? decodeURIComponent(email) : data.user?.email || '',
            picture: picture ? decodeURIComponent(picture) : undefined
          })
          setIsLoading(false)
        } catch (err) {
          setErrorMessage('Authentication failed. Please try again.')
          setIsLoading(false)
        }
      }
      
      redeemCode()
    } else if (user) {
      setLinkedInData({
        name: user.name || '',
        email: user.email || '',
        picture: user.avatar_url
      })
    }
  }, [searchParams, user, setToken])

  useEffect(() => {
    if (!isAuthenticated && !searchParams.get('code')) {
      navigate('/join-network/expert')
    }
  }, [isAuthenticated, navigate, searchParams])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleMultiSelect = (field: 'specializations' | 'industries', value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].includes(value)
        ? prev[field].filter(v => v !== value)
        : [...prev[field], value]
    }))
  }

  const handleAddSkill = () => {
    if (formData.skillInput.trim() && !formData.skills.includes(formData.skillInput.trim())) {
      setFormData(prev => ({
        ...prev,
        skills: [...prev.skills, prev.skillInput.trim()],
        skillInput: ''
      }))
    }
  }

  const handleRemoveSkill = (skill: string) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.filter(s => s !== skill)
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    setErrorMessage(null)

    try {
      const response = await fetch('/api/v1/experts/apply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: formData.headline,
          location: formData.location,
          timezone: formData.timezone,
          primary_category: formData.primary_category || null,
          specializations: formData.specializations.length > 0 ? formData.specializations : null,
          industries: formData.industries.length > 0 ? formData.industries : null,
          years_experience: formData.years_experience ? parseInt(formData.years_experience) : null,
          education: formData.education || null,
          certifications: formData.certifications || null,
          hourly_rate_cents: formData.hourly_rate ? parseInt(formData.hourly_rate) * 100 : null,
          availability_description: formData.availability || null,
          portfolio_highlights: formData.bio || null
        })
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to submit application')
      }

      setSuccessMessage('Your expert profile has been created successfully!')
      setTimeout(() => {
        navigate('/expert/dashboard')
      }, 2000)
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to submit application')
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <button
          onClick={() => navigate('/network')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Network
        </button>

        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          <div className="bg-indigo-600 px-8 py-8 text-white">
            <div className="flex items-center gap-4">
              {linkedInData?.picture ? (
                <img 
                  src={linkedInData.picture} 
                  alt={linkedInData.name} 
                  className="w-16 h-16 rounded-full border-2 border-white/30"
                />
              ) : (
                <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
                  <User className="w-8 h-8" />
                </div>
              )}
              <div>
                <h1 className="text-2xl font-bold">Complete Your Expert Profile</h1>
                <p className="text-white/80 mt-1">
                  {linkedInData?.name ? `Welcome, ${linkedInData.name}!` : 'Tell us about your expertise'}
                </p>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="p-8 space-y-8">
            {successMessage && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                <p className="text-green-800">{successMessage}</p>
              </div>
            )}

            {errorMessage && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800">{errorMessage}</p>
              </div>
            )}

            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <User className="w-5 h-5 text-indigo-600" />
                Basic Information
              </h2>
              <div className="grid gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Professional Headline *
                  </label>
                  <input
                    type="text"
                    name="headline"
                    value={formData.headline}
                    onChange={handleInputChange}
                    placeholder="e.g., Senior Product Manager | 10+ Years in SaaS"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Bio
                  </label>
                  <textarea
                    name="bio"
                    value={formData.bio}
                    onChange={handleInputChange}
                    placeholder="Tell potential clients about your background and what makes you unique..."
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <MapPin className="w-4 h-4 inline mr-1" />
                      Location
                    </label>
                    <input
                      type="text"
                      name="location"
                      value={formData.location}
                      onChange={handleInputChange}
                      placeholder="e.g., San Francisco, CA"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <Clock className="w-4 h-4 inline mr-1" />
                      Timezone
                    </label>
                    <input
                      type="text"
                      name="timezone"
                      value={formData.timezone}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-indigo-600" />
                Expertise
              </h2>
              <div className="grid gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Primary Category *
                  </label>
                  <select
                    name="primary_category"
                    value={formData.primary_category}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    required
                  >
                    <option value="">Select a category</option>
                    {categoryOptions.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Specializations (select all that apply)
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {specializationOptions.map(opt => (
                      <button
                        key={opt.value}
                        type="button"
                        onClick={() => handleMultiSelect('specializations', opt.value)}
                        className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                          formData.specializations.includes(opt.value)
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Industries (select all that apply)
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {industryOptions.map(opt => (
                      <button
                        key={opt.value}
                        type="button"
                        onClick={() => handleMultiSelect('industries', opt.value)}
                        className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                          formData.industries.includes(opt.value)
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Skills
                  </label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      name="skillInput"
                      value={formData.skillInput}
                      onChange={handleInputChange}
                      placeholder="Add a skill and press Enter"
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddSkill())}
                    />
                    <button
                      type="button"
                      onClick={handleAddSkill}
                      className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                    >
                      Add
                    </button>
                  </div>
                  {formData.skills.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {formData.skills.map(skill => (
                        <span
                          key={skill}
                          className="inline-flex items-center gap-1 px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm"
                        >
                          {skill}
                          <button
                            type="button"
                            onClick={() => handleRemoveSkill(skill)}
                            className="ml-1 hover:text-indigo-600"
                          >
                            &times;
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-indigo-600" />
                Experience & Education
              </h2>
              <div className="grid gap-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Years of Experience
                    </label>
                    <input
                      type="number"
                      name="years_experience"
                      value={formData.years_experience}
                      onChange={handleInputChange}
                      placeholder="e.g., 10"
                      min="0"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <DollarSign className="w-4 h-4 inline mr-1" />
                      Hourly Rate (USD)
                    </label>
                    <input
                      type="number"
                      name="hourly_rate"
                      value={formData.hourly_rate}
                      onChange={handleInputChange}
                      placeholder="e.g., 150"
                      min="0"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Education
                  </label>
                  <input
                    type="text"
                    name="education"
                    value={formData.education}
                    onChange={handleInputChange}
                    placeholder="e.g., MBA, Stanford Graduate School of Business"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <Award className="w-4 h-4 inline mr-1" />
                    Certifications
                  </label>
                  <textarea
                    name="certifications"
                    value={formData.certifications}
                    onChange={handleInputChange}
                    placeholder="List your relevant certifications..."
                    rows={2}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
              </div>
            </section>

            <div className="pt-6 border-t border-gray-200">
              <button
                type="submit"
                disabled={isSaving}
                className="w-full flex items-center justify-center gap-2 bg-indigo-600 text-white py-3 px-6 rounded-xl font-semibold hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSaving ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    <Save className="w-5 h-5" />
                    Create Expert Profile
                  </>
                )}
              </button>
              <p className="text-center text-sm text-gray-500 mt-4">
                Your profile will be reviewed before being listed on the platform.
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
