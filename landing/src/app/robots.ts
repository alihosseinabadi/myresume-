import type { MetadataRoute } from 'next'

const SITE = process.env.NEXT_PUBLIC_SITE_URL ?? 'https://myresume.app'

export default function robots(): MetadataRoute.Robots {
  return {
    // `/c/<payload>` links are one person's CV brief: crawlable never, personal always.
    rules: { userAgent: '*', allow: '/', disallow: ['/api/', '/c/'] },
    sitemap: `${SITE}/sitemap.xml`,
  }
}
