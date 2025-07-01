'use client'

import Link from 'next/link'
import TypewriterTitle from '@/components/TypewriterTitle'
import ThemeToggle from '@/components/ThemeToggle'
import StatusBadge from '@/components/StatusBadge'

export default function DemoPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header Section */}
      <header className="main-header">
        <TypewriterTitle text="VISUAL DEMO" className="main-title" delay={100} />
        <p className="main-subtitle">Showcasing Enhanced Design Features</p>
      </header>

      {/* Navigation & Theme Toggle */}
      <div className="flex flex-col sm:flex-row justify-between items-center mb-16">
        <nav className="main-nav space-x-6 text-sm mb-6 sm:mb-0">
          <Link href="/" className="nav-link">Home</Link>
          <Link href="/about" className="nav-link">About</Link>
          <Link href="/archive" className="nav-link">Archive</Link>
          <Link href="/demo" className="nav-link font-bold">Demo</Link>
        </nav>
        <div className="flex items-center gap-4">
          <Link href="/submit" className="brand-button">
            Submit a Leak
          </Link>
          <ThemeToggle />
        </div>
      </div>

      {/* Main Content */}
      <main className="space-y-12">
        {/* Status Badges Section */}
        <section>
          <h2 className="text-2xl font-bold mb-6 brand-accent">Status Badges</h2>
          <div className="flex flex-wrap gap-3 mb-4">
            <StatusBadge type="breaking" />
            <StatusBadge type="exclusive" />
            <StatusBadge type="verified" />
            <StatusBadge type="new" />
            <StatusBadge type="updated" />
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            These badges can be used to highlight special content status
          </p>
        </section>

        {/* Typography Showcase */}
        <section>
          <h2 className="text-2xl font-bold mb-6 brand-accent">Enhanced Typography</h2>
          
          {/* Drop Cap Example */}
          <div className="mb-8">
            <h3 className="text-lg font-bold mb-3 font-mono-special">Drop Cap</h3>
            <p className="drop-cap text-lg leading-relaxed">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor 
              incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud 
              exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
            </p>
          </div>

          {/* Pull Quote Example */}
          <div className="mb-8">
            <h3 className="text-lg font-bold mb-3 font-mono-special">Pull Quote</h3>
            <blockquote className="pull-quote">
              The truth will set you free, but first it will make you miserable.
            </blockquote>
          </div>
        </section>

        {/* Dark Mode Comparison */}
        <section>
          <h2 className="text-2xl font-bold mb-6 brand-accent">Theme Toggle</h2>
          <p className="text-lg mb-4">
            Click the theme toggle button in the top navigation to switch between light and dark modes. 
            The dark mode features vintage sepia tones for a classic newspaper feel.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border-2 brand-border rounded-lg p-6">
              <h3 className="font-bold mb-2">Light Mode</h3>
              <p className="text-sm">
                Warm parchment background with deep burgundy accents
              </p>
            </div>
            <div className="border-2 brand-border rounded-lg p-6">
              <h3 className="font-bold mb-2">Dark Mode</h3>
              <p className="text-sm">
                Dark sepia tones with vintage newspaper aesthetic
              </p>
            </div>
          </div>
        </section>

        {/* Sample Article Card */}
        <section>
          <h2 className="text-2xl font-bold mb-6 brand-accent">Article Preview</h2>
          <article className="article-card group">
            <div className="article-link">
              <div className="flex items-center justify-between mb-2">
                <div className="case-file">
                  <span>Published: 15 Jan 2025</span>
                  {' | '}
                  <span>Case File: #LL-001-AAA</span>
                </div>
                <StatusBadge type="breaking" />
              </div>
              <h2 className="article-title text-3xl md:text-4xl leading-tight mb-4 transition-colors duration-300 ease-in-out">
                Sample Article with Visual Enhancements
              </h2>
              <p className="article-excerpt">
                This is a preview of how articles look with the new visual design system, 
                including status badges, improved typography, and dark mode support.
              </p>
              <div className="read-more group-hover:underline">
                Read More &rarr;
              </div>
            </div>
          </article>
        </section>

        {/* Animation Examples */}
        <section>
          <h2 className="text-2xl font-bold mb-6 brand-accent">Animations</h2>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-bold mb-2 font-mono-special">Typewriter Effect</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                Refresh the page to see the title animate with a typewriter effect
              </p>
            </div>
            <div>
              <h3 className="text-lg font-bold mb-2 font-mono-special">Hover Effects</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Hover over article titles and links to see smooth transitions
              </p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="main-footer">
        <p className="footer-text">&copy; 2025 LexLeaks. Visual Demo</p>
        <p className="footer-text mt-1">Showcasing enhanced design features</p>
      </footer>
    </div>
  )
} 