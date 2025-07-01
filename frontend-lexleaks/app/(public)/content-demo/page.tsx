'use client'

import Link from 'next/link'
import { useState } from 'react'
import TypewriterTitle from '@/components/TypewriterTitle'
import ThemeToggle from '@/components/ThemeToggle'
import SearchFilter, { FilterState } from '@/components/SearchFilter'
import ImpactTracker from '@/components/ImpactTracker'
import DocumentViewer from '@/components/DocumentViewer'
import LanguageSelector from '@/components/LanguageSelector'

// Mock data for demonstration
const mockImpacts = [
  { id: 'impact1', title: 'Judicial Inquiry Launched', description: 'Following our report, the Judicial Conduct Committee has launched a formal investigation into Judge Harrison\'s financial disclosures.', date: '2025-02-15', type: 'investigation' as const, status: 'in_progress' as const, relatedPostId: 1 },
  { id: 'impact2', title: 'New Disclosure Law Proposed', description: 'A new bill has been proposed in the state legislature requiring stricter financial disclosures from all public officials, citing our report as a key driver.', date: '2025-03-01', type: 'policy_change' as const, status: 'pending' as const, relatedPostId: 1 },
  { id: 'impact3', title: 'Firm Partner Resigns', description: 'A senior partner at the implicated law firm has resigned amidst the fallout from the leak.', date: '2025-02-20', type: 'resignation' as const, status: 'completed' as const, relatedPostId: 2 },
  { id: 'impact4', title: 'Class Action Lawsuit Filed', description: 'A class action lawsuit has been filed against Titan Industries on behalf of the affected residents.', date: '2025-04-10', type: 'legal_action' as const, status: 'in_progress' as const, relatedPostId: 1 },
]

const mockDocumentUrl = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

export default function ContentDemoPage() {
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [searchLoading, setSearchLoading] = useState(false)

  const handleSearch = (filters: FilterState) => {
    setSearchLoading(true)
    console.log('Searching with filters:', filters)
    // Simulate API call
    setTimeout(() => {
      setSearchResults([
        { id: 1, title: 'Search Result 1', excerpt: 'This is a filtered search result...' },
        { id: 2, title: 'Search Result 2', excerpt: 'This is another filtered search result...' },
      ])
      setSearchLoading(false)
    }, 1000)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header Section */}
      <header className="main-header">
        <TypewriterTitle text="CONTENT FEATURES" className="main-title" delay={100} />
        <p className="main-subtitle">Showcasing Advanced Content Capabilities</p>
      </header>

      {/* Navigation & Theme Toggle */}
      <div className="flex flex-col sm:flex-row justify-between items-center mb-16">
        <nav className="main-nav space-x-6 text-sm mb-6 sm:mb-0">
          <Link href="/" className="nav-link">Home</Link>
          <Link href="/demo" className="nav-link">Visual Demo</Link>
          <Link href="/content-demo" className="nav-link font-bold">Content Demo</Link>
        </nav>
        <div className="flex items-center gap-4">
          <LanguageSelector />
          <ThemeToggle />
        </div>
      </div>

      {/* Main Content */}
      <main className="space-y-16">
        {/* Search & Filters Section */}
        <section>
          <h2 className="text-3xl font-bold mb-6 brand-accent">Search & Filters</h2>
          <SearchFilter onSearch={handleSearch} loading={searchLoading} />
          {searchLoading ? (
            <div className="text-center">Loading search results...</div>
          ) : (
            searchResults.length > 0 && (
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <h4 className="font-semibold mb-2">Search Results:</h4>
                <ul className="space-y-2">
                  {searchResults.map(result => (
                    <li key={result.id} className="p-2 border-l-2 border-primary-500">
                      <strong>{result.title}</strong> - {result.excerpt}
                    </li>
                  ))}
                </ul>
              </div>
            )
          )}
        </section>

        {/* Impact Tracking Section */}
        <section>
          <h2 className="text-3xl font-bold mb-6 brand-accent">Impact Tracking</h2>
          <ImpactTracker impacts={mockImpacts} />
        </section>

        {/* Document Viewer Section */}
        <section>
          <h2 className="text-3xl font-bold mb-6 brand-accent">Document Viewer</h2>
          <DocumentViewer 
            documentUrl={mockDocumentUrl} 
            title="Exhibit A: Financial Records"
            allowRedaction={true}
          />
        </section>

        {/* Multi-language Support Section */}
        <section>
          <h2 className="text-3xl font-bold mb-6 brand-accent">Multi-language Support</h2>
          <p className="text-lg mb-4">
            Use the language selector in the top navigation to switch languages. 
            This demonstrates the UI for language selection; a full i18n implementation would be needed for content translation.
          </p>
          <div className="p-6 border-2 brand-border rounded-lg text-center">
            <h3 className="font-bold text-xl mb-2">Current Language</h3>
            <p>Check the top-right corner to see the language selector in action.</p>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="main-footer mt-16">
        <p className="footer-text">&copy; 2025 LexLeaks. Content Features Demo</p>
      </footer>
    </div>
  )
} 