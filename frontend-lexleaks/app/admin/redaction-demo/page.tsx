'use client'

import { useState } from 'react'
import Link from 'next/link'
import dynamic from 'next/dynamic'
import type { Redaction } from '@/components/DocumentViewer'

// Dynamic import for DocumentViewer to avoid SSR issues
const DocumentViewer = dynamic(() => import('@/components/DocumentViewer'), {
  ssr: false,
  loading: () => (
    <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-8 text-center">
      <p>Loading document viewer...</p>
    </div>
  )
})
import ThemeToggle from '@/components/ThemeToggle'

export default function RedactionDemoPage() {
  const [redactions, setRedactions] = useState<Redaction[]>([
    {
      id: 'sample-1',
      page: 1,
      x: 100,
      y: 100,
      width: 200,
      height: 50,
      reason: 'Personal Information'
    }
  ])
  const [showRedactions, setShowRedactions] = useState(false)

  const handleRedactionsChange = (newRedactions: Redaction[]) => {
    setRedactions(newRedactions)
  }

  const exportRedactions = () => {
    const dataStr = JSON.stringify(redactions, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    
    const exportFileDefaultName = 'redactions.json'
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
              Document Redaction Tool
            </h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Admin tool for redacting sensitive information from documents
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/admin/dashboard"
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              Back to Dashboard
            </Link>
            <ThemeToggle />
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">How to use:</h3>
          <ol className="list-decimal list-inside space-y-1 text-sm text-blue-800 dark:text-blue-400">
            <li>Click the redaction tool button (eye with slash icon) to enter redaction mode</li>
            <li>Click and drag on the document to create redaction boxes</li>
            <li>Click on existing redactions to select them, then delete if needed</li>
            <li>Use the clear button to remove all redactions</li>
            <li>Export redactions as JSON for permanent storage</li>
          </ol>
        </div>

        {/* Controls */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={showRedactions}
                  onChange={(e) => setShowRedactions(e.target.checked)}
                  className="rounded border-gray-300 dark:border-gray-600"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Preview with redactions
                </span>
              </label>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                Total redactions: {redactions.length}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={exportRedactions}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                disabled={redactions.length === 0}
              >
                Export Redactions
              </button>
            </div>
          </div>
        </div>

        {/* Document Viewer */}
        <div className="mb-8">
          <DocumentViewer
            documentUrl="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
            title="Sample Document for Redaction"
            redactedSections={showRedactions ? redactions : []}
            onRedactionsChange={handleRedactionsChange}
            allowRedaction={true}
          />
        </div>

        {/* Redaction List */}
        {redactions.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold mb-4">Redaction Details</h3>
            <div className="space-y-2">
              {redactions.map((redaction, index) => (
                <div key={redaction.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded">
                  <div className="text-sm">
                    <span className="font-medium">Redaction {index + 1}</span>
                    <span className="text-gray-600 dark:text-gray-400 ml-2">
                      Page {redaction.page} • 
                      Position: ({Math.round(redaction.x)}, {Math.round(redaction.y)}) • 
                      Size: {Math.round(redaction.width)}×{Math.round(redaction.height)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 