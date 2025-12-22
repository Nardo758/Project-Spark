import { useState } from 'react'
import { Link } from 'react-router-dom'
import { 
  Brain, Upload, MessageCircle, Settings, Zap, FileText, 
  TrendingUp, Clock, Star, ChevronRight, Plus
} from 'lucide-react'

const knowledgeSources = [
  { name: 'Business_plan.pdf', size: '2.1MB', date: 'Feb 10', type: 'pdf' },
  { name: 'Competitor_analysis.html', size: '156KB', date: 'Feb 12', type: 'url' },
  { name: 'Personal_skills.txt', size: '15KB', date: 'Today', type: 'text' },
]

const recentChats = [
  { question: "What's the best market for my SaaS idea?", answer: "Based on your skills in healthcare..." },
  { question: "Generate a roadmap for my AI startup", answer: "Here's a 90-day plan tailored to your..." },
]

export default function BrainDashboard() {
  const [knowledgeScore] = useState(78)

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl flex items-center justify-center">
            <Brain className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">My AI Co-founder</h1>
            <p className="text-gray-600">Basic Plan • Storage: 2.4/10GB</p>
          </div>
        </div>
        <div className="mt-4 md:mt-0 flex gap-3">
          <button className="px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 font-medium text-gray-700">
            <Settings className="w-5 h-5" />
          </button>
          <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium">
            Upgrade Brain
          </button>
        </div>
      </div>

      <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl p-6 mb-8 border border-purple-200">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">Brain Health</h2>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Knowledge Score</span>
                  <span className="font-semibold text-purple-700">{knowledgeScore}%</span>
                </div>
                <div className="h-3 bg-purple-100 rounded-full w-64">
                  <div 
                    className="h-3 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full"
                    style={{ width: `${knowledgeScore}%` }}
                  ></div>
                </div>
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">Last trained: 2 hours ago</p>
          </div>
          <div className="mt-4 md:mt-0">
            <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium flex items-center gap-2">
              <Zap className="w-5 h-5" />
              Daily Training Ready
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Link
          to="/brain/chat"
          className="bg-white p-4 rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-md transition-all text-center"
        >
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <MessageCircle className="w-6 h-6 text-purple-600" />
          </div>
          <span className="font-medium text-gray-900">Ask AI Co-founder</span>
        </Link>
        <Link
          to="/brain/upload"
          className="bg-white p-4 rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-md transition-all text-center"
        >
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <Upload className="w-6 h-6 text-blue-600" />
          </div>
          <span className="font-medium text-gray-900">Upload Knowledge</span>
        </Link>
        <Link
          to="/brain/training"
          className="bg-white p-4 rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-md transition-all text-center"
        >
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <Star className="w-6 h-6 text-green-600" />
          </div>
          <span className="font-medium text-gray-900">Daily Questions</span>
        </Link>
        <Link
          to="/brain/settings"
          className="bg-white p-4 rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-md transition-all text-center"
        >
          <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <Settings className="w-6 h-6 text-gray-600" />
          </div>
          <span className="font-medium text-gray-900">Brain Settings</span>
        </Link>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Knowledge Sources</h2>
            <button className="text-sm text-purple-600 font-medium hover:text-purple-700 flex items-center gap-1">
              <Plus className="w-4 h-4" />
              Add More
            </button>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
            {knowledgeSources.map((source, i) => (
              <div key={i} className="p-4 flex items-center justify-between hover:bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    source.type === 'pdf' ? 'bg-red-100' :
                    source.type === 'url' ? 'bg-blue-100' : 'bg-gray-100'
                  }`}>
                    <FileText className={`w-5 h-5 ${
                      source.type === 'pdf' ? 'text-red-600' :
                      source.type === 'url' ? 'text-blue-600' : 'text-gray-600'
                    }`} />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{source.name}</p>
                    <p className="text-xs text-gray-500">{source.size} • Added: {source.date}</p>
                  </div>
                </div>
                <ChevronRight className="w-5 h-5 text-gray-400" />
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Conversations</h2>
            <Link to="/brain/chat" className="text-sm text-purple-600 font-medium hover:text-purple-700">
              View All
            </Link>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
            {recentChats.map((chat, i) => (
              <div key={i} className="p-4 hover:bg-gray-50 cursor-pointer">
                <p className="font-medium text-gray-900 text-sm mb-1">Q: {chat.question}</p>
                <p className="text-sm text-gray-500 truncate">A: {chat.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-8 bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Productivity Gains</h2>
        <div className="grid grid-cols-3 gap-6">
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Clock className="w-5 h-5 text-purple-600" />
              <span className="text-3xl font-bold text-gray-900">6.2</span>
            </div>
            <p className="text-sm text-gray-500">Hours saved this week</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Zap className="w-5 h-5 text-green-600" />
              <span className="text-3xl font-bold text-gray-900">14</span>
            </div>
            <p className="text-sm text-gray-500">Tasks automated</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              <span className="text-3xl font-bold text-gray-900">8</span>
            </div>
            <p className="text-sm text-gray-500">Decisions assisted</p>
          </div>
        </div>
      </div>

      <div className="mt-8 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl p-6 text-white">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h3 className="text-lg font-semibold mb-1">Smart Suggestion</h3>
            <p className="text-purple-100">Your Brain noticed you research healthcare. Here are 3 relevant opportunities →</p>
          </div>
          <Link
            to="/discover?filter=healthcare"
            className="mt-4 md:mt-0 px-4 py-2 bg-white text-purple-600 rounded-lg font-medium hover:bg-purple-50"
          >
            View Opportunities
          </Link>
        </div>
      </div>
    </div>
  )
}
