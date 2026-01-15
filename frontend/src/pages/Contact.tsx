import { useState } from 'react'
import { Mail, MessageSquare, Building2, Clock, Send, CheckCircle, MapPin, Phone } from 'lucide-react'

export default function Contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    subject: 'general',
    message: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [error, setError] = useState('')

  const subjects = [
    { value: 'general', label: 'General Inquiry' },
    { value: 'sales', label: 'Sales & Enterprise' },
    { value: 'support', label: 'Technical Support' },
    { value: 'partnership', label: 'Partnership Opportunity' },
    { value: 'press', label: 'Press & Media' }
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError('')

    try {
      const response = await fetch('/api/v1/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      setIsSubmitted(true)
    } catch (err) {
      setError('Failed to send message. Please try again or email us directly.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  if (isSubmitted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-6">
        <div className="max-w-md w-full text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Message Sent!</h1>
          <p className="text-gray-600 mb-6">
            Thank you for reaching out. Our team will get back to you within 1-2 business days.
          </p>
          <button 
            onClick={() => {
              setIsSubmitted(false)
              setFormData({ name: '', email: '', company: '', subject: 'general', message: '' })
            }}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition-colors"
          >
            Send Another Message
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <section className="bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 text-white py-16">
        <div className="max-w-6xl mx-auto px-6">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Get in Touch</h1>
          <p className="text-xl text-purple-100 max-w-2xl">
            Have questions about OppGrid? Want to explore enterprise solutions? 
            We're here to help you discover your next opportunity.
          </p>
        </div>
      </section>

      <section className="py-16">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid lg:grid-cols-3 gap-12">
            <div className="lg:col-span-2">
              <div className="bg-white rounded-2xl border border-gray-200 p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Send us a message</h2>
                
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                        Your Name *
                      </label>
                      <input
                        type="text"
                        id="name"
                        name="name"
                        required
                        value={formData.name}
                        onChange={handleChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none"
                        placeholder="John Smith"
                      />
                    </div>
                    <div>
                      <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                        Email Address *
                      </label>
                      <input
                        type="email"
                        id="email"
                        name="email"
                        required
                        value={formData.email}
                        onChange={handleChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none"
                        placeholder="john@company.com"
                      />
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-2">
                        Company (Optional)
                      </label>
                      <input
                        type="text"
                        id="company"
                        name="company"
                        value={formData.company}
                        onChange={handleChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none"
                        placeholder="Acme Inc."
                      />
                    </div>
                    <div>
                      <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-2">
                        Subject *
                      </label>
                      <select
                        id="subject"
                        name="subject"
                        required
                        value={formData.subject}
                        onChange={handleChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none bg-white"
                      >
                        {subjects.map(subject => (
                          <option key={subject.value} value={subject.value}>
                            {subject.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div>
                    <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                      Message *
                    </label>
                    <textarea
                      id="message"
                      name="message"
                      required
                      rows={6}
                      value={formData.message}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none resize-none"
                      placeholder="Tell us how we can help you..."
                    />
                  </div>

                  {error && (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                      {error}
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full md:w-auto inline-flex items-center justify-center gap-2 px-8 py-4 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isSubmitting ? (
                      <>Sending...</>
                    ) : (
                      <>Send Message <Send className="w-4 h-4" /></>
                    )}
                  </button>
                </form>
              </div>
            </div>

            <div className="space-y-6">
              <div className="bg-white rounded-2xl border border-gray-200 p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Quick Contact</h3>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center shrink-0">
                      <Mail className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Email</div>
                      <a href="mailto:hello@oppgrid.com" className="text-gray-900 hover:text-purple-600">
                        hello@oppgrid.com
                      </a>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center shrink-0">
                      <Phone className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Phone</div>
                      <a href="tel:+1-555-OPP-GRID" className="text-gray-900 hover:text-purple-600">
                        +1 (555) OPP-GRID
                      </a>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center shrink-0">
                      <MapPin className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Location</div>
                      <div className="text-gray-900">San Francisco, CA</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-2xl border border-gray-200 p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Response Time</h3>
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center shrink-0">
                    <Clock className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <div className="text-gray-900 font-medium">1-2 Business Days</div>
                    <div className="text-sm text-gray-500">
                      We aim to respond to all inquiries within 48 hours.
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-purple-600 to-indigo-600 rounded-2xl p-6 text-white">
                <div className="flex items-center gap-3 mb-4">
                  <Building2 className="w-6 h-6" />
                  <h3 className="font-semibold">Enterprise Solutions</h3>
                </div>
                <p className="text-purple-100 text-sm mb-4">
                  Looking for custom integrations, dedicated support, or team features? 
                  Let's discuss how OppGrid can scale with your organization.
                </p>
                <a 
                  href="mailto:enterprise@oppgrid.com"
                  className="inline-flex items-center gap-2 text-sm font-medium hover:underline"
                >
                  Contact Enterprise Sales <MessageSquare className="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
