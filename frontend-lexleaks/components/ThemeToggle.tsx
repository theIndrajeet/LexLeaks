'use client'

import { useTheme } from '@/contexts/ThemeContext'

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()

  return (
    <button
      onClick={toggleTheme}
      className="relative w-12 h-12 rounded-full bg-gray-200 dark:bg-gray-800 flex items-center justify-center transition-all duration-300 hover:scale-110"
      aria-label="Toggle theme"
    >
      {/* Sun icon for light mode */}
      <svg
        className={`absolute w-6 h-6 text-yellow-500 transition-all duration-300 ${
          theme === 'light' ? 'opacity-100 rotate-0' : 'opacity-0 rotate-90'
        }`}
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
        />
      </svg>

      {/* Moon icon for dark mode */}
      <svg
        className={`absolute w-6 h-6 text-amber-200 transition-all duration-300 ${
          theme === 'dark' ? 'opacity-100 rotate-0' : 'opacity-0 -rotate-90'
        }`}
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
        />
      </svg>
    </button>
  )
} 