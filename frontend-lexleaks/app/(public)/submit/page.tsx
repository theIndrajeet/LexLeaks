'use client'

import Link from 'next/link'
import ThemeToggle from '@/components/ThemeToggle'

export default function SubmitPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header Section */}
      <header className="main-header">
        <h1 className="main-title">LEXLEAKS</h1>
        <p className="main-subtitle">Exposing the Fine Print.</p>
      </header>

      {/* Navigation & Submit Button */}
      <div className="flex flex-col sm:flex-row justify-between items-center mb-16">
        <nav className="main-nav space-x-6 text-sm mb-6 sm:mb-0">
          <Link href="/" className="nav-link">Home</Link>
          <Link href="/about" className="nav-link">About</Link>
          <Link href="/archive" className="nav-link">Archive</Link>
        </nav>
        <div className="flex items-center gap-4">
          <Link href="/submit" className="brand-button">
            Submit a Leak
          </Link>
          
          <ThemeToggle />
        </div>
      </div>

      {/* Main Content */}
      <main>
        <article className="mb-16">
          {/* Page Title */}
          <div className="case-file">
            <span>Document: Submission Guidelines</span>
            {' | '}
            <span>Classification: Confidential</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-8 brand-text">
            Submit Your Leak
          </h1>

          {/* Important Notice */}
          <div className="border-l-4 brand-border pl-6 mb-12">
            <p className="text-xl italic leading-relaxed text-gray-600">
              "Your identity is sacred to us. We use military-grade encryption and secure 
              submission systems to protect our sources."
            </p>
          </div>

          {/* Submission Guidelines */}
          <div className="prose prose-lg max-w-none text-justify leading-relaxed mb-12">
            <h2 className="text-2xl font-bold mb-6 brand-accent">Before You Submit</h2>
            
            <p className="mb-6">
              LexLeaks is dedicated to exposing corruption, misconduct, and unethical practices 
              in the legal industry. We take the security of our sources extremely seriously and 
              have implemented multiple layers of protection.
            </p>

            <h3 className="text-xl font-bold mb-4 font-mono-special uppercase tracking-wide">What We're Looking For</h3>
            <ul className="space-y-2 mb-8">
              <li>• Evidence of legal malpractice or professional misconduct</li>
              <li>• Judicial corruption or conflicts of interest</li>
              <li>• Law firm fraud or unethical billing practices</li>
              <li>• Bar association cover-ups or regulatory failures</li>
              <li>• Systematic discrimination or harassment in legal institutions</li>
              <li>• Violations of attorney-client privilege</li>
              <li>• Any documented wrongdoing that serves the public interest</li>
            </ul>

            <h3 className="text-xl font-bold mb-4 font-mono-special uppercase tracking-wide">Security Recommendations</h3>
            <ol className="space-y-2 mb-8">
              <li>1. Use a secure, anonymous connection (Tor recommended)</li>
              <li>2. Create a new, anonymous email address for communication</li>
              <li>3. Remove metadata from all documents before submission</li>
              <li>4. Do not submit from work computers or networks</li>
              <li>5. Consider using a public WiFi connection</li>
              <li>6. Never include personally identifying information unless necessary</li>
            </ol>

            <h2 className="text-2xl font-bold mb-6 brand-accent mt-12">Submission Methods</h2>

            <div className="space-y-8">
              <div className="border-2 brand-border rounded-lg p-6">
                <h3 className="text-xl font-bold mb-3 font-mono-special">Method 1: Secure Web Form</h3>
                <p className="mb-4">
                  Our secure submission form is currently being upgraded to ensure maximum protection. 
                  Please use one of the alternative methods below in the meantime.
                </p>
                <p className="text-sm italic text-gray-600">
                  Expected availability: Coming soon
                </p>
              </div>

              <div className="border-2 brand-border rounded-lg p-6">
                <h3 className="text-xl font-bold mb-3 font-mono-special">Method 2: Encrypted Email</h3>
                <p className="mb-4">
                  Send encrypted emails to: <span className="font-mono-special font-bold">tips@lexleaks.secure</span>
                </p>
                <p className="mb-4">
                  Our PGP public key fingerprint:<br />
                  <span className="font-mono-special text-sm">
                    4A7B 9E2F 8C1D 3F6A 5B9C 2D1E 7F8A 6C4B E9D3
                  </span>
                </p>
                <p className="text-sm">
                  Download our full PGP public key from our secure server.
                </p>
              </div>

              <div className="border-2 brand-border rounded-lg p-6">
                <h3 className="text-xl font-bold mb-3 font-mono-special">Method 3: Physical Mail</h3>
                <p className="mb-4">
                  For extremely sensitive physical documents, mail to:
                </p>
                <p className="font-mono-special text-sm">
                  LexLeaks<br />
                  P.O. Box 7734<br />
                  Station A<br />
                  Toronto, ON M5W 1X5<br />
                  Canada
                </p>
                <p className="text-sm mt-4 italic">
                  Use gloves when handling documents. Do not include return addresses.
                </p>
              </div>
            </div>

            <h2 className="text-2xl font-bold mb-6 brand-accent mt-12">What Happens Next</h2>
            
            <ol className="space-y-4">
              <li>
                <strong>1. Initial Review:</strong> Our security team reviews all submissions for authenticity and relevance.
              </li>
              <li>
                <strong>2. Verification:</strong> We verify claims through multiple independent sources and documentation.
              </li>
              <li>
                <strong>3. Legal Review:</strong> Our legal team ensures publication serves the public interest.
              </li>
              <li>
                <strong>4. Source Protection:</strong> All identifying information is removed or encrypted.
              </li>
              <li>
                <strong>5. Publication:</strong> Stories are published with maximum impact while protecting sources.
              </li>
            </ol>

            <div className="border-2 border-red-300 bg-red-50 rounded-lg p-6 mt-12">
              <h3 className="text-xl font-bold mb-3 text-red-800">Important Warning</h3>
              <p className="text-red-700">
                Do not submit false information. We thoroughly verify all claims and will 
                pursue legal action against those who attempt to use our platform for 
                defamation or false accusations.
              </p>
            </div>
          </div>

          {/* Back to Stories Link */}
          <div className="mt-12 pt-8 border-t-2 brand-border">
            <Link
              href="/"
              className="read-more hover:underline"
            >
              ← Back to All Stories
            </Link>
          </div>
        </article>

        {/* Contact Support */}
        <div className="border-2 brand-border rounded-lg p-8 text-center">
          <h3 className="text-2xl font-bold mb-4">Need Help?</h3>
          <p className="text-lg leading-relaxed mb-6">
            If you have questions about the submission process or need technical assistance, 
            our security team is here to help. Remember: your safety is our priority.
          </p>
          <p className="font-mono-special">
            Secure contact: security@lexleaks.secure
          </p>
        </div>
      </main>

      {/* Footer */}
      <footer className="main-footer">
        <p className="footer-text">&copy; 2025 LexLeaks. All Rights Reserved.</p>
        <p className="footer-text mt-1">Dedicated to transparency and accountability in the legal industry.</p>
      </footer>
    </div>
  )
} 