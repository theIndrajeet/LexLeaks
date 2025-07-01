'use client'

import { useState } from 'react'
import Link from 'next/link'
import TypewriterTitle from '@/components/TypewriterTitle'
import ThemeToggle from '@/components/ThemeToggle'
import StatusBadge from '@/components/StatusBadge'
import LanguageSelector from '@/components/LanguageSelector'
import SearchFilter from '@/components/SearchFilter'
import ImpactTracker from '@/components/ImpactTracker'
import DocumentViewer from '@/components/DocumentViewer'
import PostCard from '@/components/PostCard'

export default function DemoPage() {
  const [searchResults, setSearchResults] = useState<any>(null)

  // Demo data
  const demoPost = {
    id: 1,
    title: "Law Firm's Secret Commission Deal with Litigation Funders",
    slug: "law-firms-secret-commission-deal",
    excerpt: "Internal documents reveal major law firm taking undisclosed commissions from litigation funding arrangements, creating serious conflicts of interest.",
    status: "published",
    category: "corporate",
    published_at: new Date().toISOString(),
    created_at: new Date().toISOString(),
    author: {
      id: 1,
      username: "investigator"
    }
  }

  const demoImpacts = [
    {
      id: 1,
      title: "State Bar Investigation Launched",
      description: "Following our exposé, the State Bar Association announced a formal investigation into the law firm's undisclosed commission arrangements with litigation funders.",
      date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      type: "investigation" as const,
      status: "in_progress" as const,
      post_id: 1,
      created_at: new Date().toISOString()
    },
    {
      id: 2,
      title: "Managing Partner Resignation",
      description: "The managing partner implicated in the scheme resigned from their position, citing 'personal reasons' in their departure statement.",
      date: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
      type: "resignation" as const,
      status: "completed" as const,
      post_id: 1,
      created_at: new Date().toISOString()
    },
    {
      id: 3,
      title: "New Ethics Guidelines Proposed",
      description: "The American Bar Association announced proposed amendments to ethics rules specifically addressing litigation funding disclosure requirements.",
      date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      type: "policy_change" as const,
      status: "pending" as const,
      post_id: 1,
      created_at: new Date().toISOString()
    }
  ]

  const handleSearch = (filters: any) => {
    setSearchResults(filters)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <header className="main-header mb-8">
        <TypewriterTitle text="LEXLEAKS DEMO" className="main-title" delay={100} />
        <p className="main-subtitle">Component Showcase</p>
      </header>

      {/* Navigation */}
      <div className="flex flex-col sm:flex-row justify-between items-center mb-16">
        <nav className="main-nav space-x-6 text-sm mb-6 sm:mb-0">
          <Link href="/" className="nav-link">Home</Link>
          <Link href="/about" className="nav-link">About</Link>
          <Link href="/archive" className="nav-link">Archive</Link>
          <Link href="/demo" className="nav-link font-bold">Demo</Link>
        </nav>
        <div className="flex items-center gap-4">
          <LanguageSelector />
          <ThemeToggle />
        </div>
      </div>

      <main className="space-y-16">
        {/* Status Badges Section */}
        <section>
          <h2 className="text-2xl font-bold mb-6">Status Badges</h2>
          <div className="flex flex-wrap gap-4">
            <StatusBadge type="breaking" />
            <StatusBadge type="exclusive" />
            <StatusBadge type="verified" />
            <StatusBadge type="new" />
            <StatusBadge type="updated" />
          </div>
        </section>

        {/* Search & Filter Section */}
        <section>
          <h2 className="text-2xl font-bold mb-6">Search & Filter Component</h2>
          <SearchFilter onSearch={handleSearch} />
          {searchResults && (
            <div className="mt-4 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
              <p className="text-sm font-mono">Search Results:</p>
              <pre className="text-xs mt-2">{JSON.stringify(searchResults, null, 2)}</pre>
            </div>
          )}
        </section>

        {/* Post Card Section */}
        <section>
          <h2 className="text-2xl font-bold mb-6">Post Card Component</h2>
          <div className="max-w-2xl">
            <PostCard post={demoPost} showStatus={true} />
          </div>
        </section>

        {/* Impact Tracker Section */}
        <section>
          <h2 className="text-2xl font-bold mb-6">Impact Tracker Component</h2>
          <div className="max-w-4xl">
            <ImpactTracker impacts={demoImpacts} />
          </div>
        </section>

        {/* Document Viewer Section */}
        <section>
          <h2 className="text-2xl font-bold mb-6">Document Viewer Component</h2>
          <div className="max-w-4xl space-y-6">
            {/* Regular Document Viewer */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Standard Document Viewer</h3>
              <DocumentViewer
                documentUrl="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
                title="Sample Document"
              />
            </div>

            {/* Document Viewer with Pre-defined Redactions */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Document with Redactions</h3>
              <DocumentViewer
                documentUrl="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
                title="Redacted Evidence"
                redactedSections={[
                  { id: '1', page: 1, x: 100, y: 150, width: 300, height: 50 },
                  { id: '2', page: 1, x: 150, y: 250, width: 250, height: 30 }
                ]}
              />
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                This document has pre-defined redactions to protect sensitive information. 
                In production, these would be loaded from your database.
              </p>
            </div>

            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <p className="text-sm text-blue-800 dark:text-blue-300">
                <strong>Admin Feature:</strong> Admins can enable interactive redaction mode by setting 
                <code className="mx-1 px-2 py-1 bg-blue-100 dark:bg-blue-800 rounded">allowRedaction={`{true}`}</code>
                on the DocumentViewer component. See the admin redaction demo at 
                <Link href="/admin/redaction-demo" className="ml-1 underline">/admin/redaction-demo</Link>
              </p>
            </div>
          </div>
        </section>

        {/* Typography Examples */}
        <section>
          <h2 className="text-2xl font-bold mb-6">Typography Enhancements</h2>
          <div className="prose prose-lg dark:prose-invert max-w-none">
            <p className="drop-cap">
              This paragraph demonstrates the drop cap style that's automatically applied to the first paragraph of articles. 
              The large initial letter creates a classic newspaper feel that fits perfectly with the LexLeaks brand.
            </p>
            <blockquote className="pull-quote">
              "Pull quotes like this one can be used to highlight important statements or key findings from leaked documents."
            </blockquote>
            <p>
              Regular paragraphs maintain excellent readability with carefully chosen typography settings, including 
              proper line height and spacing for both light and dark modes.
            </p>
          </div>
        </section>

        {/* Color Palette */}
        <section>
          <h2 className="text-2xl font-bold mb-6">Color Palette & Dark Mode</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="w-full h-24 bg-primary-600 rounded-lg mb-2"></div>
              <p className="text-sm">Primary</p>
            </div>
            <div className="text-center">
              <div className="w-full h-24 bg-secondary-600 rounded-lg mb-2"></div>
              <p className="text-sm">Secondary</p>
            </div>
            <div className="text-center">
              <div className="w-full h-24 bg-gray-900 dark:bg-gray-100 rounded-lg mb-2"></div>
              <p className="text-sm">Text</p>
            </div>
            <div className="text-center">
              <div className="w-full h-24 bg-red-600 rounded-lg mb-2"></div>
              <p className="text-sm">Accent</p>
            </div>
          </div>
          <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
            Toggle between light and dark modes using the button in the navigation to see how all components adapt.
          </p>
        </section>
      </main>

      {/* Footer */}
      <footer className="main-footer">
        <p className="footer-text">&copy; 2025 LexLeaks. All Rights Reserved.</p>
        <p className="footer-text mt-1">Component showcase for development purposes.</p>
      </footer>
    </div>
  )
} 