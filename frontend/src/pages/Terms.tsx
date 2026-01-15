import { Link } from 'react-router-dom'

export default function Terms() {
  const lastUpdated = 'January 1, 2026'

  return (
    <div className="min-h-screen bg-gray-50">
      <section className="bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 text-white py-16">
        <div className="max-w-4xl mx-auto px-6">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Terms of Service</h1>
          <p className="text-purple-100">Last updated: {lastUpdated}</p>
        </div>
      </section>

      <section className="py-16">
        <div className="max-w-4xl mx-auto px-6">
          <div className="bg-white rounded-2xl border border-gray-200 p-8 md:p-12">
            <div className="prose prose-gray max-w-none">
              <p className="text-lg text-gray-600 mb-8">
                Welcome to OppGrid. By accessing or using our platform, you agree to be bound by these Terms of Service. 
                Please read them carefully before using our services.
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">1. Acceptance of Terms</h2>
              <p className="text-gray-600 mb-4">
                By creating an account or using OppGrid's services, you acknowledge that you have read, understood, 
                and agree to be bound by these Terms of Service, our Privacy Policy, and any additional terms that 
                may apply to specific features or services.
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">2. Description of Services</h2>
              <p className="text-gray-600 mb-4">
                OppGrid provides an AI-powered opportunity intelligence platform that includes:
              </p>
              <ul className="list-disc pl-6 text-gray-600 mb-4 space-y-2">
                <li>Business opportunity discovery and analysis tools</li>
                <li>Market research and validation frameworks</li>
                <li>Expert network and consultation services</li>
                <li>Funding discovery and SBA loan program information</li>
                <li>AI-powered insights and recommendations</li>
                <li>Collaboration and workspace tools</li>
              </ul>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">3. Account Registration</h2>
              <p className="text-gray-600 mb-4">
                To access certain features, you must create an account. You agree to:
              </p>
              <ul className="list-disc pl-6 text-gray-600 mb-4 space-y-2">
                <li>Provide accurate, current, and complete information</li>
                <li>Maintain and update your account information</li>
                <li>Keep your password secure and confidential</li>
                <li>Accept responsibility for all activities under your account</li>
                <li>Notify us immediately of any unauthorized access</li>
              </ul>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">4. Subscription and Payments</h2>
              <p className="text-gray-600 mb-4">
                OppGrid offers various subscription tiers (Explorer, Builder, Scaler, Enterprise) with different 
                features and pricing. By subscribing, you agree to:
              </p>
              <ul className="list-disc pl-6 text-gray-600 mb-4 space-y-2">
                <li>Pay all applicable fees based on your chosen plan</li>
                <li>Automatic renewal unless cancelled before the renewal date</li>
                <li>Price changes with 30 days advance notice</li>
                <li>No refunds for partial subscription periods unless required by law</li>
              </ul>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">5. Pay-Per-Unlock and One-Time Purchases</h2>
              <p className="text-gray-600 mb-4">
                Certain reports, analyses, and premium content may be available for one-time purchase. 
                Once unlocked, content access is subject to our time-decay access policies. All purchases 
                are final and non-refundable unless the content is materially defective.
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">6. Expert Network Services</h2>
              <p className="text-gray-600 mb-4">
                When engaging with experts through our platform:
              </p>
              <ul className="list-disc pl-6 text-gray-600 mb-4 space-y-2">
                <li>Experts are independent contractors, not OppGrid employees</li>
                <li>OppGrid facilitates connections but does not guarantee outcomes</li>
                <li>Payment for expert services is processed through our platform</li>
                <li>Disputes should first be addressed through our resolution process</li>
              </ul>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">7. Acceptable Use</h2>
              <p className="text-gray-600 mb-4">You agree not to:</p>
              <ul className="list-disc pl-6 text-gray-600 mb-4 space-y-2">
                <li>Use the service for any unlawful purpose</li>
                <li>Attempt to gain unauthorized access to any part of the service</li>
                <li>Interfere with or disrupt the service or servers</li>
                <li>Scrape, copy, or redistribute our content without permission</li>
                <li>Use automated systems to access the service without our consent</li>
                <li>Impersonate any person or entity</li>
                <li>Share account credentials with unauthorized users</li>
              </ul>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">8. Intellectual Property</h2>
              <p className="text-gray-600 mb-4">
                All content, features, and functionality of OppGrid are owned by us and protected by 
                intellectual property laws. You may not reproduce, distribute, or create derivative 
                works without our express written permission.
              </p>
              <p className="text-gray-600 mb-4">
                You retain ownership of any content you submit to OppGrid but grant us a license to 
                use, store, and display that content as necessary to provide our services.
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">9. Disclaimer of Warranties</h2>
              <p className="text-gray-600 mb-4">
                OppGrid is provided "as is" without warranties of any kind. We do not guarantee:
              </p>
              <ul className="list-disc pl-6 text-gray-600 mb-4 space-y-2">
                <li>The accuracy or completeness of opportunity analyses</li>
                <li>Business success or investment returns</li>
                <li>Uninterrupted or error-free service</li>
                <li>Results from expert consultations</li>
              </ul>
              <p className="text-gray-600 mb-4">
                Our AI-generated insights are for informational purposes only and should not be 
                considered professional financial, legal, or business advice.
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">10. Limitation of Liability</h2>
              <p className="text-gray-600 mb-4">
                To the maximum extent permitted by law, OppGrid shall not be liable for any indirect, 
                incidental, special, consequential, or punitive damages, including loss of profits, 
                data, or business opportunities, arising from your use of our services.
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">11. Indemnification</h2>
              <p className="text-gray-600 mb-4">
                You agree to indemnify and hold OppGrid harmless from any claims, damages, or expenses 
                arising from your use of the service, violation of these terms, or infringement of 
                any third-party rights.
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">12. Termination</h2>
              <p className="text-gray-600 mb-4">
                We may suspend or terminate your account at any time for violations of these terms. 
                You may cancel your account at any time. Upon termination, your right to use the 
                service ceases immediately.
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">13. Changes to Terms</h2>
              <p className="text-gray-600 mb-4">
                We may update these Terms of Service from time to time. We will notify you of 
                material changes via email or through the platform. Continued use after changes 
                constitutes acceptance of the new terms.
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">14. Governing Law</h2>
              <p className="text-gray-600 mb-4">
                These Terms shall be governed by the laws of the State of California, without 
                regard to conflict of law principles. Any disputes shall be resolved in the 
                courts of San Francisco County, California.
              </p>

              <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">15. Contact Information</h2>
              <p className="text-gray-600 mb-4">
                For questions about these Terms of Service, please contact us at:
              </p>
              <div className="bg-gray-50 rounded-lg p-4 text-gray-600">
                <p>OppGrid, Inc.</p>
                <p>Email: legal@oppgrid.com</p>
                <p>Address: San Francisco, CA</p>
              </div>
            </div>
          </div>

          <div className="mt-8 text-center">
            <p className="text-gray-600 mb-4">
              Have questions about our terms?
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
