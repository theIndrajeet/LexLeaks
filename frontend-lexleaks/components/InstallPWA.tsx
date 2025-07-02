'use client'

import { useState, useEffect } from 'react'

export default function InstallPWA() {
  const [supportsPWA, setSupportsPWA] = useState(false)
  const [promptInstall, setPromptInstall] = useState<any>(null)
  const [isIOS, setIsIOS] = useState(false)
  const [isInStandaloneMode, setIsInStandaloneMode] = useState(false)

  useEffect(() => {
    // Check if already in standalone mode
    setIsInStandaloneMode(window.matchMedia('(display-mode: standalone)').matches)
    
    // Check if iOS
    setIsIOS(
      /iPad|iPhone|iPod/.test(navigator.userAgent) && !(window as any).MSStream
    )

    const handler = (e: any) => {
      e.preventDefault()
      console.log('PWA install prompt fired')
      setSupportsPWA(true)
      setPromptInstall(e)
    }

    window.addEventListener('beforeinstallprompt', handler)

    return () => window.removeEventListener('beforeinstallprompt', handler)
  }, [])

  const onClick = (evt: React.MouseEvent) => {
    evt.preventDefault()
    if (!promptInstall) {
      return
    }
    promptInstall.prompt()
  }

  // Don't show if already installed
  if (isInStandaloneMode) {
    return null
  }

  // iOS specific install instructions
  if (isIOS && !supportsPWA) {
    return (
      <div className="fixed bottom-4 right-4 z-50 max-w-sm">
        <div className="bg-[#fdf6e3] dark:bg-[#1a1612] border-2 brand-border rounded-lg shadow-lg p-4">
          <div className="flex items-start">
            <div className="flex-1">
              <h3 className="font-mono-special text-sm font-bold brand-text mb-2">
                Install LexLeaks App
              </h3>
              <p className="text-xs brand-text opacity-80 mb-2">
                Tap the share button <span className="inline-block">⎙</span> and select "Add to Home Screen"
              </p>
            </div>
            <button
              onClick={() => setIsIOS(false)}
              className="ml-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            >
              ×
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Standard install prompt
  if (!supportsPWA) {
    return null
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <button
        className="flex items-center gap-2 px-6 py-3 bg-[#8B0000] dark:bg-[#d4766f] text-white rounded-lg shadow-lg hover:bg-[#a50000] dark:hover:bg-[#c56660] transition-colors font-mono-special text-sm"
        onClick={onClick}
      >
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
        Install LexLeaks App
      </button>
    </div>
  )
} 