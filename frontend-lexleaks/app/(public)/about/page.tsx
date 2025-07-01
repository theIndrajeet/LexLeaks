import { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'About LexLeaks',
  description: 'Learn about LexLeaks mission to expose corruption and promote transparency in the legal industry.',
}

export default function AboutPage() {
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
          <Link href="/about" className="nav-link brand-accent font-bold">About</Link>
          <Link href="/archive" className="nav-link">Archive</Link>
        </nav>
        <Link href="/submit" className="brand-button">
          Submit a Leak
        </Link>
      </div>

      {/* Main Content */}
      <main>
        <article className="mb-16">
          {/* Page Title */}
          <div className="case-file">
            <span>Document: About LexLeaks</span>
            {' | '}
            <span>Classification: Public</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-8 brand-text">
            Our Mission: Truth in the Legal Industry
          </h1>

          {/* Mission Statement */}
          <div className="border-l-4 brand-border pl-6 mb-12">
            <p className="text-xl italic leading-relaxed text-gray-600">
              "The legal profession, built on principles of justice and truth, sometimes falls short of its own ideals. 
              LexLeaks exists to bridge that gap through secure, anonymous whistleblowing."
            </p>
          </div>

          {/* Main Content */}
          <div className="prose prose-lg max-w-none text-justify leading-relaxed mb-12">
            <h2 className="text-2xl font-bold mb-6 brand-accent">Why We Exist</h2>
            
            <p className="mb-6">
              The legal system is the cornerstone of a just society. When that system is corrupted by greed, bias, 
              or misconduct, the very foundations of justice are undermined. We believe that transparency is not just 
              beneficial—it is essential for maintaining public trust in our legal institutions.
            </p>

            <p className="mb-6">
              Every day, legal professionals witness or become aware of wrongdoing within their firms, courts, 
              or regulatory bodies. Yet many remain silent, fearing retaliation, career damage, or professional 
              ostracism. LexLeaks provides a secure platform where truth can emerge without these fears.
            </p>

            <h2 className="text-2xl font-bold mb-6 brand-accent mt-12">What We Investigate</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              <div>
                <h3 className="text-lg font-bold mb-4 font-mono-special uppercase tracking-wide">Professional Misconduct</h3>
                <ul className="space-y-2 text-base">
                  <li>• Breach of client confidentiality</li>
                  <li>• Conflicts of interest</li>
                  <li>• Fraudulent billing practices</li>
                  <li>• Incompetent representation</li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-lg font-bold mb-4 font-mono-special uppercase tracking-wide">Institutional Corruption</h3>
                <ul className="space-y-2 text-base">
                  <li>• Judicial misconduct</li>
                  <li>• Case fixing or manipulation</li>
                  <li>• Bribery and kickbacks</li>
                  <li>• Systematic bias</li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-lg font-bold mb-4 font-mono-special uppercase tracking-wide">Firm Practices</h3>
                <ul className="space-y-2 text-base">
                  <li>• Workplace harassment</li>
                  <li>• Unethical business practices</li>
                  <li>• Client fund misappropriation</li>
                  <li>• Cover-up of misconduct</li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-lg font-bold mb-4 font-mono-special uppercase tracking-wide">Regulatory Issues</h3>
                <ul className="space-y-2 text-base">
                  <li>• Bar association misconduct</li>
                  <li>• Inadequate disciplinary actions</li>
                  <li>• Regulatory capture</li>
                  <li>• Policy manipulation</li>
                </ul>
              </div>
            </div>

            <h2 className="text-2xl font-bold mb-6 brand-accent mt-12">Our Core Principles</h2>

            <div className="space-y-8">
              <div className="border-2 brand-border rounded-lg p-6">
                <h3 className="text-xl font-bold mb-3 font-mono-special">Security First</h3>
                <p>
                  We employ military-grade encryption, anonymous submission systems, and rigorous operational 
                  security to protect our sources. Your identity is sacred to us.
                </p>
              </div>

              <div className="border-2 brand-border rounded-lg p-6">
                <h3 className="text-xl font-bold mb-3 font-mono-special">Rigorous Verification</h3>
                <p>
                  Every submission undergoes thorough fact-checking and verification. We cross-reference 
                  claims with multiple sources and evidence before publication.
                </p>
              </div>

              <div className="border-2 brand-border rounded-lg p-6">
                <h3 className="text-xl font-bold mb-3 font-mono-special">Maximum Impact</h3>
                <p>
                  We focus on stories that can create meaningful change and improve accountability 
                  in the legal system. Every published leak serves the public interest.
                </p>
              </div>
            </div>

            <p className="mt-12 text-lg">
              The legal profession has the power to shape society, protect the innocent, and deliver justice. 
              When that power is abused, we all suffer. By shining light on corruption and misconduct, 
              we can help restore integrity to the system that serves us all.
            </p>
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

        {/* Call to Action */}
        <div className="border-2 brand-border rounded-lg p-8 text-center">
          <h3 className="text-2xl font-bold mb-4">Ready to Expose the Truth?</h3>
          <p className="text-lg leading-relaxed mb-6">
            If you have information about corruption or misconduct in the legal industry, 
            we want to hear from you. Your courage can protect others and bring accountability 
            to those who abuse their power.
          </p>
          <Link href="/submit" className="brand-button">
            Submit Your Leak
          </Link>
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