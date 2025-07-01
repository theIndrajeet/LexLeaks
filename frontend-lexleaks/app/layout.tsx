import './globals.css'
import { Metadata } from 'next'
import { ThemeProvider } from '@/contexts/ThemeContext'

export const metadata: Metadata = {
  title: {
    default: 'LexLeaks - Exposing Legal Industry Secrets',
    template: '%s | LexLeaks'
  },
  description: 'A secure platform for whistleblowing in the legal industry. Exposing corruption, misconduct, and unethical practices.',
  keywords: ['whistleblowing', 'legal industry', 'corruption', 'transparency', 'ethics'],
  authors: [{ name: 'LexLeaks Team' }],
  creator: 'LexLeaks',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://lexleaks.com',
    title: 'LexLeaks - Exposing Legal Industry Secrets',
    description: 'A secure platform for whistleblowing in the legal industry.',
    siteName: 'LexLeaks',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'LexLeaks - Exposing Legal Industry Secrets',
    description: 'A secure platform for whistleblowing in the legal industry.',
    creator: '@lexleaks',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className="h-full brand-bg antialiased">
        <ThemeProvider>
          <div className="min-h-full">
            {children}
          </div>
        </ThemeProvider>
      </body>
    </html>
  )
} 