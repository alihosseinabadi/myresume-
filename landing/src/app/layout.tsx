import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? 'https://myresume.app'),
  title: 'MyResume Studio — write a CV that sounds like you',
  description:
    'One panel: type a job title, get recruiter-grade wording, restyle it across 11 templates in 24 languages, match it to the words the job ad uses, then export ATS-safe PDF or Word.',
  keywords: 'CV builder, resume builder, AI CV writer, ATS keywords, cover letter builder, CV templates',
  applicationName: 'MyResume Studio',
  category: 'productivity',
  alternates: { canonical: '/' },
  openGraph: {
    title: 'MyResume Studio — write a CV that sounds like you',
    description:
      'Type a job title. Get recruiter-grade wording, restyle it, match it to the ad, export it. One panel, no signup.',
    url: 'https://myresume.app',
    siteName: 'MyResume Studio',
    locale: 'en_GB',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'MyResume Studio',
    description: 'Write, restyle and export a CV in one panel',
  },
  robots: 'index, follow',
}

export const viewport: Viewport = {
  themeColor: '#07090C',
  colorScheme: 'dark',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    // The inline script below adds the `js` class to <html> before hydration, so
    // React would otherwise report an attribute mismatch on this element.
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Confirms JS before the reveal styles may hide content. */}
        <script
          dangerouslySetInnerHTML={{ __html: `document.documentElement.classList.add('js')` }}
        />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300..800&family=JetBrains+Mono:wght@400..600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="grain font-sans antialiased">
        <a
          href="#studio"
          className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[100] focus:rounded-lg focus:bg-pop focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-void"
        >
          Skip to the studio
        </a>
        {children}
      </body>
    </html>
  )
}
