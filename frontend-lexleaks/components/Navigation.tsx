'use client'

import Link from 'next/link'
import SupabaseAuthButton from './SupabaseAuthButton'
import ThemeToggle from './ThemeToggle'

interface NavigationProps {
  currentPage?: string
  showSubmitButton?: boolean
  className?: string
}

export default function Navigation({ 
  currentPage, 
  showSubmitButton = true, 
  className = '' 
}: NavigationProps) {
  // Navigation component with JurisBrain AI link
  const navLinks = [
    { href: '/', label: 'Home' },
    { href: '/about', label: 'About' },
    { href: '/archive', label: 'Archive' },
    { href: '/find-case', label: 'Find Case' },
    { href: '/legal-ai', label: 'Deep Research' },
    { href: '/opportunities', label: 'Opportunities' }
  ]

  return (
    <div className={`flex flex-col lg:flex-row justify-between items-center mb-16 gap-6 ${className}`}>
      <nav className="main-nav flex flex-wrap justify-center gap-6 text-sm">
        {navLinks.map((link) => (
          <Link 
            key={link.href}
            href={link.href} 
            className={`nav-link ${currentPage === link.href ? 'brand-accent font-bold' : ''}`}
          >
            {link.label}
          </Link>
        ))}
      </nav>
      <div className="flex items-center gap-3">
            <SupabaseAuthButton />
        {showSubmitButton && (
          <Link href="/submit" className="brand-button">
            Submit a Leak
          </Link>
        )}
        <ThemeToggle />
      </div>
    </div>
  )
}
