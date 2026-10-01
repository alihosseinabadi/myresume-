'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import Icon from '@/components/shared/Icon'
import { LOCALES } from '@/lib/seo'
import { TEMPLATES } from '@/lib/templates'
import {
  briefFromStudio,
  firstName,
  hostOf,
  shareUrl,
  type StudioSeed,
} from '@/lib/share'

/**
 * "Send as a link": the sender's job advert, template and language are packed
 * into the URL, so whoever opens it lands on a CV brief that is already theirs.
 */
export default function ShareLink({ seed }: { seed: StudioSeed }) {
  const [open, setOpen] = useState(false)
  const [from, setFrom] = useState(seed.from ?? '')
  const [to, setTo] = useState(seed.to ?? '')
  const [note, setNote] = useState(seed.note ?? '')
  const [origin, setOrigin] = useState('')
  const [copied, setCopied] = useState(false)
  const [canShare, setCanShare] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  // `window` is client-only state: reading it while rendering would desync SSR.
  useEffect(() => {
    setOrigin(window.location.origin)
    setCanShare(typeof navigator.share === 'function')
  }, [])

  const brief = useMemo(
    () => briefFromStudio({ ...seed, from, to, note }),
    [seed, from, to, note],
  )
  const link = useMemo(() => shareUrl(brief, origin), [origin, brief])

  const template = TEMPLATES.find((item) => item.id === brief.template)
  const language = LOCALES.find((item) => item.code === brief.locale)
  const host = hostOf(brief.url)
  const sender = firstName(from)

  const facets = [
    brief.role ? { label: 'role', value: brief.role } : null,
    host ? { label: 'advert', value: host } : null,
    !host && brief.text ? { label: 'advert', value: 'pasted text' } : null,
    template ? { label: 'template', value: template.name } : null,
    language ? { label: 'language', value: language.label } : null,
  ].filter(Boolean) as { label: string; value: string }[]

  async function copy() {
    try {
      await navigator.clipboard.writeText(link)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 2200)
    } catch {
      // Clipboard permission can be denied — let the sender copy by hand.
      inputRef.current?.select()
    }
  }

  async function shareNatively() {
    try {
      await navigator.share({
        title: sender ? `${sender} sent you a CV brief` : 'A CV brief for you',
        text: note || 'Open this link and your CV is already half-built.',
        url: link,
      })
    } catch {
      // Dismissing the share sheet is not an error.
    }
  }

  return (
    <div className="mt-6 rounded-2xl border border-line bg-void/50 p-5">

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <span className="eyebrow">Send it on</span>
          <h4 className="display mt-2 text-2xl text-text">Hand this CV over as a link.</h4>
          <p className="mt-2 max-w-md text-[13px] leading-relaxed text-dim">
            The advert, the template and the language travel inside the URL. Whoever opens
            it gets the same brief, their own name on the page, and a CV they can download
            in one click — no account for either of you.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setOpen((value) => !value)}
          aria-expanded={open}
          className={`inline-flex shrink-0 items-center gap-2 rounded-pill px-5 py-3 text-sm font-bold transition ${
            open
              ? 'border border-line text-dim hover:border-pop/50 hover:text-text'
              : 'btn-primary'
          }`}
        >
          <Icon name="share" className="h-4 w-4" />
          {open ? 'Hide the link' : 'Send as a link'}
        </button>
      </div>

      {open && (
        <div className="mt-5 border-t border-line2 pt-5">
          <div className="grid gap-3 sm:grid-cols-2">
            <Field
              label="Your name"
              hint="signs the link"
              value={from}
              onChange={setFrom}
              placeholder="Sara"
            />
            <Field
              label="Their name"
              hint="printed on their CV"
              value={to}
              onChange={setTo}
              placeholder="Alex"
            />
          </div>

          <div className="mt-3">
            <Field
              label="One line for them"
              hint="optional"
              value={note}
              onChange={setNote}
              placeholder="Saw this and thought of you — go get it."
            />
          </div>

          <div className="mt-4 flex flex-col gap-2 sm:flex-row">
            <input
              ref={inputRef}
              readOnly
              value={link}
              onFocus={(event) => event.currentTarget.select()}
              aria-label="Your shareable CV link"
              className="w-full min-w-0 rounded-xl border border-line bg-void/60 px-3.5 py-3 font-mono text-[11px] text-dim outline-none transition focus:border-pop"
            />
            <button
              type="button"
              onClick={copy}
              className="btn-primary inline-flex shrink-0 items-center justify-center gap-2 rounded-xl px-5 py-3 text-sm font-bold"
            >
              <Icon name={copied ? 'check' : 'copy'} className="h-4 w-4" />
              {copied ? 'Link copied' : 'Copy link'}
            </button>
            {canShare && (
              <button
                type="button"
                onClick={shareNatively}
                className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl border border-line px-5 py-3 text-sm font-semibold text-text transition hover:border-pop/50"
              >
                <Icon name="share" className="h-4 w-4" />
                Share
              </button>
            )}
          </div>

          <div className="mt-4 flex flex-wrap items-center gap-2">
            <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-dimmer">
              baked into the link
            </span>
            {facets.map((facet) => (
              <span
                key={facet.label}
                className="rounded-lg border border-line bg-panel/70 px-2.5 py-1 text-[11px] text-dim"
              >
                <span className="font-mono text-[10px] uppercase tracking-wider text-dimmer">
                  {facet.label}
                </span>{' '}
                {facet.value}
              </span>
            ))}
            <a
              href={link}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 font-mono text-[11px] text-pop transition hover:text-text"
            >
              open it yourself
              <Icon name="arrow" className="h-3 w-3" />
            </a>
          </div>

          <p className="mt-3 font-mono text-[10px] leading-relaxed text-dimmer">
            Nothing is stored on our side — the whole brief lives in the URL, so the link
            works for anyone who opens it.
          </p>
        </div>
      )}
    </div>
  )
}

/** One labelled input in the share panel. */
function Field({
  label,
  hint,
  value,
  onChange,
  placeholder,
}: {
  label: string
  hint: string
  value: string
  onChange: (value: string) => void
  placeholder: string
}) {
  return (
    <label className="block">
      <span className="flex items-baseline gap-2">
        <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-dimmer">
          {label}
        </span>
        <span className="font-mono text-[10px] text-dimmer/70">{hint}</span>
      </span>
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        aria-label={label}
        className="mt-1.5 w-full rounded-xl border border-line bg-void/60 px-3.5 py-2.5 text-sm text-text outline-none transition placeholder:text-dimmer focus:border-pop"
      />
    </label>
  )
}
