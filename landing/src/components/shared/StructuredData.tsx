import { FAQS, PRICING, TRUSTPILOT } from '@/lib/marketing'
import { TEMPLATES } from '@/lib/templates'
import { TOOLS } from '@/lib/content'

const SITE = process.env.NEXT_PUBLIC_SITE_URL ?? 'https://myresume.app'

/** JSON-LD: WebApplication + FAQPage, so search engines can surface rich results. */
export default function StructuredData() {
  const graph = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'WebApplication',
        '@id': `${SITE}/#app`,
        name: 'MyResume',
        url: SITE,
        applicationCategory: 'BusinessApplication',
        operatingSystem: 'Any',
        description:
          'Create a recruiter-ready CV online with AI-assisted wording, recruiter-approved templates and ATS-safe PDF or Word export.',
        offers: PRICING.map((plan) => ({
          '@type': 'Offer',
          name: plan.name,
          price: plan.price.replace(/[^0-9.]/g, ''),
          priceCurrency: 'EUR',
          description: plan.note,
        })),
        aggregateRating: {
          '@type': 'AggregateRating',
          ratingValue: TRUSTPILOT.score,
          reviewCount: '3000',
          bestRating: '5',
        },
        featureList: TOOLS.map((tool) => tool.name),
      },
      {
        '@type': 'FAQPage',
        '@id': `${SITE}/#faq`,
        mainEntity: FAQS.map((faq) => ({
          '@type': 'Question',
          name: faq.q,
          acceptedAnswer: { '@type': 'Answer', text: faq.a },
        })),
      },
      {
        '@type': 'ItemList',
        '@id': `${SITE}/#templates`,
        name: 'CV templates',
        numberOfItems: TEMPLATES.length,
        itemListElement: TEMPLATES.map((template, index) => ({
          '@type': 'ListItem',
          position: index + 1,
          name: `${template.name} CV template`,
          description: template.tagline,
        })),
      },
    ],
  }

  return (
    <script
      type="application/ld+json"
      // Structured data is generated from our own content constants.
      dangerouslySetInnerHTML={{ __html: JSON.stringify(graph) }}
    />
  )
}
