import { useState } from 'react'
import { Lightbulb, Wand2, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'

export default function IdeaEngine() {
  const [idea, setIdea] = useState('')
  const [isValidating, setIsValidating] = useState(false)
  const [validationResult, setValidationResult] = useState<null | { score: number; feedback: string[] }>(null)

  const handleValidate = async () => {
    if (!idea.trim()) return
    
    setIsValidating(true)
    setValidationResult(null)
    
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    setValidationResult({
      score: 78,
      feedback: [
        'Strong market demand identified in healthcare sector',
        'Competition is moderate - differentiation needed',
        'Technical feasibility is high based on current technologies',
        'Recommend focusing on B2B segment first',
      ]
    })
    setIsValidating(false)
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        <div className="w-16 h-16 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
          <Lightbulb className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-4">AI Idea Engine</h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Validate your business idea with AI-powered analysis. Get instant feedback on 
          market potential, competition, and feasibility.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-gray-200 p-8 mb-8">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Describe your business idea
        </label>
        <textarea
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          placeholder="Example: A mobile app that connects local farmers directly with restaurants, eliminating middlemen and ensuring fresh produce delivery within 24 hours..."
          rows={6}
          className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
        />
        <div className="mt-4 flex justify-between items-center">
          <span className="text-sm text-gray-500">
            {idea.length}/2000 characters
          </span>
          <button
            onClick={handleValidate}
            disabled={!idea.trim() || isValidating}
            className="inline-flex items-center gap-2 px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {isValidating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Wand2 className="w-5 h-5" />
                Validate Idea
              </>
            )}
          </button>
        </div>
      </div>

      {validationResult && (
        <div className="bg-white rounded-2xl border border-gray-200 p-8 animate-fade-in">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Validation Results</h2>
            <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              validationResult.score >= 70 ? 'bg-green-50 text-green-700' :
              validationResult.score >= 50 ? 'bg-yellow-50 text-yellow-700' :
              'bg-red-50 text-red-700'
            }`}>
              {validationResult.score >= 70 ? (
                <CheckCircle className="w-5 h-5" />
              ) : (
                <AlertCircle className="w-5 h-5" />
              )}
              <span className="font-bold text-lg">{validationResult.score}% Score</span>
            </div>
          </div>
          
          <div className="space-y-4">
            <h3 className="font-medium text-gray-900">AI Feedback</h3>
            <ul className="space-y-3">
              {validationResult.feedback.map((item, i) => (
                <li key={i} className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-600">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="flex flex-col sm:flex-row gap-4">
              <button className="flex-1 px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 font-medium">
                Generate Full Roadmap
              </button>
              <button className="flex-1 px-6 py-3 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 font-medium">
                Find Similar Opportunities
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
