/**
 * Shareable "CV brief" links.
 *
 * A job advert, template and language are packed into a compact base64url payload
 * that travels inside the URL itself (`/c/<payload>`), so a shared CV needs no
 * database, no account and no session to open. The sender can paste the result
 * into WhatsApp, LinkedIn or email, and the recipient lands on a page that is
 * already written for them.
 *
 * A link's payload is attacker-controllable, so `decodeBrief` treats it as
 * hostile input: unknown keys are dropped, every string is clamped, and the
 * template/locale must match a real catalogue entry.
 */

import { LOCALES } from './seo'
import { TEMPLATES } from './templates'

export const SHARE_VERSION = 1

/** Longest each field may be inside a link, so URLs stay pasteable. */
const LIMITS = {
  name: 48,
  role: 80,
  url: 400,
  text: 700,
  note: 180,
} as const

export type ShareBrief = {
  /** Who sent the link. */
  from?: string
  /** Who it is for — this becomes the name on the CV. */
  to?: string
  /** The role the CV should be written for. */
  role?: string
  /** Advert URL, when the sender built the CV from a job link. */
  url?: string
  /** Advert text, when the sender pasted it (only carried when there is no URL). */
  text?: string
  /** Template id, validated against the catalogue. */
  template?: string
  /** Locale code, validated against the locale list. */
  locale?: string
  /** Short personal note, shown to the recipient. */
  note?: string
}

/** Trim, collapse runs of whitespace and clamp to a field limit. */
function clean(value: unknown, limit: number): string {
  if (typeof value !== 'string') return ''
  return value.replace(/\s+/g, ' ').trim().slice(0, limit)
}

/** Keep only absolute http(s) links — anything else is dropped. */
function httpUrl(value: unknown): string {
  const cleaned = clean(value, LIMITS.url)
  return /^https?:\/\/\S+$/i.test(cleaned) ? cleaned : ''
}

function toBase64Url(bytes: Uint8Array): string {
  let binary = ''
  for (let index = 0; index < bytes.length; index += 1) {
    binary += String.fromCharCode(bytes[index])
  }
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

function fromBase64Url(token: string): Uint8Array {
  const padded = token.replace(/-/g, '+').replace(/_/g, '/')
  const binary = atob(padded + '='.repeat((4 - (padded.length % 4)) % 4))
  const bytes = new Uint8Array(binary.length)
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index)
  }
  return bytes
}

/** Encode a brief. Empty fields are omitted, which keeps links short. */
export function encodeBrief(brief: ShareBrief): string {
  const payload: Record<string, string | number> = { v: SHARE_VERSION }
  const put = (key: keyof ShareBrief, value: string | undefined, limit: number) => {
    const cleaned = clean(value, limit)
    if (cleaned) payload[key] = cleaned
  }

  put('from', brief.from, LIMITS.name)
  put('to', brief.to, LIMITS.name)
  put('role', brief.role, LIMITS.role)
  const url = httpUrl(brief.url)
  if (url) payload.url = url
  put('text', brief.text, LIMITS.text)
  if (TEMPLATES.some((item) => item.id === brief.template)) payload.template = brief.template as string
  if (LOCALES.some((item) => item.code === brief.locale)) payload.locale = brief.locale as string
  put('note', brief.note, LIMITS.note)

  return toBase64Url(new TextEncoder().encode(JSON.stringify(payload)))
}

/**
 * Decode a link payload. Returns `null` for anything malformed, truncated or
 * hostile, so the page can show a friendly explanation instead of throwing.
 */
export function decodeBrief(token: string): ShareBrief | null {
  if (!token || token.length > 4000) return null

  let parsed: unknown
  try {
    parsed = JSON.parse(new TextDecoder().decode(fromBase64Url(token)))
  } catch {
    return null
  }
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return null

  const data = parsed as Record<string, unknown>
  if (data.v !== SHARE_VERSION) return null

  const brief: ShareBrief = {
    from: clean(data.from, LIMITS.name),
    to: clean(data.to, LIMITS.name),
    role: clean(data.role, LIMITS.role),
    url: httpUrl(data.url),
    text: clean(data.text, LIMITS.text),
    template: TEMPLATES.some((item) => item.id === data.template) ? String(data.template) : '',
    locale: LOCALES.some((item) => item.code === data.locale) ? String(data.locale) : '',
    note: clean(data.note, LIMITS.note),
  }

  // A link with nothing usable in it is not worth a page.
  if (!brief.role && !brief.url && !brief.text && !brief.note) return null
  return brief
}

/** The path a sender shares. */
export function sharePath(brief: ShareBrief): string {
  return `/c/${encodeBrief(brief)}`
}

/** The absolute link a sender shares. */
export function shareUrl(brief: ShareBrief, origin: string): string {
  return `${origin.replace(/\/$/, '')}${sharePath(brief)}`
}

/** First name only — used for the greeting and bylines. */
export function firstName(value?: string): string {
  return clean(value, LIMITS.name).split(' ')[0] ?? ''
}

/** Readable host for a job link (`jobs.acme.com`), for the chips. */
export function hostOf(url?: string): string {
  const cleaned = httpUrl(url)
  if (!cleaned) return ''
  try {
    return new URL(cleaned).hostname.replace(/^www\./, '')
  } catch {
    return ''
  }
}

/** What the studio input should show when a brief arrives from a link. */
export function briefToInput(brief?: ShareBrief): string {
  if (!brief) return ''
  return brief.url || brief.text || brief.role || ''
}

/** Inputs the sender's studio already knows about. */
export type StudioSeed = {
  from?: string
  to?: string
  note?: string
  role?: string
  jobUrl?: string
  advertText?: string
  template?: string
  locale?: string
}

/**
 * Build the brief a sender shares.
 *
 * A URL brief makes the recipient re-read the advert, which keeps the company
 * and location on their CV; pasted advert text is only carried when that is all
 * the sender had, so the recipient's build never depends on scraping.
 */
export function briefFromStudio(seed: StudioSeed): ShareBrief {
  return {
    from: seed.from ?? '',
    to: seed.to ?? '',
    note: seed.note ?? '',
    role: seed.role ?? '',
    url: seed.jobUrl ?? '',
    text: seed.jobUrl ? '' : seed.advertText ?? '',
    template: seed.template ?? '',
    locale: seed.locale ?? '',
  }
}
