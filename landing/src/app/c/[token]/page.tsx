import type { Metadata } from 'next'
import Icon from '@/components/shared/Icon'
import Logo from '@/components/shared/Logo'
import GiftHero from '@/components/share/GiftHero'
import Studio from '@/components/studio/Studio'
import { decodeBrief, firstName } from '@/lib/share'

/**
 * A shared CV brief: `/c/<base64url payload>`.
 *
 * The payload carries the whole brief, so this page needs no database and no
 * session — it decodes, greets the recipient, and opens the studio pre-filled.
 * These links are personal, so they are kept out of the index and out of the
 * sitemap, but the preview cards still get a real title for chat apps.
 */

type PageProps = { params: Promise<{ token: string }> }

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { token } = await params
  const brief = decodeBrief(token)

  if (!brief) {
    return {
      title: 'This CV link is incomplete — MyResume Studio',
      robots: { index: false, follow: false },
    }
  }

  const sender = firstName(brief.from) || 'A friend'
  const title = brief.role
    ? `${sender} sent you a CV written for ${brief.role}`
    : `${sender} sent you a CV brief`
  const description =
    brief.note ||
    `Open the link and the CV is already briefed${brief.role ? ` for ${brief.role}` : ''} — template, language and advert included.`

  return {
    title,
    description,
    alternates: { canonical: `/c/${token}` },
    // One person's link belongs to that person, not to a search engine.
    robots: { index: false, follow: true },
    openGraph: { title, description, type: 'article' },
    twitter: { card: 'summary_large_image', title, description },
  }
}

export default async function SharedCvPage({ params }: PageProps) {
  const { token } = await params
  const brief = decodeBrief(token)

  return (
    <>
      <ShareHeader />
      <main>
        {brief ? <GiftHero brief={brief} /> : <BrokenLink />}
        <section className="shell py-12 md:py-16">
          <Studio brief={brief ?? undefined} />
        </section>
      </main>
      <footer className="shell border-t border-line2 py-8">
        <p className="font-mono text-[11px] leading-relaxed text-dimmer">
          Built by the offline engine or your own AI provider · PDF, DOCX and TXT export ·{' '}
          <a href="/" className="text-pop transition hover:text-text">
            myresume.app
          </a>
        </p>
      </footer>
    </>
  )
}

/** Slim header: the main nav anchors only exist on the landing page. */
function ShareHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-line bg-void/85 backdrop-blur-xl">
      <nav className="shell flex h-16 items-center justify-between gap-4">
        <a href="/" aria-label="MyResume Studio home">
          <Logo />
        </a>
        <a
          href="/"
          className="inline-flex items-center gap-2 rounded-pill border border-line px-4 py-2 font-mono text-[11px] uppercase tracking-[0.14em] text-dim transition hover:border-pop/50 hover:text-text"
        >
          <Icon name="link" className="h-3.5 w-3.5" />
          full studio
        </a>
      </nav>
    </header>
  )
}

/** Shown when the payload is truncated or unreadable — common in chat apps. */
function BrokenLink() {
  return (
    <section className="shell pt-12">
      <div className="panel p-6 sm:p-8">
        <span className="grid h-12 w-12 place-items-center rounded-2xl border border-line text-dim">
          <Icon name="link" className="h-6 w-6" />
        </span>
        <span className="eyebrow mt-5 block">Link not recognised</span>
        <h1 className="display mt-3 text-[2.1rem] text-text sm:text-[2.7rem]">
          This CV link did not survive the trip.
        </h1>
        <p className="mt-3 max-w-xl text-[15px] leading-relaxed text-dim">
          Chat apps sometimes shorten or wrap long links. Ask whoever sent it to share it
          again — or start from scratch below and paste the advert yourself.
        </p>
      </div>
    </section>
  )
}
