import { Link } from 'react-router-dom'
import Logo from '../components/Logo'

function PrivacyPolicy() {
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
        <h1 className="text-4xl font-bold text-[#111827] mb-4">Privacy Policy</h1>
        <p className="text-[#4b5563] mb-8">Last updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</p>

        <div className="prose prose-lg max-w-none space-y-6 text-[#111827]">
          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">1. Introduction</h2>
            <p className="text-[#4b5563] leading-relaxed">
              Aigis Marketing ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, 
              use, disclose, and safeguard your information when you use our Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">2. Information We Collect</h2>
            <p className="text-[#4b5563] leading-relaxed mb-3">We collect information that you provide directly to us, including:</p>
            <ul className="list-disc list-inside text-[#4b5563] space-y-2 ml-4">
              <li><strong>Account Information:</strong> Username, email address, and password</li>
              <li><strong>Content:</strong> Documents, brand context, competitors, and marketing posts you create</li>
              <li><strong>Usage Data:</strong> Information about how you use our Service</li>
              <li><strong>Device Information:</strong> IP address, browser type, and device identifiers</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">3. How We Use Your Information</h2>
            <p className="text-[#4b5563] leading-relaxed mb-3">We use the information we collect to:</p>
            <ul className="list-disc list-inside text-[#4b5563] space-y-2 ml-4">
              <li>Provide, maintain, and improve our Service</li>
              <li>Process your transactions and send related information</li>
              <li>Send you technical notices and support messages</li>
              <li>Respond to your comments, questions, and requests</li>
              <li>Monitor and analyze trends, usage, and activities</li>
              <li>Detect, prevent, and address technical issues</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">4. Data Storage and Security</h2>
            <p className="text-[#4b5563] leading-relaxed">
              We implement appropriate technical and organizational security measures to protect your personal information. However, 
              no method of transmission over the Internet or electronic storage is 100% secure. While we strive to use commercially 
              acceptable means to protect your information, we cannot guarantee absolute security.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">5. Third-Party Services</h2>
            <p className="text-[#4b5563] leading-relaxed">
              We use third-party services to help us operate our Service, including but not limited to:
            </p>
            <ul className="list-disc list-inside text-[#4b5563] space-y-2 ml-4 mt-3">
              <li><strong>AI Services:</strong> OpenAI, Google Cloud (Imagen, Veo), and Hyperspell for content generation and memory storage</li>
              <li><strong>Hosting:</strong> Vercel for frontend hosting and Render for backend services</li>
              <li><strong>Integrations:</strong> Notion and Google Drive for content import</li>
            </ul>
            <p className="text-[#4b5563] leading-relaxed mt-3">
              These third parties have access to your information only to perform specific tasks on our behalf and are obligated not to 
              disclose or use it for any other purpose.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">6. Data Retention</h2>
            <p className="text-[#4b5563] leading-relaxed">
              We retain your personal information for as long as your account is active or as needed to provide you with our Service. 
              We will retain and use your information as necessary to comply with our legal obligations, resolve disputes, and enforce our agreements.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">7. Your Rights</h2>
            <p className="text-[#4b5563] leading-relaxed mb-3">You have the right to:</p>
            <ul className="list-disc list-inside text-[#4b5563] space-y-2 ml-4">
              <li>Access and receive a copy of your personal data</li>
              <li>Rectify inaccurate or incomplete personal data</li>
              <li>Request deletion of your personal data</li>
              <li>Object to processing of your personal data</li>
              <li>Request restriction of processing your personal data</li>
              <li>Data portability - receive your data in a structured format</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">8. Cookies and Tracking</h2>
            <p className="text-[#4b5563] leading-relaxed">
              We use cookies and similar tracking technologies to track activity on our Service and hold certain information. 
              You can instruct your browser to refuse all cookies or to indicate when a cookie is being sent.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">9. Children's Privacy</h2>
            <p className="text-[#4b5563] leading-relaxed">
              Our Service is not intended for children under the age of 13. We do not knowingly collect personal information from children 
              under 13. If you are a parent or guardian and believe your child has provided us with personal information, please contact us.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">10. Changes to This Privacy Policy</h2>
            <p className="text-[#4b5563] leading-relaxed">
              We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on 
              this page and updating the "Last updated" date.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-[#111827] mb-3">11. Contact Us</h2>
            <p className="text-[#4b5563] leading-relaxed">
              If you have any questions about this Privacy Policy, please contact us at:
            </p>
            <p className="text-[#1e293b] font-medium mt-2">
              Email: privacy@aigismarketing.com
            </p>
          </section>
        </div>

        {/* Footer Links */}
        <div className="mt-12 pt-8 border-t border-[#e5e7eb] flex gap-6 text-sm">
          <Link to="/terms-of-service" className="text-[#1e293b] hover:underline">Terms of Service</Link>
          <Link to="/" className="text-[#1e293b] hover:underline">Home</Link>
        </div>
      </div>
    </div>
  )
}

export default PrivacyPolicy

