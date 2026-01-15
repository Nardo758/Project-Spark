import { Link } from 'react-router-dom'
import { Shield, Eye, Lock, UserCheck, Bell, Trash2 } from 'lucide-react'

export default function Privacy() {
  const lastUpdated = 'January 1, 2026'

  const highlights = [
    {
      icon: Shield,
      title: 'Data Protection',
      description: 'We use industry-standard encryption and security measures to protect your data.'
    },
    {
      icon: Eye,
      title: 'Transparency',
      description: 'We clearly explain what data we collect and how we use it.'
    },
    {
      icon: Lock,
      title: 'Your Control',
      description: 'You can access, update, or delete your personal data at any time.'
    },
    {
      icon: UserCheck,
      title: 'No Selling',
      description: 'We never sell your personal information to third parties.'
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <section className="bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 text-white py-16">
        <div className="max-w-4xl mx-auto px-6">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Privacy Policy</h1>
          <p className="text-purple-100">Last updated: {lastUpdated}</p>
        </div>
      </section>

      <section className="py-12 bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {highlights.map((item, index) => (
              <div key={index} className="flex items-start gap-4">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center shrink-0">
                  <item.icon className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">{item.title}</h3>
                  <p className="text-sm text-gray-600">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16">
        <div className="max-w-4xl mx-auto px-6">
          <div className="bg-white rounded-2xl border border-gray-200 p-8 md:p-12">
            <div className="prose prose-gray max-w-none">
              <p className="text-lg text-gray-600 mb-8">
                At OppGrid, we take your privacy seriously. This Privacy Policy explains how we collect, 
                use, disclose, and safeguard your information when you use our platform.
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">1. Information We Collect</h2>
              
              <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">Information You Provide</h3>
              <ul className="list-disc pl-6 text-gray-600 mb-4 space-y-2">
                <li><strong>Account Information:</strong> Name, email address, password, and profile details</li>
                <li><strong>Payment Information:</strong> Billing address and payment method details (processed securely via Stripe)</li>
                <li><strong>Profile Data:</strong> Professional information, company details, and preferences</li>
                <li><strong>Communications:</strong> Messages, feedback, and support requests</li>
                <li><strong>User Content:</strong> Workspaces, notes, and opportunity analyses you create</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">Information Collected Automatically</h3>
              <ul className="list-disc pl-6 text-gray-600 mb-4 space-y-2">
                <li><strong>Usage Data:</strong> Pages visited, features used, and interaction patterns</li>
                <li><strong>Device Information:</strong> Browser type, operating system, and device identifiers</li>
                <li><strong>Log Data:</strong> IP address, access times, and referring URLs</li>
                <li><strong>Cookies:</strong> Session cookies and analytics cookies (see Cookie Policy below)</li>
              </ul>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">2. How We Use Your Information</h2>
              <p className="text-gray-600 mb-4">We use collected information to:</p>
              <ul className="list-disc pl-6 text-gray-600 mb-4 space-y-2">
                <li>Provide, maintain, and improve our services</li>
                <li>Process transactions and send related information</li>
                <li>Send you technical notices, updates, and support messages</li>
                <li>Respond to your comments, questions, and requests</li>
                <li>Personalize your experience and provide relevant opportunities</li>
                <li>Train and improve our AI models (using anonymized data)</li>
                <li>Monitor and analyze trends, usage, and activities</li>
                <li>Detect, investigate, and prevent fraudulent transactions</li>
                <li>Comply with legal obligations</li>
              </ul>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">3. Information Sharing</h2>
              <p className="text-gray-600 mb-4">We may share your information with:</p>
              <ul className="list-disc pl-6 text-gray-600 mb-4 space-y-2">
                <li><strong>Service Providers:</strong> Third-party vendors who assist in operating our platform (hosting, analytics, payment processing)</li>
                <li><strong>Expert Network:</strong> When you engage with experts, we share necessary contact and project information</li>
                <li><strong>Legal Requirements:</strong> When required by law or to protect our rights</li>
                <li><strong>Business Transfers:</strong> In connection with any merger, acquisition, or sale of assets</li>
              </ul>
              <p className="text-gray-600 mb-4">
                <strong>We do not sell your personal information to third parties.</strong>
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">4. Data Security</h2>
              <p className="text-gray-600 mb-4">
                We implement appropriate technical and organizational security measures to protect your data:
              </p>
              <ul className="list-disc pl-6 text-gray-600 mb-4 space-y-2">
                <li>SSL/TLS encryption for data in transit</li>
                <li>Encryption at rest for sensitive data</li>
                <li>Regular security assessments and audits</li>
                <li>Access controls and authentication requirements</li>
                <li>Employee training on data protection</li>
              </ul>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">5. Your Rights and Choices</h2>
              
              <div className="bg-purple-50 rounded-xl p-6 my-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <UserCheck className="w-5 h-5 text-purple-600" />
                  Your Data Rights
                </h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="flex items-start gap-3">
                    <Eye className="w-5 h-5 text-purple-600 mt-0.5" />
                    <div>
                      <div className="font-medium text-gray-900">Access</div>
                      <div className="text-sm text-gray-600">Request a copy of your personal data</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Lock className="w-5 h-5 text-purple-600 mt-0.5" />
                    <div>
                      <div className="font-medium text-gray-900">Correction</div>
                      <div className="text-sm text-gray-600">Update inaccurate or incomplete data</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Trash2 className="w-5 h-5 text-purple-600 mt-0.5" />
                    <div>
                      <div className="font-medium text-gray-900">Deletion</div>
                      <div className="text-sm text-gray-600">Request deletion of your data</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Bell className="w-5 h-5 text-purple-600 mt-0.5" />
                    <div>
                      <div className="font-medium text-gray-900">Opt-Out</div>
                      <div className="text-sm text-gray-600">Unsubscribe from marketing communications</div>
                    </div>
                  </div>
                </div>
              </div>

              <p className="text-gray-600 mb-4">
                To exercise these rights, please contact us at privacy@oppgrid.com or through your account settings.
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">6. Cookies and Tracking</h2>
              <p className="text-gray-600 mb-4">We use cookies and similar technologies to:</p>
              <ul className="list-disc pl-6 text-gray-600 mb-4 space-y-2">
                <li><strong>Essential Cookies:</strong> Required for the platform to function properly</li>
                <li><strong>Analytics Cookies:</strong> Help us understand how you use OppGrid</li>
                <li><strong>Preference Cookies:</strong> Remember your settings and preferences</li>
              </ul>
              <p className="text-gray-600 mb-4">
                You can manage cookie preferences through your browser settings. Note that disabling 
                certain cookies may affect platform functionality.
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">7. Data Retention</h2>
              <p className="text-gray-600 mb-4">
                We retain your personal data for as long as your account is active or as needed to 
                provide services. After account deletion, we may retain certain information as 
                required by law or for legitimate business purposes (such as fraud prevention).
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">8. International Data Transfers</h2>
              <p className="text-gray-600 mb-4">
                Your information may be transferred to and processed in countries other than your 
                country of residence. We ensure appropriate safeguards are in place for such 
                transfers in compliance with applicable data protection laws.
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">9. Children's Privacy</h2>
              <p className="text-gray-600 mb-4">
                OppGrid is not intended for users under 18 years of age. We do not knowingly collect 
                personal information from children. If you believe we have collected data from a 
                child, please contact us immediately.
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">10. California Privacy Rights (CCPA)</h2>
              <p className="text-gray-600 mb-4">
                California residents have additional rights under the California Consumer Privacy Act:
              </p>
              <ul className="list-disc pl-6 text-gray-600 mb-4 space-y-2">
                <li>Right to know what personal information is collected</li>
                <li>Right to know whether personal information is sold or disclosed</li>
                <li>Right to say no to the sale of personal information</li>
                <li>Right to equal service and price</li>
              </ul>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">11. European Privacy Rights (GDPR)</h2>
              <p className="text-gray-600 mb-4">
                If you are in the European Economic Area, you have rights under the General Data 
                Protection Regulation, including access, rectification, erasure, restriction, 
                portability, and objection. Our legal basis for processing is typically consent, 
                contractual necessity, or legitimate interests.
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">12. Changes to This Policy</h2>
              <p className="text-gray-600 mb-4">
                We may update this Privacy Policy from time to time. We will notify you of any 
                material changes by posting the new policy on this page and updating the "Last 
                updated" date. We encourage you to review this policy periodically.
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">13. Contact Us</h2>
              <p className="text-gray-600 mb-4">
                If you have questions about this Privacy Policy or our data practices, please contact us:
              </p>
              <div className="bg-gray-50 rounded-lg p-4 text-gray-600">
                <p>OppGrid, Inc.</p>
                <p>Email: privacy@oppgrid.com</p>
                <p>Address: San Francisco, CA</p>
              </div>
              <p className="text-gray-600 mt-4">
                For GDPR-related inquiries, you may also contact our Data Protection Officer at dpo@oppgrid.com.
              </p>
            </div>
          </div>

          <div className="mt-8 text-center">
            <p className="text-gray-600 mb-4">
              Have questions about your privacy?
            </p>
            <Link 
              to="/contact" 
              className="inline-flex items-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition-colors"
            >
              Contact Us
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
