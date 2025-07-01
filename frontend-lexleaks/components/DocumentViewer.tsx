'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/esm/Page/AnnotationLayer.css'
import 'react-pdf/dist/esm/Page/TextLayer.css'

// Set up the worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`

export interface Redaction {
  id: string
  page: number
  x: number
  y: number
  width: number
  height: number
  reason?: string
}

interface DocumentViewerProps {
  documentUrl: string
  title: string
  redactedSections?: Redaction[]
  onRedactionsChange?: (redactions: Redaction[]) => void
  allowRedaction?: boolean
}

export default function DocumentViewer({ 
  documentUrl, 
  title, 
  redactedSections = [], 
  onRedactionsChange,
  allowRedaction = false 
}: DocumentViewerProps) {
  const [numPages, setNumPages] = useState<number | null>(null)
  const [pageNumber, setPageNumber] = useState(1)
  const [scale, setScale] = useState(1.0)
  const [isRedactionMode, setIsRedactionMode] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [rotation, setRotation] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Interactive redaction state
  const [localRedactions, setLocalRedactions] = useState<Redaction[]>(redactedSections)
  const [isDrawing, setIsDrawing] = useState(false)
  const [drawStart, setDrawStart] = useState<{ x: number; y: number } | null>(null)
  const [currentRedaction, setCurrentRedaction] = useState<Partial<Redaction> | null>(null)
  const [selectedRedactionId, setSelectedRedactionId] = useState<string | null>(null)
  
  const pageRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setLocalRedactions(redactedSections)
  }, [redactedSections])

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages)
    setIsLoading(false)
    setError(null)
  }

  const onDocumentLoadError = (error: Error) => {
    setError(error.message)
    setIsLoading(false)
  }

  const changePage = (offset: number) => {
    setPageNumber(prevPageNumber => {
      const newPageNumber = prevPageNumber + offset
      return Math.max(1, Math.min(newPageNumber, numPages || 1))
    })
  }

  const handlePageInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10)
    if (value && value >= 1 && value <= (numPages || 1)) {
      setPageNumber(value)
    }
  }

  const zoomIn = () => setScale(prev => Math.min(prev + 0.2, 3))
  const zoomOut = () => setScale(prev => Math.max(prev - 0.2, 0.5))
  const resetZoom = () => setScale(1.0)
  
  const rotate = () => setRotation(prev => (prev + 90) % 360)

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.getElementById('pdf-container')?.requestFullscreen()
      setIsFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsFullscreen(false)
    }
  }

  const downloadDocument = () => {
    const link = document.createElement('a')
    link.href = documentUrl
    link.download = `${title}.pdf`
    link.click()
  }

  // Interactive redaction functions
  const handleMouseDown = (e: React.MouseEvent) => {
    if (!isRedactionMode || !allowRedaction || !pageRef.current) return
    
    const rect = pageRef.current.getBoundingClientRect()
    const x = (e.clientX - rect.left) / scale
    const y = (e.clientY - rect.top) / scale
    
    setIsDrawing(true)
    setDrawStart({ x, y })
    setCurrentRedaction({
      id: `redaction-${Date.now()}`,
      page: pageNumber,
      x,
      y,
      width: 0,
      height: 0
    })
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDrawing || !drawStart || !pageRef.current || !currentRedaction) return
    
    const rect = pageRef.current.getBoundingClientRect()
    const currentX = (e.clientX - rect.left) / scale
    const currentY = (e.clientY - rect.top) / scale
    
    const width = Math.abs(currentX - drawStart.x)
    const height = Math.abs(currentY - drawStart.y)
    const x = Math.min(drawStart.x, currentX)
    const y = Math.min(drawStart.y, currentY)
    
    setCurrentRedaction({
      ...currentRedaction,
      x,
      y,
      width,
      height
    })
  }

  const handleMouseUp = () => {
    if (!isDrawing || !currentRedaction) return
    
    setIsDrawing(false)
    
    if (currentRedaction.width! > 5 && currentRedaction.height! > 5) {
      const newRedaction = currentRedaction as Redaction
      const updatedRedactions = [...localRedactions, newRedaction]
      setLocalRedactions(updatedRedactions)
      
      if (onRedactionsChange) {
        onRedactionsChange(updatedRedactions)
      }
    }
    
    setCurrentRedaction(null)
    setDrawStart(null)
  }

  const handleRedactionClick = (redactionId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!allowRedaction) return
    setSelectedRedactionId(redactionId)
  }

  const deleteRedaction = (redactionId: string) => {
    const updatedRedactions = localRedactions.filter(r => r.id !== redactionId)
    setLocalRedactions(updatedRedactions)
    setSelectedRedactionId(null)
    
    if (onRedactionsChange) {
      onRedactionsChange(updatedRedactions)
    }
  }

  const clearAllRedactions = () => {
    setLocalRedactions([])
    setSelectedRedactionId(null)
    
    if (onRedactionsChange) {
      onRedactionsChange([])
    }
  }

  const renderPage = useCallback((pageNum: number) => {
    const pageRedactions = localRedactions.filter(r => r.page === pageNum)
    const isCurrentPageDrawing = isDrawing && currentRedaction?.page === pageNum
    
    return (
      <div 
        ref={pageRef}
        className="relative inline-block"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ cursor: isRedactionMode && allowRedaction ? 'crosshair' : 'default' }}
      >
        <Page
          pageNumber={pageNum}
          scale={scale}
          rotate={rotation}
          renderTextLayer={true}
          renderAnnotationLayer={true}
        />
        
        {/* Render existing redactions */}
        {pageRedactions.map((redaction) => (
          <div
            key={redaction.id}
            className={`absolute bg-black ${
              selectedRedactionId === redaction.id ? 'ring-2 ring-red-500' : ''
            } ${allowRedaction && isRedactionMode ? 'cursor-pointer hover:opacity-80' : ''}`}
            style={{
              left: `${redaction.x * scale}px`,
              top: `${redaction.y * scale}px`,
              width: `${redaction.width * scale}px`,
              height: `${redaction.height * scale}px`,
              transform: `rotate(${rotation}deg)`,
              transformOrigin: 'top left'
            }}
            onClick={(e) => handleRedactionClick(redaction.id, e)}
          />
        ))}
        
        {/* Render current drawing redaction */}
        {isCurrentPageDrawing && currentRedaction && (
          <div
            className="absolute bg-black opacity-50 pointer-events-none"
            style={{
              left: `${currentRedaction.x! * scale}px`,
              top: `${currentRedaction.y! * scale}px`,
              width: `${currentRedaction.width! * scale}px`,
              height: `${currentRedaction.height! * scale}px`,
              transform: `rotate(${rotation}deg)`,
              transformOrigin: 'top left'
            }}
          />
        )}
      </div>
    )
  }, [scale, rotation, localRedactions, isDrawing, currentRedaction, selectedRedactionId, isRedactionMode, allowRedaction])

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg overflow-hidden">
      {/* Toolbar */}
      <div className="bg-gray-100 dark:bg-gray-800 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => changePage(-1)}
              disabled={pageNumber <= 1}
              className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              title="Previous page"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            
            <div className="flex items-center gap-2 text-sm">
              <input
                type="number"
                min="1"
                max={numPages || 1}
                value={pageNumber}
                onChange={handlePageInput}
                className="w-16 px-2 py-1 border rounded dark:bg-gray-700 dark:border-gray-600"
              />
              <span className="text-gray-600 dark:text-gray-400">
                of {numPages || '...'}
              </span>
            </div>

            <button
              onClick={() => changePage(1)}
              disabled={!numPages || pageNumber >= numPages}
              className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              title="Next page"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <div className="flex items-center gap-2">
            {/* Zoom controls */}
            <button
              onClick={zoomOut}
              className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
              title="Zoom out"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
              </svg>
            </button>
            
            <span className="text-sm text-gray-600 dark:text-gray-400 min-w-[50px] text-center">
              {Math.round(scale * 100)}%
            </span>
            
            <button
              onClick={zoomIn}
              className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
              title="Zoom in"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
              </svg>
            </button>
            
            <button
              onClick={resetZoom}
              className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
              title="Reset zoom"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>

            <div className="w-px h-6 bg-gray-300 dark:bg-gray-600" />

            {/* Other tools */}
            <button
              onClick={rotate}
              className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
              title="Rotate"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>

            {allowRedaction && (
              <>
                <button
                  onClick={() => setIsRedactionMode(!isRedactionMode)}
                  className={`p-2 rounded ${
                    isRedactionMode 
                      ? 'bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400' 
                      : 'hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                  title={isRedactionMode ? "Exit redaction mode" : "Enter redaction mode"}
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                </button>

                {localRedactions.length > 0 && (
                  <button
                    onClick={clearAllRedactions}
                    className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 text-red-600 dark:text-red-400"
                    title="Clear all redactions"
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                )}
              </>
            )}

            <button
              onClick={toggleFullscreen}
              className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
              title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {isFullscreen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                )}
              </svg>
            </button>

            <button
              onClick={downloadDocument}
              className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
              title="Download"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Document Viewer */}
      <div 
        id="pdf-container"
        className="relative bg-gray-50 dark:bg-gray-950 overflow-auto"
        style={{ height: isFullscreen ? '100vh' : '600px' }}
      >
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        )}
        
        {error && (
          <div className="absolute inset-0 flex items-center justify-center p-8">
            <div className="text-center">
              <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <p className="text-gray-600 dark:text-gray-400">Failed to load document</p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">{error}</p>
            </div>
          </div>
        )}

        <div className="flex justify-center p-4">
          <Document
            file={documentUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={onDocumentLoadError}
            loading={null}
            className="max-w-full"
          >
            {renderPage(pageNumber)}
          </Document>
        </div>

        {/* Redaction Mode Indicator and Controls */}
        {isRedactionMode && !isLoading && allowRedaction && (
          <div className="absolute top-4 left-4 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 px-3 py-1 rounded-full text-sm font-medium">
            Redaction Mode Active - Click and drag to redact
          </div>
        )}

        {/* Selected Redaction Controls */}
        {selectedRedactionId && allowRedaction && (
          <div className="absolute bottom-4 left-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-3 flex items-center gap-2">
            <span className="text-sm text-gray-600 dark:text-gray-400">Redaction selected</span>
            <button
              onClick={() => deleteRedaction(selectedRedactionId)}
              className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
            >
              Delete
            </button>
            <button
              onClick={() => setSelectedRedactionId(null)}
              className="px-3 py-1 bg-gray-200 dark:bg-gray-700 rounded text-sm hover:bg-gray-300 dark:hover:bg-gray-600"
            >
              Cancel
            </button>
          </div>
        )}

        {/* Redaction Count */}
        {localRedactions.length > 0 && (
          <div className="absolute top-4 right-4 bg-gray-100 dark:bg-gray-800 px-3 py-1 rounded-full text-sm">
            {localRedactions.filter(r => r.page === pageNumber).length} redactions on this page
          </div>
        )}
      </div>
    </div>
  )
} 