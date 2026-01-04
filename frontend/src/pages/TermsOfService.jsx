import { Link } from 'react-router-dom'
import Logo from '../components/Logo'

function TermsOfService() {
  return (
    <div className="min-h-screen bg-white" style={{ fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif" }}>
      {/* Header */}
      <div className="border-b border-[#e5e7eb]">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <Link to="/" className="flex items-center gap-3">
            <Logo />
            <span className="text-xl font-semibold text-[#111827]">Aigis Marketing</span>
          </Link>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-6 py-12">
        <h1 className="text-4xl font-bold text-[#111827] mb-4">Terms of Service</h1>
        <p className="text-[#4b5563] mb-8">Last updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</p>

        <div className="prose prose-lg max-w-none space-y-6 text-[#111827]">
          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">1. Acceptance of Terms</h2>
            <p className="text-[#4b5563] leading-relaxed">
              By accessing and using Aigis Marketing ("Service"), you accept and agree to be bound by the terms and provision of this agreement. 
              If you do not agree to abide by the above, please do not use this service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">2. Use License</h2>
            <p className="text-[#4b5563] leading-relaxed mb-3">
              Permission is granted to temporarily use Aigis Marketing for personal, non-commercial transitory viewing only. This is the grant of a license, not a transfer of title, and under this license you may not:
            </p>
            <ul className="list-disc list-inside text-[#4b5563] space-y-2 ml-4">
              <li>Modify or copy the materials</li>
              <li>Use the materials for any commercial purpose or for any public display</li>
              <li>Attempt to reverse engineer any software contained on Aigis Marketing</li>
              <li>Remove any copyright or other proprietary notations from the materials</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">3. User Accounts</h2>
            <p className="text-[#4b5563] leading-relaxed">
              When you create an account with us, you must provide information that is accurate, complete, and current at all times. 
              You are responsible for safeguarding the password and for all activities that occur under your account.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">4. Content and Intellectual Property</h2>
            <p className="text-[#4b5563] leading-relaxed">
              The Service and its original content, features, and functionality are and will remain the exclusive property of Aigis Marketing 
              and its licensors. The Service is protected by copyright, trademark, and other laws.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">5. User-Generated Content</h2>
            <p className="text-[#4b5563] leading-relaxed">
              You retain ownership of any content you submit, post, or display on or through the Service. By submitting content, you grant us 
              a worldwide, non-exclusive, royalty-free license to use, reproduce, modify, and distribute such content for the purpose of operating 
              and providing the Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">6. Prohibited Uses</h2>
            <p className="text-[#4b5563] leading-relaxed mb-3">You may not use the Service:</p>
            <ul className="list-disc list-inside text-[#4b5563] space-y-2 ml-4">
              <li>In any way that violates any applicable national or international law or regulation</li>
              <li>To transmit, or procure the sending of, any advertising or promotional material without our prior written consent</li>
              <li>To impersonate or attempt to impersonate the company, a company employee, another user, or any other person or entity</li>
              <li>In any way that infringes upon the rights of others, or in any way is illegal, threatening, fraudulent, or harmful</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">7. Termination</h2>
            <p className="text-[#4b5563] leading-relaxed">
              We may terminate or suspend your account and bar access to the Service immediately, without prior notice or liability, 
              for any reason whatsoever, including without limitation if you breach the Terms.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">8. Disclaimer</h2>
            <p className="text-[#4b5563] leading-relaxed">
              The information on this Service is provided on an "as is" basis. To the fullest extent permitted by law, this Company excludes 
              all representations, warranties, conditions, and terms relating to our Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">9. Limitation of Liability</h2>
            <p className="text-[#4b5563] leading-relaxed">
              In no event shall Aigis Marketing, nor its directors, employees, partners, agents, suppliers, or affiliates, be liable for 
              any indirect, incidental, special, consequential, or punitive damages, including without limitation, loss of profits, data, use, 
              goodwill, or other intangible losses, resulting from your use of the Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">10. Changes to Terms</h2>
            <p className="text-[#4b5563] leading-relaxed">
              We reserve the right, at our sole discretion, to modify or replace these Terms at any time. If a revision is material, 
              we will provide at least 30 days notice prior to any new terms taking effect.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">11. Contact Information</h2>
            <p className="text-[#4b5563] leading-relaxed">
              If you have any questions about these Terms of Service, please contact us at:
            </p>
            <p className="text-[#1e293b] font-medium mt-2">
              Email: support@aigismarketing.com
            </p>
          </section>
        </div>

        {/* Footer Links */}
        <div className="mt-12 pt-8 border-t border-[#e5e7eb] flex gap-6 text-sm">
          <Link to="/privacy-policy" className="text-[#1e293b] hover:underline">Privacy Policy</Link>
          <Link to="/" className="text-[#1e293b] hover:underline">Home</Link>
        </div>
      </div>
    </div>
  )
}

export default TermsOfService









