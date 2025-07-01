'use client'

import { useState, useEffect } from 'react'

interface TypewriterTitleProps {
  text: string
  className?: string
  delay?: number
}

export default function TypewriterTitle({ text, className = '', delay = 100 }: TypewriterTitleProps) {
  const [displayText, setDisplayText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)
  const [showCursor, setShowCursor] = useState(true)

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayText(prev => prev + text[currentIndex])
        setCurrentIndex(prev => prev + 1)
      }, delay)
      return () => clearTimeout(timeout)
    }
  }, [currentIndex, delay, text])

  // Blinking cursor effect
  useEffect(() => {
    const interval = setInterval(() => {
      setShowCursor(prev => !prev)
    }, 500)
    return () => clearInterval(interval)
  }, [])

  return (
    <h1 className={`${className} relative`}>
      {displayText}
      <span
        className={`inline-block w-1 h-full bg-current ml-1 transition-opacity duration-100 ${
          showCursor ? 'opacity-100' : 'opacity-0'
        }`}
        style={{ verticalAlign: 'text-bottom' }}
      />
    </h1>
  )
}